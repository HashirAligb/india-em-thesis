"""
pytest suite for Layer 2 scoring functions.
Mirrors _verify_defaults() in src/layer2.py as a proper test suite.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.layer2 import (
    score_valuation,
    score_demographics,
    score_governance,
    score_digital_adoption,
    score_external_macro,
    compute_ladder_verdict,
)


# ── Default-value lock tests (locked Rung 3 verdict) ─────────────────────────

def test_valuation_default_score():
    assert score_valuation()["score"] == "neutral_to_caution"

def test_valuation_default_no_severe_gate():
    assert score_valuation()["gate_trips_severe"] is False

def test_demographics_default_score():
    assert score_demographics()["score"] == "favorable"

def test_governance_default_score():
    assert score_governance()["score"] == "neutral_lean_negative"

def test_digital_adoption_default_score():
    assert score_digital_adoption()["score"] == "neutral"

def test_external_macro_default_score():
    assert score_external_macro()["score"] == "at_risk_mild"

def test_external_macro_default_no_severe_gate():
    assert score_external_macro()["gate_trips_severe"] is False

def test_ladder_verdict_defaults_rung3():
    scores = {
        "valuation":        score_valuation(),
        "demographics":     score_demographics(),
        "governance":       score_governance(),
        "digital_adoption": score_digital_adoption(),
        "external_macro":   score_external_macro(),
    }
    assert compute_ladder_verdict(scores)["rung"] == 3


# ── Gating indicator threshold tests ─────────────────────────────────────────

def test_valuation_severe_gate_trips_at_40pct():
    result = score_valuation(premium=0.40)
    assert result["score"] == "severe"
    assert result["gate_trips_severe"] is True

def test_valuation_severe_gate_not_tripped_just_below_40pct():
    assert score_valuation(premium=0.399)["gate_trips_severe"] is False

def test_valuation_severe_gate_trips_above_40pct():
    assert score_valuation(premium=0.50)["gate_trips_severe"] is True

def test_valuation_at_atrisk_boundary():
    assert score_valuation(premium=0.30)["score"] == "at_risk_mild"

def test_external_macro_severe_gate_on_inr():
    result = score_external_macro(inr_dep_pct=8.0, oil_share_pct=10.0)
    assert result["score"] == "severe"
    assert result["gate_trips_severe"] is True

def test_external_macro_severe_gate_on_oil():
    result = score_external_macro(inr_dep_pct=1.0, oil_share_pct=45.0)
    assert result["score"] == "severe"
    assert result["gate_trips_severe"] is True

def test_external_macro_neutral_below_both_thresholds():
    result = score_external_macro(inr_dep_pct=1.9, oil_share_pct=14.9)
    assert result["score"] == "neutral"
    assert result["gate_trips_severe"] is False


# ── Structural blocker tests ──────────────────────────────────────────────────

def test_governance_favorable_with_one_below_zero():
    scores = {
        "dim_a": -0.1, "dim_b": 0.5, "dim_c": 0.3,
        "dim_d": 0.2,  "dim_e": 0.1, "dim_f": 0.8,
    }
    assert score_governance(india_scores_2023=scores)["score"] == "favorable"

def test_governance_lean_negative_with_five_below_zero():
    scores = {
        "dim_a": -0.14, "dim_b": -0.84, "dim_c": 0.42,
        "dim_d": -0.13, "dim_e": -0.09, "dim_f": -0.34,
    }
    assert score_governance(india_scores_2023=scores)["score"] == "neutral_lean_negative"

def test_digital_adoption_favorable_at_peer():
    assert score_digital_adoption(india_pct=71.0, peer_median_pct=71.0)["score"] == "favorable"

def test_digital_adoption_not_favorable_below_peer():
    assert score_digital_adoption(india_pct=48.0, peer_median_pct=71.0)["score"] != "favorable"

def test_digital_adoption_at_risk_large_gap_downtrend():
    result = score_digital_adoption(india_pct=40.0, peer_median_pct=71.0, trend_direction="down")
    assert result["score"] == "at_risk_mild"


# ── Ladder verdict routing tests ──────────────────────────────────────────────

def test_ladder_severe_gate_gives_rung4():
    scores = {
        "valuation":        score_valuation(premium=0.50),
        "demographics":     score_demographics(),
        "governance":       score_governance(),
        "digital_adoption": score_digital_adoption(),
        "external_macro":   score_external_macro(),
    }
    assert compute_ladder_verdict(scores)["rung"] == 4

def test_ladder_all_structural_favorable_gives_rung1():
    gov_all_pos = {f"d{i}": 0.5 for i in range(6)}
    scores = {
        "valuation":        score_valuation(premium=0.05),
        "demographics":     score_demographics(),
        "governance":       score_governance(india_scores_2023=gov_all_pos),
        "digital_adoption": score_digital_adoption(india_pct=75.0, peer_median_pct=71.0),
        "external_macro":   score_external_macro(inr_dep_pct=1.0, oil_share_pct=10.0),
    }
    assert compute_ladder_verdict(scores)["rung"] == 1

def test_ladder_governance_blocker_gives_rung3():
    gov_5neg = {f"d{i}": -0.5 for i in range(5)}
    gov_5neg["d5"] = 0.5
    scores = {
        "valuation":        score_valuation(premium=0.05),
        "demographics":     score_demographics(),
        "governance":       score_governance(india_scores_2023=gov_5neg),
        "digital_adoption": score_digital_adoption(india_pct=75.0, peer_median_pct=71.0),
        "external_macro":   score_external_macro(inr_dep_pct=1.0, oil_share_pct=10.0),
    }
    assert compute_ladder_verdict(scores)["rung"] == 3
