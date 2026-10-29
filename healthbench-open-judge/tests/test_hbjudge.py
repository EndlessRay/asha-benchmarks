"""Tests for healthbench-open-judge (no network).

  python3 -m pytest bench-public/healthbench-open-judge/tests -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

from hbjudge.client import parse_grade  # noqa: E402
from hbjudge.grading import aggregate, example_score, paired_delta, summarize  # noqa: E402
from hbjudge.judges import PROFILES  # noqa: E402
from hbjudge.polarity import AFFIRMS, DENIES, OMISSION_LEAD, is_flip  # noqa: E402
from hbjudge.template import GRADER_TEMPLATE, TEMPLATE_SHA256, render, rubric_str  # noqa: E402

# sha256 of simple-evals healthbench_eval.py GRADER_TEMPLATE (stripped), verified 2026-10-28
SIMPLE_EVALS_TEMPLATE_SHA256_PREFIX = "2adffd51fd259554"


def test_template_is_the_pinned_simple_evals_text():
    assert TEMPLATE_SHA256.startswith(SIMPLE_EVALS_TEMPLATE_SHA256_PREFIX)
    assert "<<conversation>>" in GRADER_TEMPLATE and "<<rubric_item>>" in GRADER_TEMPLATE


def test_render_matches_simple_evals_layout():
    text = render([{"role": "user", "content": "q"}], "a", rubric_str("Says X", 5))
    assert "user: q\n\nassistant: a" in text
    assert "[5] Says X" in text
    assert rubric_str("Fails to mention X", -8.0) == "[-8] Fails to mention X"
    assert rubric_str("Partial", 2.5) == "[2.5] Partial"


def test_parse_grade_never_invents_a_verdict():
    assert parse_grade('```json\n{"explanation": "ok", "criteria_met": true}\n```') == (True, "ok")
    assert parse_grade('{"criteria_met": false, "explanation": "no"}') == (False, "no")
    # some pipelines read the word "true" anywhere as a verdict; this harness does not
    assert parse_grade("I think this is true but cannot format JSON") == (None, "")
    assert parse_grade('{"criteria_met": "yes"}') == (None, "")


def test_example_score_unclipped_and_missing():
    rubrics = [{"points": 5}, {"points": -10}]
    assert example_score(rubrics, [False, True]) == pytest.approx(-2.0)  # unclipped per example
    assert example_score(rubrics, [True, None]) is None


def _g(pid, met, tags=("theme:x",)):
    rubrics = [{"criterion": "Says X", "points": 5, "tags": ["axis:a"]}, {"criterion": "Fails to mention Y", "points": -5, "tags": ["axis:b"]}]
    return {"prompt_id": pid, "example_tags": list(tags), "rubrics": rubrics,
            "rubric_grades": [{"criterion": r["criterion"], "points": r["points"], "tags": r["tags"], "criteria_met": m,
                               "explanation": "The response does mention Y." if r["points"] < 0 else "", "attempts": 1}
                              for r, m in zip(rubrics, met)]}


def test_aggregate_clips_mean_and_scores_tags():
    graded = [_g("a", [True, False]), _g("b", [False, True]), _g("c", [True, True])]
    agg = aggregate(graded)
    # example scores 1.0, -1.0, 0.0 -> mean 0.0
    assert agg["score"]["mean"] == pytest.approx(0.0) and agg["score"]["n"] == 3
    assert agg["example_tags"]["theme:x"]["mean"] == pytest.approx(0.0)
    assert agg["rubric_tags"]["axis:a"]["mean"] == pytest.approx(2 / 3)
    assert "axis:b" not in agg["rubric_tags"]  # no positive points under that tag


def test_summary_reports_missing_and_polarity():
    graded = [_g("a", [True, True]), _g("b", [True, None])]
    s = summarize(graded, PROFILES["flashlite-v1"])
    assert s["missing_grades"]["criteria_missing"] == 1 and s["missing_grades"]["examples_excluded"] == 1
    assert s["score"]["n"] == 1
    assert s["polarity_audit"]["omission_penalties_marked_met"] == 1
    assert s["polarity_audit"]["flagged_flips"] == 1


def test_is_flip():
    assert is_flip("Fails to mention Y", True, "The response does mention Y explicitly.")
    assert not is_flip("Fails to mention Y", True, "The response does not mention Y.")
    assert not is_flip("Mentions Y", True, "The response does mention Y.")


def test_polarity_regexes_match_the_study_tool():
    tool = PKG.parents[1] / "Docs" / "preprint" / "nonmaleficence-2026-10" / "_tools" / "grader_polarity.py"
    if not tool.exists():
        pytest.skip("source study tool not available in this checkout")
    src = tool.read_text(encoding="utf-8")
    for rx in (OMISSION_LEAD, AFFIRMS, DENIES):
        assert rx.pattern in src.replace('"\n    r"', "")


def test_paired_delta():
    a = [_g("a", [True, False]), _g("b", [True, False])]
    b = [_g("a", [False, False]), _g("b", [True, False])]
    d = paired_delta(a, b)
    assert d["n"] == 2 and d["delta"] == pytest.approx(50.0)


def test_profiles_are_frozen_and_named():
    for name, p in PROFILES.items():
        assert p.name == name
        with pytest.raises(Exception):
            p.model = "other"  # type: ignore[misc]


def test_panel_averages_verdicts_and_scores_fractionally(tmp_path):
    import json

    from hbjudge.cli import main
    from hbjudge.grading import example_score, panel_merge

    rubrics = [{"criterion": "A", "points": 4}, {"criterion": "B", "points": -2}]

    def run(a, b):
        return [{"prompt_id": "p1", "rubrics": rubrics, "example_tags": [],
                 "rubric_grades": [{"criterion": "A", "points": 4, "criteria_met": a}, {"criterion": "B", "points": -2, "criteria_met": b}]}]

    merged = panel_merge([run(True, True), run(False, True)], ["j1", "j2"])
    assert [x["criteria_met"] for x in merged[0]["rubric_grades"]] == [0.5, 1.0]
    assert example_score(rubrics, [0.5, 1.0]) == (2 - 2) / 4
    assert panel_merge([run(True, None), run(True, True)], ["j1", "j2"])[0]["rubric_grades"][1]["criteria_met"] is None

    for name, (a, b) in {"j1": (True, False), "j2": (True, True)}.items():
        d = tmp_path / name
        d.mkdir()
        (d / "graded.jsonl").write_text(json.dumps(run(a, b)[0]) + "\n", encoding="utf-8")
    assert main(["panel", str(tmp_path / "j1" / "graded.jsonl"), str(tmp_path / "j2" / "graded.jsonl"), "--out", str(tmp_path / "panel")]) == 0
    summary = json.loads((tmp_path / "panel" / "summary.json").read_text())
    assert summary["panel"] == ["j1", "j2"] and abs(summary["score"]["mean"] - 0.75) < 1e-9
