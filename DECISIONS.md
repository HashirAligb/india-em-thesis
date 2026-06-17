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
**Decision**: Convert all Indian equity returns to USD terms using spot INR/USD rates before any performance comparison.
**Rationale**: The thesis is written from the perspective of a USD-denominated global allocator. Local-currency returns are misleading without currency adjustment.
**Alternatives considered**: Using hedged returns; rejected because INR hedging costs are a real cost that should not be abstracted away in the stress test.

---

### [2026-06-10] Valuation Metric Priority
**Decision**: Use trailing P/E and P/B as the primary valuation metrics, treating valuation as a hurdle rate. CAPE is placed in a lower tier due to cross-country data availability constraints.
**Rationale**: Trailing P/E and P/B are widely available for USD ETFs and support a pragmatic, comparable valuation screen. India's premium (if any) over EEM/FXI must be justified by superior returns or lower risk, not assumed acceptable.
**Alternatives considered**: CAPE; excluded from primary tier because of inconsistent availability across markets. EV/EBITDA remains useful as a secondary sector-level metric.

---

### [2026-06-10] Governance Risk Quantification
**Decision**: Use World Bank WGI composite score (average of 6 dimensions) as primary governance proxy, supplemented by Transparency International CPI.
**Rationale**: WGI is the most widely used cross-country governance dataset with a long history (1996–present). CPI adds a corruption-specific signal.
**Alternatives considered**: V-Dem dataset; richer but harder to operationalise into a single comparable score.

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

---

### [2026-06-10] Digital Infrastructure Proxy
**Decision**: Use UPI monthly transaction volume (value, not count) as a supporting structural narrative indicator, not as a direct input to regression/correlation analysis.
**Rationale**: UPI volume is useful for the structural story around digital infrastructure adoption, but using it directly to predict returns risks spurious correlation.
**Alternatives considered**: Internet penetration rate; retained as a secondary structural indicator but not the headline metric.

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

## Open Questions

- [ ] How to handle the pre-2014 data quality issues in WGI scores for India vs. peers?
- [ ] Should PLI scheme disbursements be modelled as a one-time or recurring tailwind?
- [ ] Is the demographic dividend argument already priced in at current Nifty valuations?
- [ ] How to weight the China+1 supply chain argument given Vietnam and Mexico are also beneficiaries?
- [ ] Should forward P/E be used if trailing P/E data is unavailable via free APIs?
