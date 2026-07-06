"""
Silver-tier Streamlit app.
Part 1: Layer 1 historical analysis.
Part 2: Layer 2 forward-durability framework.

Run: streamlit run app.py
"""

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

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT        = os.path.dirname(__file__)
DATA_DIR    = os.path.join(ROOT, "data")
FIGURES_DIR = os.path.join(ROOT, "outputs", "figures")
L1_CSV      = os.path.join(DATA_DIR, "layer1_summary.csv")

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("India EM Thesis")
    st.caption("Thesis #16: India's Decade to Shine?")
    st.divider()
    section = st.radio(
        "Section",
        ["Part 1: Historical Analysis", "Part 2: Forward Framework"],
        index=0,
    )
    st.divider()
    st.caption(
        "Data are pinned to the locked mid-2026 case-study dataset. "
        "API-backed sources are flagged refreshable for future updates; "
        "this version does not auto-refresh, to stay consistent with the report."
    )

# ── Shared helpers ────────────────────────────────────────────────────────────
def verdict_badge(text: str, bg: str = "", fg: str = "#0D1B2A") -> None:
    preset = {
        "SUPPORTED":           "#2D9E6B",
        "PARTIALLY SUPPORTED": "#C9A84C",
        "NOT SUPPORTED":       "#E05C5C",
    }
    bg = bg or preset.get(text, "#8FA3B1")
    st.markdown(
        f'<div style="background:{bg};color:{fg};padding:16px 28px;'
        f'border-radius:8px;font-size:1.4rem;font-weight:700;'
        f'text-align:center;letter-spacing:0.05em;">{text}</div>',
        unsafe_allow_html=True,
    )


def score_badge_html(score_key: str, score_label: str, colors: dict) -> str:
    c = colors.get(score_key, "#8FA3B1")
    return (
        f'<span style="background:{c}28;border:1px solid {c};color:{c};'
        f'padding:3px 12px;border-radius:4px;font-weight:600;font-size:0.85rem;">'
        f'{score_label}</span>'
    )


def role_chip_html(role: str) -> str:
    is_gating = "gating" in role.lower()
    bg  = "#1a3a5c" if is_gating else "#1a3a28"
    clr = "#7ab4d8" if is_gating else "#7abf8e"
    lbl = "GATING" if is_gating else "STRUCTURAL"
    return (
        f'<span style="background:{bg};color:{clr};padding:2px 8px;'
        f'border-radius:3px;font-weight:600;font-size:0.72rem;'
        f'letter-spacing:0.07em;">{lbl}</span>'
    )


def indicator_header(name: str, role: str, score_key: str,
                     score_label: str, colors: dict) -> None:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(
            f"### {name} &nbsp; {role_chip_html(role)}",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div style="text-align:right;padding-top:14px;">'
            f'{score_badge_html(score_key, score_label, colors)}</div>',
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

    # ── Charts ────────────────────────────────────────────────────────────────
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
        governance_as_dataframe, digital_peer_table, scoring_summary,
        SCORE_COLORS,
    )

    data   = load_indicators()
    ladder = get_ladder_verdict(data)

    st.header("Layer 2: Forward-Durability Framework")
    st.caption(
        "Forward question: Layer 1 established historical outperformance. "
        "Layer 2 tests whether that outperformance is durable going forward, "
        "or already priced in. Source: pinned mid-2026 dataset (see sidebar note)."
    )

    st.markdown(
        "Layer 1 established that India outperformed EM ex-India and China across "
        "the 2013 to 2026 window on both cumulative return and risk-adjusted return. "
        "Layer 2 asks the harder question: is the structural opportunity still intact, "
        "or has the market already priced it in?\n\n"
        "The framework scores **five indicators** against pre-declared thresholds: "
        "**three structural** (do the fundamentals support durable outperformance?) "
        "and **two gating** (can external constraints cap the verdict?). "
        "A confidence ladder, not a vote count, determines the final verdict."
    )

    st.divider()

    # ── Indicator 1: Valuation (Gating) ───────────────────────────────────────
    val = get_indicator(data, "valuation")
    indicator_header(val["name"], val["role"], val["score"], val["score_display"], SCORE_COLORS)

    inda_pe   = get_dp(val, "inda_pe")
    msci_pe   = get_dp(val, "msci_em_pe")
    prem_low  = get_dp(val, "premium_w12")
    prem_high = get_dp(val, "premium_w15")

    prem_lo_pct = prem_low["value"] * 100
    prem_hi_pct = prem_high["value"] * 100

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "INDA trailing P/E",
        f"{inda_pe['value']:.2f}x",
        help=f"Source: {inda_pe['source']} | As of {inda_pe['as_of']}",
    )
    c2.metric(
        "MSCI EM trailing P/E",
        f"{msci_pe['value']:.2f}x",
        help=f"Source: {msci_pe['source']} | As of {msci_pe['as_of']}",
    )
    c3.metric(
        "India P/E premium to EM ex-India",
        f"{prem_lo_pct:.1f}% to {prem_hi_pct:.1f}%",
        help="Range across India weight assumptions 12% to 15%. Same ex-India construction as Layer 1.",
    )

    with st.expander("Pre-declared valuation bands (thresholds set before scoring India)"):
        for b in val["premium_bands"]:
            hi_str = (
                f"{b['range_high'] * 100:.0f}%"
                if b["range_high"] is not None
                else "above 40%"
            )
            lo_str = f"{b['range_low'] * 100:.0f}%"
            active = b["label"] == "Caution"
            marker = "   **<< India is here**" if active else ""
            st.markdown(f"- **{b['label']}:** {lo_str} to {hi_str}{marker}")

    st.markdown(
        f"**Rationale:** The {prem_lo_pct:.1f}% to {prem_hi_pct:.1f}% P/E premium places "
        f"India in the Caution band (20% to 30%). Multiple credible sources (Goldman via "
        f"Reuters, late 2025 to early 2026) report the premium is below India's own "
        f"historical norm, which softens but does not erase the headwind. Gate does not "
        f"trip severe. Caps confidence without breaking the thesis."
    )
    st.caption(f"Limitation: {val['acknowledged_limitation']}")
    st.caption(
        f"Sources: {inda_pe['source']} (as of {inda_pe['as_of']}); "
        f"{msci_pe['source']} (as of {msci_pe['as_of']})"
    )

    st.divider()

    # ── Indicator 2: Demographics (Structural) ────────────────────────────────
    dem = get_indicator(data, "demographics")
    indicator_header(dem["name"], dem["role"], dem["score"], dem["score_display"], SCORE_COLORS)

    old_ind = get_dp(dem, "old_age_dep_india")
    old_chn = get_dp(dem, "old_age_dep_china")
    tot_ind = get_dp(dem, "total_dep_india")
    tot_chn = get_dp(dem, "total_dep_china")
    flfp    = get_dp(dem, "female_lfp_india")
    tlfp    = get_dp(dem, "total_lfp_india")

    old_gap = old_chn["value"] - old_ind["value"]

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Old-age dependency",
        f"India {old_ind['value']} vs China {old_chn['value']}",
        delta=f"Less than half China's ratio (favorable)",
        delta_color="off",
        help=f"Source: {old_ind['source']} | As of {old_ind['as_of']}",
    )
    c2.metric(
        "Total age dependency",
        f"India {tot_ind['value']} vs China {tot_chn['value']}",
        help=f"Source: {tot_ind['source']} | As of {tot_ind['as_of']}",
    )
    c3.metric(
        "Female LFP: India",
        f"{flfp['value']}%",
        delta=f"Total LFP: {tlfp['value']}%",
        delta_color="off",
        help=f"Source: {flfp['source']} | As of {flfp['as_of']}",
    )

    st.markdown(
        f"**Rationale:** Old-age dependency of {old_ind['value']} vs China's "
        f"{old_chn['value']} is a genuine, durable, decade-plus structural advantage: "
        f"less than half China's ratio. India's working-age share continues rising into "
        f"the 2040s as China's falls. Female LFP at {flfp['value']}% means the "
        f"dividend is only partially realized: both a current shortfall and remaining "
        f"upside if participation rises."
    )
    st.caption(
        f"Source: {old_ind['source']} | As of {old_ind['as_of']} | "
        f"Refreshable: {'Yes' if old_ind.get('refreshable') else 'No'}"
    )

    st.divider()

    # ── Indicator 3: Governance (Structural) ──────────────────────────────────
    gov = get_indicator(data, "governance")
    indicator_header(gov["name"], gov["role"], gov["score"], gov["score_display"], SCORE_COLORS)

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

    styled_wgi = _apply_style(wgi_df.style, color_wgi_cell)
    st.dataframe(styled_wgi, use_container_width=True)
    years_str = ", ".join(str(y) for y in gov["wgi_table"]["years"])
    st.caption(
        f"{gov['wgi_table']['scale']}. "
        f"Years shown: {years_str}. "
        f"Green = above zero (above global average); red = below zero."
    )
    st.markdown(
        f"**Rationale:** {gov['score_summary']} "
        f"Against a broader EM peer set, India likely sits in the middle of the pack. "
        f"The democratic-institution edge (Voice and Accountability) is a real "
        f"differentiator from China but has compressed and turned slightly negative by 2023."
    )
    wgi_src = get_dp(gov, "wgi_source")
    st.caption(
        f"Source: {wgi_src.get('source', 'World Bank WGI 2025')} | "
        f"As of {wgi_src.get('as_of', '2026-07-02')} | "
        f"Refreshable: {'Yes' if wgi_src.get('refreshable') else 'No'}"
    )

    st.divider()

    # ── Indicator 4: Digital Financial Adoption (Structural) ──────────────────
    dig = get_indicator(data, "digital_adoption")
    indicator_header(dig["name"], dig["role"], dig["score"], dig["score_display"], SCORE_COLORS)

    ind_any  = get_dp(dig, "india_any_dig_2024")
    peer_any = get_dp(dig, "peer_median_any_dig_2024")
    ind_mch  = get_dp(dig, "india_merchant_2024")
    peer_mch = get_dp(dig, "peer_median_merchant_2024")

    gap_any = peer_any["value"] - ind_any["value"]
    gap_mch = peer_mch["value"] - ind_mch["value"]

    c1, c2 = st.columns(2)
    c1.metric(
        "Any digital payment: India vs EM peer median",
        f"{ind_any['value']}% vs {peer_any['value']}%",
        delta=f"India trails by {gap_any}pp",
        delta_color="inverse",
        help=f"Source: {ind_any['source']}",
    )
    c2.metric(
        "Digital merchant payment: India vs EM peer median",
        f"{ind_mch['value']}% vs {peer_mch['value']}%",
        delta=f"India trails by {gap_mch}pp",
        delta_color="inverse",
        help=f"Source: {ind_mch['source']}",
    )

    trend = dig["india_trend_any_digital"]
    trend_str = " → ".join(f"{t['value']}% ({t['year']})" for t in trend)
    st.markdown(f"**India adoption trend (any digital payment):** {trend_str}")

    with st.expander("EM peer comparison table, 2024 (World Bank Findex)"):
        peer_df = digital_peer_table(data)
        st.dataframe(peer_df, use_container_width=True)

    st.markdown(
        f"**Rationale:** India lags the EM peer median by {gap_any}pp on any digital "
        f"payment and {gap_mch}pp on merchant payments. Adoption is rising fast from a "
        f"low base ({trend[0]['value']}% in {trend[0]['year']} to "
        f"{trend[-1]['value']}% in {trend[-1]['year']}). "
        f"A convergence-from-behind story, not established leadership."
    )
    st.caption(dig["honest_note"])
    st.caption(
        f"Source: World Bank Global Findex 2024 (indicators g20.any, merchant.pay). "
        f"Peer set: China, Indonesia, Brazil, Mexico, South Africa, Turkey, "
        f"Thailand, Malaysia, Philippines. As of: {ind_any['as_of']}."
    )

    st.divider()

    # ── Indicator 5: External Macro Vulnerability (Gating) ────────────────────
    ext = get_indicator(data, "external_macro")
    indicator_header(ext["name"], ext["role"], ext["score"], ext["score_display"], SCORE_COLORS)

    inr_drag  = get_dp(ext, "inr_depreciation_rate")
    oil_share = get_dp(ext, "oil_import_share")
    oil_dep   = get_dp(ext, "oil_import_dependency")
    inr_corr  = get_dp(ext, "inda_inr_correlation")

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "INR depreciation vs USD",
        inr_drag["value"],
        help=f"Source: {inr_drag['source']} | As of {inr_drag['as_of']}",
    )
    c2.metric(
        "Oil share of import bill",
        oil_share["value"].replace("approximately ", "~"),
        help=f"Source: {oil_share['source']} | As of {oil_share['as_of']}",
    )
    c3.metric(
        "INDA vs INR rolling correlation (Layer 1)",
        inr_corr["value"].replace("approximately ", "~"),
        help=f"Source: {inr_corr['source']}",
    )

    st.markdown(
        "**Rationale:** INR depreciation is a persistent mild drag on USD-investor "
        "returns, but Layer 1 found roughly zero correlation between INDA and the rupee "
        "over the analysis window, meaning the drag has been absorbed historically. "
        "Oil at ~25% of imports is the shock amplifier: dormant at normal "
        "prices, dangerous in a major spike. Combined, this is a real but soft gating "
        "constraint that does not trip severe."
    )
    st.caption(ext["note"])
    st.caption(
        f"Sources: INR forecast from {inr_drag['source']} (as of {inr_drag['as_of']}); "
        f"oil exposure from {oil_share['source']}; "
        f"correlation from {inr_corr['source']}."
    )

    st.divider()

    # ── Scoring Summary ───────────────────────────────────────────────────────
    st.subheader("Scoring Summary")

    score_df = scoring_summary(data)

    _score_key_map = {
        "Neutral-to-Caution":                      "neutral_to_caution",
        "Favorable":                                "favorable",
        "Neutral / Lean-Negative":                  "neutral_lean_negative",
        "Neutral (negative level, positive trend)": "neutral",
        "At-Risk (mild-to-conditional)":            "at_risk_mild",
    }

    def style_score_cell(v):
        key   = _score_key_map.get(str(v), "neutral")
        color = SCORE_COLORS.get(key, "#8FA3B1")
        return f"background-color:{color}28;color:{color};font-weight:600"

    styled_scores = _apply_style(score_df.style, style_score_cell, subset=["score"])
    st.dataframe(styled_scores, use_container_width=True, hide_index=True)

    st.divider()

    # ── Confidence Ladder and Final Verdict ───────────────────────────────────
    st.subheader("Confidence Ladder and Final Verdict")

    rung = ladder["rung"]
    ladder_rungs = [
        (1, "Durable and reasonably priced"),
        (2, "Durable but priced"),
        (3, "Structurally attractive, but priced and macro-sensitive"),
        (4, "Not durable"),
    ]

    for r_num, r_label in ladder_rungs:
        active = r_num == rung
        bg     = "#1e3a5c" if active else "#111827"
        border = "2px solid #5B8DB8" if active else "1px solid #2a3a4a"
        weight = "700" if active else "400"
        arrow  = "   << CURRENT VERDICT" if active else ""
        st.markdown(
            f'<div style="background:{bg};border:{border};border-radius:6px;'
            f'padding:10px 18px;margin:3px 0;font-weight:{weight};">'
            f'<span style="opacity:0.55;">Rung {r_num}:</span> {r_label}{arrow}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("&nbsp;", unsafe_allow_html=True)

    # Rung verdict card
    rung_label = f"RUNG {rung}: {ladder['label'].upper()}"
    st.markdown(
        f'<div style="background:#1e3a5c;border:2px solid #5B8DB8;color:#a8c8e8;'
        f'padding:16px 28px;border-radius:8px;font-size:1.3rem;font-weight:700;'
        f'text-align:center;letter-spacing:0.04em;">{rung_label}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("&nbsp;", unsafe_allow_html=True)

    st.markdown(f"**Derivation:** {ladder['derivation']}")
    st.markdown(f"**Verdict:** {ladder['verdict_statement']}")

    st.divider()

    st.subheader("Direct Answer to the Thesis Question")
    st.info(ladder["thesis_answer"])
    st.markdown(f"**Analyst's journey:** {ladder['analysts_journey']}")

    st.divider()
    st.caption(
        "Layer 2 framework: five indicators, pre-declared thresholds, gated confidence "
        "ladder. Design notes in scratch/layer2_framework.md (not committed). "
        "Data sourced from data/layer2_indicators.json (pinned mid-2026 dataset)."
    )
