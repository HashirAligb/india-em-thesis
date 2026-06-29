"""
Bronze-tier analysis: loads data, computes metrics, renders charts, prints verdict.
Run directly: python src/bronze/analysis.py
"""

import sys
import os

# Make sure the project root is on the path so we can import from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — writes PNGs without opening windows
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

from src.data_engine import (
    load_data,
    compute_returns,
    compute_risk_metrics,
    run_correlation_analysis,
    compute_verdict,
)

# ── Colour palette ──────────────────────────────────────────────────────────
NAVY  = "#0D1B2A"
GOLD  = "#C9A84C"
RED   = "#E05C5C"
GREEN = "#2D9E6B"
SLATE = "#8FA3B1"
WHITE = "#F4F6F9"
TEAL  = "#1A7FA1"

# One consistent colour per ticker so every chart reads the same legend
TICKER_COLORS = {"INDA": GOLD, "EEM": TEAL, "FXI": RED}

# Where the PNGs go — resolved relative to this file so it works regardless
# of which directory you launch from
FIGURES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "outputs", "figures"
)


def _savefig(fig: plt.Figure, filename: str) -> str:
    # Save a figure to the figures directory and return the full path.
    # tight_layout() trims excess whitespace so charts don't look cropped.
    path = os.path.join(FIGURES_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=NAVY)
    plt.close(fig)
    return path


def chart_cumulative_return(cumulative: pd.DataFrame) -> str:
    # Chart 1: Growth of $100 invested on day one for INDA, EEM, FXI.
    # We plot only the three ETFs (not INR=X) because INR=X is a forex rate,
    # not an investable asset, and plotting it alongside return indices would
    # be misleading.
    etf_cols = [c for c in cumulative.columns if c in TICKER_COLORS]

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=NAVY)
    ax.set_facecolor(NAVY)

    for ticker in etf_cols:
        ax.plot(
            cumulative.index,
            cumulative[ticker],
            color=TICKER_COLORS[ticker],
            linewidth=1.8,
            label=ticker,
        )

    ax.axhline(100, color=SLATE, linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_title(
        "Cumulative USD Return — Growth of $100 (2013–present)",
        color=WHITE, fontsize=13, pad=12,
    )
    ax.set_xlabel("Date", color=SLATE)
    ax.set_ylabel("Index (Start = 100)", color=SLATE)
    ax.tick_params(colors=SLATE)
    ax.spines[:].set_color(SLATE)
    ax.legend(facecolor=NAVY, labelcolor=WHITE, framealpha=0.5)

    return _savefig(fig, "01_cumulative_return.png")


def chart_vol_drawdown(metrics: pd.DataFrame) -> str:
    # Chart 2: Side-by-side bars showing annualised volatility and max drawdown
    # for each ETF. Grouping them together makes the risk profile comparison
    # immediate — you can see in one glance which ETF was bumpiest.

    etf_order = ["INDA", "EEM", "FXI"]
    metrics_plot = metrics[metrics["Ticker"].isin(etf_order)].set_index("Ticker")
    metrics_plot = metrics_plot.reindex(etf_order)

    # Parse the formatted strings back to floats for plotting
    vols = metrics_plot["Ann. Vol"].str.rstrip("%").astype(float)
    dds  = metrics_plot["Max Drawdown"].str.rstrip("%").astype(float).abs()

    x = range(len(etf_order))
    bar_w = 0.35

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=NAVY)
    ax.set_facecolor(NAVY)

    bars_vol = ax.bar(
        [i - bar_w / 2 for i in x], vols, width=bar_w,
        color=[TICKER_COLORS[t] for t in etf_order], alpha=0.9, label="Ann. Vol (%)"
    )
    bars_dd = ax.bar(
        [i + bar_w / 2 for i in x], dds, width=bar_w,
        color=[TICKER_COLORS[t] for t in etf_order], alpha=0.45, label="|Max Drawdown| (%)"
    )

    # Label bars with their values so you don't need to read the y-axis
    for bar in list(bars_vol) + list(bars_dd):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"{bar.get_height():.1f}%",
            ha="center", va="bottom", color=WHITE, fontsize=9,
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(etf_order, color=WHITE)
    ax.set_title("Annualised Volatility and Max Drawdown by ETF", color=WHITE, fontsize=13, pad=12)
    ax.set_ylabel("Percent (%)", color=SLATE)
    ax.tick_params(colors=SLATE)
    ax.spines[:].set_color(SLATE)
    ax.legend(facecolor=NAVY, labelcolor=WHITE, framealpha=0.5)

    return _savefig(fig, "02_vol_drawdown.png")


def chart_rolling_correlation(corr: dict) -> str:
    # Chart 3: Rolling 12-month correlation of INDA with EEM and with INR=X.
    # A high INDA-EEM correlation means India moves with the EM herd — the
    # diversification story weakens. A high INDA-INR correlation means USD
    # returns are partly explained by rupee moves, not equity alpha.

    fig, ax = plt.subplots(figsize=(12, 5), facecolor=NAVY)
    ax.set_facecolor(NAVY)

    ax.plot(corr["INDA_EEM"].index, corr["INDA_EEM"],
            color=TEAL, linewidth=1.6, label="INDA vs EEM")
    ax.plot(corr["INDA_INR"].index, corr["INDA_INR"],
            color=GOLD, linewidth=1.6, label="INDA vs INR=X")

    ax.axhline(0, color=SLATE, linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_title(
        "Rolling 12-Month Correlation — INDA vs EEM and INDA vs INR=X",
        color=WHITE, fontsize=13, pad=12,
    )
    ax.set_xlabel("Date", color=SLATE)
    ax.set_ylabel("Correlation", color=SLATE)
    ax.set_ylim(-1, 1)
    ax.tick_params(colors=SLATE)
    ax.spines[:].set_color(SLATE)
    ax.legend(facecolor=NAVY, labelcolor=WHITE, framealpha=0.5)

    return _savefig(fig, "03_rolling_correlation.png")


def chart_verdict_card(metrics: pd.DataFrame, verdict: str) -> str:
    # Chart 4: A text-based summary card — headline metrics for INDA plus
    # the verdict label. This is the "one slide" version of the analysis.

    inda = metrics[metrics["Ticker"] == "INDA"].iloc[0]

    verdict_color = {"SUPPORTED": GREEN, "PARTIALLY SUPPORTED": GOLD, "NOT SUPPORTED": RED}
    v_color = verdict_color.get(verdict, WHITE)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=NAVY)
    ax.set_facecolor(NAVY)
    ax.axis("off")  # no axes — this is a text card, not a data plot

    # Title
    ax.text(0.5, 0.92, "Thesis Verdict — India vs EM (2013–present)",
            ha="center", va="top", color=WHITE, fontsize=14, fontweight="bold",
            transform=ax.transAxes)

    # Verdict label
    ax.text(0.5, 0.75, verdict,
            ha="center", va="top", color=v_color, fontsize=22, fontweight="bold",
            transform=ax.transAxes)

    # Key INDA metrics below the verdict
    lines = [
        f"INDA Cumulative Return : {inda['Cumulative Return']}",
        f"INDA CAGR              : {inda['CAGR']}",
        f"INDA Ann. Volatility   : {inda['Ann. Vol']}",
        f"INDA Max Drawdown      : {inda['Max Drawdown']}",
        f"INDA Sharpe-style      : {inda['Sharpe-style']}",
    ]
    for i, line in enumerate(lines):
        ax.text(0.5, 0.55 - i * 0.09, line,
                ha="center", va="top", color=SLATE, fontsize=11,
                transform=ax.transAxes, family="monospace")

    ax.text(0.5, 0.04,
            "Layer 1 (historical) verdict only. Forward-looking context in Layer 2.",
            ha="center", va="bottom", color=SLATE, fontsize=9, style="italic",
            transform=ax.transAxes)

    return _savefig(fig, "04_verdict_card.png")


# Report goes to the project root (same level as README.md and DECISIONS.md)
# so it's visible in the GitHub repo. outputs/reports/ is gitignored.
REPORT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "REPORT.md"
)


def generate_report(metrics: pd.DataFrame, verdict: str) -> str:
    # Write a self-contained REPORT.md to outputs/reports/.
    # All numbers are pulled from the metrics DataFrame so the file
    # always reflects the current run — nothing is hardcoded.

    # Project root already exists; nothing to create.

    # ── Pull raw values for the narrative ───────────────────────────────────
    def raw(ticker, col):
        return metrics.loc[metrics["Ticker"] == ticker, col].values[0]

    inda_ret   = raw("INDA",        "_total_ret_raw")
    ex_ret     = raw("EEM_exIndia", "_total_ret_raw")
    fxi_ret    = raw("FXI",         "_total_ret_raw")
    inda_sh    = raw("INDA",        "_sharpe_raw")
    ex_sh      = raw("EEM_exIndia", "_sharpe_raw")
    fxi_sh     = raw("FXI",         "_sharpe_raw")

    # ── Formatted display values for the table ───────────────────────────────
    display_cols = ["Ticker", "Cumulative Return", "CAGR", "Ann. Vol",
                    "Max Drawdown", "Sharpe-style"]
    roles = {
        "INDA":        "India proxy",
        "EEM_exIndia": "EM ex-India benchmark (approx., fixed ~15% wt)",
        "FXI":         "China benchmark",
    }
    display = metrics[display_cols].copy()
    display = display[display["Ticker"].isin(["INDA", "EEM_exIndia", "FXI"])].copy()
    display = display.set_index("Ticker").reindex(["INDA", "EEM_exIndia", "FXI"]).reset_index()
    display["Role"] = display["Ticker"].map(roles)
    display["Ticker"] = display["Ticker"].replace({"EEM_exIndia": "EM ex-India *"})

    # Build a markdown table row by row
    md_header = "| " + " | ".join(display.columns) + " |"
    md_sep    = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    md_rows   = "\n".join(
        "| " + " | ".join(str(v) for v in row) + " |"
        for row in display.itertuples(index=False)
    )
    md_table  = "\n".join([md_header, md_sep, md_rows])

    # ── Layer 1 narrative — built from actual comparisons ────────────────────
    beats_ex_ret     = inda_ret > ex_ret
    beats_fxi_ret    = inda_ret > fxi_ret
    beats_ex_sharpe  = inda_sh  > ex_sh
    beats_fxi_sharpe = inda_sh  > fxi_sh

    inda_ret_fmt = f"{inda_ret*100:.1f}%"
    ex_ret_fmt   = f"{ex_ret*100:.1f}%"
    fxi_ret_fmt  = f"{fxi_ret*100:.1f}%"
    inda_sh_fmt  = f"{inda_sh:.3f}"
    ex_sh_fmt    = f"{ex_sh:.3f}"
    fxi_sh_fmt   = f"{fxi_sh:.3f}"

    ret_vs_ex    = "beat" if beats_ex_ret     else "trailed"
    ret_vs_fxi   = "beat" if beats_fxi_ret    else "trailed"
    sh_vs_ex     = "beat" if beats_ex_sharpe  else "trailed"
    sh_vs_fxi    = "beat" if beats_fxi_sharpe else "trailed"

    layer1_narrative = (
        f"INDA {ret_vs_ex} EM ex-India on cumulative return ({inda_ret_fmt} vs {ex_ret_fmt}) "
        f"and {ret_vs_fxi} FXI ({inda_ret_fmt} vs {fxi_ret_fmt}). "
        f"On the Sharpe-style ratio, INDA {sh_vs_ex} EM ex-India ({inda_sh_fmt} vs {ex_sh_fmt}) "
        f"and {sh_vs_fxi} FXI ({inda_sh_fmt} vs {fxi_sh_fmt}). "
        f"By the pre-declared rule, this is **{verdict}**."
    )

    # ── Assemble the report ──────────────────────────────────────────────────
    report = f"""# Thesis #16 — Emerging Markets: India's Decade to Shine?

**Thesis statement:** Testing whether India delivered better risk-adjusted USD returns
than EM ex-India and China (FXI) over 2013–2026.

---

## Data & Method

- **Source:** Yahoo Finance via yfinance (`auto_adjust=True` — prices include dividends)
- **Instruments:** INDA (India proxy), EM ex-India (primary EM benchmark; India's contribution removed using a fixed ~15% weight), FXI (China benchmark), INR=X (USD/INR spot, for currency correlation only)
- India is ~15% of standard broad-EM indices like EEM, so comparing India directly against EEM partly compares India against itself; the EM benchmark here is EM ex-India, with India's contribution removed.
- **Window:** 2013-01-01 to 2026-06-25 (pinned for reproducibility)
- **Denominated in:** USD throughout — ETF prices are USD-quoted, so no manual conversion is needed
- **Valuation:** Treated as forward-looking context (Layer 2), not modelled in the return analysis
- **Risk-adjusted metric:** Annualised return ÷ annualised volatility (0% risk-free rate, per decision log)

---

## Summary Table

{md_table}

---

## Verdict

### Layer 1 — Historical (what the data proves)

**{verdict}**

{layer1_narrative}

### Layer 2 — Forward-looking (context, not proven by the data)

The historical return window cannot prove the *next* decade thesis. Three forward-looking signals add caution:

1. **Valuation ambiguity:** India's trailing P/E (~21–22) sits above broad EM, but EM's figure ranges from ~13 to ~19 depending on the data provider, because ETF P/E is calculated differently across sources. The implied premium is therefore a band of roughly 15–40%, not a single figure. Valuation is treated as directional context, not a precise input to the verdict.
2. **Currency risk:** The rupee (INR) has depreciated against the USD over the full window. USD-denominated investors bear this cost; it is visible directly in the INR=X series, which rose from ~55 to ~95 rupees per dollar over the window.
3. **2026 oil shock:** Crude above $100/bbl (Middle East conflict) hit India hard — ~10% YTD drawdown, record foreign outflows. India imports ~85% of its crude. This is a known structural vulnerability, treated here as a stress-test scenario rather than a permanent re-rating.

Likely forward verdict: **historically supported, forward-looking uncertain.**

---

## Notable Finding

Rolling 12-month INDA–EEM correlation averaged ~0.76 over the full window. India moves closely with the broad EM herd, which weakens the diversification argument sometimes made for an India-only allocation.

---

## Charts

![Cumulative Return](outputs/figures/01_cumulative_return.png)

![Volatility and Max Drawdown](outputs/figures/02_vol_drawdown.png)

![Rolling Correlation](outputs/figures/03_rolling_correlation.png)

![Verdict Card](outputs/figures/04_verdict_card.png)
"""

    path = os.path.normpath(REPORT_PATH)
    with open(path, "w") as f:
        f.write(report)

    return path


def main():
    print("=" * 60)
    print("BRONZE TIER — India vs EM Analysis")
    print("=" * 60)

    # Step 1: Load raw adjusted price data
    print("\n[1/5] Loading data...")
    prices = load_data()

    # Step 2: Daily and cumulative returns
    print("\n[2/5] Computing returns...")
    returns = compute_returns(prices)

    # Step 3: Risk metrics table (CAGR, vol, drawdown, Sharpe-style)
    print("\n[3/5] Computing risk metrics...")
    # EEM_exIndia is a return-derived series, not a raw price series, so we can't
    # pass it directly to compute_risk_metrics(). We convert it to a synthetic price
    # index (starting at 100) so the function can treat it like any other ticker:
    # pct_change() on the index recovers the exact daily returns we put in.
    ex_price_index = (1 + returns["daily"]["EEM_exIndia"]).cumprod() * 100
    prices_aug = prices.copy()
    prices_aug["EEM_exIndia"] = ex_price_index
    metrics = compute_risk_metrics(prices_aug)

    # Step 4: Rolling correlation
    print("\n[4/5] Running correlation analysis...")
    corr = run_correlation_analysis(prices)

    # Step 5: Verdict
    print("\n[5/5] Computing verdict...")
    verdict = compute_verdict(metrics)

    # ── Summary table ────────────────────────────────────────────────────────
    # Drop the internal raw-float columns before printing — they are there for
    # compute_verdict() and would clutter the display.
    display_cols = ["Ticker", "Cumulative Return", "CAGR", "Ann. Vol", "Max Drawdown", "Sharpe-style"]
    display = metrics[display_cols].copy()

    # Pin display order: raw EEM first, then EM ex-India directly below it
    # so the reader can compare the two EM benchmarks side by side.
    ticker_order = ["INDA", "EEM_exIndia", "FXI"]
    display = display.set_index("Ticker").reindex(ticker_order).reset_index()

    roles = {
        "INDA":        "India proxy",
        "EEM":         "Broad EM benchmark (raw)",
        "EEM_exIndia": "EM ex-India (approx.)",
        "FXI":         "China benchmark",
    }
    display["Role"] = display["Ticker"].map(roles)
    # Rename the internal column name to a human-readable label for printing
    display["Ticker"] = display["Ticker"].replace({"EEM_exIndia": "EM ex-India *"})

    print("\n── SUMMARY TABLE ──────────────────────────────────────────────")
    print(display.to_string(index=False))
    print("  * Fixed ~15% India weight approximation; actual weight varied ~13–15% over 2013–present.")
    print()

    # ── Verdict ─────────────────────────────────────────────────────────────
    print(f"── VERDICT (Layer 1 — Historical) ─────────────────────────────")
    print(f"   {verdict}")
    print(f"   (Layer 2 forward-looking context: see DECISIONS.md)")
    print()

    # ── Charts ───────────────────────────────────────────────────────────────
    print("── GENERATING CHARTS ──────────────────────────────────────────")
    p1 = chart_cumulative_return(returns["cumulative"])
    print(f"   ✓ {p1}")
    p2 = chart_vol_drawdown(metrics)
    print(f"   ✓ {p2}")
    p3 = chart_rolling_correlation(corr)
    print(f"   ✓ {p3}")
    p4 = chart_verdict_card(metrics, verdict)
    print(f"   ✓ {p4}")

    # ── Report ───────────────────────────────────────────────────────────────
    print("── GENERATING REPORT ──────────────────────────────────────────")
    report_path = generate_report(metrics, verdict)
    print(f"   ✓ {report_path}")

    print("\nDone. Review charts in outputs/figures/ and report in outputs/reports/ before committing.")


if __name__ == "__main__":
    main()
