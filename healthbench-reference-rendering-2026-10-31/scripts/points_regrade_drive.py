#!/usr/bin/env python3
"""Drive tests/healthbench_grader.py's HealthBenchGrader.grade_sample over a penalty-only input and keep every row.

The grader's own loop saves a row only when its score is defined, and a penalty-only item has no positive
points, so its score is undefined. This driver calls the same grade_sample (same prompt, rendering and model
settings) and writes every returned row. Resumes by prompt_id. Stops when more than half of the first 100
criterion calls fail (quota or billing).

  python3 points_regrade_drive.py --grader grader.py --input in/X.jsonl --output out/X.jsonl --model gpt-4.1
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
from pathlib import Path

FAILED = ("Error", "Max retries", "Backup parse", "Parse failed")


def load_grader(path: Path):
    spec = importlib.util.spec_from_file_location("hb_grader", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


async def run(a) -> dict:
    mod = load_grader(a.grader)
    g = mod.HealthBenchGrader(
        results_file=a.input, output_file=a.output.with_suffix(".grader_state.jsonl"),
        api_key=os.environ.get("OPENAI_API_KEY", ""), model=a.model,
        rubric_concurrency=a.rubric_concurrency, sample_concurrency=a.sample_concurrency,
        reasoning_effort=a.reasoning_effort, rubric_render="points",
    )
    done = set()
    if a.output.exists():
        with open(a.output, encoding="utf-8") as fh:
            done = {json.loads(l)["prompt_id"] for l in fh if l.strip()}
    with open(a.input, encoding="utf-8") as fh:
        rows = [r for r in (json.loads(l) for l in fh if l.strip()) if r["prompt_id"] not in done]
    sem = asyncio.Semaphore(a.sample_concurrency)
    lock = asyncio.Lock()
    stats = {"calls": 0, "failed": 0, "rows": 0}

    with open(a.output, "a", encoding="utf-8") as out:
        async def one(r):
            async with sem:
                if stats["calls"] >= 100 and stats["failed"] > stats["calls"] / 2:
                    return
                res = await g.grade_sample(r)
            grades = res.get("rubric_grades") or []
            async with lock:
                out.write(json.dumps(res, ensure_ascii=False) + "\n")
                out.flush()
                stats["rows"] += 1
                stats["calls"] += len(grades)
                stats["failed"] += sum(1 for x in grades if str(x.get("explanation") or "").startswith(FAILED))

        await asyncio.gather(*(one(r) for r in rows))
    stats["stopped_on_failures"] = stats["calls"] >= 100 and stats["failed"] > stats["calls"] / 2
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grader", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--reasoning-effort", default=None)
    ap.add_argument("--sample-concurrency", type=int, default=8)
    ap.add_argument("--rubric-concurrency", type=int, default=4)
    a = ap.parse_args()
    stats = asyncio.run(run(a))
    print(json.dumps({"output": str(a.output), **stats}))
    return 2 if stats["stopped_on_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
