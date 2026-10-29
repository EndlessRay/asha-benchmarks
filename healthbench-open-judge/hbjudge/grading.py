"""Grade HealthBench completions and aggregate exactly as simple-evals does.

Per example: achieved points (met criteria, negative points included) divided
by the sum of positive points, unclipped. Overall and per-tag: mean of the
example scores clipped to [0, 1], with a 1,000-sample bootstrap std. Example
tags (themes, physician categories) score the whole example; rubric tags
(axes) score only the criteria carrying the tag.

Missing grades are never converted into verdicts. An example with any
missing grade is excluded from the scores and listed in the summary, with the
score the run would have had if missing grades counted as "not met".
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import __version__
from .client import Client
from .judges import Profile
from .polarity import is_flip, is_omission
from .template import TEMPLATE_SHA256, render, rubric_str


def example_score(rubrics: list[dict], met: list[bool | None]) -> float | None:
    possible = sum(r["points"] for r in rubrics if r["points"] > 0)
    if possible <= 0 or any(m is None for m in met):
        return None
    # a panel verdict is the mean of its judges' verdicts, so met may be fractional
    return sum(r["points"] * float(m) for r, m in zip(rubrics, met)) / possible


def clipped_stats(values: list[float], seed: int = 0) -> dict:
    if not values:
        return {"mean": None, "n": 0, "bootstrap_std": None}
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    boots = np.clip(v[rng.integers(0, len(v), size=(1000, len(v)))].mean(axis=1), 0, 1)
    return {"mean": float(np.clip(v.mean(), 0, 1)), "n": int(len(v)), "bootstrap_std": float(boots.std())}


def aggregate(graded: list[dict]) -> dict:
    overall, ex_tags, rb_tags = [], defaultdict(list), defaultdict(list)
    for g in graded:
        met = [x["criteria_met"] for x in g["rubric_grades"]]
        s = example_score(g["rubrics"], met)
        if s is None:
            continue
        overall.append(s)
        for t in g.get("example_tags", []):
            ex_tags[t].append(s)
        by_tag = defaultdict(lambda: ([], []))
        for rb, m in zip(g["rubrics"], met):
            for t in rb.get("tags", []):
                by_tag[t][0].append(rb)
                by_tag[t][1].append(m)
        for t, (rbs, ms) in by_tag.items():
            ts = example_score(rbs, ms)
            if ts is not None:
                rb_tags[t].append(ts)
    return {
        "score": clipped_stats(overall),
        "example_tags": {t: clipped_stats(v) for t, v in sorted(ex_tags.items())},
        "rubric_tags": {t: clipped_stats(v) for t, v in sorted(rb_tags.items())},
    }


def grade_run(examples: list[dict], client: Client, profile: Profile, out_path: Path, concurrency: int = 16, max_attempts: int = 5) -> dict:
    """examples: dicts with prompt_id, prompt (message list), completion, rubrics, example_tags.
    Resumable: examples already present in out_path are skipped."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["prompt_id"])
    todo = [e for e in examples if e["prompt_id"] not in done]
    t0 = time.time()

    def one(ex: dict) -> dict:
        grades = []
        for rb in ex["rubrics"]:
            item = rubric_str(rb["criterion"], rb["points"]) if profile.show_points else rb["criterion"]
            met, expl, attempts = client.grade(render(ex["prompt"], ex["completion"], item), max_attempts=max_attempts)
            grades.append({"criterion": rb["criterion"], "points": rb["points"], "tags": rb.get("tags", []),
                           "criteria_met": met, "explanation": expl, "attempts": attempts})
        return {"prompt_id": ex["prompt_id"], "example_tags": ex.get("example_tags", []), "rubrics": ex["rubrics"], "rubric_grades": grades}

    with open(out_path, "a", encoding="utf-8") as fh, ThreadPoolExecutor(concurrency) as pool:
        futs = [pool.submit(one, ex) for ex in todo]
        for k, f in enumerate(as_completed(futs), 1):
            fh.write(json.dumps(f.result(), ensure_ascii=False) + "\n")
            if k % 50 == 0:
                fh.flush()
                print(f"  graded {k}/{len(todo)} examples, {time.time() - t0:.0f}s", flush=True)
    graded = [json.loads(l) for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return summarize(graded, profile, client)


def summarize(graded: list[dict], profile: Profile, client: Client | None = None) -> dict:
    n_crit = sum(len(g["rubric_grades"]) for g in graded)
    missing = [x for g in graded for x in g["rubric_grades"] if x["criteria_met"] is None]
    retried = sum(1 for g in graded for x in g["rubric_grades"] if x.get("attempts", 1) > 1)
    incomplete = [g["prompt_id"] for g in graded if any(x["criteria_met"] is None for x in g["rubric_grades"])]
    as_not_met = [
        example_score(g["rubrics"], [bool(x["criteria_met"]) for x in g["rubric_grades"]]) for g in graded
    ]
    om_met = flips = 0
    for g in graded:
        for x in g["rubric_grades"]:
            if x["points"] < 0 and x["criteria_met"] and is_omission(x["criterion"]):
                om_met += 1
                flips += is_flip(x["criterion"], x["criteria_met"], x["explanation"])
    return {
        "harness": f"healthbench-open-judge {__version__}",
        "profile": profile.name,
        "model": client.model if client else profile.model,
        "template_sha256": TEMPLATE_SHA256,
        "show_points": profile.show_points,
        "graded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "examples": len(graded),
        "criteria": n_crit,
        "missing_grades": {
            "criteria_missing": len(missing),
            "rate": len(missing) / n_crit if n_crit else 0.0,
            "criteria_needing_retry": retried,
            "examples_excluded": len(incomplete),
            "excluded_prompt_ids": incomplete[:50],
            "score_if_missing_counted_not_met": clipped_stats([s for s in as_not_met if s is not None])["mean"],
        },
        "polarity_audit": {
            "omission_penalties_marked_met": om_met,
            "flagged_flips": flips,
            "flip_share": flips / om_met if om_met else 0.0,
        },
        "usage": client.usage if client else None,
        **aggregate(graded),
    }


def panel_merge(runs: list[list[dict]], labels: list[str]) -> list[dict]:
    """Per-criterion mean of several judges' verdicts, on examples every run graded with the same rubric.
    A criterion any member left ungraded stays missing."""
    by_id = [{g["prompt_id"]: g for g in run} for run in runs]
    out = []
    for pid in sorted(set.intersection(*[set(b) for b in by_id])):
        rows = [b[pid] for b in by_id]
        crits = [[x["criterion"] for x in r["rubric_grades"]] for r in rows]
        if any(c != crits[0] for c in crits[1:]):
            continue
        grades = []
        for i, x in enumerate(rows[0]["rubric_grades"]):
            votes = [r["rubric_grades"][i]["criteria_met"] for r in rows]
            met = None if any(v is None for v in votes) else sum(float(v) for v in votes) / len(votes)
            grades.append({"criterion": x["criterion"], "points": x["points"], "tags": x.get("tags", []),
                           "criteria_met": met, "members": dict(zip(labels, votes))})
        out.append({"prompt_id": pid, "example_tags": rows[0].get("example_tags", []), "rubrics": rows[0]["rubrics"],
                    "rubric_grades": grades})
    return out


def paired_delta(a: list[dict], b: list[dict], seed: int = 0, boot: int = 2000) -> dict:
    """Paired difference A minus B over examples complete in both runs (points, 0 to 100)."""
    sa = {g["prompt_id"]: example_score(g["rubrics"], [x["criteria_met"] for x in g["rubric_grades"]]) for g in a}
    sb = {g["prompt_id"]: example_score(g["rubrics"], [x["criteria_met"] for x in g["rubric_grades"]]) for g in b}
    ids = sorted(p for p in set(sa) & set(sb) if sa[p] is not None and sb[p] is not None)
    if not ids:
        return {"n": 0}
    d = np.array([sa[p] - sb[p] for p in ids])
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(boot, len(d)))].mean(axis=1)
    return {"n": len(ids), "delta": 100 * float(d.mean()), "ci95": [100 * float(np.percentile(m, 2.5)), 100 * float(np.percentile(m, 97.5))]}
