"""Command line: grade, compare, panel, validate.

  hbjudge grade --data healthbench.jsonl --completions my_model.jsonl --profile flashlite-v1 --out runs/my_model
  hbjudge compare runs/model_a/graded.jsonl runs/model_b/graded.jsonl
  hbjudge panel runs/model_a_flashlite/graded.jsonl runs/model_a_oss/graded.jsonl --out runs/model_a_panel
  hbjudge validate --meta-eval oss_meta_eval.jsonl --profile oss120b-v1 --n 3000 --out runs/validate_oss120b
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

from .client import Client
from .grading import aggregate, grade_run, paired_delta, panel_merge, summarize
from .judges import PROFILES
from .template import render

DATA_URLS = {
    "healthbench": "https://openaipublic.blob.core.windows.net/simple-evals/healthbench/2025-05-07-06-14-12_oss_eval.jsonl",
    "hard": "https://openaipublic.blob.core.windows.net/simple-evals/healthbench/hard_2025-05-08-21-00-10.jsonl",
    "consensus": "https://openaipublic.blob.core.windows.net/simple-evals/healthbench/consensus_2025-05-09-20-00-46.jsonl",
    "meta_eval": "https://openaipublic.blob.core.windows.net/simple-evals/healthbench/2025-05-07-06-14-12_oss_meta_eval.jsonl",
}


def read_jsonl(p: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def _client(a) -> tuple:
    profile = PROFILES[a.profile]
    return profile, Client(profile, base_url=a.base_url, model=a.model)


def cmd_grade(a) -> int:
    data = {r["prompt_id"]: r for r in read_jsonl(a.data)}
    examples = []
    for c in read_jsonl(a.completions):
        row = data.get(c["prompt_id"])
        if row is None:
            print(f"skip unknown prompt_id {c['prompt_id']}", file=sys.stderr)
            continue
        comp = c["completion"]
        if isinstance(comp, list):
            comp = "\n\n".join(m.get("content", "") for m in comp if m.get("role") != "user")
        examples.append({"prompt_id": row["prompt_id"], "prompt": row["prompt"], "completion": comp,
                         "rubrics": row["rubrics"], "example_tags": row.get("example_tags", [])})
    if a.limit:
        examples = examples[: a.limit]
    profile, client = _client(a)
    out = Path(a.out)
    summary = grade_run(examples, client, profile, out / "graded.jsonl", concurrency=a.concurrency, max_attempts=a.max_attempts)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    s, m = summary["score"], summary["missing_grades"]
    print(f"score {100 * s['mean']:.2f} (bootstrap std {100 * s['bootstrap_std']:.2f}, n={s['n']}); "
          f"missing grades {m['criteria_missing']} of {summary['criteria']} ({100 * m['rate']:.2f}%), examples excluded {m['examples_excluded']}; "
          f"polarity flags {summary['polarity_audit']['flagged_flips']}")
    return 0


def cmd_compare(a) -> int:
    res = paired_delta(read_jsonl(a.a), read_jsonl(a.b), seed=a.seed)
    print(json.dumps(res, indent=2))
    return 0


def cmd_panel(a) -> int:
    runs = [read_jsonl(p) for p in a.graded]
    labels = [Path(p).parent.name or Path(p).stem for p in a.graded]
    merged = panel_merge(runs, labels)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "graded.jsonl").write_text("".join(json.dumps(g, ensure_ascii=False) + "\n" for g in merged), encoding="utf-8")
    n_crit = sum(len(g["rubric_grades"]) for g in merged)
    missing = sum(1 for g in merged for x in g["rubric_grades"] if x["criteria_met"] is None)
    summary = {"panel": labels, "examples": len(merged), "criteria": n_crit,
               "missing_grades": {"criteria_missing": missing, "rate": missing / n_crit if n_crit else 0.0},
               **aggregate(merged)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    s = summary["score"]
    print(f"panel {'+'.join(labels)}: score {100 * s['mean']:.2f} (bootstrap std {100 * s['bootstrap_std']:.2f}, n={s['n']}); "
          f"missing grades {missing} of {n_crit}")
    return 0


def macro_f1(pairs: list[tuple[bool, bool]]) -> float:
    f1s = []
    for cls in (True, False):
        tp = sum(1 for x, y in pairs if x == cls and y == cls)
        fp = sum(1 for x, y in pairs if x == cls and y != cls)
        fn = sum(1 for x, y in pairs if x != cls and y == cls)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * p * r / (p + r) if p + r else 0.0)
    return sum(f1s) / 2


def cmd_validate(a) -> int:
    """Physician agreement on OpenAI's meta-eval (simple-evals metric: pooled pairwise balanced F1)."""
    from concurrent.futures import ThreadPoolExecutor

    rows = [r for r in read_jsonl(a.meta_eval) if len(r["binary_labels"]) >= 2]
    random.Random(a.seed).shuffle(rows)
    rows = rows[: a.n]
    profile, client = _client(a)

    def one(r):
        met, expl, attempts = client.grade(render(r["prompt"], r["completion"], r["rubric"]), max_attempts=a.max_attempts)
        return met

    with ThreadPoolExecutor(a.concurrency) as pool:
        labels = list(pool.map(one, rows))
    keep = [i for i, v in enumerate(labels) if v is not None]
    rng = np.random.default_rng(a.seed)

    def judge_mf1(idx):
        return macro_f1([(labels[i], p) for i in idx for p in rows[i]["binary_labels"]])

    def physician_mf1(idx):
        per = {}
        for i in idx:
            lab, ids = rows[i]["binary_labels"], rows[i]["anonymized_physician_ids"]
            for k, pid in enumerate(ids):
                per.setdefault(pid, []).extend((lab[k], o) for o in lab[:k] + lab[k + 1 :])
        tot = sum(len(v) for v in per.values())
        return sum(len(v) * macro_f1(v) for v in per.values()) / tot

    boots = [rng.choice(keep, len(keep)) for _ in range(a.boot)]
    j, ph = judge_mf1(keep), physician_mf1(keep)
    jb = np.array([judge_mf1(b) for b in boots])
    pb = np.array([physician_mf1(b) for b in boots])
    res = {
        "profile": profile.name, "model": client.model, "n": len(rows), "missing": len(rows) - len(keep),
        "judge_mf1": j, "judge_ci95": [float(np.percentile(jb, 2.5)), float(np.percentile(jb, 97.5))],
        "typical_physician_mf1": ph,
        "judge_minus_physician": j - ph, "diff_ci95": [float(np.percentile(jb - pb, 2.5)), float(np.percentile(jb - pb, 97.5))],
        "published_reference": {"gpt-4.1": 0.709, "gpt-4.1-mini": 0.661, "source": "HealthBench paper (arXiv:2505.08775), Table 6"},
        "usage": client.usage,
    }
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "validate.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res, indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="hbjudge")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("grade", "validate"):
        s = sub.add_parser(name)
        s.add_argument("--profile", required=True, choices=sorted(PROFILES))
        s.add_argument("--base-url", default=None, help="override the profile endpoint (local or proxy)")
        s.add_argument("--model", default=None, help="override the served model name (not the model family)")
        s.add_argument("--concurrency", type=int, default=16)
        s.add_argument("--max-attempts", type=int, default=5, help="re-asks for an unparsable reply before the grade is reported missing")
        s.add_argument("--out", required=True)
        s.add_argument("--seed", type=int, default=20261028)
    g = sub.choices["grade"]
    g.add_argument("--data", required=True, help="HealthBench JSONL (see DATA_URLS in cli.py)")
    g.add_argument("--completions", required=True, help="JSONL with prompt_id and completion")
    g.add_argument("--limit", type=int, default=0)
    v = sub.choices["validate"]
    v.add_argument("--meta-eval", required=True)
    v.add_argument("--n", type=int, default=3000)
    v.add_argument("--boot", type=int, default=500)
    p = sub.add_parser("panel", help="mean of several judges' per-criterion verdicts on the same answers")
    p.add_argument("graded", nargs="+", help="graded.jsonl files from different judges on the same answers")
    p.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--seed", type=int, default=20261028)
    a = ap.parse_args(argv)
    return {"grade": cmd_grade, "compare": cmd_compare, "validate": cmd_validate, "panel": cmd_panel}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
