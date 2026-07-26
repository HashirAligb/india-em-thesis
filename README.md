# Thesis #16: Emerging Markets — India's Decade to Shine?

A two-layer quantitative framework testing whether India can outperform broad EM
and China in USD terms, or whether the "India decade" narrative is overhyped and
already priced in.

**Thesis stance:** Skeptical. China remains the dominant EM; India's decade narrative
may be overhyped or already priced in.

---

## How It Works

The analysis runs in two sequential layers.

### Layer 1 — Historical Performance (2013–2026)

Compares INDA (India ETF), EM ex-India (EEM with India's contribution removed),
and FXI (China ETF) across cumulative return, CAGR, annualised volatility,
max drawdown, and a Sharpe-style ratio (annualised return / annualised vol,
0% risk-free rate). Also tracks the rolling 12-month correlation between INDA
and the EM ex-India benchmark, and between INDA and the USD/INR spot rate.

All returns are in USD, dividend-adjusted. The EM ex-India benchmark removes India's
weight using a fixed 15% approximation: `r_ex = (r_eem − 0.15 × r_inda) / (1 − 0.15)`.

**Layer 1 verdict rule:** SUPPORTED if INDA beats both benchmarks on cumulative
return AND Sharpe-style ratio; PARTIALLY SUPPORTED if it beats on one; NOT SUPPORTED
otherwise.

### Layer 2 — Forward Framework (mid-2026 snapshot)

Five indicators scored against pre-declared thresholds on a four-rung confidence
ladder. Thresholds were fixed before scoring began and are not tuned to the data.

| Indicator | Role | Current score |
|---|---|---|
| Valuation (P/E premium) | Gating | Neutral to Caution (23.9% premium) |
| Demographics | Structural | Favorable |
| Governance (WGI) | Structural | Neutral-Lean-Negative |
| Digital Adoption (Findex) | Structural | Neutral |
| External Macro (INR + oil) | Gating (soft) | At-risk mild |

**Ladder verdict rule:**
1. If any gating indicator trips the severe threshold → Rung 4 (Not durable).
2. Else if any structural indicator is not Favorable → Rung 3 (Structurally
   attractive, but priced and macro-sensitive).
3. Else if valuation is Favorable or Neutral → Rung 1 (Durable and reasonably
   priced). Otherwise → Rung 2 (Durable but priced).

**Current verdict: Rung 3.** Governance and Digital Adoption are not Favorable;
no severe gate is tripped.

### AI Audit Layer (Assumption Auditor)

A Python module (`src/assumption_audit.py`) stress-tests the Rung 3 verdict:
it identifies upgrade blockers, computes the nearest downgrade boundary (the
valuation premium must reach the declared 40% severe gate — currently 16.1pp
away), and checks stability across three threshold profiles.

An LLM pipeline (`src/verdict_agents.py`) then narrates the audit result using
Google Gemini. The architecture enforces a strict separation: Python computes
every number, the first Gemini call explains the Python output in plain English,
a Python fact-validator checks that the explanation contains no invented numbers
or imminence language, and a second Gemini call checks for soft overreach.
If any LLM call fails, the deterministic verdict is unchanged.

---

## Architecture

```
src/
  bronze/
    analysis.py       # Layer 1: downloads data, computes metrics, generates charts
  data_engine.py      # Downloads and caches price data via yfinance
  layer2.py           # Layer 2: scoring functions and compute_ladder_verdict()
  assumption_audit.py # Stress-tests the verdict; produces AuditResult
  verdict_agents.py   # Gemini agent pipeline (explain -> validate -> check overreach)
  wb_refresh.py       # Live World Bank API refresh (WGI, Findex)

data/
  layer1_summary.csv          # Pinned Layer 1 metrics
  layer1_rolling_corr.csv     # Pinned rolling correlation series
  layer2_indicators.json      # All Layer 2 indicator values and metadata

outputs/figures/              # Four static chart PNGs (auto-generated)

app.py                        # Streamlit app (display only, no compute logic)
DECISIONS.md                  # Methodology log: what was tried, changed, and why
tests/
  test_layer2.py              # pytest suite for Layer 2 scoring functions
```

The app contains no scoring logic. All computations happen in `src/`. The
Streamlit layer reads results and renders them.

---

## Setup

```bash
git clone https://github.com/HashirAligb/india-em-thesis.git
cd india-em-thesis
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

For the AI audit layer, create a `.env` file with your Google AI Studio key:

```
GEMINI_API_KEY=your_key_here
```

---

## Running

```bash
# Streamlit app (main interface)
streamlit run app.py

# Regenerate Layer 1 charts and metrics (downloads live data)
python src/bronze/analysis.py

# Verify Layer 2 defaults reproduce Rung 3
python src/layer2.py

# Run assumption audit smoke test
python src/assumption_audit.py

# Run agent pipeline smoke test (requires GEMINI_API_KEY in .env)
python src/verdict_agents.py

# Run tests
pytest tests/
```

---

## Data Sources

| Data | Source | Refresh method |
|---|---|---|
| ETF prices (INDA, EEM, FXI, INR=X) | Yahoo Finance via yfinance | `python src/bronze/analysis.py` |
| WGI governance scores | World Bank API (source=3, .EST codes) | Sidebar refresh button |
| Digital adoption (Findex) | World Bank Findex API | Sidebar refresh button |
| INDA P/E, MSCI EM P/E | iShares / MSCI factsheets | Manual (pinned mid-2026) |
| INR depreciation rate, oil share | Analyst consensus (MUFG/Reuters) | Manual (pinned mid-2026) |

The app displays whether live or pinned data is active. Layer 2 scoring uses
pinned mid-2026 data by default for reproducibility.

---

## Verification

`src/layer2.py` includes `_verify_defaults()`, which asserts that the five
scoring functions with pre-declared defaults reproduce the locked Rung 3 verdict
exactly. `pytest tests/` runs the same assertions as a proper test suite.

---

## Key Decisions and Failures

See `DECISIONS.md` for the full methodology log, including:
- Benchmark contamination fix (original code compared INDA against raw EEM,
  which includes ~15% India — effectively India vs. itself)
- Currency and oil merged into one indicator (separating them double-counted
  the same risk)
- Risk-adjusted metric added to Layer 1 verdict after red-team (cumulative
  return alone was insufficient)
- Indicators dropped from Layer 2 (FDI, geopolitical tailwinds, earnings premium)
  and why
