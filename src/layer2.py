"""
Layer 2 compute module.

Reads data/layer2_indicators.json and exposes clean Python objects
for the Streamlit app. Holds no display logic.
"""

import json
import os
import pandas as pd

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_INDICATORS_PATH = os.path.join(_DATA_DIR, "layer2_indicators.json")


# ── Data loaders ──────────────────────────────────────────────────────────────

def load_indicators() -> dict:
    with open(_INDICATORS_PATH, "r") as f:
        return json.load(f)


def get_metadata(data: dict) -> dict:
    return data["metadata"]


def get_indicator(data: dict, key: str) -> dict:
    return data["indicators"][key]


def get_ladder_verdict(data: dict) -> dict:
    return data["ladder_verdict"]


def governance_as_dataframe(data: dict) -> pd.DataFrame:
    """Return the WGI table as a DataFrame indexed by dimension."""
    ind = get_indicator(data, "governance")
    table = ind["wgi_table"]
    years = table["years"]

    rows = []
    for dim in table["dimensions"]:
        row = {"Dimension": dim["name"]}
        for yr in years:
            row[f"India {yr}"] = dim["india"][str(yr)]
            row[f"China {yr}"] = dim["china"][str(yr)]
        rows.append(row)

    return pd.DataFrame(rows).set_index("Dimension")


def digital_peer_table(data: dict) -> pd.DataFrame:
    """Return the Findex 2024 cross-country table as a DataFrame."""
    ind = get_indicator(data, "digital_adoption")
    rows = ind["peer_table_2024"]
    df = pd.DataFrame(rows)
    df.columns = ["Country", "Any digital payment (%)", "Digital merchant payment (%)"]
    return df.set_index("Country")


def scoring_summary(data: dict) -> pd.DataFrame:
    rows = get_ladder_verdict(data)["scoring_summary"]
    return pd.DataFrame(rows)


# ── Display helpers ───────────────────────────────────────────────────────────

SCORE_COLORS = {
    "favorable":             "#2D9E6B",
    "neutral_to_caution":    "#C9A84C",
    "neutral":               "#8FA3B1",
    "neutral_lean_negative": "#C9A84C",
    "at_risk_mild":          "#E05C5C",
    "severe":                "#8B0000",
}

SCORE_ICONS = {
    "favorable":             "Favorable",
    "neutral_to_caution":    "Neutral-to-Caution",
    "neutral":               "Neutral",
    "neutral_lean_negative": "Neutral / Lean-Negative",
    "at_risk_mild":          "At-Risk (mild-to-conditional)",
    "severe":                "Severe (gate trips)",
}

RUNG_LABELS = {
    1: "Durable and reasonably priced",
    2: "Durable but priced",
    3: "Structurally attractive, but priced and macro-sensitive",
    4: "Not durable",
}


# ── Scoring functions ─────────────────────────────────────────────────────────

# Maps valuation band label (from the JSON) -> (score_key, gate_trips_severe)
_VALUATION_BAND_TO_SCORE: dict[str, tuple[str, bool]] = {
    "Favorable":           ("favorable",         False),
    "Neutral":             ("neutral",            False),
    "Caution":             ("neutral_to_caution", False),
    "At-risk":             ("at_risk_mild",       False),
    "Severe (gate trips)": ("severe",             True),
}


def score_valuation(premium: float = 0.239, bands: list | None = None) -> dict:
    """
    Score India's P/E premium to EM ex-India against the pre-declared bands.

    premium: fractional premium, e.g. 0.239 = 23.9%. Default is the mid-point of
             the locked range (w=13%).
    bands:   list of {label, range_low, range_high} dicts. Loaded from JSON if None.

    Returns {"score": str, "score_display": str, "gate_trips_severe": bool}.
    """
    if bands is None:
        bands = get_indicator(load_indicators(), "valuation")["premium_bands"]

    for band in sorted(bands, key=lambda b: b["range_low"]):
        lo = band["range_low"]
        hi = band["range_high"]
        in_band = (premium >= lo) if hi is None else (lo <= premium < hi)
        if in_band:
            key, severe = _VALUATION_BAND_TO_SCORE[band["label"]]
            return {"score": key, "score_display": SCORE_ICONS[key], "gate_trips_severe": severe}

    return {"score": "neutral", "score_display": SCORE_ICONS["neutral"], "gate_trips_severe": False}


def score_demographics(
    old_age_dep_india: float = 10.0,
    old_age_dep_china: float = 21.0,
    female_lfp_pct: float = 35.0,
    max_ratio_for_favorable: float = 0.60,
) -> dict:
    """
    Score India's demographic position relative to China.

    Favorable if India's old-age dependency ratio < max_ratio_for_favorable * China's.
    Default threshold 0.60: India (10) vs China (21) gives ratio 0.48, comfortably favorable.

    Female LFP is returned as a conversion_caveat flag (True when < 45%), not a
    score modifier.

    Returns {"score": str, "score_display": str, "conversion_caveat": bool}.
    """
    ratio = old_age_dep_india / old_age_dep_china if old_age_dep_china > 0 else 1.0
    key = "favorable" if ratio < max_ratio_for_favorable else "neutral"
    return {
        "score": key,
        "score_display": SCORE_ICONS[key],
        "conversion_caveat": female_lfp_pct < 45.0,
    }


def score_governance(
    india_scores_2023: dict | None = None,
    neutral_neg_threshold: int = 4,
) -> dict:
    """
    Score India's WGI governance profile (six dimensions, 2023).

    Counts how many of the six WGI dimensions have India below zero (below the
    global mean). Pre-declared thresholds:
      0-1 below zero               -> favorable
      2 to (threshold - 1)         -> neutral
      threshold (4) to 6           -> neutral_lean_negative

    india_scores_2023: {dimension_name: float} for India 2023. Loaded from JSON if None.
    neutral_neg_threshold: minimum count of below-zero dimensions to score
                           neutral_lean_negative (default 4).

    Returns {"score": str, "score_display": str, "below_zero_count": int}.
    """
    if india_scores_2023 is None:
        data = load_indicators()
        gov_ind = get_indicator(data, "governance")
        india_scores_2023 = {
            dim["name"]: dim["india"]["2023"]
            for dim in gov_ind["wgi_table"]["dimensions"]
        }

    below_zero = sum(1 for v in india_scores_2023.values() if v < 0)

    if below_zero <= 1:
        key = "favorable"
    elif below_zero < neutral_neg_threshold:
        key = "neutral"
    else:
        key = "neutral_lean_negative"

    return {
        "score": key,
        "score_display": SCORE_ICONS[key],
        "below_zero_count": below_zero,
    }


def score_digital_adoption(
    india_pct: float = 48.0,
    peer_median_pct: float = 71.0,
    trend_direction: str = "up",
    large_gap: float = 20.0,
) -> dict:
    """
    Score India's digital financial adoption vs the EM peer median.

    india_pct >= peer_median_pct              -> favorable (India leads)
    india_pct < peer_median_pct - large_gap:
      trend "up"                              -> neutral (convergence from behind)
      trend "flat" or "down"                  -> at_risk_mild
    india within large_gap of peers           -> neutral (approaching peers)

    Returns {"score": str, "score_display": str, "gap_pp": float}.
    """
    gap = peer_median_pct - india_pct

    if india_pct >= peer_median_pct:
        key = "favorable"
        display = SCORE_ICONS["favorable"]
    elif gap > large_gap:
        if trend_direction == "up":
            key = "neutral"
            display = "Neutral (negative level, positive trend)"
        else:
            key = "at_risk_mild"
            display = SCORE_ICONS["at_risk_mild"]
    else:
        key = "neutral"
        display = SCORE_ICONS["neutral"]

    return {"score": key, "score_display": display, "gap_pp": gap}


def score_external_macro(
    inr_dep_pct: float = 3.5,
    oil_share_pct: float = 25.0,
    inr_mild_threshold: float = 2.0,
    oil_mild_threshold: float = 15.0,
    inr_severe_threshold: float = 8.0,
    oil_severe_threshold: float = 45.0,
) -> dict:
    """
    Score India's combined external macro vulnerability (INR drag + oil exposure).

    Currency drag and oil exposure are one indicator because oil shocks drive
    rupee pressure; separating them would double-count the same underlying risk.

    Severe gate trips if:  inr_dep >= inr_severe_threshold OR oil >= oil_severe_threshold
    At-risk (mild) if:     either mild threshold is crossed without hitting severe
    Neutral otherwise.

    Defaults reflect the locked mid-2026 values: INR ~3.5%/yr (midpoint of 3-4%),
    oil share ~25% of imports.

    Returns {"score": str, "score_display": str, "gate_trips_severe": bool}.
    """
    if (inr_dep_pct >= inr_severe_threshold) or (oil_share_pct >= oil_severe_threshold):
        return {
            "score": "severe",
            "score_display": SCORE_ICONS["severe"],
            "gate_trips_severe": True,
        }

    at_risk = (inr_dep_pct >= inr_mild_threshold) or (oil_share_pct >= oil_mild_threshold)
    key = "at_risk_mild" if at_risk else "neutral"
    return {
        "score": key,
        "score_display": SCORE_ICONS[key],
        "gate_trips_severe": False,
    }


# ── Confidence ladder ─────────────────────────────────────────────────────────

_STRUCTURAL_KEYS = ("demographics", "governance", "digital_adoption")
_GATING_KEYS     = ("valuation", "external_macro")

_DISPLAY_NAMES = {
    "valuation":        "Valuation",
    "demographics":     "Demographics",
    "governance":       "Governance",
    "digital_adoption": "Digital Adoption",
    "external_macro":   "External Macro",
}


def compute_ladder_verdict(scores: dict) -> dict:
    """
    Apply the pre-declared confidence ladder rule to five scored indicators.

    Pre-declared rule (set before scoring began):
      1. Any gating indicator gate_trips_severe=True  -> Rung 4 (hard cap).
      2. No severe gate, structural support incomplete
         (at least one structural indicator != "favorable") -> Rung 3.
      3. No severe gate, all structural favorable:
         - valuation in {"favorable", "neutral"} -> Rung 1.
         - valuation is "neutral_to_caution" or worse -> Rung 2.

    scores: dict keyed by indicator name; each value is the dict returned by the
            corresponding score_* function. Gating entries must include
            "gate_trips_severe".

    Returns {"rung": int, "label": str, "derivation": str}.
    """
    # Step 1: severe gate check
    any_severe = any(
        scores.get(k, {}).get("gate_trips_severe", False)
        for k in _GATING_KEYS
    )
    if any_severe:
        tripped = [k for k in _GATING_KEYS if scores.get(k, {}).get("gate_trips_severe")]
        return {
            "rung": 4,
            "label": RUNG_LABELS[4],
            "derivation": (
                f"Gate(s) tripped severe: {', '.join(_DISPLAY_NAMES[k] for k in tripped)}. "
                "Verdict forced to Rung 4 regardless of structural strength."
            ),
        }

    # Step 2: structural completeness
    non_favorable = [
        k for k in _STRUCTURAL_KEYS
        if scores.get(k, {}).get("score") != "favorable"
    ]
    if non_favorable:
        return {
            "rung": 3,
            "label": RUNG_LABELS[3],
            "derivation": (
                "No gate tripped severe. Structural support is incomplete: "
                f"{', '.join(_DISPLAY_NAMES[k] for k in non_favorable)} not favorable. "
                "Per the pre-declared rule, incomplete structural support "
                "with no severe gate -> Rung 3."
            ),
        }

    # Step 3: all structural favorable -- Rung 1 vs 2 by valuation
    val_score = scores.get("valuation", {}).get("score", "neutral")
    if val_score in ("favorable", "neutral"):
        return {
            "rung": 1,
            "label": RUNG_LABELS[1],
            "derivation": (
                "No gate tripped severe. All structural indicators favorable. "
                "Valuation is not a headwind -> Rung 1."
            ),
        }
    return {
        "rung": 2,
        "label": RUNG_LABELS[2],
        "derivation": (
            "No gate tripped severe. All structural indicators favorable. "
            "Valuation embeds a premium -> Rung 2 rather than Rung 1."
        ),
    }


# ── Default verification ──────────────────────────────────────────────────────

def _verify_defaults() -> None:
    """
    Call every score_* function with no arguments (defaults) and assert the
    results match the locked mid-2026 verdict exactly.

    Expected: valuation=neutral_to_caution, demographics=favorable,
              governance=neutral_lean_negative, digital_adoption=neutral,
              external_macro=at_risk_mild, rung=3.

    Raises AssertionError on any divergence.
    """
    print("Verifying that defaults reproduce the locked Rung 3 verdict...\n")

    val = score_valuation()
    assert val["score"] == "neutral_to_caution", \
        f"valuation: expected neutral_to_caution, got {val['score']}"
    assert val["gate_trips_severe"] is False
    print(f"  valuation        : {val['score_display']:<40}  gate_severe={val['gate_trips_severe']}")

    dem = score_demographics()
    assert dem["score"] == "favorable", \
        f"demographics: expected favorable, got {dem['score']}"
    print(f"  demographics     : {dem['score_display']:<40}  caveat={dem['conversion_caveat']}")

    gov = score_governance()
    assert gov["score"] == "neutral_lean_negative", \
        f"governance: expected neutral_lean_negative, got {gov['score']}"
    print(f"  governance       : {gov['score_display']:<40}  below_zero={gov['below_zero_count']}/6")

    dig = score_digital_adoption()
    assert dig["score"] == "neutral", \
        f"digital_adoption: expected neutral, got {dig['score']}"
    print(f"  digital_adoption : {dig['score_display']:<40}  gap={dig['gap_pp']:.0f}pp")

    ext = score_external_macro()
    assert ext["score"] == "at_risk_mild", \
        f"external_macro: expected at_risk_mild, got {ext['score']}"
    assert ext["gate_trips_severe"] is False
    print(f"  external_macro   : {ext['score_display']:<40}  gate_severe={ext['gate_trips_severe']}")

    verdict = compute_ladder_verdict({
        "valuation":        val,
        "demographics":     dem,
        "governance":       gov,
        "digital_adoption": dig,
        "external_macro":   ext,
    })
    assert verdict["rung"] == 3, f"rung: expected 3, got {verdict['rung']}"

    print(f"\n  Verdict: Rung {verdict['rung']} -- {verdict['label']}")
    print(f"  {verdict['derivation']}")
    print("\nAll assertions passed. Locked Rung 3 verdict reproduced.")


if __name__ == "__main__":
    _verify_defaults()
