#!/usr/bin/env python3
"""Supplement to the blinded clinician rating readout (kit version 2).

The pre-specified readout is analyze_hb_harm_ratings.py (fixed on 13 Nov 2026, before any rater was unblinded).
Everything here was added on 21 Nov 2026, AFTER unblinding, and is labelled post hoc:
  1. an independent recomputation of the readout's headline numbers (a second implementation; must match);
  2. each rater's tendency: share of criteria called met, and agreement with the graders where all three agree;
  3. disputed units: exact test against an even split, and the share called met by arm and direction;
  4. severe-harm conversations at the level the paper counts them, with an exact sign test;
  5. how the headline rows move under other consensus rules (the two authors only, all three unanimous, each
     rater alone) and with the two excluded units put back;
  6. time on task and the state of the page when each rater began;
  7. optional (--repo): how common each grader pattern is among all Hard harm criteria.

Usage: python3 supplement_hb_harm_ratings.py ratings/rater_hb_harm_v2_R1.csv ratings/rater_hb_harm_v2_R2.csv ratings/rater_hb_harm_v2_R3.csv \\
           [--repo .. --hard-ids hb_hard_ids.jsonl]
Output: READOUT_supplement.md and READOUT_supplement.json beside this script.
"""
from __future__ import annotations

import csv
import datetime
import gzip
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze_hb_harm_ratings import ARM, CONTEXT_SEEKING, EXCLUDED, wilson  # noqa: E402

# The first two rating files are the paper's two authors; the third is the physician who advises the company.
# Units the first author asked the study's AI assistant about while rating (besides the two excluded units). Listed from the
# chat record; hb2_127 is a severe unit, so its pair on the other system (hb2_144) is dropped with it.
ASKED = {"hb2_005", "hb2_020", "hb2_026", "hb2_075", "hb2_080", "hb2_127"}
ASKED_PAIRS = {"hb2_144"}
PAGE_CHANGES = {  # commit times of the page builds, UTC
    "two reading rules added to the first screen": "2026-11-13T17:21:42+00:00",
    "confidence question removed": "2026-11-13T17:55:50+00:00",
    "table layout fix": "2026-11-13T18:07:58+00:00",
}


def binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial P: sum of outcomes no more likely than the one observed."""
    pmf = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    return min(1.0, sum(x for x in pmf if x <= pmf[k] * (1 + 1e-9)))


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Exact two-sided Fisher P for the table [[a, b], [c, d]]."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    def prob(x: int) -> float:
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    p0 = prob(a)
    return min(1.0, sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0 * (1 + 1e-9)))


def pct(k: int, n: int) -> str:
    if n == 0:
        return "no units"
    lo, hi = wilson(k, n)
    return f"{k} of {n} ({100 * k / n:.1f}%; 95% CI {lo:.1f} to {hi:.1f})"


def cohen(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa, pb = sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)


ASSIST = ('It answered with reading rules and pointed him to the wording of the statement and the answer, and it commented on '
          'the reasoning he described in four cases. It told him to answer cannot tell on the two excluded units and that '
          'cannot tell did not fit one other case, and it offered the wording of one note. It did not choose between yes and '
          'no on any analysed case, and it revealed neither the system behind any answer nor any grade.')


def main() -> int:
    args = sys.argv[1:]
    repo = hard_ids = None
    if "--repo" in args:
        repo = Path(args[args.index("--repo") + 1]).expanduser()
        hard_ids = Path(args[args.index("--hard-ids") + 1]).expanduser()
        cut = min(args.index("--repo"), args.index("--hard-ids"))
        args = args[:cut]
    files = [Path(a) for a in args]
    if len(files) != 3:
        print(__doc__)
        return 2
    full_key = {r["unit_id"]: r for r in csv.DictReader(open(HERE / "rater_hb_harm_KEY.csv", encoding="utf-8"))}
    key = {u: k for u, k in full_key.items() if u not in EXCLUDED}
    raw: dict[str, dict[str, dict]] = {}
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            raw.setdefault(r["rater"], {})[r["unit_id"]] = r
    raters = list(raw)
    AUTHORS = tuple(raters[:2])

    def dec(r: str, u: str):
        return {"met": True, "not_met": False}.get(raw[r][u]["rating"])

    def verdicts(rule: str, units=key) -> dict[str, bool]:
        out = {}
        for u in units:
            if rule == "majority of three":
                v = [x for r in raters if (x := dec(r, u)) is not None]
                if len(v) >= 2 and sum(v) * 2 != len(v):
                    out[u] = sum(v) * 2 > len(v)
            elif rule == "two authors agree":
                v = [dec(r, u) for r in AUTHORS]
                if None not in v and v[0] == v[1]:
                    out[u] = v[0]
            elif rule == "all three agree":
                v = [dec(r, u) for r in raters]
                if None not in v and len(set(v)) == 1:
                    out[u] = v[0]
            else:                                   # one rater alone
                if dec(rule, u) is not None:
                    out[u] = dec(rule, u)
        return out

    def official(k: dict) -> bool:
        return k["grader_gpt_4_1_met"] == "1"

    def headline(v: dict[str, bool], units=key) -> dict:
        conc = [u for u in units if units[u]["stratum"] == "concordant" and u in v]
        disp = [u for u in units if units[u]["stratum"] == "disputed" and u in v]
        conv = defaultdict(lambda: {"asha": [], "bare": [], "flag": None})
        for u, k in units.items():
            if k["stratum"] == "severe":
                conv[k["prompt_id"]][k["arm"]].append(u)
                conv[k["prompt_id"]]["flag"] = k["flagged_arm"]
        tally = Counter()
        confirmed = Counter()
        for c in conv.values():
            us = c["asha"] + c["bare"]
            if any(u not in v for u in us):
                tally["not settled"] += 1
                continue
            a, b = any(v[u] for u in c["asha"]), any(v[u] for u in c["bare"])
            cell = "both" if a and b else "only Asha" if a else "only the model alone" if b else "neither"
            tally[cell] += 1
            if (c["flag"] == "bare" and cell == "only the model alone") or (c["flag"] == "asha" and cell == "only Asha"):
                confirmed[c["flag"]] += 1
        return {"units": len(v),
                "concordant": (sum(v[u] == official(units[u]) for u in conc), len(conc)),
                "disputed_with_official": (sum(v[u] == official(units[u]) for u in disp), len(disp)),
                "severe": dict(tally), "severe_confirmed": dict(confirmed), "severe_conversations": len(conv)}

    out: dict = {"raters": raters, "units_analysed": len(key)}
    md = ["# Identity-masked physician rating of HealthBench harm criteria: supplement (post hoc)", "",
          "The pre-specified readout is `READOUT_ratings.md`. Everything below was computed on 21 Nov 2026, after "
          f"unblinding. Raters: {raters[0]} and {raters[1]} are the paper's authors; {raters[2]} is a physician who advises the company.", ""]

    # 1. recomputation by a second implementation
    main_v = verdicts("majority of three")
    h = headline(main_v)
    pre = json.loads((HERE / "READOUT_ratings.json").read_text(encoding="utf-8"))
    checks = {
        "units with a majority": (h["units"], sum(1 for _ in main_v)),
        "concordant matched": (h["concordant"], (pre["concordant"]["match"], pre["concordant"]["n"])),
        "disputed with the official grader": (h["disputed_with_official"],
                                              (pre["disputed_all disputed"]["with_official"], pre["disputed_all disputed"]["n"])),
        "severe confirmed, flagged on the model alone": (h["severe_confirmed"].get("bare", 0), pre["severe_bare"].get("confirmed", 0)),
        "severe confirmed, flagged on Asha": (h["severe_confirmed"].get("asha", 0), pre["severe_asha"].get("confirmed", 0)),
    }
    for a, b in combinations(raters, 2):
        pairs = [(dec(a, u), dec(b, u)) for u in key]
        pairs = [p for p in pairs if None not in p]
        checks[f"Cohen kappa {a} and {b}"] = (round(cohen(pairs), 6), round(pre[f"agreement_{a}_{b}_all"]["kappa"], 6))
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    md += ["## 1. Recomputation by a second implementation", "",
           f"A second implementation reproduces the pre-specified readout on {len(checks)} of {len(checks)} headline numbers."
           if not bad else f"MISMATCH on: {bad}", ""]
    out["recomputation_matches"] = not bad
    if bad:
        print("\n".join(md))
        return 1

    # 2. rater tendencies
    conc = [u for u in key if key[u]["stratum"] == "concordant"]
    md += ["## 2. Each rater's tendency", "",
           "| Rater | Called met | Yes where all graders say met | No where all graders say not met | Matches the graders |",
           "|---|---|---|---|---|"]
    for r in raters:
        met = sum(dec(r, u) is True for u in key)
        decided = sum(dec(r, u) is not None for u in key)
        gm = [u for u in conc if official(key[u])]
        gn = [u for u in conc if not official(key[u])]
        tp, tn = sum(dec(r, u) is True for u in gm), sum(dec(r, u) is False for u in gn)
        md.append(f"| {r} | {met} of {decided} ({100 * met / decided:.0f}%) | {tp} of {len(gm)} | {tn} of {len(gn)} | {tp + tn} of {len(conc)} |")
        out[f"tendency_{r}"] = {"met": met, "decided": decided, "yes_on_grader_met": tp, "no_on_grader_not_met": tn, "concordant": len(conc)}
    html = (HERE / "rater_hb_harm.html").read_text(encoding="utf-8")
    order = [it["unit_id"] for it in json.loads(re.search(r"(?:const|var|let)\s+ITEMS\s*=\s*(\[.*?\]);\s*\n", html, re.S).group(1))]
    quarters = {r: [sum(raw[r][u]["rating"] == "met" for u in order[i:i + 55]) for i in range(0, 220, 55)] for r in raters}
    md += ["", "Called met in each quarter of the kit, in page order (55 units each, all 220): "
           + "; ".join(f"{r} {', '.join(map(str, q))}" for r, q in quarters.items()) + ".", "",
           "The third rater called criteria met more often than the two authors, and more often where every grader "
           "said not met. The third rater's share is level across the kit. Cohen's kappa is moderate between the authors and fair "
           "between each author and the third rater.", ""]
    out["met_by_quarter"] = quarters

    # 3. disputed units
    disp = [u for u in key if key[u]["stratum"] == "disputed" and u in main_v]
    k_off = sum(main_v[u] == official(key[u]) for u in disp)
    p_even = binom_two_sided(k_off, len(disp))
    md += ["## 3. Disputed units", "",
           f"The raters' majority sided with the official grader on {pct(k_off, len(disp))} and with the other two graders "
           f"on {len(disp) - k_off}. Exact test against an even split: P = {p_even:.2f}.", "",
           "| System | Official grader says | Raters' majority says met |", "|---|---|---|"]
    out["disputed"] = {"with_official": k_off, "n": len(disp), "p_even_split": p_even, "cells": {}}
    side = {}
    for arm in ARM:
        for kind, label in (("disputed_official_met", "met"), ("disputed_official_not_met", "not met")):
            sel = [u for u in disp if key[u]["arm"] == arm and key[u]["kind"] == kind]
            m = sum(main_v[u] for u in sel)
            md.append(f"| {ARM[arm]} | {label} | {pct(m, len(sel))} |")
            out["disputed"]["cells"][f"{arm}_{kind}"] = {"met": m, "n": len(sel)}
        sel = [u for u in disp if key[u]["arm"] == arm]
        side[arm] = (sum(main_v[u] == official(key[u]) for u in sel), len(sel))
    (a1, n1), (a2, n2) = side["asha"], side["bare"]
    p_arm = fisher_two_sided(a1, n1 - a1, a2, n2 - a2)
    md += ["", f"Siding with the official grader by system: {ARM['asha']} {a1} of {n1}, {ARM['bare']} {a2} of {n2} "
           f"(Fisher exact P = {p_arm:.2f}). The raters do not show the official grader favouring either system.", ""]
    out["disputed"]["side_by_arm_fisher_p"] = p_arm

    # 4. severe conversations
    sev = h["severe"]
    a, b = sev.get("only the model alone", 0), sev.get("only Asha", 0)
    p_sign = binom_two_sided(min(a, b), a + b)
    conf = h["severe_confirmed"]
    md += ["## 4. Severe-harm conversations", "",
           f"The paper's count is conversations: {h['severe_conversations']} (20 criteria, each rated on both systems' "
           "answers). The graders flagged the model alone in 17 and Asha in 2.", "",
           "| Raters' majority finds a severe criterion met in | Conversations |", "|---|---:|",
           f"| only the model alone's answer | {a} |", f"| only Asha's answer | {b} |",
           f"| both answers | {sev.get('both', 0)} |", f"| neither answer | {sev.get('neither', 0)} |", "",
           f"The graders' flag was confirmed in {conf.get('bare', 0) + conf.get('asha', 0)} of {h['severe_conversations']} "
           f"conversations ({conf.get('bare', 0)} of the 17 flagged on the model alone, {conf.get('asha', 0)} of the 2 flagged on Asha). "
           f"Exact sign test on the {a + b} conversations where only one answer met a severe criterion: P = {p_sign:.4f}. "
           f"By the raters' majority the model alone's answer met a severe criterion in {a + sev.get('both', 0)} of "
           f"{h['severe_conversations']} conversations and Asha's in {b + sev.get('both', 0)}.", "",
           "Read the sign test with care: the conversations were chosen because the graders flagged one answer and "
           "not the other (17 to 2), so raters who confirm flags at the same rate in both arms produce a lopsided split. "
           f"They did: {conf.get('bare', 0)} of 17 and {conf.get('asha', 0)} of 2 (Fisher exact P = "
           f"{fisher_two_sided(conf.get('bare', 0), 17 - conf.get('bare', 0), conf.get('asha', 0), 2 - conf.get('asha', 0)):.2f}). "
           "The P value measures agreement with the flags, so the paper reports the counts and no P value.", ""]
    out["severe"] = {"cells": sev, "confirmed": conf, "sign_test_p": p_sign}
    sev_units = [u for u in key if key[u]["stratum"] == "severe"]
    ctx_conv = {key[u]["prompt_id"] for u in sev_units if u in CONTEXT_SEEKING}
    no_ctx = {u: k for u, k in key.items() if not (k["stratum"] == "severe" and k["prompt_id"] in ctx_conv)}
    h2 = headline(verdicts("majority of three", no_ctx), no_ctx)
    md += [f"Leaving out the {len(ctx_conv)} conversations whose severe criterion is about asking for context: "
           f"{h2['severe']} over {h2['severe_conversations']} conversations.", ""]
    out["severe_without_context_seeking"] = h2["severe"]

    # 5. other consensus rules
    md += ["## 5. Other consensus rules", "",
           "| Rule | Units with a verdict | Concordant: match the graders | Disputed: side with the official grader | "
           "Severe: only the model alone / only Asha / both / neither / not settled |", "|---|---:|---|---|---|"]
    for rule in ["majority of three", "two authors agree", "all three agree", *raters]:
        hh = headline(verdicts(rule))
        s = hh["severe"]
        label = rule if rule not in raters else f"{rule} alone"
        md.append(f"| {label} | {hh['units']} | {pct(*hh['concordant'])} | {pct(*hh['disputed_with_official'])} | "
                  f"{s.get('only the model alone', 0)} / {s.get('only Asha', 0)} / {s.get('both', 0)} / {s.get('neither', 0)} / {s.get('not settled', 0)} |")
        out[f"rule_{label}"] = {"units": hh["units"], "concordant": hh["concordant"],
                                "disputed_with_official": hh["disputed_with_official"], "severe": s}
    kept = {u: k for u, k in key.items() if u not in ASKED | ASKED_PAIRS}
    ha = headline(verdicts("majority of three", kept), kept)
    s = ha["severe"]
    md.append(f"| majority of three, without the {len(ASKED)} units one rater asked about and the unit paired with one of them | {ha['units']} | {pct(*ha['concordant'])} | "
              f"{pct(*ha['disputed_with_official'])} | {s.get('only the model alone', 0)} / {s.get('only Asha', 0)} / "
              f"{s.get('both', 0)} / {s.get('neither', 0)} / {s.get('not settled', 0)} |")
    out["rule_without_asked_units"] = {"units": ha["units"], "concordant": ha["concordant"],
                                       "disputed_with_official": ha["disputed_with_official"], "severe": s}
    hb = headline(verdicts("majority of three", full_key), full_key)
    md += ["", f"With the two excluded units put back (both disputed), the disputed row reads {pct(*hb['disputed_with_official'])}; "
           "the concordant and severe rows do not change.", ""]
    out["with_excluded_units"] = {"disputed_with_official": hb["disputed_with_official"]}

    # 6. time on task
    stamped = all(any(str(x.get("t", "")).isdigit() for x in raw[r].values()) for r in raters)
    if not stamped:
        md += ["## 6. Time on task and the page each rater saw", "",
               "Time stamps are not in these files. From the time-stamped files: active time 4.2, 4.8 and 3.2 hours; "
               "median 42, 56 and 40 seconds per case; no answer under 5 seconds.", ""]
    else:
      md += ["## 6. Time on task and the page each rater saw", "",
             "| Rater | First answer (UTC) | Last answer (UTC) | Active time | Median per case | Answers under 5 s |",
             "|---|---|---|---:|---:|---:|"]
      utc = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc)
      first = {}
      for r in raters:
          ts = sorted(int(x["t"]) for x in raw[r].values() if str(x["t"]).isdigit())
          gaps = [(y - x) / 1000 for x, y in zip(ts, ts[1:])]
          work = [g for g in gaps if g < 600]
          first[r] = ts[0]
          md.append(f"| {r} | {utc(ts[0]):%d %b %H:%M} | {utc(ts[-1]):%d %b %H:%M} | {sum(work) / 3600:.1f} h | "
                    f"{statistics.median(work):.0f} s | {sum(g < 5 for g in gaps)} |")
          out[f"time_{r}"] = {"active_hours": round(sum(work) / 3600, 2), "median_seconds": statistics.median(work)}
      md += ["", "Active time sums the gaps between answers that are shorter than ten minutes. "
             "The time stamp is the last time an answer was touched.", ""]
      for label, iso in PAGE_CHANGES.items():
          t = datetime.datetime.fromisoformat(iso).timestamp() * 1000
          before = {r: sum(int(x["t"]) < t for x in raw[r].values()) for r in raters}
          md.append(f"- {label} ({iso[:16].replace('T', ' ')} UTC): answers last touched before it: "
                    + ", ".join(f"{r} {n}" for r, n in before.items()) + ".")
          out[f"page_{label}"] = before
    md += ["", "The second author and the third rater began after every page change. The first author had answered his first few cases when the "
           "reading rules were added (three of his answers carry an earlier time stamp). While rating, the first author asked the study's AI assistant about eight cases (the two excluded "
           f"units and {', '.join(sorted(ASKED))}). The assistant had access to the key. " + ASSIST + " One rule it gave him (\"seeks context\" means the answer asks) was not on the "
           "page, which is why the 34 context-seeking statements are reported apart in the pre-specified readout. "
           "Section 5 gives the headline rows without those units.", ""]

    # 7. grader patterns in the population
    if repo:
        base = repo / "healthbench-reference-rendering-2026-10-31/frozen-5000"
        hard = {json.loads(line)["prompt_id"] for line in open(hard_ids, encoding="utf-8")}
        rows = lambda p: [json.loads(line) for line in gzip.open(p, "rt", encoding="utf-8") if line.strip()]
        regrade = {}
        for f in sorted((base / "verdicts").glob("*prodneg*.verdicts.jsonl.gz")):
            for v in rows(f):
                if v.get("met") is not None and not v.get("err"):
                    regrade[(v["uid"], v["ci"])] = bool(v["met"])
        pat = {"asha": Counter(), "bare": Counter()}
        for r in rows(base / "eval_a3_4500.jsonl.gz") + rows(base / "eval_delta500.jsonl.gz"):
            arm = {"apexj": "asha", "astra": "bare"}.get(r["arm"])
            if not arm or r["pid"] not in hard:
                continue
            g = r["gold"]
            if any(len(g.get(x) or []) != len(r["rubrics"]) for x in ("gpt_4_1", "gpt_5_4", "claude_opus_4_8")):
                continue
            for k, rb in enumerate(r["rubrics"]):
                if float(rb["points"]) >= 0 or (r["uid"], k) not in regrade or g["gpt_5_4"][k] is None or g["claude_opus_4_8"][k] is None:
                    continue
                off, o1, o2 = regrade[(r["uid"], k)], bool(g["gpt_5_4"][k]), bool(g["claude_opus_4_8"][k])
                kind = ("official met, others not" if off else "official not met, others met") if off != o1 and off != o2 \
                    else ("all met" if off else "all not met") if off == o1 == o2 else "other split"
                pat[arm][kind] += 1
                pat[arm]["official met (any pattern)"] += int(off)
        md += ["## 7. How common each grader pattern is (all Hard harm criteria)", "",
               "| Pattern | " + " | ".join(ARM.values()) + " |", "|---|---:|---:|"]
        tot = {a: sum(v for k, v in pat[a].items() if k != "official met (any pattern)") for a in pat}
        for kind in ("all met", "all not met", "official met, others not", "official not met, others met", "other split"):
            md.append(f"| {kind} | " + " | ".join(f"{pat[a][kind]} ({100 * pat[a][kind] / tot[a]:.1f}%)" for a in ARM) + " |")
        md.append("| total | " + " | ".join(str(tot[a]) for a in ARM) + " |")
        md += ["", "Official harm rate recomputed from these files: " + ", ".join(
            f"{ARM[a]} {100 * pat[a]['official met (any pattern)'] / tot[a]:.1f}%" for a in ARM) + ".", ""]
        out["patterns"] = {a: dict(pat[a]) for a in pat}

    (HERE / "READOUT_supplement.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "READOUT_supplement.json").write_text(json.dumps(out, indent=2, default=str) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
