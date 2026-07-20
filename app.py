"""
Silver-tier Streamlit app.
Part 1: Layer 1 historical analysis.
Part 2: Layer 2 forward-durability framework (interactive threshold explorer).

Run: streamlit run app.py
"""

import datetime
import io
import os
import sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India EM Thesis",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Visual theme (CSS injection) ─────────────────────────────────────────────
# Wrapped in display:none so the <style> block applies globally but the
# surrounding Streamlit container does not render as a visible element.
st.markdown("""<div style="display:none"><style>
/* --- Sidebar: warm dark mahogany --- */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
    background-color: #2A0E0E !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
    color: #E8D8C0 !important;
}
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] div[data-testid="stCaption"] p {
    color: #A08878 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #4A1A1A !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #3A1010 !important;
    border: 1px solid #5C1A1B !important;
    color: #E8D8C0 !important;
    border-radius: 20px !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #5C1A1B !important;
    color: #FBF7EF !important;
    border-color: #7A2A2B !important;
}
/* Sidebar headings: override the global burgundy h1/h2/h3 so they read on dark bg */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #E8D8C0 !important;
    font-family: Georgia, Cambria, serif !important;
    border-bottom: none !important;
    padding-bottom: 0 !important;
}
/* Radio option text in sidebar */
section[data-testid="stSidebar"] [data-testid="stRadio"] p,
section[data-testid="stSidebar"] [data-testid="stRadio"] span {
    color: #E8D8C0 !important;
}

/* --- Page headers: serif burgundy --- */
h2 {
    color: #5C1A1B !important;
    font-family: Georgia, Cambria, serif !important;
    font-weight: 800 !important;
    border-bottom: 2px solid #5C1A1B;
    padding-bottom: 0.3em;
    margin-bottom: 0.5em;
}
h3 {
    color: #3A1010 !important;
    font-family: Georgia, Cambria, serif !important;
    font-weight: 600 !important;
}

/* --- Metric cards: warm cream --- */
[data-testid="stMetric"] {
    background: #FBF7EF !important;
    border: 1px solid #D8C8A8 !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    box-shadow: 0 1px 4px rgba(92,26,27,0.07) !important;
}
[data-testid="stMetricLabel"] div {
    font-size: 0.75rem !important;
    color: #8A7B6B !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] div {
    color: #2C1A0E !important;
    font-weight: 700 !important;
    font-variant-numeric: tabular-nums !important;
}

/* --- DataFrames --- */
[data-testid="stDataFrame"] {
    border: 1px solid #D8C8A8 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(92,26,27,0.07) !important;
}



/* --- Dividers --- */
hr {
    border-color: #D8C8A8 !important;
    margin-top: 1.2em !important;
    margin-bottom: 1.2em !important;
}

/* --- Captions --- */
div[data-testid="stCaption"] p {
    color: #8A7B6B !important;
    font-size: 0.82rem !important;
}

/* --- Primary buttons (sliders, expander toggles, main CTA) --- */
.stButton > button[kind="primary"],
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background-color: #5C1A1B !important;
    color: #FBF7EF !important;
    border-radius: 20px !important;
}
.stButton > button {
    border-radius: 20px !important;
}

/* --- Download button: burgundy pill --- */
[data-testid="stDownloadButton"] > button {
    background-color: #5C1A1B !important;
    color: #FBF7EF !important;
    border: none !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.4rem !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background-color: #7A2A2B !important;
    box-shadow: 0 2px 8px rgba(92,26,27,0.28) !important;
}

/* --- Alert boxes --- */
[data-testid="stAlert"] {
    border-radius: 9px !important;
    border-width: 1px !important;
}

/* --- Metric value and label: allow wrapping, never clip --- */
[data-testid="stMetricValue"] div,
[data-testid="stMetricValue"] > div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    word-break: break-word !important;
    line-height: 1.3 !important;
}
[data-testid="stMetricLabel"] div,
[data-testid="stMetricLabel"] > div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.3 !important;
}

/* --- Expanders only (not all details elements) --- */
[data-testid="stExpander"] details {
    background-color: #FBF7EF !important;
    border: 1px solid #D8C8A8 !important;
    border-radius: 10px !important;
}
</style></div>""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT          = os.path.dirname(__file__)
DATA_DIR      = os.path.join(ROOT, "data")
FIGURES_DIR   = os.path.join(ROOT, "outputs", "figures")
L1_CSV        = os.path.join(DATA_DIR, "layer1_summary.csv")
L1_CORR_CSV   = os.path.join(DATA_DIR, "layer1_rolling_corr.csv")

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("India EM Thesis")
    st.caption("Thesis #16: India's Decade to Shine?")
    st.divider()
    section = st.radio(
        "Section",
        ["Part 1: Historical Analysis", "Part 2: Forward Framework", "What Moves the Verdict?"],
        index=0,
    )
    st.divider()
    st.caption(
        "Data are pinned to the locked mid-2026 case-study dataset. "
        "API-backed sources are flagged refreshable for future updates; "
        "this version does not auto-refresh, to stay consistent with the report."
    )

# ── Shared helpers ────────────────────────────────────────────────────────────
def verdict_badge(text: str, bg: str = "", fg: str = "#FBF7EF") -> None:
    preset = {
        "SUPPORTED":           "#1A6B3C",
        "PARTIALLY SUPPORTED": "#A06010",
        "NOT SUPPORTED":       "#9C1A18",
    }
    bg = bg or preset.get(text, "#4A6B8A")
    st.markdown(
        f'<div style="background:{bg};color:{fg};padding:18px 28px;'
        f'border-radius:10px;font-size:1.4rem;font-weight:800;'
        f'font-family:Georgia,Cambria,serif;'
        f'text-align:center;letter-spacing:0.06em;'
        f'box-shadow:0 2px 10px rgba(92,26,27,0.20);">{text}</div>',
        unsafe_allow_html=True,
    )


def score_badge_html(score_key: str, score_label: str, colors: dict) -> str:
    c = colors.get(score_key, "#4A6B8A")
    return (
        f'<span style="background:{c}18;border:1.5px solid {c};color:{c};'
        f'padding:4px 14px;border-radius:12px;font-weight:700;font-size:0.8rem;'
        f'letter-spacing:0.01em;">'
        f'{score_label}</span>'
    )


def role_chip_html(role: str) -> str:
    is_gating = "gating" in role.lower()
    bg  = "#F5E8E8" if is_gating else "#E8F0E8"
    clr = "#8B1515" if is_gating else "#1A5A30"
    lbl = "GATING" if is_gating else "STRUCTURAL"
    return (
        f'<span style="background:{bg};color:{clr};padding:2px 8px;'
        f'border-radius:3px;font-weight:700;font-size:0.67rem;'
        f'letter-spacing:0.09em;">{lbl}</span>'
    )


def indicator_header(name: str, role: str, score_key: str,
                     score_label: str, colors: dict) -> None:
    color = colors.get(score_key, "#4A6B8A")
    is_gating = "gating" in role.lower()
    role_bg  = "#F5E8E8" if is_gating else "#E8F0E8"
    role_clr = "#8B1515" if is_gating else "#1A5A30"
    role_lbl = "GATING" if is_gating else "STRUCTURAL"
    st.markdown(
        f'<div style="background:#FBF7EF;border-left:4px solid {color};'
        f'border-radius:0 10px 10px 0;padding:14px 20px 12px 20px;'
        f'margin:20px 0 8px 0;box-shadow:0 1px 4px rgba(92,26,27,0.07);">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'flex-wrap:wrap;gap:8px;">'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<span style="font-size:1.05rem;font-weight:700;color:#3A1010;'
        f'font-family:Georgia,Cambria,serif;">{name}</span>'
        f'<span style="background:{role_bg};color:{role_clr};padding:2px 8px;'
        f'border-radius:3px;font-weight:700;font-size:0.67rem;letter-spacing:0.09em;">'
        f'{role_lbl}</span>'
        f'</div>'
        f'<span style="background:{color}18;border:1.5px solid {color};color:{color};'
        f'padding:4px 14px;border-radius:12px;font-weight:700;font-size:0.8rem;">'
        f'{score_label}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def get_dp(indicator: dict, dp_id: str) -> dict:
    for dp in indicator.get("data_points", []):
        if dp["id"] == dp_id:
            return dp
    return {}


def _apply_style(styler, fn, **kwargs):
    try:
        return styler.map(fn, **kwargs)
    except AttributeError:
        return styler.applymap(fn, **kwargs)


# ── Part 1 ────────────────────────────────────────────────────────────────────
if section == "Part 1: Historical Analysis":

    st.header("Layer 1: Historical Performance (2013 to 2026)")
    st.caption(
        "Window: 2013-01-01 to 2026-06-25, pinned for reproducibility. "
        "Source: Yahoo Finance via yfinance (auto_adjust=True). "
        "All returns in USD."
    )

    # ── Summary table ─────────────────────────────────────────────────────────
    st.subheader("Summary Table")

    try:
        df = pd.read_csv(L1_CSV)
    except FileNotFoundError:
        st.error(f"Layer 1 summary CSV not found at {L1_CSV}")
        st.stop()

    display = df[["display_name", "role", "cumulative_return_pct",
                  "cagr_pct", "ann_vol_pct", "max_drawdown_pct", "sharpe_style"]].copy()
    display.columns = [
        "Ticker", "Role",
        "Cumulative Return", "CAGR",
        "Ann. Vol", "Max Drawdown", "Sharpe-style",
    ]
    display["Cumulative Return"] = display["Cumulative Return"].apply(lambda v: f"{v:+.1f}%")
    display["CAGR"]              = display["CAGR"].apply(lambda v: f"{v:.2f}%")
    display["Ann. Vol"]          = display["Ann. Vol"].apply(lambda v: f"{v:.2f}%")
    display["Max Drawdown"]      = display["Max Drawdown"].apply(lambda v: f"{v:.1f}%")
    display["Sharpe-style"]      = display["Sharpe-style"].apply(lambda v: f"{v:.3f}")
    display = display.set_index("Ticker")

    st.dataframe(display, use_container_width=True)
    st.caption(
        "EM ex-India benchmark: India's contribution removed using a fixed ~15% weight "
        "(same ex-India construction as used in the verdict). "
        "Sharpe-style ratio uses 0% risk-free rate (documented in DECISIONS.md)."
    )

    st.divider()

    # ── Verdict ───────────────────────────────────────────────────────────────
    st.subheader("Layer 1 Verdict")

    inda = df[df["ticker"] == "INDA"].iloc[0]
    ex   = df[df["ticker"] == "EEM_exIndia"].iloc[0]
    fxi  = df[df["ticker"] == "FXI"].iloc[0]

    beats_ex_ret     = inda["cumulative_return_pct"] > ex["cumulative_return_pct"]
    beats_fxi_ret    = inda["cumulative_return_pct"] > fxi["cumulative_return_pct"]
    beats_ex_sharpe  = inda["sharpe_style"]          > ex["sharpe_style"]
    beats_fxi_sharpe = inda["sharpe_style"]          > fxi["sharpe_style"]

    if (beats_ex_ret and beats_fxi_ret) and (beats_ex_sharpe and beats_fxi_sharpe):
        verdict = "SUPPORTED"
    elif (beats_ex_ret and beats_fxi_ret) or (beats_ex_sharpe and beats_fxi_sharpe):
        verdict = "PARTIALLY SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    verdict_badge(verdict)

    st.markdown(
        f"""
**Rule (pre-declared):** SUPPORTED if INDA beats both EM ex-India and FXI on cumulative
return AND Sharpe-style ratio. PARTIALLY SUPPORTED if on exactly one measure.
NOT SUPPORTED otherwise.

INDA cumulative return: **{inda['cumulative_return_pct']:+.1f}%** vs
EM ex-India: **{ex['cumulative_return_pct']:+.1f}%** and
FXI: **{fxi['cumulative_return_pct']:+.1f}%**.

INDA Sharpe-style: **{inda['sharpe_style']:.3f}** vs
EM ex-India: **{ex['sharpe_style']:.3f}** and
FXI: **{fxi['sharpe_style']:.3f}**.
        """
    )

    st.caption(
        "Layer 1 verdict covers the historical window only. "
        "Forward-looking context is in Part 2 (Layer 2 Forward Framework)."
    )

    st.divider()

    # ── Interactive: Rolling 12-Month Correlation ─────────────────────────────
    st.subheader("Rolling 12-Month Correlation (Interactive)")
    try:
        corr_df = pd.read_csv(L1_CORR_CSV, index_col="date", parse_dates=True)
        corr_df = corr_df.rename(columns={
            "INDA_EEM_exIndia": "INDA vs EM ex-India",
            "INDA_INR":         "INDA vs INR (USD/INR spot)",
        })
        st.line_chart(corr_df, use_container_width=True)
        st.caption(
            "Rolling 252-trading-day correlation. "
            "EM ex-India benchmark: India's contribution removed at fixed ~15% weight "
            "(same construction as the Layer 1 return benchmark). "
            "Window: 2014-01-16 to 2026-06-25 (pinned; first 252 days consumed by the rolling window). "
            "Near-zero INDA/INR correlation over the full window confirms the persistent "
            "currency drag has historically been absorbed by India's equity returns. "
            "Note: the Notable Finding (~0.76 average correlation) is INDA vs raw EEM, "
            "not INDA vs EM ex-India; the ex-India series averages ~0.61 over the same window."
        )
    except FileNotFoundError:
        st.warning(
            "layer1_rolling_corr.csv not found in data/. "
            "Showing the static chart below. "
            "Run the pin script in the project scratchpad to regenerate."
        )

    st.divider()

    # ── Static Charts ─────────────────────────────────────────────────────────
    st.subheader("Charts")

    chart_files = [
        ("01_cumulative_return.png",  "Chart 1: Cumulative USD Return (Growth of $100)"),
        ("02_vol_drawdown.png",        "Chart 2: Annualised Volatility and Max Drawdown"),
        ("03_rolling_correlation.png", "Chart 3: Rolling 12-Month Correlation"),
        ("04_verdict_card.png",        "Chart 4: Verdict Card"),
    ]

    for fname, caption in chart_files:
        path = os.path.join(FIGURES_DIR, fname)
        if os.path.exists(path):
            st.image(path, caption=caption, use_container_width=True)
        else:
            st.warning(
                f"{fname} not found. Run `python src/bronze/analysis.py` "
                "to regenerate the figures."
            )

# ── Part 2 ────────────────────────────────────────────────────────────────────
elif section == "Part 2: Forward Framework":
    from src.layer2 import (
        load_indicators, get_indicator, get_ladder_verdict,
        governance_as_dataframe, digital_peer_table,
        SCORE_COLORS, SCORE_ICONS, RUNG_LABELS,
        score_valuation, score_demographics, score_governance,
        score_digital_adoption, score_external_macro,
        compute_ladder_verdict,
    )
    from src.wb_refresh import fetch_wgi, fetch_findex

    # ── UI color overrides (display layer only; does not affect scoring logic) ─
    _UI_COLORS: dict = {
        "favorable":             "#1A6B3C",
        "neutral_to_caution":    "#A06010",
        "neutral":               "#4A6B8A",
        "neutral_lean_negative": "#8A4010",
        "at_risk_mild":          "#9C1A18",
        "severe":                "#6B0A0A",
    }

    # ── Threshold defaults ────────────────────────────────────────────────────
    _DEFAULTS: dict = {
        "th_val_caution":  20,
        "th_val_atrisk":   30,
        "th_val_severe":   40,
        "th_gov_count":    4,
        "th_dig_gap":      20,
        "th_dem_ratio":    60,
        "th_ext_inr_mild": 2.0,
        "th_ext_inr_sev":  8.0,
        "th_ext_oil_mild": 15,
        "th_ext_oil_sev":  45,
    }
    for _k, _v in _DEFAULTS.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ── Refresh state ─────────────────────────────────────────────────────────
    for _rk in ("wgi_live", "findex_live", "wgi_error", "findex_error"):
        if _rk not in st.session_state:
            st.session_state[_rk] = None

    # ── Callbacks ─────────────────────────────────────────────────────────────
    def _reset_thresholds() -> None:
        for _k, _v in _DEFAULTS.items():
            st.session_state[_k] = _v

    def _do_refresh_wgi() -> None:
        result = fetch_wgi()
        if result is not None:
            st.session_state["wgi_live"]  = result
            st.session_state["wgi_error"] = None
        else:
            st.session_state["wgi_error"] = (
                "WGI refresh failed. World Bank API may be unavailable or slow. "
                "Pinned data is still shown."
            )

    def _do_refresh_findex() -> None:
        result = fetch_findex()
        if result is not None:
            st.session_state["findex_live"]  = result
            st.session_state["findex_error"] = None
        else:
            st.session_state["findex_error"] = (
                "Findex refresh failed. World Bank API may be unavailable or slow. "
                "Pinned data is still shown."
            )

    def _revert_to_pinned() -> None:
        st.session_state["wgi_live"]    = None
        st.session_state["findex_live"] = None
        st.session_state["wgi_error"]   = None
        st.session_state["findex_error"] = None

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.markdown("**Threshold Explorer**")
        _off_thresh = any(
            st.session_state.get(_k) != _v for _k, _v in _DEFAULTS.items()
        )
        if _off_thresh:
            st.caption(
                "Non-default thresholds active. "
                "Declared verdict uses the pre-declared defaults."
            )
        st.button("Reset to pre-declared thresholds", on_click=_reset_thresholds)

        st.markdown("*Valuation bands*")
        st.slider("Neutral / Caution split (pre-declared: 20%)",
                  10, 35, step=5, format="%d%%", key="th_val_caution")
        st.slider("Caution / At-risk split (pre-declared: 30%)",
                  20, 50, step=5, format="%d%%", key="th_val_atrisk")
        st.slider("At-risk / Severe split (pre-declared: 40%)",
                  30, 60, step=5, format="%d%%", key="th_val_severe")

        st.markdown("*Governance*")
        st.slider("Lean-Negative if N+ dims below zero (pre-declared: 4)",
                  2, 6, step=1, key="th_gov_count")

        st.markdown("*Digital adoption*")
        st.slider("Peer-gap threshold for large lag (pre-declared: 20pp)",
                  5, 35, step=5, format="%dpp", key="th_dig_gap")

        st.markdown("*Demographics*")
        st.slider("Old-age dep ratio ceiling for Favorable (pre-declared: 60%)",
                  35, 85, step=5, format="%d%%", key="th_dem_ratio")

        st.markdown("*External macro*")
        st.slider("INR mild threshold (pre-declared: 2.0%/yr)",
                  0.5, 5.0, step=0.5, format="%.1f%%", key="th_ext_inr_mild")
        st.slider("INR severe threshold (pre-declared: 8.0%/yr)",
                  5.0, 15.0, step=1.0, format="%.1f%%", key="th_ext_inr_sev")
        st.slider("Oil mild threshold (pre-declared: 15%)",
                  5, 25, step=5, format="%d%%", key="th_ext_oil_mild")
        st.slider("Oil severe threshold (pre-declared: 45%)",
                  30, 60, step=5, format="%d%%", key="th_ext_oil_sev")

        st.divider()
        st.markdown("**Live Data Refresh**")
        st.caption(
            "Default: pinned mid-2026 dataset. "
            "Refresh to pull current World Bank figures. "
            "WGI takes ~10 s (6 sequential API calls)."
        )

        _ca, _cb = st.columns(2)
        _ca.button("Refresh WGI", on_click=_do_refresh_wgi,
                   help="Pull live World Bank Governance Indicators")
        _cb.button("Refresh Findex", on_click=_do_refresh_findex,
                   help="Pull live World Bank Global Findex 2024")

        _wgi_ts    = (st.session_state["wgi_live"]    or {}).get("fetched_at")
        _findex_ts = (st.session_state["findex_live"] or {}).get("fetched_at")

        if st.session_state["wgi_error"]:
            st.error(st.session_state["wgi_error"])
        elif _wgi_ts:
            st.caption(f"WGI: live ({_wgi_ts[:16]} UTC)")
        else:
            st.caption("WGI: pinned")

        if st.session_state["findex_error"]:
            st.error(st.session_state["findex_error"])
        elif _findex_ts:
            st.caption(f"Findex: live ({_findex_ts[:16]} UTC)")
        else:
            st.caption("Findex: pinned")

        _any_live = bool(st.session_state["wgi_live"] or st.session_state["findex_live"])
        if _any_live:
            st.button("Revert to pinned data", on_click=_revert_to_pinned)

    # ── Load pinned data ──────────────────────────────────────────────────────
    data    = load_indicators()
    val_ind = get_indicator(data, "valuation")
    dem_ind = get_indicator(data, "demographics")
    gov_ind = get_indicator(data, "governance")
    dig_ind = get_indicator(data, "digital_adoption")
    ext_ind = get_indicator(data, "external_macro")
    pinned  = get_ladder_verdict(data)

    # ── Resolve data sources (live if refreshed, else pinned) ─────────────────
    # WGI governance dimensions for scoring
    if st.session_state["wgi_live"]:
        _india_23 = {
            dim["name"]: dim["india"]["2023"]
            for dim in st.session_state["wgi_live"]["dimensions"]
        }
    else:
        _india_23 = {
            d["name"]: d["india"]["2023"]
            for d in gov_ind["wgi_table"]["dimensions"]
        }

    # Findex values for scoring
    if st.session_state["findex_live"]:
        _fl = st.session_state["findex_live"]
        _india_any = _fl["india_any"]
        _peer_any  = _fl["peer_median_any"]
    else:
        _fl = None
        _india_any = next(
            dp["value"] for dp in dig_ind["data_points"]
            if dp["id"] == "india_any_dig_2024"
        )
        _peer_any = next(
            dp["value"] for dp in dig_ind["data_points"]
            if dp["id"] == "peer_median_any_dig_2024"
        )

    # Pinned data values used in panels (unchanged by live refresh)
    _prem    = next(dp["value"] for dp in val_ind["data_points"] if dp["id"] == "premium_w13")
    _dem_dp  = {dp["id"]: dp["value"] for dp in dem_ind["data_points"]}

    # ── Live scoring from slider thresholds ───────────────────────────────────
    def _build_val_bands(caution_pct: int, atrisk_pct: int, severe_pct: int) -> list:
        c = caution_pct / 100
        a = max(atrisk_pct / 100, c + 0.05)
        s = max(severe_pct / 100, a + 0.05)
        return [
            {"label": "Favorable",          "range_low": 0.0,  "range_high": 0.10},
            {"label": "Neutral",             "range_low": 0.10, "range_high": c},
            {"label": "Caution",             "range_low": c,    "range_high": a},
            {"label": "At-risk",             "range_low": a,    "range_high": s},
            {"label": "Severe (gate trips)", "range_low": s,    "range_high": None},
        ]

    _live_bands = _build_val_bands(
        st.session_state["th_val_caution"],
        st.session_state["th_val_atrisk"],
        st.session_state["th_val_severe"],
    )

    live_val = score_valuation(premium=_prem, bands=_live_bands)
    live_dem = score_demographics(
        old_age_dep_india=_dem_dp["old_age_dep_india"],
        old_age_dep_china=_dem_dp["old_age_dep_china"],
        female_lfp_pct=_dem_dp["female_lfp_india"],
        max_ratio_for_favorable=st.session_state["th_dem_ratio"] / 100,
    )
    live_gov = score_governance(
        india_scores_2023=_india_23,
        neutral_neg_threshold=st.session_state["th_gov_count"],
    )
    live_dig = score_digital_adoption(
        india_pct=_india_any,
        peer_median_pct=_peer_any,
        trend_direction="up",
        large_gap=float(st.session_state["th_dig_gap"]),
    )
    live_ext = score_external_macro(
        inr_dep_pct=3.5,
        oil_share_pct=25.0,
        inr_mild_threshold=st.session_state["th_ext_inr_mild"],
        oil_mild_threshold=float(st.session_state["th_ext_oil_mild"]),
        inr_severe_threshold=st.session_state["th_ext_inr_sev"],
        oil_severe_threshold=float(st.session_state["th_ext_oil_sev"]),
    )

    live_scores  = {
        "valuation":        live_val,
        "demographics":     live_dem,
        "governance":       live_gov,
        "digital_adoption": live_dig,
        "external_macro":   live_ext,
    }
    live_verdict = compute_ladder_verdict(live_scores)

    off_default = any(st.session_state.get(_k) != _v for _k, _v in _DEFAULTS.items())
    off_live    = bool(st.session_state["wgi_live"] or st.session_state["findex_live"])

    # ── Helper: data source tag ───────────────────────────────────────────────
    def _src_tag(kind: str) -> str:
        """Return a short inline label showing whether data is live or pinned."""
        ts = (st.session_state[f"{kind}_live"] or {}).get("fetched_at", "")
        if ts:
            return f"Live (World Bank API, {ts[:10]})"
        return "Pinned (mid-2026 dataset)"

    # ── Page header ───────────────────────────────────────────────────────────
    st.header("Layer 2: Forward-Durability Framework")
    st.caption(
        "Forward question: Layer 1 established historical outperformance. "
        "Layer 2 tests whether that outperformance is durable going forward, "
        "or already priced in. Source: pinned mid-2026 dataset (see sidebar)."
    )

    if off_default:
        st.warning(
            "Threshold Explorer is active: one or more thresholds differ from the "
            "pre-declared defaults. Scores, summary, and verdict below reflect your "
            "current settings. The declared Rung 3 verdict uses the pre-declared defaults "
            "(reset via the sidebar button)."
        )

    if off_live:
        _live_parts = []
        if st.session_state["wgi_live"]:
            _live_parts.append(f"WGI governance (fetched {_wgi_ts[:16]} UTC)")
        if st.session_state["findex_live"]:
            _live_parts.append(f"Findex digital (fetched {_findex_ts[:16]} UTC)")
        st.info(
            "Live data active: "
            + " | ".join(_live_parts)
            + ". Scores and verdict below reflect the live figures. "
            "Values shown may differ from the pinned dataset."
        )

    st.markdown(
        "Layer 1 established that India outperformed EM ex-India and China across "
        "the 2013 to 2026 window on both cumulative return and risk-adjusted return. "
        "Layer 2 asks the harder question: is the structural opportunity still intact, "
        "or has the market already priced it in?\n\n"
        "The framework scores **five indicators** against pre-declared thresholds: "
        "**three structural** (do the fundamentals support durable outperformance?) "
        "and **two gating** (can external constraints cap the verdict?). "
        "A confidence ladder, not a vote count, determines the final verdict. "
        "Use the Threshold Explorer in the sidebar to test alternative scoring assumptions "
        "or refresh WGI and Findex to pull current World Bank data."
    )

    st.divider()

    # ── Indicator 1: Valuation (Gating) ───────────────────────────────────────
    indicator_header(val_ind["name"], val_ind["role"],
                     live_val["score"], live_val["score_display"], _UI_COLORS)

    inda_pe   = get_dp(val_ind, "inda_pe")
    msci_pe   = get_dp(val_ind, "msci_em_pe")
    prem_low  = get_dp(val_ind, "premium_w12")
    prem_high = get_dp(val_ind, "premium_w15")
    prem_lo_pct = prem_low["value"] * 100
    prem_hi_pct = prem_high["value"] * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("INDA trailing P/E", f"{inda_pe['value']:.2f}x",
              help=f"Source: {inda_pe['source']} | As of {inda_pe['as_of']}")
    c2.metric("MSCI EM trailing P/E", f"{msci_pe['value']:.2f}x",
              help=f"Source: {msci_pe['source']} | As of {msci_pe['as_of']}")
    c3.metric("P/E premium (India / EM)",
              f"{prem_lo_pct:.1f}-{prem_hi_pct:.1f}%",
              help="Range across India weight assumptions 12% to 15%. Same ex-India construction as Layer 1.")

    with st.expander("Valuation bands (current thresholds)"):
        for b in _live_bands:
            hi_str = (f"{b['range_high'] * 100:.0f}%"
                      if b["range_high"] is not None else "above last split")
            lo_str = f"{b['range_low'] * 100:.0f}%"
            in_band = (
                (b["range_high"] is None and _prem >= b["range_low"])
                or (b["range_high"] is not None and b["range_low"] <= _prem < b["range_high"])
            )
            marker = "   **<< India (~23.9%) is here**" if in_band else ""
            st.markdown(f"- **{b['label']}:** {lo_str} to {hi_str}{marker}")

    if live_val["gate_trips_severe"]:
        st.markdown(
            f"**Rationale:** At the current Severe threshold, the {prem_lo_pct:.1f}% to "
            f"{prem_hi_pct:.1f}% premium triggers a severe gate. This forces the verdict "
            f"to Rung 4 regardless of structural scores."
        )
    else:
        st.markdown(
            f"**Rationale:** The {prem_lo_pct:.1f}% to {prem_hi_pct:.1f}% P/E premium places "
            f"India in the **{live_val['score_display']}** zone. Multiple credible sources "
            f"(Goldman via Reuters, late 2025 to early 2026) report the premium is below "
            f"India's own historical norm, which softens but does not erase the headwind. "
            f"Gate does not trip severe."
        )
    st.caption(f"Limitation: {val_ind['acknowledged_limitation']}")
    st.caption(
        f"Sources: {inda_pe['source']} (as of {inda_pe['as_of']}); "
        f"{msci_pe['source']} (as of {msci_pe['as_of']}) | "
        f"Refreshable: No (P/E data requires licensed provider)"
    )

    st.divider()

    # ── Indicator 2: Demographics (Structural) ────────────────────────────────
    indicator_header(dem_ind["name"], dem_ind["role"],
                     live_dem["score"], live_dem["score_display"], _UI_COLORS)

    old_ind = get_dp(dem_ind, "old_age_dep_india")
    old_chn = get_dp(dem_ind, "old_age_dep_china")
    tot_ind = get_dp(dem_ind, "total_dep_india")
    tot_chn = get_dp(dem_ind, "total_dep_china")
    flfp    = get_dp(dem_ind, "female_lfp_india")
    tlfp    = get_dp(dem_ind, "total_lfp_india")

    c1, c2, c3 = st.columns(3)
    c1.metric("Old-age dep. (India / China)",
              f"{old_ind['value']} / {old_chn['value']}",
              delta="Less than half China's ratio (favorable)",
              delta_color="off",
              help=f"Source: {old_ind['source']} | As of {old_ind['as_of']}")
    c2.metric("Total age dep. (India / China)",
              f"{tot_ind['value']} / {tot_chn['value']}",
              help=f"Source: {tot_ind['source']} | As of {tot_ind['as_of']}")
    c3.metric("Female LFP: India", f"{flfp['value']}%",
              delta=f"Total LFP: {tlfp['value']}%",
              delta_color="off",
              help=f"Source: {flfp['source']} | As of {flfp['as_of']}")

    _ratio = old_ind["value"] / old_chn["value"]
    st.markdown(
        f"**Rationale:** Old-age dependency ratio is {old_ind['value']} vs China's "
        f"{old_chn['value']} (ratio {_ratio:.2f}). Current threshold: Favorable if ratio "
        f"< {st.session_state['th_dem_ratio']}% (pre-declared: 60%). "
        f"Female LFP at {flfp['value']}% means the dividend is only partially realized: "
        f"both a current shortfall and remaining upside if participation rises."
    )
    st.caption(
        f"Source: {old_ind['source']} | As of {old_ind['as_of']} | "
        f"Refreshable: No (World Bank WDI; use WGI refresh button for governance only)"
    )

    st.divider()

    # ── Indicator 3: Governance (Structural) ──────────────────────────────────
    indicator_header(gov_ind["name"], gov_ind["role"],
                     live_gov["score"], live_gov["score_display"], _UI_COLORS)

    # Build WGI table from live or pinned data
    if st.session_state["wgi_live"]:
        _wgi_dims = st.session_state["wgi_live"]["dimensions"]
        _years    = [2014, 2019, 2023]
        _wgi_rows = []
        for dim in _wgi_dims:
            row = {"Dimension": dim["name"]}
            for yr in _years:
                row[f"India {yr}"] = dim["india"].get(str(yr))
                row[f"China {yr}"] = dim["china"].get(str(yr))
            _wgi_rows.append(row)
        wgi_df = pd.DataFrame(_wgi_rows).set_index("Dimension")
    else:
        wgi_df = governance_as_dataframe(data)

    def color_wgi_cell(v):
        if not isinstance(v, (int, float)):
            return ""
        if v > 0.2:
            return "background-color:#1a3d2b;color:#7ecf9f"
        elif v > 0:
            return "background-color:#1e3a24;color:#a8d5b5"
        elif v > -0.3:
            return "background-color:#3a2828;color:#e0b0b0"
        else:
            return "background-color:#4a1818;color:#f5c0c0"

    # Show 2023 columns only (fits container without horizontal scroll)
    _wgi_2023_cols = [c for c in wgi_df.columns if "2023" in str(c)]
    wgi_2023 = wgi_df[_wgi_2023_cols] if _wgi_2023_cols else wgi_df
    st.dataframe(_apply_style(wgi_2023.style, color_wgi_cell), use_container_width=True)
    with st.expander("Full WGI history (2014, 2019, 2023)"):
        st.dataframe(_apply_style(wgi_df.style, color_wgi_cell), use_container_width=True)
    years_str = ", ".join(str(y) for y in gov_ind["wgi_table"]["years"])
    st.caption(
        f"{gov_ind['wgi_table']['scale']}. "
        f"Years shown: {years_str}. Green = above zero; red = below zero."
    )
    st.markdown(
        f"**Rationale:** {live_gov['below_zero_count']} of 6 WGI dimensions are below zero "
        f"for India (2023). Current threshold: Lean-Negative if {st.session_state['th_gov_count']}+ "
        f"dimensions below zero (pre-declared: 4). India leads on Rule of Law and Voice and "
        f"Accountability vs China but trails on Government Effectiveness and Control of Corruption."
    )
    wgi_src = get_dp(gov_ind, "wgi_source")
    st.caption(
        f"Data source: {_src_tag('wgi')} | "
        f"Refreshable: Yes (use Refresh WGI button in sidebar)"
    )

    st.divider()

    # ── Indicator 4: Digital Financial Adoption (Structural) ──────────────────
    indicator_header(dig_ind["name"], dig_ind["role"],
                     live_dig["score"], live_dig["score_display"], _UI_COLORS)

    # Resolve display values (live or pinned)
    if _fl:
        _d_india_any   = _fl["india_any"]
        _d_peer_any    = _fl["peer_median_any"]
        _d_india_merch = _fl["india_merchant"]
        _d_peer_merch  = _fl["peer_median_merchant"]
    else:
        ind_any_dp  = get_dp(dig_ind, "india_any_dig_2024")
        peer_any_dp = get_dp(dig_ind, "peer_median_any_dig_2024")
        ind_mch_dp  = get_dp(dig_ind, "india_merchant_2024")
        peer_mch_dp = get_dp(dig_ind, "peer_median_merchant_2024")
        _d_india_any   = ind_any_dp["value"]
        _d_peer_any    = peer_any_dp["value"]
        _d_india_merch = ind_mch_dp["value"]
        _d_peer_merch  = peer_mch_dp["value"]

    _gap_any = _d_peer_any  - _d_india_any
    _gap_mch = _d_peer_merch - _d_india_merch

    c1, c2 = st.columns(2)
    c1.metric("Any digital pay. (India / EM median)",
              f"{_d_india_any}% / {_d_peer_any}%",
              delta=f"India trails by {_gap_any:.1f}pp",
              delta_color="inverse")
    c2.metric("Merchant payments (India / EM median)",
              f"{_d_india_merch}% / {_d_peer_merch}%",
              delta=f"India trails by {_gap_mch:.1f}pp",
              delta_color="inverse")

    trend     = dig_ind["india_trend_any_digital"]
    trend_str = " -> ".join(f"{t['value']}% ({t['year']})" for t in trend)
    st.markdown(f"**India adoption trend (any digital payment):** {trend_str}")

    # Peer table (live or pinned)
    with st.expander("EM peer comparison table, 2024 (World Bank Findex)"):
        if _fl:
            _ptable = pd.DataFrame([
                {
                    "Country":                     r["country"],
                    "Any digital payment (%)":     r["any_pct"],
                    "Digital merchant payment (%)": r["merchant_pct"],
                }
                for r in _fl["peer_table"]
            ]).set_index("Country")
        else:
            _ptable = digital_peer_table(data)
        st.dataframe(_ptable, use_container_width=True)

    st.markdown(
        f"**Rationale:** India lags the EM peer median by {_gap_any:.1f}pp on any digital "
        f"payment and {_gap_mch:.1f}pp on merchant payments. Current threshold: a gap above "
        f"{st.session_state['th_dig_gap']}pp (pre-declared: 20pp) with an upward trend "
        f"scores Neutral. Adoption is rising fast from {trend[0]['value']}% "
        f"({trend[0]['year']}) to {trend[-1]['value']}% ({trend[-1]['year']})."
    )
    st.caption(dig_ind["honest_note"])
    st.caption(
        f"Data source: {_src_tag('findex')} | "
        f"Refreshable: Yes (use Refresh Findex button in sidebar)"
    )

    st.divider()

    # ── Indicator 5: External Macro Vulnerability (Gating) ────────────────────
    indicator_header(ext_ind["name"], ext_ind["role"],
                     live_ext["score"], live_ext["score_display"], _UI_COLORS)

    inr_drag  = get_dp(ext_ind, "inr_depreciation_rate")
    oil_share = get_dp(ext_ind, "oil_import_share")
    inr_corr  = get_dp(ext_ind, "inda_inr_correlation")

    c1, c2, c3 = st.columns(3)
    c1.metric("INR depreciation vs USD",
              inr_drag["value"].replace("per year", "/yr"),
              help=f"Source: {inr_drag['source']} | As of {inr_drag['as_of']}")
    c2.metric("Oil share of import bill",
              oil_share["value"].replace("approximately ", "~"),
              help=f"Source: {oil_share['source']} | As of {oil_share['as_of']}")
    c3.metric("INDA vs INR correlation (Layer 1)",
              inr_corr["value"].replace("approximately ", "~"),
              help=f"Source: {inr_corr['source']}")

    st.markdown(
        f"**Rationale:** INR at ~3.5%/yr depreciation vs mild threshold "
        f"{st.session_state['th_ext_inr_mild']}%/yr (severe: {st.session_state['th_ext_inr_sev']}%/yr). "
        f"Oil at ~25% of imports vs mild threshold {st.session_state['th_ext_oil_mild']}% "
        f"(severe: {st.session_state['th_ext_oil_sev']}%). "
        f"Current signal: **{live_ext['score_display']}**. "
        f"Layer 1 found ~0 rolling correlation between INDA and the rupee, "
        f"meaning the currency drag has been absorbed historically. "
        f"Oil shock risk is conditional, not structural."
    )
    st.caption(ext_ind["note"])
    st.caption(
        f"Sources: INR forecast from {inr_drag['source']} (as of {inr_drag['as_of']}); "
        f"oil data from {oil_share['source']} | "
        f"Refreshable: No (forecast data, not a stable API)"
    )

    st.divider()

    # ── Live Scoring Summary ───────────────────────────────────────────────────
    st.subheader("Scoring Summary")

    _label_map = {
        "valuation":        ("Valuation",                   "Gating"),
        "demographics":     ("Demographics",                 "Structural"),
        "governance":       ("Governance",                   "Structural"),
        "digital_adoption": ("Digital Adoption",             "Structural"),
        "external_macro":   ("External Macro Vulnerability", "Gating (soft)"),
    }
    summary_df = pd.DataFrame([
        {
            "indicator": _label_map[k][0],
            "role":      _label_map[k][1],
            "score":     v["score_display"],
        }
        for k, v in live_scores.items()
    ])

    # HTML table replaces st.dataframe here so score labels never clip
    _sum_rows = ""
    for _, row in summary_df.iterrows():
        score_key_lookup = next(
            (k for k, v in live_scores.items() if v["score_display"] == row["score"]),
            None,
        )
        _c = _UI_COLORS.get(
            live_scores[score_key_lookup]["score"] if score_key_lookup else "neutral",
            "#4A6B8A",
        )
        _sum_rows += (
            f'<tr style="border-top:1px solid #E8DEC8;">'
            f'<td style="padding:9px 14px;font-weight:600;color:#2C1A0E;">'
            f'{row["indicator"]}</td>'
            f'<td style="padding:9px 14px;color:#8A7B6B;font-size:0.85rem;">'
            f'{row["role"]}</td>'
            f'<td style="padding:9px 14px;">'
            f'<span style="background:{_c}28;border:1.5px solid {_c};color:{_c};'
            f'padding:3px 11px;border-radius:10px;font-weight:700;font-size:0.8rem;'
            f'white-space:normal;">{row["score"]}</span></td>'
            f'</tr>'
        )
    st.markdown(
        f'<div style="border:1px solid #D8C8A8;border-radius:10px;overflow:hidden;'
        f'box-shadow:0 1px 4px rgba(92,26,27,0.07);">'
        f'<table style="width:100%;border-collapse:collapse;background:#FBF7EF;">'
        f'<thead><tr style="background:#F0E8D8;">'
        f'<th style="padding:10px 14px;text-align:left;color:#8A7B6B;font-size:0.72rem;'
        f'text-transform:uppercase;letter-spacing:0.07em;font-weight:700;">Indicator</th>'
        f'<th style="padding:10px 14px;text-align:left;color:#8A7B6B;font-size:0.72rem;'
        f'text-transform:uppercase;letter-spacing:0.07em;font-weight:700;">Role</th>'
        f'<th style="padding:10px 14px;text-align:left;color:#8A7B6B;font-size:0.72rem;'
        f'text-transform:uppercase;letter-spacing:0.07em;font-weight:700;">Score</th>'
        f'</tr></thead>'
        f'<tbody>{_sum_rows}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

    # ── Download button ───────────────────────────────────────────────────────
    _thresh_labels = {
        "th_val_caution":  "Valuation Neutral/Caution split (%)",
        "th_val_atrisk":   "Valuation Caution/At-risk split (%)",
        "th_val_severe":   "Valuation At-risk/Severe split (%)",
        "th_gov_count":    "Governance Lean-Neg threshold (dims below 0)",
        "th_dig_gap":      "Digital adoption large-gap threshold (pp)",
        "th_dem_ratio":    "Demographics old-age ratio ceiling (%)",
        "th_ext_inr_mild": "External macro INR mild threshold (%/yr)",
        "th_ext_inr_sev":  "External macro INR severe threshold (%/yr)",
        "th_ext_oil_mild": "External macro oil mild threshold (%)",
        "th_ext_oil_sev":  "External macro oil severe threshold (%)",
    }

    def _build_export_csv() -> str:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        thresh_status = "non-default thresholds active" if off_default else "pre-declared defaults"
        data_status   = "live World Bank API" if off_live else "pinned mid-2026 dataset"
        lines = [
            f"# India EM Thesis -- Layer 2 Framework State Export ({ts})",
            f"# Threshold status: {thresh_status}",
            f"# Data source: {data_status}",
            "",
            "INDICATOR SCORES",
            "Indicator,Role,Score",
        ]
        for k, v in live_scores.items():
            name, role = _label_map[k]
            lines.append(f"{name},{role},{v['score_display']}")
        lines += [
            "",
            "THRESHOLD VALUES",
            "Threshold,Pre-declared Default,Current Value,Off-Default",
        ]
        for k, default_val in _DEFAULTS.items():
            current_val = st.session_state.get(k, default_val)
            off = "Yes" if current_val != default_val else "No"
            label = _thresh_labels.get(k, k)
            lines.append(f"{label},{default_val},{current_val},{off}")
        return "\n".join(lines)

    _export_fname = (
        f"india_em_framework_"
        f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}.csv"
    )
    st.download_button(
        label="Download framework state (CSV)",
        data=_build_export_csv(),
        file_name=_export_fname,
        mime="text/csv",
        help="Exports all five indicator scores and the current threshold values to a CSV file.",
    )

    st.divider()

    # ── Live Confidence Ladder and Verdict ────────────────────────────────────
    st.subheader("Confidence Ladder and Final Verdict")

    rung = live_verdict["rung"]

    _rung_styles = {
        1: ("#0E2818", "#1A6B3C", "#5CD898"),
        2: ("#2A1608", "#A06010", "#E8A840"),
        3: ("#081A20", "#1A7070", "#5CC4C0"),
        4: ("#250808", "#9C1A18", "#F09090"),
    }

    for r_num, r_label in RUNG_LABELS.items():
        active = r_num == rung
        if active:
            bg, border, clr = _rung_styles[r_num]
            weight, arrow = "700", "  < current verdict"
            color_css = f"color:{clr};"
        else:
            bg, border = "#1E0E0E", "#3A1818"
            weight, arrow, color_css = "400", "", "color:#A07060;"
        st.markdown(
            f'<div style="background:{bg};border:2px solid {border};border-radius:6px;'
            f'padding:11px 18px;margin:3px 0;font-weight:{weight};{color_css}">'
            f'<span style="opacity:0.45;font-size:0.78rem;letter-spacing:0.05em;">'
            f'RUNG {r_num}</span>'
            f'<span style="margin-left:10px;">{r_label}</span>'
            f'<span style="font-size:0.78rem;opacity:0.7;margin-left:6px;">{arrow}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    _vbg, _vborder, _vtxt = _rung_styles[rung]
    st.markdown(
        f'<div style="background:{_vbg};border:2px solid {_vborder};color:{_vtxt};'
        f'margin-top:10px;padding:18px 28px;border-radius:10px;font-size:1.25rem;font-weight:800;'
        f'font-family:Georgia,Cambria,serif;'
        f'text-align:center;letter-spacing:0.05em;'
        f'box-shadow:0 2px 10px rgba(92,26,27,0.25);">'
        f'RUNG {rung}: {RUNG_LABELS[rung].upper()}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"**Derivation:** {live_verdict['derivation']}")
    st.markdown(f"**Declared verdict:** {pinned['verdict_statement']}")

    st.divider()

    st.subheader("Direct Answer to the Thesis Question")
    st.info(pinned["thesis_answer"])
    st.markdown(f"**Analyst's journey:** {pinned['analysts_journey']}")

    st.divider()
    _data_note = []
    if off_live:
        _data_note.append("live World Bank API data active")
    else:
        _data_note.append("pinned mid-2026 dataset")
    if off_default:
        _data_note.append("non-default thresholds active")
    st.caption(
        "Layer 2 framework: five indicators, pre-declared thresholds, gated confidence "
        f"ladder. Currently showing: {' | '.join(_data_note)}. "
        "Declared Rung 3 verdict uses pre-declared defaults and pinned data. "
        "Data from data/layer2_indicators.json and World Bank API."
    )

elif section == "What Moves the Verdict?":
    import json as _json
    from src.assumption_audit import run_assumption_audit, _FULL_DEFAULTS
    from src.verdict_agents import run_pipeline

    # ── Load pinned data and run the audit (pure Python, always runs) ──────────
    _audit_data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "layer2_indicators.json"
    )
    with open(_audit_data_path) as _f:
        _audit_raw = _json.load(_f)

    _audit = run_assumption_audit(_audit_raw, _FULL_DEFAULTS)

    d   = _audit["nearest_downgrade"]
    ps  = _audit["profile_stability"]
    blk = _audit["upgrade_blockers"]

    # ── Page header ────────────────────────────────────────────────────────────
    st.header("What Moves the Verdict?")
    st.caption(
        "This section stress-tests the Rung 3 verdict. "
        "All numbers below are produced by the same Python scoring model "
        "that drives Part 2. The LLM narrative (if available) only explains "
        "what the model found -- it does not add claims or forecasts of its own."
    )

    st.divider()

    # ── Current standing ───────────────────────────────────────────────────────
    st.subheader("Current Standing")
    _rung_clr = "#1A7070"
    st.markdown(
        f'<div style="background:#081A20;border:2px solid {_rung_clr};'
        f'color:#5CC4C0;padding:14px 22px;border-radius:8px;'
        f'font-size:1.2rem;font-weight:800;font-family:Georgia,Cambria,serif;'
        f'letter-spacing:0.05em;text-align:center;margin-bottom:8px;">'
        f'RUNG {_audit["current_rung"]}: {_audit["current_rung_label"].upper()}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**Derivation:** {_audit['current_derivation']}")

    st.divider()

    # ── Upgrade blockers ───────────────────────────────────────────────────────
    st.subheader("What Would Trigger an Upgrade?")
    st.markdown(
        "Rungs 1 and 2 require favorable scores on governance and digital adoption. "
        "Both are blocked by fixed data constraints -- threshold changes alone cannot "
        "resolve them."
    )

    _blocker_cols = st.columns(2)
    for _i, (_col, _blocker) in enumerate(zip(_blocker_cols, blk)):
        with _col:
            st.markdown(
                f'<div style="background:#FBF7EF;border:1.5px solid #D8C8A8;'
                f'border-radius:10px;padding:16px 18px;'
                f'box-shadow:0 1px 4px rgba(92,26,27,0.07);">'
                f'<div style="font-size:0.7rem;text-transform:uppercase;'
                f'letter-spacing:0.08em;color:#8A7B6B;font-weight:700;margin-bottom:6px;">'
                f'Upgrade Blocker {_i + 1}</div>'
                f'<div style="font-size:1rem;font-weight:700;color:#3A1010;'
                f'font-family:Georgia,Cambria,serif;margin-bottom:8px;">'
                f'{_blocker["indicator"]}</div>'
                f'<div style="font-size:0.875rem;color:#2C1A0E;line-height:1.5;">'
                f'{_blocker["why_threshold_cant_fix"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Nearest downgrade boundary ─────────────────────────────────────────────
    st.subheader("Nearest Downgrade Boundary")
    st.markdown(
        "The table below shows the only path to Rung 4 visible in the current data. "
        "This is a model boundary defined before scoring began, not a market forecast "
        "or a projection of where the premium is headed."
    )

    _dc1, _dc2, _dc3 = st.columns(3)
    _dc1.metric(
        "Current P/E premium",
        f"{d['current_value_pct']}%",
        help="India vs EM ex-India. Source: pinned mid-2026 dataset.",
    )
    _dc2.metric(
        "Declared severe gate",
        f"{d['trigger_value_pct']:.0f}%",
        help="Pre-declared threshold. Fixed before scoring; not tuned to data.",
    )
    _dc3.metric(
        "Gap to severe gate",
        f"{d['gap_pp']}pp",
        help=f"Relative to current: {d['gap_relative_pct']}% increase needed.",
    )

    st.markdown(
        f'<div style="background:#FBF7EF;border-left:4px solid #A06010;'
        f'padding:12px 16px;border-radius:0 8px 8px 0;margin-top:8px;">'
        f'<span style="color:#A06010;font-weight:700;">Plausibility: </span>'
        f'<span style="color:#2C1A0E;">{d["plausibility_label"].capitalize()}. '
        f'{d["boundary_note"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Profile stability ──────────────────────────────────────────────────────
    st.subheader("Framework Robustness")

    _stable_color = "#1A6B3C" if ps["stable"] else "#9C1A18"
    _stable_label = "Stable across all tested profiles" if ps["stable"] else "Varies across profiles"
    st.markdown(
        f'<div style="background:#FBF7EF;border:1.5px solid #D8C8A8;'
        f'border-radius:10px;padding:14px 18px;'
        f'box-shadow:0 1px 4px rgba(92,26,27,0.07);">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        f'<span style="background:{_stable_color}28;border:1.5px solid {_stable_color};'
        f'color:{_stable_color};padding:2px 12px;border-radius:10px;'
        f'font-weight:700;font-size:0.8rem;">{_stable_label}</span>'
        f'</div>'
        f'<div style="color:#2C1A0E;font-size:0.9rem;line-height:1.6;">{ps["note"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Agent narrative ────────────────────────────────────────────────────────
    st.subheader("Analytical Narrative")
    st.caption(
        "The narrative below is generated by an LLM agent chain. "
        "The agents may only reference numbers and claims present in the Python audit above. "
        "If the LLM is unavailable, the deterministic verdict above is unchanged."
    )

    if "wmv_pipeline_outputs" not in st.session_state:
        st.session_state["wmv_pipeline_outputs"] = None

    _run_col, _clear_col = st.columns([2, 1])
    _run_btn   = _run_col.button("Generate narrative", key="wmv_run")
    _clear_btn = _clear_col.button("Clear", key="wmv_clear")

    if _clear_btn:
        st.session_state["wmv_pipeline_outputs"] = None

    if _run_btn:
        with st.spinner("Running agent pipeline..."):
            try:
                st.session_state["wmv_pipeline_outputs"] = run_pipeline(_audit)
            except Exception as _exc:
                st.session_state["wmv_pipeline_outputs"] = {
                    "analysis": f"[Pipeline unavailable: {_exc}]",
                    "validation": {"passed": False, "failures": [str(_exc)], "warnings": []},
                    "overreach_check": "",
                }

    _out = st.session_state.get("wmv_pipeline_outputs")

    if _out is None:
        st.info("Click 'Generate narrative' to run the LLM agent pipeline.")
    else:
        _analysis  = _out.get("analysis", "").replace("—", ",").replace("–", ",")
        _val       = _out.get("validation", {})
        _overreach = _out.get("overreach_check", "").replace("—", ",").replace("–", ",")

        if _analysis.startswith("["):
            st.error(_analysis)
        else:
            st.markdown(_analysis)

            # Validation badge
            if _val.get("passed"):
                _vchip_bg, _vchip_fg, _vchip_txt = "#1A6B3C28", "#1A6B3C", "Fact-check passed"
            else:
                _vchip_bg, _vchip_fg, _vchip_txt = "#9C1A1828", "#9C1A18", "Fact-check failed"
            st.markdown(
                f'<span style="background:{_vchip_bg};border:1.5px solid {_vchip_fg};'
                f'color:{_vchip_fg};padding:2px 12px;border-radius:10px;'
                f'font-weight:700;font-size:0.8rem;">{_vchip_txt}</span>',
                unsafe_allow_html=True,
            )
            for _fail in _val.get("failures", []):
                st.warning(f"Validation: {_fail}")
            for _warn in _val.get("warnings", []):
                st.caption(f"Note: {_warn}")

            if _overreach:
                with st.expander("Overreach check"):
                    st.markdown(_overreach)

    st.divider()
    st.caption(
        "All quantitative claims in this section derive from "
        "src/assumption_audit.py using pre-declared defaults and pinned data. "
        "The LLM pipeline (src/verdict_agents.py) uses Google Gemini; "
        "key loaded from .env. Narrative does not affect the scored verdict."
    )
