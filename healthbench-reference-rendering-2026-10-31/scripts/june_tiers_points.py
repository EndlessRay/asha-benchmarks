#!/usr/bin/env python3
"""June 2026 Asha tiers on HealthBench Hard: as-run (text rendering) and merged [points] scores, and tier pairs.

  python3 june_tiers_points.py --hbp-score hbp_score.py --out OUT.json \
      --arm base=ASRUN_graded.jsonl::MERGED.jsonl --arm mid=... --arm apex=...
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def per_item(path: Path, hs) -> dict:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            grades = r.get("rubric_grades") or []
            if any(hs.grade_failed(g) for g in grades):
                continue
            s = hs.raw_example_score(grades)
            if s is not None:
                out[r["prompt_id"]] = s
    return out


def summary(v: dict) -> dict:
    n = len(v)
    return {"n": n, "score": round(100 * min(1, max(0, sum(v.values()) / n)), 2)}


def pair(a: dict, b: dict, hs) -> dict:
    ids = sorted(set(a) & set(b))
    d = [a[i] - b[i] for i in ids]
    return {"n": len(ids), "diff": round(100 * sum(d) / len(d), 2),
            "better": sum(x > 1e-12 for x in d), "worse": sum(x < -1e-12 for x in d),
            "tied": sum(abs(x) <= 1e-12 for x in d), "sign_p": hs.sign_test_p(d)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hbp-score", type=Path, required=True)
    ap.add_argument("--arm", action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("hbp_score", a.hbp_score)
    hs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hs)
    arms = {}
    for spec_ in a.arm:
        label, files = spec_.split("=", 1)
        asrun, merged = files.split("::")
        arms[label] = {"asrun": per_item(Path(asrun), hs), "points": per_item(Path(merged), hs)}
    out = {"arms": {k: {r: summary(v[r]) for r in ("asrun", "points")} for k, v in arms.items()}, "pairs": {}}
    labels = list(arms)
    for x, y in zip(labels[1:], labels[:-1]):
        for r in ("asrun", "points"):
            out["pairs"][f"{x}_vs_{y}|{r}"] = pair(arms[x][r], arms[y][r], hs)
    a.out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
