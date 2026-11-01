#!/usr/bin/env python3
"""HealthBench Professional scorer, faithful to the publication.

Implements the scoring rules of Soskin Hicks et al. (2026), HealthBench
Professional (arXiv:2604.27470), sections 4.1 to 4.3, verbatim:

  raw example score      s_i = sum(points of met criteria) / sum(positive points)
  length-adjusted score  s_len_i = s_i - 2.94e-5 * (chars_i - 2000)
  benchmark score        mean of per-example scores, clipped to [0, 1]
  multiple samples       per-example mean over trials, then the aggregate
  standard error         sigma^2 = mean within-example sample variance
                         tau^2   = max(0, Var(example means) - sigma^2 / m_bar)
                         SE      = sqrt(tau^2 / n + sigma^2 / (n * m_bar))
  confidence interval    mean +/- 1.96 * SE
  arm comparison         paired two-sided t test on example-level means

Length is the final answer in characters, thinking excluded (the runner only
stores the final answer). Bootstrap CIs and the exact sign test are reported
as secondary statistics for continuity with the September slices.

Usage:
  hbp_score.py --dataset prof_dataset_clean.jsonl \
      --arm p6=t1_graded.jsonl::t1_raw.jsonl,t2_graded.jsonl::t2_raw.jsonl \
      --arm apexj=... --compare apexj:p6 [--slices] [--json out.json]

A graded file is the output of tests/healthbench_grader.py (rows carry
prompt_id and rubric_grades). It does not carry the completion text, so the
completions file that was graded follows after "::" to supply lengths.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

LENGTH_COEFFICIENT = 2.94e-5  # per character, paper section 4.1
LENGTH_BASELINE = 2000        # characters receiving no adjustment
Z_95 = 1.96

# tests/healthbench_grader.py stores a failed grader call as met=false with one
# of these explanation prefixes. Scoring it as "not met" lowers positive
# criteria and inflates negative ones, so such items are excluded and counted.
FAILED_GRADE_PREFIXES = ("Error", "Backup parse", "Parse failed", "Max retries")


def grade_failed(grade: dict) -> bool:
    expl = str(grade.get("explanation") or "")
    return expl.startswith(FAILED_GRADE_PREFIXES)


# ---------------------------------------------------------------- scoring

def raw_example_score(grades: Sequence[dict]) -> Optional[float]:
    """Paper 4.1: met criteria earn their points (negative included);
    normalised by the sum of positive points. None when no positive points."""
    possible = 0.0
    earned = 0.0
    for g in grades:
        pts = float(g.get("points", g.get("rubric_points", 0)) or 0)
        met = bool(g.get("met", g.get("criteria_met", False)))
        if pts > 0:
            possible += pts
        if met:
            earned += pts
    if possible <= 0:
        return None
    return earned / possible


def length_adjusted(score: float, n_chars: int) -> float:
    return score - LENGTH_COEFFICIENT * (n_chars - LENGTH_BASELINE)


def clip01(x: float) -> float:
    return min(1.0, max(0.0, x))


# ---------------------------------------------------------------- statistics

def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (Numerical Recipes)."""
    max_iter, eps, fpmin = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > fpmin else fpmin)
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > fpmin else fpmin)
        c = 1.0 + aa / (c if abs(c) > fpmin else fpmin)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > fpmin else fpmin)
        c = 1.0 + aa / (c if abs(c) > fpmin else fpmin)
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t: float, df: float) -> float:
    """Two-sided p-value of Student's t with df degrees of freedom."""
    if df <= 0:
        return float("nan")
    if math.isinf(t):
        return 0.0
    x = df / (df + t * t)
    return regularized_incomplete_beta(df / 2.0, 0.5, x)


def paper_se(example_means: Sequence[float], within_vars: Sequence[float], m_counts: Sequence[int]) -> Tuple[float, float, float]:
    """Paper 4.3: returns (SE, sigma2, tau2)."""
    n = len(example_means)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    m_bar = sum(m_counts) / n
    sigma2 = sum(within_vars) / n
    var_means = statistics.variance(example_means)
    tau2 = max(0.0, var_means - sigma2 / m_bar)
    se = math.sqrt(tau2 / n + sigma2 / (n * m_bar))
    return se, sigma2, tau2


def boot_ci(values: Sequence[float], n_boot: int = 4000, seed: int = 62) -> Tuple[float, float]:
    rng = random.Random(seed)
    k = len(values)
    means = sorted(statistics.fmean(rng.choices(values, k=k)) for _ in range(n_boot))
    return means[int(0.025 * n_boot)], means[min(n_boot - 1, int(0.975 * n_boot))]


def sign_test_p(diffs: Sequence[float]) -> float:
    """Two-sided exact sign test, ties dropped."""
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


# ---------------------------------------------------------------- loading

def load_completion_lengths(path: Path) -> Dict[str, int]:
    out: Dict[str, int] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            comp = row.get("completion") or []
            text = comp[0].get("content", "") if comp else ""
            pid = row.get("prompt_id") or row.get("conversation_id") or row.get("id")
            if pid is not None:
                out[str(pid)] = len(text or "")
    return out


class Trial:
    """One graded trial: prompt_id -> (raw, length_adjusted or None, chars or None).

    A completion of zero characters that is present in the completions file is a
    real empty answer (provider refusal): it scores 0 raw and receives the
    paper's short-answer adjustment (+2.94e-5 * 2000). A prompt_id absent from
    the completions file has an unknown length and is excluded from the
    length-adjusted metric only."""

    def __init__(self, path: Path):
        self.path = path
        self.rows: Dict[str, Tuple[float, Optional[float], Optional[int]]] = {}
        self.excluded_failed_grades = 0
        self.length_missing = 0
        self.empty_answers = 0

    def __contains__(self, pid: str) -> bool:
        return pid in self.rows

    def __getitem__(self, pid: str):
        return self.rows[pid]

    def keys(self):
        return self.rows.keys()


def load_trial(graded_path: Path, lengths: Optional[Dict[str, int]], keep_failed: bool = False) -> Trial:
    trial = Trial(graded_path)
    with open(graded_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            grades = row.get("rubric_grades") or row.get("grades") or []
            if not keep_failed and any(grade_failed(g) for g in grades):
                trial.excluded_failed_grades += 1
                continue
            s = raw_example_score(grades)
            if s is None:
                continue
            pid = str(row.get("prompt_id"))
            comp = row.get("completion") or []
            n_chars: Optional[int] = len(comp[0].get("content", "") or "") if comp else None
            if not n_chars and lengths is not None:
                n_chars = lengths.get(pid)  # None when the id is absent, 0 for a real empty answer
            if n_chars is None:
                trial.length_missing += 1
                trial.rows[pid] = (s, None, None)
            else:
                if n_chars == 0:
                    trial.empty_answers += 1
                trial.rows[pid] = (s, length_adjusted(s, n_chars), n_chars)
    if trial.excluded_failed_grades:
        print(f"  WARNING {graded_path.name}: {trial.excluded_failed_grades} items excluded "
              f"(failed grader calls stored as met=false)")
    if trial.length_missing:
        print(f"  WARNING {graded_path.name}: {trial.length_missing} items without completion "
              f"length; kept for raw, excluded from length-adjusted")
    return trial


def parse_arm_spec(spec: str) -> Tuple[str, List[Tuple[Path, Optional[Path]]]]:
    """LABEL=graded1[::comp1],graded2[::comp2],..."""
    if "=" not in spec:
        raise SystemExit(f"--arm needs LABEL=files, got {spec!r}")
    label, files = spec.split("=", 1)
    trials: List[Tuple[Path, Optional[Path]]] = []
    for item in files.split(","):
        item = item.strip()
        if not item:
            continue
        graded, _, comp = item.partition("::")
        trials.append((Path(graded), Path(comp) if comp else None))
    if not trials:
        raise SystemExit(f"--arm {label}: no trial files")
    return label.strip(), trials


def load_tags(dataset: Optional[Path]) -> Dict[str, List[str]]:
    tags: Dict[str, List[str]] = {}
    if dataset is None:
        return tags
    with open(dataset, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            pid = str(row.get("prompt_id") or row.get("id"))
            t = list(row.get("example_tags") or [])
            for key in ("use_case", "type", "difficulty", "specialty"):
                if row.get(key):
                    t.append(f"{key}:{row[key]}")
            tags[pid] = t
    return tags


# ---------------------------------------------------------------- arm model

class Arm:
    def __init__(self, label: str):
        self.label = label
        self.trials: List[Trial] = []

    def add_trial(self, trial: Trial) -> None:
        self.trials.append(trial)

    def example_ids(self) -> List[str]:
        ids: set = set()
        for t in self.trials:
            ids.update(t.keys())
        return sorted(ids)

    def exclusions(self) -> dict:
        return {
            "excluded_failed_grades": sum(t.excluded_failed_grades for t in self.trials),
            "length_missing": sum(t.length_missing for t in self.trials),
            "empty_answers": sum(t.empty_answers for t in self.trials),
        }

    def answered_ids(self) -> List[str]:
        """Example ids with a non-empty answer in every trial that has them (the
        conditional-on-answering view; comparable to tables that substituted
        another model's answer on refusals, without the substitution)."""
        out = []
        for pid in self.example_ids():
            vals = [t[pid][2] for t in self.trials if pid in t]
            if vals and all(v is None or v > 0 for v in vals) and any(v for v in vals):
                out.append(pid)
        return out

    def per_example(self, metric: int, ids: Optional[Iterable[str]] = None) -> Tuple[List[str], List[float], List[float], List[int]]:
        """metric 0 = raw, 1 = length-adjusted, 2 = chars.
        Returns (ids, example means, within-example sample variances, sample counts).
        Items whose length is unknown carry None for metrics 1 and 2 and are skipped there."""
        use_ids = list(ids) if ids is not None else self.example_ids()
        out_ids: List[str] = []
        means: List[float] = []
        vars_: List[float] = []
        counts: List[int] = []
        for pid in use_ids:
            vals = [t[pid][metric] for t in self.trials if pid in t and t[pid][metric] is not None]
            if not vals:
                continue
            out_ids.append(pid)
            means.append(statistics.fmean(vals))
            vars_.append(statistics.variance(vals) if len(vals) >= 2 else 0.0)
            counts.append(len(vals))
        return out_ids, means, vars_, counts

    def summary(self, metric: int, ids: Optional[Iterable[str]] = None) -> dict:
        _, means, vars_, counts = self.per_example(metric, ids)
        if not means:
            return {"n": 0}
        se, sigma2, tau2 = paper_se(means, vars_, counts)
        mean = statistics.fmean(means)
        lo, hi = boot_ci(means) if len(means) >= 2 else (mean, mean)
        return {
            "n": len(means),
            "samples_per_example": statistics.fmean(counts),
            "mean": clip01(mean),
            "mean_unclipped": mean,
            "se": se,
            "ci95": [clip01(mean - Z_95 * se), clip01(mean + Z_95 * se)] if not math.isnan(se) else None,
            "boot_ci95": [lo, hi],
            "sigma2_within": sigma2,
            "tau2_between": tau2,
        }

    def length_summary(self) -> dict:
        _, means, _, _ = self.per_example(2)
        if not means:
            return {}
        srt = sorted(means)
        return {"mean_chars": statistics.fmean(means), "median_chars": srt[len(srt) // 2]}


def compare_arms(a: Arm, b: Arm, metric: int) -> dict:
    ids = sorted(set(a.example_ids()) & set(b.example_ids()))
    _, ma, _, _ = a.per_example(metric, ids)
    _, mb, _, _ = b.per_example(metric, ids)
    diffs = [x - y for x, y in zip(ma, mb)]
    n = len(diffs)
    if n < 2:
        return {"n": n}
    mean_d = statistics.fmean(diffs)
    sd = statistics.stdev(diffs)
    se = sd / math.sqrt(n)
    t = mean_d / se if se > 0 else (0.0 if mean_d == 0 else math.inf)
    p = t_two_sided_p(t, n - 1) if se > 0 else (1.0 if mean_d == 0 else 0.0)
    lo, hi = boot_ci(diffs)
    return {
        "n_paired": n,
        "mean_diff": mean_d,
        "se": se,
        "t": t,
        "df": n - 1,
        "p_two_sided": p,
        "ci95": [mean_d - Z_95 * se, mean_d + Z_95 * se],
        "boot_ci95": [lo, hi],
        "sign_test_p": sign_test_p(diffs),
        "wins": sum(1 for d in diffs if d > 0),
        "losses": sum(1 for d in diffs if d < 0),
        "ties": sum(1 for d in diffs if d == 0),
    }


# ---------------------------------------------------------------- reporting

def pct(x: Optional[float]) -> str:
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x * 100:.2f}"


def fmt_ci(ci: Optional[Sequence[float]]) -> str:
    if not ci:
        return "n/a"
    return f"[{ci[0] * 100:.1f}, {ci[1] * 100:.1f}]"


def report_arm(arm: Arm, tags: Dict[str, List[str]], slices: bool) -> dict:
    out = {"label": arm.label, "trials": len(arm.trials), "length": arm.length_summary(),
           "exclusions": arm.exclusions()}
    print(f"\n== arm {arm.label}: {len(arm.trials)} trial(s) ==")
    ex = out["exclusions"]
    if ex["excluded_failed_grades"] or ex["length_missing"] or ex["empty_answers"]:
        print(f"  exclusions        failed-grade items={ex['excluded_failed_grades']} "
              f"length-missing items={ex['length_missing']} empty answers scored 0={ex['empty_answers']}")
    for name, metric in (("raw", 0), ("length_adjusted", 1)):
        s = arm.summary(metric)
        out[name] = s
        if s.get("n"):
            print(f"  {name:16s} n={s['n']} m={s['samples_per_example']:.2f} "
                  f"mean={pct(s['mean'])} CI95={fmt_ci(s['ci95'])} (paper SE) "
                  f"boot={fmt_ci(s['boot_ci95'])} sigma2={s['sigma2_within']:.4f} tau2={s['tau2_between']:.4f}")
    if ex["empty_answers"]:
        ids = arm.answered_ids()
        out["answered_only"] = {"n": len(ids), "raw": arm.summary(0, ids), "length_adjusted": arm.summary(1, ids)}
        a = out["answered_only"]
        print(f"  answered-only     n={len(ids)} raw={pct(a['raw'].get('mean'))} "
              f"len-adj={pct(a['length_adjusted'].get('mean'))} CI95={fmt_ci(a['length_adjusted'].get('ci95'))} "
              f"(conditional on a non-empty answer; primary numbers above score empties as 0)")
    ls = out["length"]
    if ls:
        print(f"  length            mean={ls['mean_chars']:.0f} median={ls['median_chars']:.0f} chars "
              f"(penalty at median {LENGTH_COEFFICIENT * (ls['median_chars'] - LENGTH_BASELINE) * 100:+.2f} pp)")
    if slices and tags:
        out["slices"] = {}
        keys = sorted({t for pid in arm.example_ids() for t in tags.get(pid, []) if not t.startswith("specialty:")})
        for key in keys:
            ids = [pid for pid in arm.example_ids() if key in tags.get(pid, [])]
            if len(ids) < 10:
                continue
            s_raw = arm.summary(0, ids)
            s_len = arm.summary(1, ids)
            out["slices"][key] = {"raw": s_raw, "length_adjusted": s_len}
            print(f"    {key:28s} n={len(ids):3d} raw={pct(s_raw['mean'])} len-adj={pct(s_len['mean'])} CI95={fmt_ci(s_len['ci95'])}")
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", type=Path, default=None, help="dataset JSONL for slice tags")
    ap.add_argument("--arm", action="append", default=[], help="LABEL=graded[::completions][,graded2[::completions2]...]")
    ap.add_argument("--compare", action="append", default=[], help="A:B paired comparison (A minus B)")
    ap.add_argument("--slices", action="store_true", help="report use_case / type / difficulty slices")
    ap.add_argument("--json", type=Path, default=None, help="write the full report as JSON")
    ap.add_argument("--keep-failed-grades", action="store_true",
                    help="score items whose grader calls failed (stored as met=false) instead of excluding them")
    args = ap.parse_args(argv)

    if not args.arm:
        ap.error("at least one --arm is required")

    tags = load_tags(args.dataset)
    arms: Dict[str, Arm] = {}
    for spec in args.arm:
        label, trials = parse_arm_spec(spec)
        arm = arms.setdefault(label, Arm(label))
        for graded, comp in trials:
            if not graded.is_file():
                print(f"  WARNING arm {label}: missing graded file {graded}, trial skipped")
                continue
            if comp is not None and not comp.is_file():
                print(f"  WARNING arm {label}: missing completions file {comp}, lengths unknown")
                comp = None
            lengths = load_completion_lengths(comp) if comp else None
            arm.add_trial(load_trial(graded, lengths, keep_failed=args.keep_failed_grades))
    arms = {k: v for k, v in arms.items() if v.trials}
    if not arms:
        print("no arm has a graded trial; nothing to score")
        return 3

    report: dict = {
        "method": "Soskin Hicks et al. 2026, arXiv:2604.27470, sections 4.1-4.3",
        "length_coefficient": LENGTH_COEFFICIENT,
        "length_baseline_chars": LENGTH_BASELINE,
        "arms": {},
        "comparisons": {},
    }
    for label, arm in arms.items():
        report["arms"][label] = report_arm(arm, tags, args.slices)

    for spec in args.compare:
        if ":" not in spec:
            ap.error(f"--compare needs A:B, got {spec!r}")
        a, b = spec.split(":", 1)
        if a not in arms or b not in arms:
            print(f"\n  WARNING --compare {spec}: arm without graded trials, comparison skipped")
            report["comparisons"][spec] = {"skipped": "arm without graded trials"}
            continue
        print(f"\n== compare {a} minus {b} (paired, example-level means) ==")
        comp = {}
        for name, metric in (("raw", 0), ("length_adjusted", 1)):
            c = compare_arms(arms[a], arms[b], metric)
            comp[name] = c
            if c.get("n_paired"):
                print(f"  {name:16s} n={c['n_paired']} diff={c['mean_diff'] * 100:+.2f} pp "
                      f"CI95={fmt_ci(c['ci95'])} t={c['t']:.2f} p={c['p_two_sided']:.4f} "
                      f"boot={fmt_ci(c['boot_ci95'])} sign p={c['sign_test_p']:.3f} "
                      f"W/L/T={c['wins']}/{c['losses']}/{c['ties']}")
        report["comparisons"][f"{a}:{b}"] = comp

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
