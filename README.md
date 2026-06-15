# Thesis #16: Emerging Markets: India's Decade to Shine?

A quantitative and qualitative framework to test whether India can outperform broad EM and China in USD terms, or whether the India "decade" narrative is overhyped and already priced in.

---

## Thesis Statement

I am skeptical: I believe China remains the dominant / more advanced EM, and India's "decade" narrative may be overhyped or already priced in.

The primary question is whether India can deliver measurably better risk-adjusted USD returns than EM (EEM) and China (FXI/MCHI) over 2013–present, while any valuation premium is justified by superior fundamentals.

What would prove this wrong: If India shows measurably better risk-adjusted USD returns vs EM and China over the 2013–present period, AND any current valuation premium is justified by superior fundamentals.

---

## Project Structure

```
india-em-thesis/
├── data/
│   ├── raw/          # Unmodified source data (yfinance pulls, World Bank CSVs, etc.)
│   └── processed/    # Cleaned, merged, and transformed datasets
├── notebooks/        # Exploratory and presentation notebooks
├── src/
│   ├── data/         # Data ingestion and cleaning modules
│   ├── analysis/     # Modelling, stress testing, and statistical work
│   └── viz/          # Chart and figure generation
├── outputs/
│   ├── figures/      # Saved charts and plots
│   └── reports/      # Rendered summaries and tables
└── tests/            # Unit tests for src modules
```

---

## Research Pillars

### Bull Case (Tailwinds)
| Pillar | Key Metrics |
|---|---|
| Demographics | Working-age population share, dependency ratio vs. China |
| Digital Infrastructure | UPI transaction volume, internet penetration, Aadhaar coverage |
| Geopolitical Tailwinds | FDI inflows, PLI scheme capex, supply chain diversification proxies |
| Macro Fundamentals | GDP growth, current account trajectory, forex reserves |

### Bear Case (Stress Tests)
| Risk | Key Metrics |
|---|---|
| Governance & Rule of Law | World Bank WGI scores, ease of doing business rank, contract enforcement |
| Currency Volatility | INR/USD historical vol, real effective exchange rate, drawdown analysis |
| Valuation | Nifty P/E vs. EM peers, CAPE, EV/EBITDA sector comps |
| Liquidity & Contagion | Correlation with broad EM selloffs, FII flow reversals |

---

## Verdict Framework

The thesis is **confirmed** if, after stress-testing:
1.  Expected 10-year USD-adjusted return exceeds EM ex-India benchmark by ≥2% annualised.

   (My rationale: India trades at a ~20-30% valuation premium over broad EM; 2% annual 
   outperformance is the approximate return needed to justify that premium over a 
   10-year horizon.) 

2. Max drawdown under adverse currency + governance shock does not exceed peer EM average.
3. Valuation premium is justified by superior earnings growth trajectory (PEG-adjusted).

---

## Planned lower-tier analysis (due June 22)
1. Cumulative USD return chart: INDA vs EEM vs FXI/MCHI
2. Volatility and max drawdown comparison across all three
3. Correlation analysis: India returns vs EM returns and vs USD/INR
4. Current valuation snapshot (P/E, P/B) for INDA vs EEM vs FXI
5. Written verdict framed as supported / partially supported / not supported

> Note: This README and `DECISIONS.md` were refined through review by two AI models (Claude and GPT) before any code was written, as part of the documented decision process.

---

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Data Sources

- **Market data**: `yfinance` (Nifty 50, sectoral indices, EM ETFs)
- **Macro data**: World Bank API, IMF WEO, RBI publications
- **Governance data**: World Bank Worldwide Governance Indicators (WGI)
- **Demographics**: UN Population Division, Census of India
- **Digital infra**: NPCI (UPI stats), TRAI (telecom data), MeitY publications
