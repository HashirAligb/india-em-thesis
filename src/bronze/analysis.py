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
    metrics = compute_risk_metrics(prices)

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

    # Add a Role column so the table is self-explanatory
    roles = {"INDA": "India proxy", "EEM": "Broad EM benchmark", "FXI": "China benchmark"}
    display["Role"] = display["Ticker"].map(roles)

    print("\n── SUMMARY TABLE ──────────────────────────────────────────────")
    print(display.to_string(index=False))
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

    print("\nDone. Review charts in outputs/figures/ before committing.")


if __name__ == "__main__":
    main()
