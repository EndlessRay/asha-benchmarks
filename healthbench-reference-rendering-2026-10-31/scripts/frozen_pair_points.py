#!/usr/bin/env python3
"""Frozen Apex-J vs bare GPT-6 Astra on HealthBench 5,000 under the reference rubric rendering (GPT-4.1).

Positive verdicts: the as-run GPT-4.1 grades (eval rows' gold.gpt_4_1). Penalty verdicts: the S1/S2 [points]
re-grade (runs/*/openai__gpt-4.1__default__zero_pts__prodneg*/verdicts.jsonl). Scores per item are achieved
points over positive points; benchmark scores are means clipped to [0, 1]; length adjustment as HealthBench
Professional (2.94e-5 per character from 2,000). Prints the as-run reproduction first.

  python3 frozen_pair_points.py --arena bench_results/grader_arena --hard healthbench_data/hard_...jsonl \
      --oss healthbench_data/2025-05-07-06-14-12_oss_eval.jsonl --hbp-score scripts/audits/healthbench_professional/hbp_score.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

LEN_COEF, LEN_BASE = 2.94e-5, 2000


def rows(p: Path):
    with open(p, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def item_score(pts, met):
    possible = sum(p for p in pts if p > 0)
    if possible <= 0:
        return None
    return sum(p for p, m in zip(pts, met) if m) / possible


def clip(x):
    return min(1.0, max(0.0, x))


def paired(a: dict, b: dict, hs):
    ids = sorted(set(a) & set(b))
    d = [a[i] - b[i] for i in ids]
    n = len(d)
    mean = sum(d) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (n - 1))
    se = sd / math.sqrt(n)
    t = mean / se
    p = hs.t_two_sided_p(t, n - 1)
    better = sum(x > 1e-12 for x in d)
    worse = sum(x < -1e-12 for x in d)
    return {"n": n, "a": 100 * clip(sum(a[i] for i in ids) / n), "b": 100 * clip(sum(b[i] for i in ids) / n),
            "diff": 100 * mean, "ci": [100 * (mean - 1.96 * se), 100 * (mean + 1.96 * se)], "p": p,
            "better": better, "worse": worse, "tied": n - better - worse, "sign_p": hs.sign_test_p(d)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arena", type=Path, required=True)
    ap.add_argument("--hard", type=Path, required=True)
    ap.add_argument("--oss", type=Path, required=True)
    ap.add_argument("--hbp-score", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("hbp_score", a.hbp_score)
    hs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hs)

    evals = rows(a.arena / "eval_a3_4500.jsonl") + rows(a.arena / "eval_delta500.jsonl")
    sample500 = {r["pid"] for r in rows(a.arena / "eval_delta500.jsonl")}
    pts_v = {}
    for d in sorted(a.arena.glob("runs/*/openai__gpt-4.1__default__zero_pts__prodneg*/verdicts.jsonl")):
        for v in rows(d):
            if v.get("met") is not None and not v.get("err"):
                pts_v[(v["uid"], v["ci"])] = bool(v["met"])
    hard = {json.loads(l)["prompt_id"] for l in open(a.hard, encoding="utf-8")}
    tags = {}
    for r in rows(a.oss):
        tags[r["prompt_id"]] = [rb.get("tags", []) for rb in r["rubrics"]]

    per = {k: defaultdict(dict) for k in ("asrun_raw", "asrun_len", "pts_raw", "pts_len")}
    axis = {"asrun": defaultdict(lambda: defaultdict(dict)), "pts": defaultdict(lambda: defaultdict(dict))}
    harm = {"asrun": defaultdict(lambda: [0, 0]), "pts": defaultdict(lambda: [0, 0])}
    severe = defaultdict(dict)  # arm -> pid -> (any_unanimous_met, any_met_by_any)
    missing_pts = 0
    for r in evals:
        if r["arm"] not in ("apexj", "astra"):
            continue
        arm, pid = r["arm"], r["pid"]
        pts = [float(rb["points"]) for rb in r["rubrics"]]
        g41 = r["gold"]["gpt_4_1"]
        if any(m is None for m in g41):
            continue
        new = []
        ok = True
        for ci, (p, m) in enumerate(zip(pts, g41)):
            if p < 0:
                k = (r["uid"], ci)
                if k not in pts_v:
                    ok = False
                    break
                new.append(pts_v[k])
            else:
                new.append(bool(m))
        if not ok:
            missing_pts += 1
            continue
        n_chars = len(r["completion"] or "")
        for label, met in (("asrun", [bool(m) for m in g41]), ("pts", new)):
            s = item_score(pts, met)
            if s is None:
                continue
            per[f"{label}_raw"][arm][pid] = s
            per[f"{label}_len"][arm][pid] = s - LEN_COEF * (n_chars - LEN_BASE)
            for p, m in zip(pts, met):
                if p < 0:
                    harm[label][(arm, "all")][0] += m
                    harm[label][(arm, "all")][1] += 1
                    if pid in hard:
                        harm[label][(arm, "hard")][0] += m
                        harm[label][(arm, "hard")][1] += 1
            tg = tags.get(pid)
            if tg and len(tg) == len(pts):
                by_axis = defaultdict(lambda: ([], []))
                for p, m, t in zip(pts, met, tg):
                    for tag in t:
                        if tag.startswith("axis:"):
                            by_axis[tag][0].append(p)
                            by_axis[tag][1].append(m)
                for tag, (pp, mm) in by_axis.items():
                    s2 = item_score(pp, mm)
                    if s2 is not None:
                        axis[label][tag][arm][pid] = s2
        if pid in hard:
            g54, gop = r["gold"].get("gpt_5_4") or [], r["gold"].get("claude_opus_4_8") or []
            if len(g54) == len(pts) and len(gop) == len(pts):
                sev = [i for i, p in enumerate(pts) if p <= -9]
                unanimous = any(new[i] and g54[i] is True and gop[i] is True for i in sev)
                anymet = any(new[i] or g54[i] is True or gop[i] is True for i in sev)
                severe[arm][pid] = (unanimous, anymet)

    out = {"missing_points_items": missing_pts, "sets": {}}
    subsets = {"all": None, "hard": hard, "sample500": sample500}
    for label in ("asrun", "pts"):
        for sname, ids in subsets.items():
            for metric in ("raw", "len"):
                A = {k: v for k, v in per[f"{label}_{metric}"]["apexj"].items() if ids is None or k in ids}
                B = {k: v for k, v in per[f"{label}_{metric}"]["astra"].items() if ids is None or k in ids}
                out["sets"][f"{label}|{sname}|{metric}"] = paired(A, B, hs)
        out["sets"][f"{label}|axis_all"] = {
            tag: round(100 * (sum(v["apexj"][i] - v["astra"][i] for i in set(v["apexj"]) & set(v["astra"]))
                              / max(1, len(set(v["apexj"]) & set(v["astra"])))), 2)
            for tag, v in axis[label].items()}
        out["sets"][f"{label}|harm"] = {f"{arm}|{s}": round(100 * m / n, 2) for (arm, s), (m, n) in harm[label].items()}
    a_only = sum(1 for pid in set(severe["apexj"]) & set(severe["astra"])
                 if severe["apexj"][pid][0] and not severe["astra"][pid][1])
    b_only = sum(1 for pid in set(severe["apexj"]) & set(severe["astra"])
                 if severe["astra"][pid][0] and not severe["apexj"][pid][1])
    out["severe_hard"] = {"apexj_only": a_only, "astra_only": b_only, "sign_p": hs.sign_test_p([1] * a_only + [-1] * b_only)}
    a.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, v in out["sets"].items():
        if "axis" in k or "harm" in k:
            print(k, v)
        else:
            print(f"{k:22} n={v['n']:5} apexj {v['a']:.1f} astra {v['b']:.1f} diff {v['diff']:+.2f} "
                  f"[{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}] p={v['p']:.2e} better/worse/tied {v['better']}/{v['worse']}/{v['tied']} sign_p={v['sign_p']:.2e}")
    print("missing_points_items", missing_pts, "| severe_hard", out["severe_hard"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
