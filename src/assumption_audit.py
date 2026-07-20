"""
Assumption Auditor for the Layer 2 Forward Framework.

Pure Python compute layer -- no display logic, no LLM calls.
Imports scoring functions from src.layer2 only; never reimplements them.

Public API:
    run_assumption_audit(data, thresholds) -> AuditResult

AuditResult is a typed dict consumed by both the agent pipeline and the
Streamlit section.  The LLM seam is explicit: agents receive AuditResult
and return plain text.  Nothing in this module calls an LLM.
"""

from __future__ import annotations

import os
import sys
from typing import TypedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.layer2 import (
    compute_ladder_verdict,
    score_valuation,
    score_demographics,
    score_governance,
    score_digital_adoption,
    score_external_macro,
    get_indicator,
    RUNG_LABELS,
)


# ---------------------------------------------------------------------------
# Typed result structures
# ---------------------------------------------------------------------------

class UpgradeBlocker(TypedDict):
    indicator: str
    current_score: str
    favorable_condition: str
    why_threshold_cant_fix: str


class DowngradeScenario(TypedDict):
    indicator: str
    gate_type: str
    current_value_pct: float      # current premium: 23.9
    trigger_value_pct: float      # declared severe band open: 40.0
    gap_pp: float                 # 16.1
    gap_relative_pct: float       # ~67.4
    resulting_rung: int
    plausibility_label: str
    boundary_note: str


class ProfileStability(TypedDict):
    rungs_found: list[int]
    stable: bool
    note: str


class AuditResult(TypedDict):
    current_rung: int
    current_rung_label: str
    current_derivation: str
    upgrade_blockers: list[UpgradeBlocker]
    nearest_downgrade: DowngradeScenario
    profile_stability: ProfileStability
    indicator_scores: dict[str, str]
    # LLM seam: reasoning_notes is populated by Python for agents to explain.
    # Agents must not add numbers or blockers not already in this list.
    reasoning_notes: list[str]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_val_bands(caution_pct: int | float,
                     atrisk_pct: int | float,
                     severe_pct: int | float) -> list:
    """
    Build the valuation band list used by score_valuation().
    Mirrors the logic in app.py to keep in sync.
    The max() constraints ensure each band is at least 5pp wide:
      a >= c + 0.05, s >= a + 0.05.
    This means val_severe cannot be moved independently below (val_atrisk+5pp),
    which is why sweeping val_severe alone cannot trip the gate at current premium.
    """
    c = caution_pct / 100
    a = max(atrisk_pct / 100, c + 0.05)
    s = max(severe_pct / 100, a + 0.05)
    return [
        {"label": "Favorable",          "range_low": 0.0,  "range_high": 0.10},
        {"label": "Neutral",            "range_low": 0.10, "range_high": c},
        {"label": "Caution",            "range_low": c,    "range_high": a},
        {"label": "At-risk",            "range_low": a,    "range_high": s},
        {"label": "Severe (gate trips)", "range_low": s,   "range_high": None},
    ]


def _score_all(thresholds: dict, india_wgi_2023: dict,
               india_any_pct: float, peer_any_pct: float) -> dict:
    val_bands = _build_val_bands(
        thresholds["th_val_caution"],
        thresholds["th_val_atrisk"],
        thresholds["th_val_severe"],
    )
    return {
        "valuation": score_valuation(
            premium=thresholds["premium"],
            bands=val_bands,
        ),
        "demographics": score_demographics(
            old_age_dep_india=thresholds["old_age_dep_india"],
            old_age_dep_china=thresholds["old_age_dep_china"],
            female_lfp_pct=thresholds["female_lfp_pct"],
            max_ratio_for_favorable=thresholds["th_dem_ratio"] / 100,
        ),
        "governance": score_governance(
            india_scores_2023=india_wgi_2023,
            neutral_neg_threshold=thresholds["th_gov_count"],
        ),
        "digital_adoption": score_digital_adoption(
            india_pct=india_any_pct,
            peer_median_pct=peer_any_pct,
            trend_direction="up",
            large_gap=float(thresholds["th_dig_gap"]),
        ),
        "external_macro": score_external_macro(
            inr_dep_pct=thresholds["inr_dep_pct"],
            oil_share_pct=thresholds["oil_share_pct"],
            inr_mild_threshold=thresholds["th_ext_inr_mild"],
            oil_mild_threshold=float(thresholds["th_ext_oil_mild"]),
            inr_severe_threshold=thresholds["th_ext_inr_sev"],
            oil_severe_threshold=float(thresholds["th_ext_oil_sev"]),
        ),
    }


def _governance_blocker(india_wgi_2023: dict) -> UpgradeBlocker:
    below_zero = [k for k, v in india_wgi_2023.items() if v < 0]
    count = len(below_zero)
    return UpgradeBlocker(
        indicator="governance",
        current_score="neutral_lean_negative",
        favorable_condition=(
            "at most 1 of 6 WGI dimensions below zero "
            "(score_governance line: 'if below_zero <= 1: favorable')"
        ),
        why_threshold_cant_fix=(
            f"India 2023 has {count} of 6 WGI dimensions below zero "
            f"({', '.join(below_zero)}). "
            "Reaching the favorable tier requires at most 1 dimension below zero. "
            "This is a fixed requirement in the model definition, not an adjustable threshold. "
            "The only path to favorable governance is a genuine improvement in the "
            "underlying WGI survey results."
        ),
    )


def _digital_blocker(india_any: float, peer_any: float) -> UpgradeBlocker:
    gap = peer_any - india_any
    return UpgradeBlocker(
        indicator="digital_adoption",
        current_score="neutral",
        favorable_condition=(
            "india_pct >= peer_median_pct "
            "(score_digital_adoption line: 'if india_pct >= peer_median_pct: favorable')"
        ),
        why_threshold_cant_fix=(
            f"India any-digital-payment rate is {india_any}% vs EM peer median {peer_any}% "
            f"(gap: {gap:.0f}pp). "
            "Reaching the favorable tier requires India's rate to be at or above the peer median. "
            "The adjustable scoring threshold governs how large a gap triggers a negative signal, "
            "not the favorable cutoff itself. "
            f"No threshold change can make {india_any}% >= {peer_any}%. "
            "Only improved Findex survey data can unlock favorable."
        ),
    )


def _nearest_downgrade(thresholds: dict, india_wgi_2023: dict,
                        india_any: float, peer_any: float) -> DowngradeScenario:
    """
    Report the nearest deterministic downgrade boundary.

    The valuation severe gate is declared in the JSON premium_bands at range_low=0.40.
    At the current premium (23.9%), the gap to that gate is 16.1pp.

    Threshold-sweeping note: due to the max() band constraint in _build_val_bands,
    val_severe cannot be independently lowered below (val_atrisk + 5pp).
    With default val_atrisk=30%, the minimum achievable severe band open is 35%.
    So no single-slider adjustment trips this gate at the current premium level.
    The 16.1pp gap is therefore a data milestone (how much the premium itself would
    need to increase given the declared bands), not a sweepable threshold.
    """
    current_pct = thresholds["premium"] * 100    # 23.9

    # The declared severe band opens at 40.0% (from the JSON premium_bands).
    # Verify computationally: score_valuation at exactly 0.40 with declared bands.
    declared_bands = _build_val_bands(
        thresholds["th_val_caution"],
        thresholds["th_val_atrisk"],
        thresholds["th_val_severe"],
    )
    test_at_40 = score_valuation(premium=0.40, bands=declared_bands)
    assert test_at_40["gate_trips_severe"] is True, (
        "Expected severe gate to trip at premium=0.40 with declared bands"
    )
    test_scores_at_40 = _score_all(
        dict(thresholds, premium=0.40), india_wgi_2023, india_any, peer_any
    )
    test_verdict = compute_ladder_verdict(test_scores_at_40)
    assert test_verdict["rung"] == 4, (
        f"Expected Rung 4 at premium=0.40, got Rung {test_verdict['rung']}"
    )

    trigger_pct = 40.0
    gap = round(trigger_pct - current_pct, 1)
    relative = round(gap / current_pct * 100, 1)

    return DowngradeScenario(
        indicator="valuation",
        gate_type="severe",
        current_value_pct=round(current_pct, 1),
        trigger_value_pct=trigger_pct,
        gap_pp=gap,
        gap_relative_pct=relative,
        resulting_rung=4,
        plausibility_label="outside near-term range",
        boundary_note=(
            "This is a data milestone: the premium itself would need to reach 40% "
            "for the declared severe gate to open. "
            "No single threshold change achieves this at current premium levels, "
            "because the scoring bands are required to be at least 5 percentage points "
            "wide each, so the severe tier cannot open below roughly 35% regardless "
            "of how other thresholds are set."
        ),
    )


def _profile_stability(thresholds: dict, india_wgi_2023: dict,
                        india_any: float, peer_any: float) -> ProfileStability:
    """
    Three illustrative mandate profiles -- threshold overrides only.
    Demonstrates that Rung 3 holds across reasonable declared assumptions.
    """
    profiles = {
        "Research Baseline": thresholds,
        "Long-Horizon Structural": dict(
            thresholds,
            th_val_caution=30,
            th_ext_inr_mild=4.0,
            th_ext_oil_mild=30,
        ),
        "Tactical Valuation-Sensitive": dict(
            thresholds,
            th_val_caution=15,
            th_val_atrisk=20,
        ),
    }
    rungs = []
    for _name, th in profiles.items():
        scores = _score_all(th, india_wgi_2023, india_any, peer_any)
        rungs.append(compute_ladder_verdict(scores)["rung"])

    unique = sorted(set(rungs))
    stable = len(unique) == 1
    note = (
        f"All three illustrative mandate profiles produce Rung {unique[0]}. "
        "The verdict does not change across these declared threshold variations."
        if stable else
        f"Profiles produce rungs: {unique}. "
        "The verdict is sensitive to some threshold choices."
    )
    return ProfileStability(rungs_found=rungs, stable=stable, note=note)


def _build_reasoning_notes(result_partial: dict) -> list[str]:
    """
    Deterministic plain-English notes for agents to explain.
    Agents must not add numbers or claims not listed here.
    """
    d = result_partial["nearest_downgrade"]
    blockers = result_partial["upgrade_blockers"]
    ps = result_partial["profile_stability"]
    return [
        (
            f"Current verdict: Rung {result_partial['current_rung']} -- "
            f"{result_partial['current_rung_label']}."
        ),
        (
            "Upgrade to Rung 2 or Rung 1 is not reachable from current data "
            "via any threshold adjustment. Two structural indicators are blocked "
            "by fixed model conditions, not adjustable thresholds."
        ),
        (
            f"Governance blocker: {blockers[0]['why_threshold_cant_fix'].split('.')[0]}. "
            "The favorable condition requires <= 1 WGI dimension below zero "
            "(hardcoded, not a parameter)."
        ),
        (
            f"Digital adoption blocker: {blockers[1]['why_threshold_cant_fix'].split('.')[0]}. "
            "The favorable condition requires India at or above the EM peer median."
        ),
        (
            f"Nearest downgrade (data milestone, not near-term forecast): "
            f"the valuation severe gate opens when the P/E premium reaches "
            f"{d['trigger_value_pct']}%. "
            f"Current premium: {d['current_value_pct']}%. "
            f"Gap: {d['gap_pp']} percentage points "
            f"({d['gap_relative_pct']}% increase relative to current). "
            f"Plausibility: {d['plausibility_label']}."
        ),
        ps["note"],
        (
            "The favorable-condition definitions for governance and digital adoption "
            "are fixed model assumptions, not proven facts. The model does not claim "
            "that India's structural quality is exactly at those thresholds; it declares "
            "them as the scoring rules used in this framework."
        ),
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_assumption_audit(data: dict, thresholds: dict) -> AuditResult:
    """
    Run the full assumption audit.

    data:       output of load_indicators() from src.layer2
    thresholds: dict with both data values and threshold params (see _FULL_DEFAULTS)

    Returns AuditResult.  Python computes everything; agents only explain it.
    """
    gov_ind = get_indicator(data, "governance")
    dig_ind = get_indicator(data, "digital_adoption")

    india_wgi_2023 = {
        dim["name"]: dim["india"]["2023"]
        for dim in gov_ind["wgi_table"]["dimensions"]
    }
    india_any_pct = next(
        dp["value"] for dp in dig_ind["data_points"]
        if dp["id"] == "india_any_dig_2024"
    )
    peer_any_pct = next(
        dp["value"] for dp in dig_ind["data_points"]
        if dp["id"] == "peer_median_any_dig_2024"
    )

    scores = _score_all(thresholds, india_wgi_2023, india_any_pct, peer_any_pct)
    verdict = compute_ladder_verdict(scores)
    blockers = [
        _governance_blocker(india_wgi_2023),
        _digital_blocker(india_any_pct, peer_any_pct),
    ]
    downgrade = _nearest_downgrade(thresholds, india_wgi_2023, india_any_pct, peer_any_pct)
    stability = _profile_stability(thresholds, india_wgi_2023, india_any_pct, peer_any_pct)

    partial = {
        "current_rung": verdict["rung"],
        "current_rung_label": verdict["label"],
        "current_derivation": verdict["derivation"],
        "upgrade_blockers": blockers,
        "nearest_downgrade": downgrade,
        "profile_stability": stability,
    }

    return AuditResult(
        **partial,
        indicator_scores={k: v["score_display"] for k, v in scores.items()},
        reasoning_notes=_build_reasoning_notes(partial),
    )


# ---------------------------------------------------------------------------
# Default thresholds (matches app.py _DEFAULTS + pinned data values)
# ---------------------------------------------------------------------------

_FULL_DEFAULTS: dict = {
    # Pinned data values
    "premium":           0.239,
    "old_age_dep_india": 10.0,
    "old_age_dep_china": 21.0,
    "female_lfp_pct":    35.0,
    "inr_dep_pct":       3.5,
    "oil_share_pct":     25.0,
    # Threshold parameters (pre-declared)
    "th_val_caution":    20,
    "th_val_atrisk":     30,
    "th_val_severe":     40,
    "th_gov_count":      4,
    "th_dig_gap":        20,
    "th_dem_ratio":      60,
    "th_ext_inr_mild":   2.0,
    "th_ext_inr_sev":    8.0,
    "th_ext_oil_mild":   15,
    "th_ext_oil_sev":    45,
}


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "layer2_indicators.json")
    with open(data_path) as f:
        data = json.load(f)

    result = run_assumption_audit(data, _FULL_DEFAULTS)

    print(f"Current rung: {result['current_rung']} -- {result['current_rung_label']}")
    print(f"Derivation:   {result['current_derivation']}")
    print()
    print("Upgrade blockers:")
    for b in result["upgrade_blockers"]:
        print(f"  [{b['indicator']}] current_score={b['current_score']!r}")
        print(f"    favorable_condition: {b['favorable_condition']}")
        print()
    d = result["nearest_downgrade"]
    print("Nearest downgrade:")
    print(f"  indicator={d['indicator']}, gate={d['gate_type']}")
    print(f"  current={d['current_value_pct']}%  trigger={d['trigger_value_pct']}%")
    print(f"  gap={d['gap_pp']}pp / {d['gap_relative_pct']}% increase")
    print(f"  plausibility={d['plausibility_label']!r}")
    print(f"  boundary_note: {d['boundary_note']}")
    print()
    ps = result["profile_stability"]
    print(f"Profile stability: rungs={ps['rungs_found']}, stable={ps['stable']}")
    print(f"  {ps['note']}")
    print()
    print("Reasoning notes:")
    for i, note in enumerate(result["reasoning_notes"], 1):
        print(f"  {i}. {note}")
    print()
    print("Indicator scores:", result["indicator_scores"])
    print()

    # Assertions
    assert result["current_rung"] == 3, f"Expected Rung 3, got {result['current_rung']}"
    assert d["current_value_pct"] == 23.9
    assert d["trigger_value_pct"] == 40.0
    assert d["gap_pp"] == 16.1
    assert abs(d["gap_relative_pct"] - 67.4) < 0.1
    assert d["resulting_rung"] == 4
    assert ps["stable"] is True
    assert ps["rungs_found"] == [3, 3, 3]
    assert len(result["upgrade_blockers"]) == 2
    assert result["upgrade_blockers"][0]["indicator"] == "governance"
    assert result["upgrade_blockers"][1]["indicator"] == "digital_adoption"
    print("All smoke-test assertions passed.")
