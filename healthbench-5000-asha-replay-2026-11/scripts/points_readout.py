#!/usr/bin/env python3
"""Amendment A3 readout: the September 5,000 corrected for Asha's late draft, under the paper's metric.

Positive verdicts: first-pass GPT-4.1 (frozen grader). Penalty verdicts: GPT-4.1 with OpenAI's reference
rendering. September's side is the published per-item data (`eval_*.jsonl` plus the `prodneg` verdicts, the
inputs of `frozen_pair_points.py`); the replay side is the merged grade files from `points_regrade.py merge`.
Item score: achieved points over positive points; set score: mean clipped to [0, 1]; length adjustment as
HealthBench Professional (2.94e-5 per character from 2,000), as in the paper.

  python3 points_readout.py --arena DIR --hard hard.jsonl --replay DIR --out READOUT_points.json
      [--check sept_check100_graded.jsonl]

--replay holds `arm_A.jsonl`, `arm_B.jsonl`, `ext_arm_B.jsonl` (completions) and `first200_A_points.jsonl`,
`first200_B_points.jsonl`, `ext_B_points.jsonl` (merged grades). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

LEN_COEF, LEN_BASE = 2.94e-5, 2000
SEED, BOOT = 20261122, 10_000
FAILED = ("Error", "Backup parse", "Parse failed", "Max retries")
N_TOTAL, N_AFFECTED = 5000, 969


def rows(p: Path):
    with open(p, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def text(c) -> str:
    if isinstance(c, list):
        return c[0].get("content", "") if c and isinstance(c[0], dict) else ""
    return c or ""


def item_score(pts, met):
    possible = sum(p for p in pts if p > 0)
    if possible <= 0:
        return None
    return sum(p for p, m in zip(pts, met) if m) / possible


def clip(x):
    return min(1.0, max(0.0, x))


def is_met(g) -> bool:
    return g.get("met") is True or str(g.get("met")).lower() == "true"


def t_p(t: float, df: int) -> float:
    # two-sided P from Student's t via the regularized incomplete beta (continued fraction)
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5

    def cf(a, b, x):
        tiny, qab, qap, qam = 1e-300, a + b, a + 1, a - 1
        c, d = 1.0, 1 - qab * x / qap
        d = 1 / (d if abs(d) > tiny else tiny)
        h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c; c = c if abs(c) > tiny else tiny
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c; c = c if abs(c) > tiny else tiny
            de = d * c
            h *= de
            if abs(de - 1) < 1e-12:
                break
        return h

    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1 - x))
    ib = front * cf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1 - front * cf(b, a, 1 - x) / b
    return min(1.0, ib)


def paired(new: dict, old: dict, boot: bool = True) -> dict:
    ids = sorted(set(new) & set(old))
    d = [new[i] - old[i] for i in ids]
    n = len(d)
    mean = sum(d) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (n - 1))
    se = sd / math.sqrt(n)
    out = {"n": n, "new": 100 * clip(sum(new[i] for i in ids) / n), "old": 100 * clip(sum(old[i] for i in ids) / n),
           "diff": 100 * mean, "ci_t": [100 * (mean - 1.96 * se), 100 * (mean + 1.96 * se)],
           "p_t": t_p(mean / se, n - 1) if se > 0 else None,
           "better": sum(x > 1e-12 for x in d), "worse": sum(x < -1e-12 for x in d)}
    if boot:
        rng = random.Random(SEED)
        bs = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOT))
        out["ci_boot"] = [100 * bs[int(0.025 * BOOT)], 100 * bs[int(0.975 * BOOT) - 1]]
    return out


def score_maps(pts, met, n_chars):
    s = item_score(pts, met)
    if s is None:
        return None
    return s, s - LEN_COEF * (n_chars - LEN_BASE)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arena", type=Path, required=True)
    ap.add_argument("--hard", type=Path, required=True)
    ap.add_argument("--replay", type=Path, required=True)
    ap.add_argument("--check", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    evals = rows(a.arena / "eval_a3_4500.jsonl") + rows(a.arena / "eval_delta500.jsonl")
    sample500 = {r["pid"] for r in rows(a.arena / "eval_delta500.jsonl")}
    hard = {json.loads(line)["prompt_id"] for line in open(a.hard, encoding="utf-8")}
    pts_v = {}
    for d in sorted(a.arena.glob("runs/*/openai__gpt-4.1__default__zero_pts__prodneg*/verdicts.jsonl")):
        for v in rows(d):
            if v.get("met") is not None and not v.get("err"):
                pts_v[(v["uid"], v["ci"])] = bool(v["met"])

    # September per-item scores (published method: frozen_pair_points.py)
    sept = {"apexj": ({}, {}), "astra": ({}, {})}
    sept_harm = {"apexj": {}, "astra": {}}
    uid_of = {}
    for r in evals:
        if r["arm"] not in sept:
            continue
        pts = [float(rb["points"]) for rb in r["rubrics"]]
        g41 = r["gold"]["gpt_4_1"]
        if r["arm"] == "apexj":
            uid_of[r["pid"]] = (r["uid"], pts)
        if any(m is None for m in g41):
            continue
        new = []
        for ci, (p, m) in enumerate(zip(pts, g41)):
            if p < 0:
                if (r["uid"], ci) not in pts_v:
                    new = None
                    break
                new.append(pts_v[(r["uid"], ci)])
            else:
                new.append(bool(m))
        if new is None:
            continue
        sc = score_maps(pts, new, len(r["completion"] or ""))
        if sc is None:
            continue
        sept[r["arm"]][0][r["pid"]], sept[r["arm"]][1][r["pid"]] = sc
        sept_harm[r["arm"]][r["pid"]] = (sum(m for p, m in zip(pts, new) if p < 0), sum(1 for p in pts if p < 0))

    out: dict = {"method": "A3, Docs/benchmarking/apexj_asha_replay_2026-11/PREREGISTRATION.md",
                 "september_items_scored": {k: len(v[0]) for k, v in sept.items()}}

    # Harness check: September answers re-graded with this lane's driver vs the published penalty verdicts
    if a.check:
        agree = total = met_new = met_old = 0
        for r in rows(a.check):
            uid, pts = uid_of[r["prompt_id"]]
            negs = [ci for ci, p in enumerate(pts) if p < 0]
            grades = r.get("rubric_grades") or []
            if len(grades) != len(negs):
                continue
            for ci, g in zip(negs, grades):
                if (uid, ci) not in pts_v or str(g.get("explanation") or "").startswith(FAILED):
                    continue
                x, y = is_met(g), pts_v[(uid, ci)]
                total += 1; agree += x == y; met_new += x; met_old += y
        po = agree / total
        pa, pb = met_new / total, met_old / total
        pe = pa * pb + (1 - pa) * (1 - pb)
        out["harness_check"] = {"criteria": total, "agreement": po, "kappa": (po - pe) / (1 - pe) if pe < 1 else None,
                                "met_rate_this_lane": pa, "met_rate_published": pb}

    # Replay arms
    def arm(comp_file: str, graded_file: str):
        comp = {r["prompt_id"]: r for r in rows(a.replay / comp_file)}
        raw, ln, harm, fails = {}, {}, {}, 0
        for g in rows(a.replay / graded_file):
            grades = g.get("rubric_grades") or []
            if any(str(x.get("explanation") or "").startswith(FAILED) for x in grades):
                fails += 1
                continue
            pts = [float(x["points"]) for x in grades]
            met = [is_met(x) for x in grades]
            sc = score_maps(pts, met, len(text(comp[g["prompt_id"]]["completion"])))
            if sc is None:
                continue
            raw[g["prompt_id"]], ln[g["prompt_id"]] = sc
            harm[g["prompt_id"]] = (sum(m for p, m in zip(pts, met) if p < 0), sum(1 for p in pts if p < 0))
        return raw, ln, harm, fails

    A_raw, A_len, _, A_f = arm("arm_A.jsonl", "first200_A_points.jsonl")
    B1_raw, B1_len, B1_h, B1_f = arm("arm_B.jsonl", "first200_B_points.jsonl")
    Bx_raw, Bx_len, Bx_h, Bx_f = arm("ext_arm_B.jsonl", "ext_B_points.jsonl")
    out["failed_items"] = {"first200_A": A_f, "first200_B": B1_f, "ext_B": Bx_f}
    B_raw, B_len, B_h = {**B1_raw, **Bx_raw}, {**B1_len, **Bx_len}, {**B1_h, **Bx_h}
    S_raw, S_len = sept["apexj"]
    T_raw, T_len = sept["astra"]

    out["fidelity_first200"] = {"raw": paired(A_raw, S_raw), "len": paired(A_len, S_len)}
    out["effect_first200_B_vs_A"] = {"raw": paired(B1_raw, A_raw), "len": paired(B1_len, A_len)}
    out["effect_968_B_vs_september"] = {"raw": paired(B_raw, S_raw), "len": paired(B_len, S_len)}
    e = out["effect_968_B_vs_september"]["raw"]
    out["projection_5000_raw"] = {k: (v * N_AFFECTED / N_TOTAL if isinstance(v, float) else [x * N_AFFECTED / N_TOTAL for x in v])
                                  for k, v in e.items() if k in ("diff", "ci_boot", "ci_t")}

    # Corrected 5,000: September per-item scores with the replayed rows swapped for arm B
    sets = {"all": None, "hard": hard, "sample500": sample500}
    corr = {}
    for metric, S, B, T in (("raw", S_raw, B_raw, T_raw), ("len", S_len, B_len, T_len)):
        C = {**S, **{k: v for k, v in B.items() if k in S}}
        for sname, ids in sets.items():
            f = (lambda m: m) if ids is None else (lambda m, ids=ids: {k: v for k, v in m.items() if k in ids})
            corr[f"{sname}|{metric}"] = {
                "as_run_vs_astra": paired(f(S), f(T), boot=False),
                "corrected_vs_astra": paired(f(C), f(T), boot=False),
                "corrected_vs_as_run": paired(f(C), f(S), boot=False),
                "rows_swapped": sum(1 for k in B if k in S and (ids is None or k in ids)),
            }
    out["corrected"] = corr

    def harm_rate(h):
        m = sum(v[0] for v in h.values()); n = sum(v[1] for v in h.values())
        return 100 * m / n if n else None
    Ch = {**sept_harm["apexj"], **{k: v for k, v in B_h.items() if k in sept_harm["apexj"]}}
    out["harm"] = {s: {"as_run": harm_rate({k: v for k, v in sept_harm["apexj"].items() if ids is None or k in ids}),
                       "corrected": harm_rate({k: v for k, v in Ch.items() if ids is None or k in ids}),
                       "astra": harm_rate({k: v for k, v in sept_harm["astra"].items() if ids is None or k in ids})}
                   for s, ids in (("all", None), ("hard", hard))}

    a.out.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("september_items_scored", "harness_check", "failed_items") if k in out}))
    for k in ("fidelity_first200", "effect_first200_B_vs_A", "effect_968_B_vs_september"):
        for m in ("raw", "len"):
            v = out[k][m]
            print(f"{k:28} {m:3} n={v['n']} new {v['new']:.2f} old {v['old']:.2f} diff {v['diff']:+.2f} "
                  f"boot [{v['ci_boot'][0]:+.2f}, {v['ci_boot'][1]:+.2f}] p={v['p_t']:.3g}")
    for k, v in corr.items():
        c, r = v["corrected_vs_astra"], v["as_run_vs_astra"]
        print(f"corrected {k:14} swapped {v['rows_swapped']:4} as-run {r['new']:.2f} -> {c['new']:.2f} vs astra {c['old']:.2f}: "
              f"diff {r['diff']:+.2f} -> {c['diff']:+.2f} [{c['ci_t'][0]:+.2f}, {c['ci_t'][1]:+.2f}]")
    print("harm", json.dumps(out["harm"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
