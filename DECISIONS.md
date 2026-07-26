# Decision Log

Tracks key analytical and methodological choices made during the research process, including the reasoning and alternatives considered. Update this file whenever a non-obvious decision is made.

---

## Analytical Decisions

### [2026-06-10] Benchmark Selection
**Decision**: Use INDA (iShares MSCI India ETF, USD-denominated) as the primary India proxy, compared against EEM (broad EM ETF) and FXI or MCHI (China ETF).
**Rationale**: USD-denominated ETFs avoid manual currency conversion while directly testing the skeptical view that China remains the stronger EM bet. This comparison was missing from the original benchmark and is central to the thesis.
**Alternatives considered**: MSCI EM ex-India; rejected because it obscures the direct India-vs-China EM comparison and still embeds indirect India exposure via broader EM allocations. Individual country peers (Brazil, Indonesia, Vietnam) were also considered but rejected for idiosyncratic noise.

---

### [2026-06-10] Currency Adjustment Methodology
**Decision**: Measure all returns in USD by using USD-denominated ETFs (INDA, EEM, FXI) rather than converting local-currency returns via spot rates. Because these funds trade in dollars, the currency effect — including rupee depreciation against the dollar — is already embedded in the fund price, so a USD investor's actual experience is captured directly.
**Rationale**: The thesis is written from the perspective of a USD-denominated global allocator; USD ETFs reflect real dollar returns without a separate conversion step.
**Alternatives considered**: Manually converting INR-denominated returns at spot rates (rejected as redundant, since USD ETFs already embed the currency effect); currency-hedged returns (rejected because INR hedging costs are a real drag that should not be abstracted away in a stress test).

---

### [2026-06-10] Valuation Metric Priority
**Decision**: Use trailing P/E and P/B as the primary valuation metrics, treating valuation as a hurdle rate. CAPE is placed in a lower tier due to cross-country data availability constraints.
**Rationale**: Trailing P/E and P/B are widely available for USD ETFs and support a pragmatic, comparable valuation screen. India's premium (if any) over EEM/FXI must be justified by superior returns or lower risk, not assumed acceptable.
**Alternatives considered**: CAPE; excluded from primary tier because of inconsistent availability across markets. EV/EBITDA remains useful as a secondary sector-level metric.

> **[REVISED 2026-07-06]** The final valuation indicator uses the trailing P/E premium only, not P/E and P/B. `score_valuation()` takes a single P/E premium parameter (`premium=0.239`) scored against pre-declared bands; the JSON carries `inda_pe` and `msci_em_pe` with premium variants. P/B was dropped and CAPE was never implemented — the two-metric design became a single-metric P/E design.

---

### [2026-06-10] Governance Risk Quantification
**Decision**: Use World Bank WGI composite score (average of 6 dimensions) as primary governance proxy, supplemented by Transparency International CPI.
**Rationale**: WGI is the most widely used cross-country governance dataset with a long history (1996–present). CPI adds a corruption-specific signal.
**Alternatives considered**: V-Dem dataset; richer but harder to operationalise into a single comparable score.

> **[REVISED 2026-07-06]** The final governance score uses the six WGI dimensions (as planned) but does NOT average them. `score_governance()` counts how many dimensions are below zero (`below_zero = sum(1 for v in india_scores_2023.values() if v < 0)`); the thresholds are 0–1 below zero → Favorable, 4+ → Lean-Negative. Transparency International CPI was not used — WGI only, no CPI in the data or code.

---

### [2026-06-10] Stress Test Scenario Design
**Decision**: Run three stress scenarios — Base, Adverse, Severe — defined along two axes: INR depreciation severity and governance deterioration magnitude.
**Rationale**: A single adverse scenario creates false precision; a range of scenarios with clearly defined assumptions is more intellectually honest.
**Scenarios**:
| Scenario | INR Depreciation (10yr cumulative) | Governance WGI Change |
|---|---|---|
| Base | -20% | Flat |
| Adverse | -35% | -0.2 SD |
| Severe | -50% | -0.5 SD |

> **[SUPERSEDED 2026-07-15]** The three-scenario Base/Adverse/Severe design was not built. Sensitivity is instead handled interactively via the Threshold Explorer (slider controls over the pre-declared thresholds), and macro risk is scored by `score_external_macro(inr_dep_pct, oil_share_pct)` with mild/severe thresholds. INR is scored as an annual depreciation rate, not a 10-year cumulative figure, and governance scoring uses a count of WGI dimensions below zero, not standard-deviation shifts. See the Threshold Explorer entry [2026-07-15].

---

### [2026-06-10] Digital Infrastructure Proxy
**Decision**: Use UPI monthly transaction volume (value, not count) as a supporting structural narrative indicator, not as a direct input to regression/correlation analysis.
**Rationale**: UPI volume is useful for the structural story around digital infrastructure adoption, but using it directly to predict returns risks spurious correlation.
**Alternatives considered**: Internet penetration rate; retained as a secondary structural indicator but not the headline metric.

> **[SUPERSEDED 2026-07-06]** UPI transaction volume and internet-penetration rate were replaced by World Bank Findex digital-payment adoption as the scored metric. `score_digital_adoption()` uses Findex `g20.any` (any digital payment, India 48% vs peer median 71%) and `merchant.pay`, both from Findex 2024. UPI/internet lacked comparable, updatable cross-country data suitable for a pre-declared threshold; Findex provided it. No UPI or internet-penetration data appears in the JSON or code.

---

### [2026-06-17] Valuation Premium Assumption Corrected
**Decision**: Report both trailing P/E and forward P/E premiums rather than relying on the original 20–30% premium assumption stated in the thesis.
**Rationale**: Live data (Yahoo Finance / iShares fund pages, June 2026) shows the two measures diverge significantly: trailing P/E implies only a ~7.5% premium (India ~21x vs. EM ~20x), while forward P/E implies a ~55–70% premium. Selecting whichever figure flatters the skeptical thesis would be analytically dishonest. The compressed trailing premium is at least partly a distortion from a temporary 2026 oil shock — Middle East conflict pushed crude above $100/bbl; India imports ~85% of its crude, driving a ~10% YTD equity decline and $20B+ in foreign outflows. This may not reflect a structural re-rating.
**Alternatives considered**: Anchoring to trailing P/E only (understates the premium); anchoring to forward P/E only (overstates it given current earnings disruption). Both rejected as cherry-picking.

---

### [2026-06-17] Commitment to Follow the Data
**Decision**: The final verdict will follow wherever the returns and valuation data point, even if that means partially disproving the original skeptical hypothesis.
**Rationale**: Verification work showed India may be less overpriced than initially assumed, and its current market weakness appears temporary rather than structural. Forcing the conclusion to match the starting thesis would undermine the analysis. Adam confirmed that disproving your own thesis is a valid and intellectually credible outcome.
**Alternatives considered**: Maintaining a fixed skeptical framing throughout; rejected because it risks confirmation bias in data selection and interpretation.

---

### [2026-06-17] Risk-Adjusted Metric Added to Verdict
**Decision**: The verdict will use a risk-adjusted measure (annualised return / annualised volatility, a Sharpe-style ratio with 0% risk-free rate) alongside cumulative return, not cumulative return alone.
**Rationale**: The thesis statement tests "risk-adjusted USD returns," but the original verdict logic only checked which ETF ended highest. Volatility and max drawdown were computed and charted but not fed into the verdict — they sat beside the decision rather than inside it. Adding return / volatility makes the verdict actually reflect the risk dimension the thesis claims to measure: India ending highest is not the same as India being the best deal once the volatility of the ride is accounted for.
**Alternatives considered**: Cumulative return only; rejected because it fails to operationalise the risk-adjusted language in the thesis statement. Full Sharpe ratio with a non-zero risk-free rate; rejected in favour of a 0% floor for simplicity and cross-window comparability.
**Source**: Surfaced during a red-team review of my methodology, June 17.

---

### [2026-06-17] Verdict Split into Historical and Forward-Looking Layers
**Decision**: Structure the verdict in two layers. Layer 1 (historical): did INDA outperform EEM and FXI on returns and risk-adjusted terms from 2013–present? Layer 2 (forward-looking): does today's valuation leave room for the thesis to hold going forward?
**Rationale**: Returns are measured over 2013–present (past); the valuation premium is a current figure (present); the thesis title concerns the next decade (future). Collapsing these into a single verdict would let past performance masquerade as proof of a future claim. Separating them keeps the analysis honest: return data can prove a historical result; valuation and the 2026 macro picture are forward-looking context, not conclusions the return data supports. Likely final verdict shape: "historically supported, forward-looking uncertain."
**Alternatives considered**: A single unified verdict; rejected because it conflates what the data proved with what it merely suggests about the future.
**Source**: Surfaced during a red-team review of my methodology, June 17.

---

### [2026-06-17] 2026 Oil Shock Treated as Stress-Test, Not Core Story
**Decision**: Treat the 2026 oil shock as a separate stress-test section, not as a driver of the core 2013–present verdict.
**Rationale**: The shock (crude above $100/bbl from Middle East conflict; India imports ~85% of its crude; ~10% YTD equity decline, $20B+ in foreign outflows) is real and verified, but it represents a single current-year regime. Letting one recent event dominate a 13-year analysis would distort the long-run picture. It belongs as forward-looking caution in Layer 2 and as a discrete stress-test scenario; the main analytical window tests whether India's return premium survived multiple historical regimes.
**Alternatives considered**: Incorporating the oil shock into the primary return window; rejected because it would give a single current event disproportionate weight in a long-horizon comparison.
**Source**: Surfaced during a red-team review of my methodology, June 17.

---

## Data Decisions

### [2026-06-10] Historical Window
**Decision**: Primary analysis uses 2013–present for market data; 2000–present where available for structural/macro indicators. 2013–present is a sub-period choice, and the longest available clean data window will be noted or shown where feasible.
**Rationale**: 2013 marks Modi-era structural reforms beginning and gives a clean post-taper-tantrum baseline for EM comparisons. Longer series for macro captures full demographic and economic cycles.

---

### [2026-06-10] Index Proxy for Indian Equities
**Decision**: Use Nifty 50 as the headline index; supplement with Nifty 500 for broader market analysis and sector indices (Nifty IT, Nifty Bank, Nifty Pharma) for sector decomposition.
**Rationale**: Nifty 50 is the most liquid and internationally recognised benchmark. Nifty 500 captures the mid/small-cap return premium that is often cited as India's structural alpha source.

---

### [2026-06-11] Risk Metrics
**Decision**: Include rolling volatility and maximum drawdown for INDA, EEM, and FXI/MCHI alongside returns.
**Rationale**: EM narratives often look strong on returns alone but can weaken materially once volatility and drawdown are considered.
**Alternatives considered**: Return-only comparison; rejected because it omits essential risk context.

---

### [2026-06-11] Dependent Variable
**Decision**: The primary dependent variable is India's USD total return performance relative to EM (EEM) and China (FXI/MCHI), not absolute return in isolation.
**Rationale**: This directly operationalizes the thesis question "is India the best EM bet" and anchors the analysis in relative performance.
**Alternatives considered**: Absolute India USD returns; rejected because it fails to test the comparative narrative core to the thesis.

---

### [2026-06-17] Price Series: Adjusted vs. Raw Close
**Decision**: Use dividend-adjusted prices (`auto_adjust=True` in yfinance) for all return calculations across INDA, EEM, and FXI/MCHI.
**Rationale**: ETFs pay dividends, which cause the raw close price to drop on the ex-dividend date even though no value is lost to the holder — the cash was distributed. Measuring returns off raw close prices would undercount total return and, because INDA, EEM, and FXI pay different dividend amounts, would distort the cross-ETF comparison in unpredictable ways.
**Alternatives considered**: Using raw close prices; rejected because it systematically understates total return and introduces a dividend-yield bias across ETFs with different payout levels.

---

## Open Questions

- [ ] How to handle the pre-2014 data quality issues in WGI scores for India vs. peers?
- [ ] Should PLI scheme disbursements be modelled as a one-time or recurring tailwind?
- [ ] Is the demographic dividend argument already priced in at current Nifty valuations?
- [ ] How to weight the China+1 supply chain argument given Vietnam and Mexico are also beneficiaries?
- [ ] Should forward P/E be used if trailing P/E data is unavailable via free APIs?

---

## Layer 2 Framework Decisions

### [2026-07-06] Indicator selection

**What:** The framework scores five indicators: valuation, demographics, governance, digital financial adoption, and external macro vulnerability. An earlier candidate list also included historical EM correlation, FDI trends, geopolitical tailwinds, and earnings growth premium.

**Why:** I applied three criteria to trim the list. The indicator had to be directly measurable from a publicly available source. It had to be relevant to the forward-durability question specifically, not a restatement of what Layer 1 already measured. And the underlying data had to be collectible without paid data access. Governance cleared all three on World Bank WGI. EM correlation failed the second criterion -- it describes past behavior, not forward conditions. Earnings growth premium failed the third. Geopolitical tailwinds failed the first.

**What changed:** Went in with a longer wishlist, came out with five. The framework is narrower than an ideal paid-data version would be; the framework limitations section says so explicitly.

---

### [2026-07-06] Governance chosen over EM correlation

**What:** Governance (World Bank WGI) filled the fifth indicator slot. Historical INDA-EEM rolling correlation was the main alternative.

**Why:** Correlation is a Layer 1 metric. It measures how India has moved relative to the EM herd historically. I already report it in the Layer 1 Notable Finding (~0.76 over the full window). Putting it back into Layer 2 as a durability signal would re-present a historical fact as a forward-looking assessment. Governance is genuinely structural: weak rule of law and corruption affect the reliability of earnings and capital returns going forward, regardless of what the return series looked like over 2013-2026.

**What changed:** Correlation stays in Layer 1 where it belongs. Governance goes into Layer 2. No double-counting.

---

### [2026-07-06] Geopolitical tailwinds dropped

**What:** The "China+1 supply chain beneficiary" and "geopolitical realignment" arguments were considered as a structural indicator and then cut from the framework.

**Why:** No defensible metric. The supply-chain argument is real -- India is capturing some manufacturing shift from China -- but there is no publicly available, comparable, and updatable time-series that isolates India's supply-chain capture in a form that can be scored with a pre-declared threshold. FDI inflows exist but reflect too many confounding factors. Including it as an unscored positive would add narrative without analytical weight and would make the framework asymmetric in a way I could not justify.

**What changed:** Geopolitical tailwinds are acknowledged in the framework context but not scored. The framework limitations section flags this as a known gap in the bull-case coverage.

---

### [2026-07-06] Currency and oil merged into one external-macro indicator

**What:** An earlier version of the framework had INR depreciation and oil exposure as two separate gating indicators. They were merged into a single external macro vulnerability indicator.

**Why:** These are the same underlying risk, not two separate ones. An oil shock raises the import bill, widens the current account deficit, pressures the rupee, and amplifies the drag on USD-denominated returns -- in that causal chain. Scoring them separately gave the same vulnerability double weight in the ladder. The merge was a double-count fix. The combined indicator still captures both sub-signals: INR depreciation has its own mild and severe thresholds, and so does oil's share of imports.

**What changed:** Two indicators became one. The ladder weighting is more honest as a result.

---

### [2026-07-06] Digital adoption added to test the bull pillar; neutral score kept

**What:** Digital financial adoption (World Bank Findex, g20.any and merchant.pay) was added specifically to test the "digital infrastructure leader" pillar of the original thesis. Findex 2024 shows India at 48% on any digital payment against an EM peer median of 71%. The score is Neutral.

**Why:** The original thesis framed India's digital infrastructure as a competitive strength and a driver of the next decade of growth. The data says India is converging from behind, not leading. The trend is real and fast (22% in 2014 to 48% in 2024), but the absolute level is 23pp below the EM peer median. The merchant-payment rate (18% vs a peer median of 51%) shows the gap is largest exactly where it matters most for listed-company revenues. I kept the Neutral score rather than adjusting it upward to fit the original narrative.

**What changed:** The indicator disconfirmed the strong form of the bull claim. The Neutral score stays. The framework notes this honestly: India's digital story is real and accelerating, but it is a convergence-from-behind story, not established EM leadership.

---

### [2026-07-06] Framework red team: fixed the real error, disclosed the rest

**What:** Before locking the thresholds, I red-teamed the framework to catch scoring bias and coverage gaps. Two outputs: a correction to the demographics score (addition of the female LFP conversion caveat), and an explicit framework limitations section covering the coverage asymmetry.

**Why:** The demographics indicator was initially framed as a clean Favorable. The red team flagged that female labor force participation at 35% means the demographic dividend is only partially realized. That is a real analytical caveat, not a minor footnote. It changes the interpretation of the score: Favorable means the age structure is genuinely advantageous, but the conversion into economic output depends on participation rising. I added the caveat to the score display and the rationale rather than ignoring it. The coverage asymmetry -- that the framework measures the risk side (valuation, external macro) more completely than the structural-opportunity side (geopolitical tailwinds absent, earnings bridge absent) -- cannot be fixed without paid data. So it is disclosed rather than minimized.

**What changed:** Demographics kept Favorable but gained an explicit conversion caveat. The framework limitations section was added. Digital adoption's Neutral score was confirmed as the correct read, not adjusted.

---

### [2026-07-15] Scoring made adjustable via the Threshold Explorer

**What:** The five indicator scores and the confidence ladder verdict are computed live from the threshold parameters, which are exposed as slider controls in the app sidebar under "Threshold Explorer." A "Reset to pre-declared thresholds" button restores the declared Rung 3 state. When any slider differs from the default, a warning banner appears explaining the user is in exploration mode.

**Why:** Pre-declared thresholds are a methodological commitment, but a second analyst should be able to test whether the verdict is robust to different assumptions. Moving the valuation Neutral/Caution split from 20% to 25% changes whether the ~24% premium scores as Neutral or Caution. Changing the governance Lean-Negative count from four below-zero dimensions to three changes the governance score. Making those sensitivity tests interactive does not change the declared verdict; it makes the declared verdict more defensible because its robustness (or lack of it) is visible.

**What changed:** Scoring functions were refactored from hardcoded strings into parameterised functions in src/layer2.py -- `score_valuation`, `score_demographics`, `score_governance`, `score_digital_adoption`, `score_external_macro`, and `compute_ladder_verdict` -- with defaults matching the pre-declared values. The Streamlit app manages threshold state in session_state and reruns all scoring functions on every slider change. Assertion tests in src/layer2.py verify that the defaults reproduce the locked Rung 3 verdict.
