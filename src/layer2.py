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
    """Return the WGI table as a DataFrame with MultiIndex columns."""
    ind = get_indicator(data, "governance")
    table = ind["wgi_table"]
    years = table["years"]

    rows = []
    for dim in table["dimensions"]:
        row = {"Dimension": dim["name"]}
        for yr in years:
            row[f"India {yr}"]  = dim["india"][str(yr)]
            row[f"China {yr}"]  = dim["china"][str(yr)]
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


# Score display helpers
SCORE_COLORS = {
    "favorable":           "#2D9E6B",
    "neutral_to_caution":  "#C9A84C",
    "neutral":             "#8FA3B1",
    "neutral_lean_negative": "#C9A84C",
    "at_risk_mild":        "#E05C5C",
}

SCORE_ICONS = {
    "favorable":             "Favorable",
    "neutral_to_caution":    "Neutral-to-Caution",
    "neutral":               "Neutral",
    "neutral_lean_negative": "Neutral / Lean-Negative",
    "at_risk_mild":          "At-Risk (mild-to-conditional)",
}
