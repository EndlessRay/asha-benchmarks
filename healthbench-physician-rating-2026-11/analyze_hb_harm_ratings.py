#!/usr/bin/env python3
"""Readout of the blinded clinician ratings of HealthBench harm criteria (kit version 2).

Input: the backup CSV each rater saves from the rating page (rater_hb_harm_v2_<initials>.csv), or one CSV
holding several raters (the "rater" column tells them apart), and rater_hb_harm_KEY.csv. Two or three raters.
Output: READOUT_ratings.md and READOUT_ratings.json beside this script.

What it reports
  1. Completion and inter-rater agreement (percent, Cohen kappa) on met / not met.
  2. Concordant units: does the clinician consensus match the verdict all three graders share?
  3. Disputed units: on criteria where the official grader differs from both others, which side the clinicians
     take, with a Wilson interval, by direction and by arm.
  4. Severe units: for each conversation behind the paper's severe-harm count, whether the clinicians confirm it
     (the flagged arm met the criterion, the other arm did not).
Consensus: with two raters, both give the same decisive verdict; with three, the majority of the decisive
verdicts (at least two raters decisive). Units with no consensus are counted and left out of the consensus rows.

Fixed on 13 Nov 2026, before any rater was unblinded and before any readout was run:
  - EXCLUDED: two units whose statement belongs to a different conversation (a fault in the benchmark file).
  - CONTEXT_SEEKING: 34 units whose statement is about the answer asking the user for information. The rating
    page did not say whether advice that covers the possibilities without asking counts as "seeking context",
    so agreement and the disputed readout are also given for these units and for the rest separately.

Usage: python3 analyze_hb_harm_ratings.py ratings/rater_hb_harm_v2_R1.csv ratings/rater_hb_harm_v2_R2.csv ratings/rater_hb_harm_v2_R3.csv
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADERS = {"gpt_4_1": "GPT-4.1 (official)", "gpt_5_4": "GPT-5.4", "claude_opus_4_8": "Claude Opus 4.8"}
ARM = {"asha": "Asha Apex-J", "bare": "GPT-6 Astra alone"}

# HealthBench prompt c067a763 (a question about Adderall in the UK) carries 13 criteria about hepatitis B
# post-exposure prophylaxis in OpenAI's released file (2025-05-07-06-14-12_oss_eval.jsonl); they belong to
# another question. Found by a rater during rating. Both kit units on that prompt are left out.
EXCLUDED = {
    "hb2_169": "statement about hepatitis B prophylaxis attached to a conversation about Adderall (benchmark file fault)",
    "hb2_201": "statement about hepatitis B prophylaxis attached to a conversation about Adderall (benchmark file fault)",
}
# Chosen by reading the statements only: the main clause says the answer asks, seeks, gathers, inquires about or
# obtains information from the user, or fails to.
CONTEXT_SEEKING = {f"hb2_{n:03d}" for n in (
    2, 24, 37, 39, 41, 44, 49, 57, 58, 60, 66, 75, 77, 84, 88, 93, 121, 125, 127, 138, 141, 144, 149, 159, 174,
    208, 217, 218, 221, 225, 239, 242, 244, 248)}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    z, p = 1.959964, k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def kappa(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    pa, pb = sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def share(k: int, n: int) -> str:
    if n == 0:
        return "no units"
    lo, hi = wilson(k, n)
    return f"{k} of {n} ({100 * k / n:.1f}%; 95% CI {lo:.1f} to {hi:.1f})"


def main() -> int:
    files = [Path(a) for a in sys.argv[1:]]
    if not files:
        print(__doc__)
        return 2
    key = {r["unit_id"]: r for r in csv.DictReader(open(HERE / "rater_hb_harm_KEY.csv", encoding="utf-8"))}
    kit_size = len(key)
    missing = (set(EXCLUDED) | CONTEXT_SEEKING) - set(key)
    if missing:
        print("Units named in this script are not in the key:", sorted(missing))
        return 1
    for u in EXCLUDED:
        del key[u]
    ratings: dict[str, dict[str, str]] = {}
    for f in files:
        got = list(csv.DictReader(open(f, encoding="utf-8")))
        if any(r["unit_id"].startswith("hb_") for r in got):
            print(f"{f.name}: these are version 1 unit ids; this kit is version 2")
            return 1
        for r in got:                       # units dropped from the kit (not in the key) are ignored
            if r["unit_id"] in key:
                ratings.setdefault(r.get("rater") or f.stem, {})[r["unit_id"]] = r["rating"]
    raters = list(ratings)
    if len(raters) < 2:
        print("Two or three raters are needed for a consensus; found:", raters)
    out = {"raters": raters, "units_in_kit": kit_size, "units_analysed": len(key), "excluded": EXCLUDED,
           "context_seeking_units": len(CONTEXT_SEEKING)}
    md = ["# Identity-masked physician rating of HealthBench harm criteria: readout", "",
          f"Kit version 2 ({kit_size} units, HealthBench Hard, reference rubric rendering). Raters: {', '.join(raters)}.", "",
          f"Analysed: {len(key)} units. Excluded before unblinding: {', '.join(EXCLUDED)}. Their statements are about "
          "hepatitis B prophylaxis and are attached, in the benchmark file itself, to a conversation about Adderall.", ""]

    md += ["## Completion", "", "| Rater | Met | Not met | Cannot tell | Unrated |", "|---|---:|---:|---:|---:|"]
    for r in raters:
        c = Counter(ratings[r].get(u, "") for u in key)
        md.append(f"| {r} | {c['met']} | {c['not_met']} | {c['cannot_tell']} | {c['']} |")
        out[f"completion_{r}"] = dict(c)

    def decisive(r, u):
        v = ratings[r].get(u, "")
        return None if v not in ("met", "not_met") else v == "met"

    consensus: dict[str, bool] = {}
    if len(raters) >= 2:
        md += ["", "## Agreement between the raters", "",
               "| Raters | Stratum | Units both rated | Agreement | Cohen kappa |", "|---|---|---:|---:|---:|"]
        for x in range(len(raters)):
            for y in range(x + 1, len(raters)):
                a, b = raters[x], raters[y]
                for stratum in ("all", "disputed", "concordant", "severe", "asks for context", "other statements"):
                    pairs = [(decisive(a, u), decisive(b, u)) for u, k in key.items()
                             if stratum in ("all", k["stratum"])
                             or (stratum == "asks for context" and u in CONTEXT_SEEKING)
                             or (stratum == "other statements" and u not in CONTEXT_SEEKING)]
                    pairs = [(p, q) for p, q in pairs if p is not None and q is not None]
                    agree = sum(p == q for p, q in pairs)
                    kp = kappa(pairs)
                    md.append(f"| {a} and {b} | {stratum} | {len(pairs)} | {100 * agree / len(pairs):.1f}% | {kp:.2f} |"
                              if pairs else f"| {a} and {b} | {stratum} | 0 | | |")
                    out[f"agreement_{a}_{b}_{stratum}"] = {"n": len(pairs), "agree": agree, "kappa": kp}
        need = 2
        for u in key:
            votes = [v for r in raters if (v := decisive(r, u)) is not None]
            yes = sum(votes)
            if len(votes) >= need and yes != len(votes) - yes and (len(raters) > 2 or yes in (0, len(votes))):
                consensus[u] = yes > len(votes) - yes
        if len(raters) > 2:
            full = [[decisive(r, u) for r in raters] for u in key]
            full = [v for v in full if all(x is not None for x in v)]
            if full:
                n, m = len(full), len(raters)
                pj = sum(sum(v) for v in full) / (n * m)
                pbar = sum((sum(v) ** 2 + (m - sum(v)) ** 2 - m) / (m * (m - 1)) for v in full) / n
                pe = pj ** 2 + (1 - pj) ** 2
                fleiss = float("nan") if pe == 1 else (pbar - pe) / (1 - pe)
                md += ["", f"Fleiss kappa across the {m} raters, on the {n} units all of them rated decisively: {fleiss:.2f}."]
                out["fleiss_kappa"] = {"n": n, "kappa": fleiss}
        verdicts = consensus
        basis = "consensus of both raters" if len(raters) == 2 else f"majority of the {len(raters)} raters"
    else:
        verdicts = {u: v for u in key if (v := decisive(raters[0], u)) is not None}
        basis = f"one rater ({raters[0]}); no consensus is possible"
    md += ["", f"Rows below use the {basis}: {len(verdicts)} of {len(key)} units."]

    md += ["", "## Concordant units (all three graders agree)", ""]
    conc = [(u, k) for u, k in key.items() if k["stratum"] == "concordant" and u in verdicts]
    hit = sum(verdicts[u] == bool(int(k["grader_gpt_4_1_met"])) for u, k in conc)
    md.append(f"Clinicians matched the graders' shared verdict on {share(hit, len(conc))}.")
    out["concordant"] = {"n": len(conc), "match": hit}

    md += ["", "## Disputed units (the official grader differs from both others)", "",
           "| Subset | Clinicians side with the official grader |", "|---|---|"]
    disp = [(u, k) for u, k in key.items() if k["stratum"] == "disputed" and u in verdicts]
    subsets = {"all disputed": lambda k: True,
               "official says met": lambda k: k["kind"] == "disputed_official_met",
               "official says not met": lambda k: k["kind"] == "disputed_official_not_met",
               **{ARM[a]: (lambda k, a=a: k["arm"] == a) for a in ARM},
               "statement asks for context": lambda k: k["unit_id"] in CONTEXT_SEEKING,
               "other statements": lambda k: k["unit_id"] not in CONTEXT_SEEKING}
    for name, pred in subsets.items():
        sel = [(u, k) for u, k in disp if pred(k)]
        side = sum(verdicts[u] == bool(int(k["grader_gpt_4_1_met"])) for u, k in sel)
        md.append(f"| {name} | {share(side, len(sel))} |")
        out[f"disputed_{name}"] = {"n": len(sel), "with_official": side}
    md += ["", "On these units GPT-5.4 and Claude Opus 4.8 agree with each other, so the remainder side with them.",
           "", f"\"Asks for context\": the {len(CONTEXT_SEEKING)} statements about the answer asking the user for information. "
           "The rating page did not say whether advice that covers the possibilities without asking counts, so these "
           "are shown apart."]

    md += ["", "## Share of rated criteria the clinicians call met, by arm", "",
           "| Stratum | " + " | ".join(ARM.values()) + " |", "|---|---|---|"]
    for stratum in ("disputed", "concordant", "severe"):
        cells = []
        for a in ARM:
            sel = [u for u, k in key.items() if k["stratum"] == stratum and k["arm"] == a and u in verdicts]
            cells.append(share(sum(verdicts[u] for u in sel), len(sel)))
        md.append(f"| {stratum} | " + " | ".join(cells) + " |")
    md += ["", "These are rates within a stratified sample, not estimates for HealthBench Hard as a whole."]

    md += ["", "## Severe-harm conversations", ""]
    conv = defaultdict(lambda: defaultdict(list))
    for u, k in key.items():
        if k["stratum"] == "severe":
            conv[(k["prompt_id"], k["flagged_arm"])][k["arm"]].append(u)
    tally = defaultdict(Counter)
    for (pid, flagged), arms in conv.items():
        other = "bare" if flagged == "asha" else "asha"
        units = arms[flagged] + arms[other]
        if any(u not in verdicts for u in units):
            tally[flagged]["not settled"] += 1
        elif any(verdicts[u] for u in arms[flagged]) and not any(verdicts[u] for u in arms[other]):
            tally[flagged]["confirmed"] += 1
        elif not any(verdicts[u] for u in arms[flagged]):
            tally[flagged]["flagged arm cleared"] += 1
        else:
            tally[flagged]["both arms met"] += 1
    md += ["| Graders flagged only | Conversations | Confirmed by clinicians | Flagged arm cleared | Both arms met | Not settled |",
           "|---|---:|---:|---:|---:|---:|"]
    for flagged in ("bare", "asha"):
        t = tally[flagged]
        md.append(f"| {ARM[flagged]} | {sum(t.values())} | {t['confirmed']} | {t['flagged arm cleared']} | "
                  f"{t['both arms met']} | {t['not settled']} |")
        out[f"severe_{flagged}"] = dict(t)
    md += ["", "Confirmed: clinicians rate a severe criterion met in the flagged arm's answer and in none of the other "
           "arm's. Not settled: the raters differ, or one could not tell, on a unit of that conversation."]

    (HERE / "READOUT_ratings.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "READOUT_ratings.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
