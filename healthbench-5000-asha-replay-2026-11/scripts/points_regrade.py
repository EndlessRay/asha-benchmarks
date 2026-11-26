#!/usr/bin/env python3
"""Re-grade penalty criteria under the reference rubric rendering and merge them into as-run grade files.

  build: archived answers + as-run grade file -> runner input whose rubrics are the penalty criteria only
      python3 points_regrade.py build --completions RUN.jsonl --graded RUN_graded.jsonl --out RUN_neg.jsonl
  merge: as-run grade file + penalty re-grade -> grade file with as-run positive verdicts and re-graded penalties
      python3 points_regrade.py merge --graded RUN_graded.jsonl --regraded RUN_neg_graded.jsonl --out RUN_points.jsonl

Re-grade the build output with tests/healthbench_grader.py --rubric-render points (feat/cheap-grader-arena).
Pre-registration: Docs/benchmarking/points_regrade_2026-10-31/PREREGISTRATION.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FAILED_PREFIXES = ("Error", "Backup parse", "Parse failed", "Max retries")


def read_rows(path: Path):
    bad = 0
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    if bad:
        print(f"  {path.name}: skipped {bad} unreadable lines", file=sys.stderr)
    return rows


def points(x) -> float:
    return float(x)


def failed(g: dict) -> bool:
    return str(g.get("explanation") or "").startswith(FAILED_PREFIXES)


def item_score(grades) -> float | None:
    possible = sum(points(g["points"]) for g in grades if points(g["points"]) > 0)
    if possible <= 0:
        return None
    earned = sum(points(g["points"]) for g in grades if str(g.get("met")).lower() == "true" or g.get("met") is True)
    return earned / possible


def build(a) -> int:
    graded = {r["prompt_id"]: r for r in read_rows(a.graded)}
    n_items = n_crit = skipped = 0
    with open(a.out, "w", encoding="utf-8") as out:
        for r in read_rows(a.completions):
            pid = r.get("prompt_id")
            g = graded.get(pid)
            if g is None:
                continue
            rubrics = r.get("rubrics") or []
            grades = g.get("rubric_grades") or []
            if len(rubrics) != len(grades) or any(
                str(rb["criterion"])[:100] != str(gr["criterion"])[:100] or points(rb["points"]) != points(gr["points"])
                for rb, gr in zip(rubrics, grades)
            ):
                skipped += 1
                continue
            neg = [rb for rb in rubrics if points(rb["points"]) < 0]
            if not neg:
                continue
            row = {k: r[k] for k in ("prompt_id", "prompt", "completion", "example_tags") if k in r}
            row["rubrics"] = neg
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_items += 1
            n_crit += len(neg)
    print(json.dumps({"out": str(a.out), "items": n_items, "penalty_criteria": n_crit, "misaligned_items_skipped": skipped}))
    return 0


def merge(a) -> int:
    regraded = {r["prompt_id"]: r.get("rubric_grades") or [] for r in read_rows(a.regraded)}
    n = replaced = missing = fails = 0
    with open(a.out, "w", encoding="utf-8") as out:
        for g in read_rows(a.graded):
            grades = g.get("rubric_grades") or []
            negs = [i for i, gr in enumerate(grades) if points(gr["points"]) < 0]
            new = regraded.get(g["prompt_id"])
            if negs and (new is None or len(new) != len(negs)):
                missing += 1
                continue
            merged = [dict(gr) for gr in grades]
            for i, ng in zip(negs, new or []):
                if str(ng["criterion"])[:100] != str(grades[i]["criterion"])[:100] or points(ng["points"]) != points(grades[i]["points"]):
                    raise SystemExit(f"criterion mismatch at {g['prompt_id']} index {i}")
                merged[i] = {"criterion": grades[i]["criterion"], "points": grades[i]["points"],
                             "met": ng["met"], "explanation": ng.get("explanation", "")}
                replaced += 1
                fails += failed(ng)
            row = dict(g)
            row["rubric_grades"] = merged
            row["rubric_render"] = "points_penalty"
            s = item_score(merged)
            row["score"] = s if s is not None else g.get("score")
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    print(json.dumps({"out": str(a.out), "items": n, "penalty_verdicts_replaced": replaced,
                      "items_without_regrade": missing, "failed_regrade_calls": fails}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--completions", type=Path, required=True)
    b.add_argument("--graded", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    m = sub.add_parser("merge")
    m.add_argument("--graded", type=Path, required=True)
    m.add_argument("--regraded", type=Path, required=True)
    m.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    return build(a) if a.cmd == "build" else merge(a)


if __name__ == "__main__":
    raise SystemExit(main())
