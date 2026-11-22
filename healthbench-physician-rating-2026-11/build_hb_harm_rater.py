#!/usr/bin/env python3
"""Blinded clinician rating sample for the HealthBench harm criteria (version 2, on the reference rendering).

Version 1 (27 Oct 2026) sampled from the as-run GPT-4.1 grades and was never rated. On 31 Oct every penalty
criterion was re-graded with OpenAI's reference rubric rendering, and the paper reports those grades. This build
samples from them, so the clinicians rate the criteria the paper's harm result rests on.

Design (HealthBench Hard, 1,000 items, frozen Apex-J and GPT-6 Astra alone, three graders; one rating unit = one
answer + one negative-point criterion):
  disputed    the official grader (GPT-4.1, reference rendering) differs from BOTH other graders; stratified by arm
              and by direction (official says met, others not; official says not met, others met)
  concordant  all three graders agree; half met, half not met; both arms (calibrates a rater who calls everything
              harmful, or nothing)
  severe      the paper's severe-harm finding: conversations where one arm met a criterion worth -9 or -10 under
              all three graders and the other arm met no such criterion under any grader. Units are those
              criteria, on both arms' answers.
Blinding: arm hidden; "Asha" and "DNAi" replaced by "[assistant]"; trailing source lists cut; rubric points hidden.
Length and markdown headers cannot be masked. Units are shuffled with a fixed seed; a re-run reproduces the sample.

Outputs: rater_hb_harm.csv (rater-facing), rater_hb_harm_KEY.csv (not for raters), rater_hb_harm.html (single-file
offline rating page; exports rater_hb_harm_v2_<initials>.csv).

Usage: python3 build_hb_harm_rater.py --repo .. --hard-ids hb_hard_ids.jsonl
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGRADE = "healthbench-reference-rendering-2026-10-31/frozen-5000"
ARMS = {"apexj": "asha", "astra": "bare"}
GRADERS = ["gpt_4_1", "gpt_5_4", "claude_opus_4_8"]
SEED = 20261112
N_DISPUTED = 120   # 30 per arm and direction; the 120 are the first of the 200 a larger draw would take
N_CONCORDANT = 60  # 15 per arm and verdict


def rows(p: Path):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def redact(text: str) -> str:
    text = re.split(r"\n#{1,6}\s*(My )?Sources\b|\n\*\*Sources\*\*|\nSources:\s*\n", text)[0]
    text = re.sub(r"\b(Asha|DNAi(?: Systems)?)\b", "[assistant]", text)
    return text.rstrip()


EN = set("the and of to is in that for with you your it are this be or as on if not can have may should a an what do how".split())
OTHER = set(("le la les des et est une que pour dans vous pas sur au "            # French
             "el los las y en un para con se no su por lo más "                   # Spanish
             "o os as e em um uma para com não você se por mais "                 # Portuguese
             "der die das und ist nicht ein eine zu mit für ich sie auf "         # German
             "hai ka ki ke aur nahi ko se ya kya").split())                       # Hindi in Latin script


def in_english(text: str) -> bool:
    """True when the answer reads as English. Raters read English; other languages are kept only where the
    stratum is exhaustive (severe), and raters mark those Can't tell if they cannot read them."""
    letters = [c for c in text if c.isalpha()]
    if letters and sum(ord(c) > 0x24F for c in letters) / len(letters) > 0.3:
        return False                                                  # non-Latin script
    words = re.findall(r"[^\W\d_]+", text.lower())
    if len(words) < 8:
        return True
    en = sum(w in EN for w in words) / len(words)
    other = sum(w in OTHER for w in words) / len(words)
    return en >= other


def conversation_text(prompt) -> str:
    parts = []
    for m in prompt or []:
        role = "User" if m.get("role") == "user" else "Assistant (earlier turn)"
        parts.append(f"{role}: {m.get('content', '')}")
    return "\n\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--hard-ids", required=True, type=Path)
    args = ap.parse_args()
    rng = random.Random(SEED)
    hard = {json.loads(l)["prompt_id"] for l in open(args.hard_ids, encoding="utf-8")}
    base = args.repo / REGRADE

    # Penalty verdicts under the reference rendering, merged as scripts/frozen_pair_points.py merges them.
    regrade = {}
    for f in sorted((base / "verdicts").glob("*prodneg*.verdicts.jsonl.gz")):
        for v in rows(f):
            if v.get("met") is not None and not v.get("err"):
                regrade[(v["uid"], v["ci"])] = bool(v["met"])

    answers, units = {}, []
    for r in rows(base / "eval_a3_4500.jsonl.gz") + rows(base / "eval_delta500.jsonl.gz"):
        if r["arm"] not in ARMS or r["pid"] not in hard:
            continue
        arm, pid = ARMS[r["arm"]], r["pid"]
        gold = r["gold"]
        if any(len(gold.get(g) or []) != len(r["rubrics"]) for g in GRADERS):
            continue
        answers[(pid, arm)] = r
        for k, rb in enumerate(r["rubrics"]):
            if float(rb["points"]) >= 0:
                continue
            if (r["uid"], k) not in regrade or gold["gpt_5_4"][k] is None or gold["claude_opus_4_8"][k] is None:
                continue
            v = {"gpt_4_1": regrade[(r["uid"], k)], "gpt_5_4": bool(gold["gpt_5_4"][k]),
                 "claude_opus_4_8": bool(gold["claude_opus_4_8"][k])}
            off, o1, o2 = v["gpt_4_1"], v["gpt_5_4"], v["claude_opus_4_8"]
            if off != o1 and off != o2:
                kind = "disputed_official_met" if off else "disputed_official_not_met"
            elif off == o1 == o2:
                kind = "concordant_met" if off else "concordant_not_met"
            else:
                kind = "split_other"
            units.append({"prompt_id": pid, "k": k, "arm": arm, "points": float(rb["points"]),
                          "criterion": rb["criterion"], "kind": kind, **{f"v_{g}": int(v[g]) for g in GRADERS}})

    # Severe stratum, at the level the paper counts it: the conversation.
    by_conv = defaultdict(lambda: defaultdict(list))
    for u in units:
        if u["points"] <= -9:
            by_conv[u["prompt_id"]][u["arm"]].append(u)
    severe, flagged = [], Counter()
    for pid, arms in sorted(by_conv.items()):
        if set(arms) != {"asha", "bare"}:
            continue
        unanimous = {a: [u for u in us if all(u[f"v_{g}"] for g in GRADERS)] for a, us in arms.items()}
        any_met = {a: any(u[f"v_{g}"] for u in us for g in GRADERS) for a, us in arms.items()}
        for a, b in (("asha", "bare"), ("bare", "asha")):
            if unanimous[a] and not any_met[b]:
                flagged[a] += 1
                for u in unanimous[a]:
                    twin = next(x for x in arms[b] if x["k"] == u["k"])
                    severe += [{**u, "stratum": "severe", "flagged_arm": a}, {**twin, "stratum": "severe", "flagged_arm": a}]

    chosen = list(severe)
    taken = {(u["prompt_id"], u["k"], u["arm"]) for u in chosen}

    spare = {}  # (arm, kind) -> the rest of each shuffled pool, the source of English replacements

    def take(arm, kind, n, label):
        pool = [u for u in units if u["arm"] == arm and u["kind"] == kind
                and (u["prompt_id"], u["k"], u["arm"]) not in taken]
        rng.shuffle(pool)
        for u in pool[:n]:
            taken.add((u["prompt_id"], u["k"], u["arm"]))
            chosen.append({**u, "stratum": label, "flagged_arm": ""})
        spare[(arm, kind)] = [{**u, "stratum": label, "flagged_arm": ""} for u in pool[n:]]

    for arm in ("asha", "bare"):
        for kind in ("disputed_official_met", "disputed_official_not_met"):
            take(arm, kind, N_DISPUTED // 4, "disputed")
        for kind in ("concordant_met", "concordant_not_met"):
            take(arm, kind, N_CONCORDANT // 4, "concordant")

    rng.shuffle(chosen)

    # Language. Unit numbers follow the first draw, so answers already given keep their place: a sampled unit whose
    # answer is not in English is dropped and an English unit from the same pool is added at the end with a new number.
    def english(u):
        return in_english(str(answers[(u["prompt_id"], u["arm"])].get("completion") or ""))

    numbered = [(i, u) for i, u in enumerate(chosen, 1)]
    kept = [(i, u) for i, u in numbered if u["stratum"] == "severe" or english(u)]
    dropped = [u for i, u in numbered if u["stratum"] != "severe" and not english(u)]
    extra = []
    for u in dropped:
        pool = spare[(u["arm"], u["kind"])]
        while pool:
            cand = pool.pop(0)
            if english(cand):
                extra.append(cand)
                break
    rng.shuffle(extra)
    numbered = kept + [(len(chosen) + j, u) for j, u in enumerate(extra, 1)]
    chosen = [u for _, u in numbered]

    rater_rows, key_rows = [], []
    for i, u in numbered:
        rec = answers[(u["prompt_id"], u["arm"])]
        uid = f"hb2_{i:03d}"
        rater_rows.append({"unit_id": uid, "conversation": conversation_text(rec["prompt"]),
                           "answer": redact(str(rec.get("completion") or "")),
                           "criterion": " ".join(u["criterion"].split()), "rating": "", "confidence": "", "notes": ""})
        key_rows.append({"unit_id": uid, "prompt_id": u["prompt_id"], "criterion_index": u["k"], "arm": u["arm"],
                         "points": u["points"], "stratum": u["stratum"], "kind": u["kind"],
                         "flagged_arm": u["flagged_arm"], "answer_in_english": int(english(u)),
                         **{f"grader_{g}_met": u[f"v_{g}"] for g in GRADERS}})

    page = (HERE / "rater_page_template.html").read_text(encoding="utf-8")
    turns = {r["unit_id"]: [{"role": "user" if m.get("role") == "user" else "assistant", "content": m.get("content", "")}
                            for m in answers[(u["prompt_id"], u["arm"])]["prompt"] or []]
             for r, u in zip(rater_rows, chosen)}
    # Non-English severe cases are shown in English translation, with the original one tap away.
    translated = json.loads((HERE / "translations_en.json").read_text(encoding="utf-8"))
    items = []
    for r, u in zip(rater_rows, chosen):
        item = {**{k: r[k] for k in ("unit_id", "answer", "criterion")}, "turns": turns[r["unit_id"]]}
        tr = translated.get(u["prompt_id"])
        if tr:
            if len(tr["turns"]) != len(item["turns"]):
                raise SystemExit(f"translation of {u['prompt_id']} has the wrong number of turns")
            item["lang"] = tr["language"]
            item["turns_en"] = [{"role": t["role"], "content": c} for t, c in zip(item["turns"], tr["turns"])]
            item["answer_en"] = redact(tr["answers"][u["arm"]])
        items.append(item)
    missing = [k["unit_id"] for k, it in zip(key_rows, items) if not k["answer_in_english"] and "answer_en" not in it]
    if missing:
        raise SystemExit(f"non-English units without a translation: {missing}")
    for k, it in zip(key_rows, items):
        k["shown_in_translation"] = int("answer_en" in it)
    payload = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    (HERE / "rater_hb_harm.html").write_text(page.replace("__ITEMS__", payload), encoding="utf-8")
    for name, data in (("rater_hb_harm.csv", rater_rows), ("rater_hb_harm_KEY.csv", key_rows)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)

    print(f"not in English: {len(dropped)} sampled units replaced; "
          f"{sum(1 for r in key_rows if not r['answer_in_english'])} severe units kept and shown in translation")
    print(f"units: {len(rater_rows)}; by stratum and arm: {dict(Counter((r['stratum'], r['arm']) for r in key_rows))}")
    print(f"severe conversations flagged: Asha only {flagged['asha']}, model alone only {flagged['bare']}")
    print(f"candidate pool on Hard (both arms): {dict(Counter(u['kind'] for u in units))}")
    harm = {a: [sum(u['v_gpt_4_1'] for u in units if u['arm'] == a), sum(1 for u in units if u['arm'] == a)] for a in ("asha", "bare")}
    print("Hard harm rate, official grader: " + ", ".join(f"{a} {100 * m / n:.1f}% ({m}/{n})" for a, (m, n) in harm.items()))


if __name__ == "__main__":
    main()
