#!/usr/bin/env python3
"""Vishwanath et al. 500 under the study's three-judge panel: corrected September row and Experiment 2.

Metric as in the paper: pooled points achieved over points possible; 95% interval from 5,000 item-bootstrap
resamples (seed 20261122); exact sign test on per-item points. Inputs are the study pipeline's output files
(`{"rows": [{"prompt_id", "point_total", "point_possible", "rubric_scores"}]}`).

  python3 panel_readout.py --sept SEPT.json --astra ASTRA.json --new NEW.json [--swap] [--noasha IDS.json] --out OUT.json

--swap: NEW holds only replayed rows; the corrected set is SEPT with those rows replaced (A3 readout 5b).
Without --swap NEW is a full 500-row run compared with SEPT item by item (Experiment 2).
--noasha: JSON list of prompt ids whose September answer lacked Asha's draft (subgroup split).
Standard library only.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import random
from pathlib import Path

SEED, BOOT = 20261122, 5000


def load(p: Path) -> dict:
    op = gzip.open if p.suffix == ".gz" else open
    with op(p, "rt", encoding="utf-8") as fh:
        return {r["prompt_id"]: r for r in json.load(fh)["rows"]}


def pool(rs) -> float:
    return 100 * sum(r["point_total"] for r in rs) / sum(r["point_possible"] for r in rs)


def item(r) -> float:
    return 100 * r["point_total"] / r["point_possible"]


def sign_p(d) -> float:
    k, n = sum(x > 0 for x in d), sum(x != 0 for x in d)
    if n == 0:
        return 1.0
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(new: dict, old: dict, ids) -> dict:
    ids = sorted(ids)
    rng = random.Random(SEED)
    bs = []
    for _ in range(BOOT):
        s = [ids[rng.randrange(len(ids))] for _ in ids]
        bs.append(pool([new[i] for i in s]) - pool([old[i] for i in s]))
    bs.sort()
    d = [item(new[i]) - item(old[i]) for i in ids]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return {"n": len(ids), "new": pool([new[i] for i in ids]), "old": pool([old[i] for i in ids]),
            "diff": pool([new[i] for i in ids]) - pool([old[i] for i in ids]),
            "ci_boot": [bs[int(0.025 * BOOT)], bs[int(0.975 * BOOT) - 1]],
            "item_mean_diff": m, "item_ci_t": [m - 1.96 * sd / len(d) ** 0.5, m + 1.96 * sd / len(d) ** 0.5],
            "better": sum(x > 0 for x in d), "worse": sum(x < 0 for x in d), "sign_p": sign_p(d)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sept", type=Path, required=True)
    ap.add_argument("--astra", type=Path, required=True)
    ap.add_argument("--new", type=Path, required=True)
    ap.add_argument("--swap", action="store_true")
    ap.add_argument("--noasha", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    sept, astra, new = load(a.sept), load(a.astra), load(a.new)
    degraded = sum(1 for r in new.values() for c in r.get("rubric_scores", [])
                   if str(c.get("panel_strategy", "")) != "majority")
    out: dict = {"new_rows": len(new), "criteria_without_three_clean_votes": degraded}
    if a.swap:
        corr = {**sept, **{k: v for k, v in new.items() if k in sept}}
        out["replayed_vs_september"] = compare(new, sept, set(new) & set(sept))
        out["as_run_vs_astra"] = compare(sept, astra, set(sept) & set(astra))
        out["corrected_vs_astra"] = compare(corr, astra, set(corr) & set(astra))
        out["corrected_vs_as_run"] = {"new": pool(corr.values()), "old": pool(sept.values()),
                                      "diff": pool(corr.values()) - pool(sept.values())}
    else:
        ids = set(new) & set(sept)
        out["new_vs_september"] = compare(new, sept, ids)
        if a.noasha:
            na = set(json.loads(a.noasha.read_text(encoding="utf-8")))
            out["new_vs_september_noasha"] = compare(new, sept, ids & na)
            out["new_vs_september_other"] = compare(new, sept, ids - na)
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    for k, v in out.items():
        if isinstance(v, dict) and "ci_boot" in v:
            print(f"{k:28} n={v['n']} new {v['new']:.2f} old {v['old']:.2f} diff {v['diff']:+.2f} "
                  f"[{v['ci_boot'][0]:+.2f}, {v['ci_boot'][1]:+.2f}] W/L {v['better']}/{v['worse']} sign p={v['sign_p']:.3g}")
        else:
            print(k, v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
