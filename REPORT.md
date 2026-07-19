# Thesis #16 — Emerging Markets: India's Decade to Shine?

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

| Ticker | Cumulative Return | CAGR | Ann. Vol | Max Drawdown | Sharpe-style | Role |
| --- | --- | --- | --- | --- | --- | --- |
| INDA | 112.3% | 5.74% | 21.60% | -45.1% | 0.266 | India proxy |
| EM ex-India * | 94.5% | 5.06% | 21.43% | -45.5% | 0.236 | EM ex-India benchmark (approx., fixed ~15% wt) |
| FXI | 5.7% | 0.41% | 26.87% | -60.8% | 0.015 | China benchmark |

---

## Verdict

### Layer 1 — Historical (what the data proves)

**SUPPORTED**

INDA beat EM ex-India on cumulative return (112.3% vs 94.5%) and beat FXI (112.3% vs 5.7%). On the Sharpe-style ratio, INDA beat EM ex-India (0.266 vs 0.236) and beat FXI (0.266 vs 0.015). By the pre-declared rule, this is **SUPPORTED**.

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
