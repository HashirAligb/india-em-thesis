# Thesis #16 — Emerging Markets: India's Decade to Shine?

**Thesis statement:** Testing whether India delivered better risk-adjusted USD returns
than EM ex-India and China (FXI) over 2013–2026.

---

## Data & Method

- **Source:** Yahoo Finance via yfinance (`auto_adjust=True` — prices include dividends)
- **Instruments:** INDA (India proxy), EM ex-India (primary EM benchmark; India's contribution removed using a fixed ~15% weight), FXI (China benchmark), INR=X (USD/INR spot, for currency correlation only)
- India is ~15% of standard broad-EM indices like EEM, so comparing India directly against EEM partly compares India against itself; the EM benchmark here is EM ex-India, with India's contribution removed. India's actual index weight drifted between roughly 12% and 15% over the analysis window; ~15% is used as the working estimate throughout.
- **Window:** 2013-01-01 to 2026-06-25 (pinned for reproducibility)
- **Denominated in:** USD throughout — ETF prices are USD-quoted, so no manual conversion is needed
- **Valuation:** Treated as forward-looking context (Layer 2), not modelled in the return analysis
- **Risk-adjusted metric:** Annualised return / annualised volatility (0% risk-free rate, per decision log)

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

### Layer 2 — Forward-Durability Framework

**The question Layer 2 is answering.** Layer 1 established that India outperformed EM ex-India and China across the 2013 to 2026 window. Layer 2 asks the harder question: is the structural opportunity still intact, or has the market already priced it in? Historical outperformance is necessary but not sufficient evidence that future outperformance is durable. A market that has already run up to reflect a promising structural story can deliver disappointing forward returns even if the story itself proves correct.

**Framework structure.** Five indicators are scored against pre-declared thresholds. Three are structural -- demographics, governance, and digital financial adoption -- and test whether the fundamental drivers of India's growth story are real and durable. Two are gating -- valuation and external macro vulnerability -- and test whether external factors cap or constrain the verdict regardless of structural strength. The rollup uses a four-rung confidence ladder, not a simple vote count. A gating indicator that reaches a severe threshold forces the verdict to the lowest rung regardless of how strong the structural case looks. Thresholds and the ladder rule were declared before the indicators were scored.

**Valuation (Gating): Neutral-to-Caution.** INDA's trailing P/E was 22.35x as of July 1 2026 (iShares fund page), against MSCI EM's 18.60x (MSCI factsheet, May 29 2026). Applying the same ex-India construction as the Layer 1 benchmark -- removing India's approximate weight from EM, tested across the 12-15% range that India's actual index weight spans -- produces an EM ex-India P/E of roughly 17.94x to 18.09x, implying a premium in the range of 23.6% to 24.6%. The pre-declared bands placed Neutral at 10-20% and Caution at 20-30%, with At-risk at 30-40% and Severe at 40% and above. The ~24% premium lands in the Caution zone. Multiple credible sources independently report the premium had compressed below India's own 10-year historical norm following a period of underperformance (Goldman Sachs via Reuters, November and December 2025; Reuters, July 2026), which softens but does not erase the headwind. The gate does not trip severe. The acknowledged limitation is that the framework cannot directly measure whether India's earnings growth premium justifies this valuation premium -- that data is not available from public sources.

**Demographics (Structural): Favorable.** India's old-age dependency ratio was 10 in 2024, against China's 21 (World Bank World Development Indicators). The India/China ratio of 0.48 is well below the 0.60 pre-declared threshold for a Favorable score. Total age dependency ratios are closer -- India 47, China 50 -- but the old-age comparison is the more forward-relevant measure because it captures the relative position of the working-age share over the coming decades. India's working-age share continues to rise while China's falls. The conversion caveat is female labor force participation, which is 35% against a total LFP rate of 59%. A demographic dividend requires conversion into employment. Female LFP at 35% is both a current shortfall and remaining upside if participation rises, and the score is Favorable with that caveat explicit. Demographics is the strongest single fact in the structural bull case.

**Governance (Structural): Neutral / Lean-Negative.** The World Bank's Worldwide Governance Indicators (WGI 2025 dataset, estimates on a scale of -2.5 to +2.5) show India scoring below zero on five of six dimensions in 2023: Voice and Accountability (-0.14), Political Stability (-0.84), Regulatory Quality (-0.13), Rule of Law (-0.09), and Control of Corruption (-0.34). Government Effectiveness is the sole positive at +0.42. China leads on Government Effectiveness (+0.78) and Control of Corruption (+0.11 vs India's -0.34). India holds a better score on Rule of Law (-0.09 vs -0.55) and historically led on Voice and Accountability, though that advantage has narrowed and turned slightly negative by 2023. The pre-declared threshold for Lean-Negative is four or more dimensions below zero; with five below zero, India lands in Neutral / Lean-Negative. The overall picture is two countries with different governance weaknesses, not India clearly ahead. Against a broader EM peer set, India likely sits in the middle of the pack. Governance is included as a structural indicator because weak rule of law and corruption reduce the reliability of earnings and capital returns; the democratic-institution advantage remains a real differentiator on policy reversibility and property rights, but it is not enough to clear a Favorable score.

**Digital Financial Adoption (Structural): Neutral.** World Bank Global Findex 2024 data (indicators g20.any and merchant.pay) shows India at 48% on any digital payment and 18% on digital merchant payment. The EM peer median across nine comparable economies (China, Indonesia, Brazil, Mexico, South Africa, Turkey, Thailand, Malaysia, Philippines) was 71% on any digital payment and 51% on merchant payment. India trails by 23pp and 33pp respectively. The trend is strongly positive -- 22% in 2014, 29% in 2017, 35% in 2021, 48% in 2024 -- but the absolute gap is large. The split between the any-digital rate (48%) and the merchant-payment rate (18%) reflects India's UPI-heavy model: person-to-person transfers and bill payments count as any-digital, but formal merchant-terminal adoption is much lower, which matters more for listed-company revenues. The score is Neutral. This indicator was included specifically to test the "digital infrastructure" pillar of the original bull case; the data partially disconfirms that narrative. India's digital story is real and accelerating, but it is a convergence-from-behind story, not established EM leadership.

**External Macro Vulnerability (Gating): At-Risk (mild-to-conditional).** The rupee has depreciated at approximately 3-4%/yr against the USD (MUFG, UBS, Reuters consensus forecast). Oil accounts for roughly 25% of India's import bill, with over 90% imported. Currency drag and oil exposure are scored as a single indicator because an oil shock and rupee depreciation represent the same underlying macro risk for India: a crude spike widens the current account deficit, pressures the rupee, and amplifies the drag on USD-denominated returns. Scoring them separately would double-count the same vulnerability. Layer 1 found the rolling correlation between INDA and the rupee was approximately zero over the full window, meaning the persistent currency drag has historically been absorbed by India's equity returns. The oil shock risk is conditional rather than structural. Neither sub-signal crosses the pre-declared severe thresholds (8%/yr for INR, 45% for oil's import share). The score is At-Risk (mild-to-conditional); the gate does not trip severe.

**Scoring summary.**

| Indicator | Role | Score |
|---|---|---|
| Valuation | Gating | Neutral-to-Caution |
| Demographics | Structural | Favorable |
| Governance | Structural | Neutral / Lean-Negative |
| Digital Adoption | Structural | Neutral (negative level, positive trend) |
| External Macro Vulnerability | Gating (soft) | At-Risk (mild-to-conditional) |

**Verdict: Rung 3 -- Structurally attractive, but priced and macro-sensitive.** Neither gating indicator trips severe: valuation is elevated but not at a historical extreme, and external macro vulnerability is real but mild. Rung 4 (Not durable) is off the table. However, the structural case is incomplete. Demographics is the one strong structural positive. Governance is mixed and scores Neutral / Lean-Negative; it is not an active negative, but it is not a bull-case driver. Digital adoption is improving from a deficit, not an established EM leader. Two of three structural indicators are Neutral rather than Favorable. Under the pre-declared ladder rule -- no severe gate and incomplete structural support -- the verdict is Rung 3, not Rung 2.

India's opportunity is real, but narrower than the original bull case implied. The market has partially priced in that opportunity through a meaningful valuation premium, though not to an obvious extreme. The forward case is conditionally durable: India can keep outperforming if earnings growth validates the premium, but the margin for disappointment is limited. This is consistent with the analyst's journey: the original skepticism about India was wrong about the historical record (Layer 1 shows clear outperformance), but the forward caution is supported by the framework (real structural advantage, partially priced in, conditional on continued execution).

**Framework limitations.** Two honest disclosures on what the framework measures and does not. First, the risk side is measured more completely than the bull case. Valuation and external macro are scored with specific thresholds and gate rules. Of the bull-case pillars, demographics is scored (Favorable), digital adoption is scored (Neutral, weaker than the original narrative implied), and geopolitical tailwinds were dropped entirely -- no defensible and updatable metric was available to quantify India's supply-chain-beneficiary position in a way that would survive scrutiny. The framework therefore finds more evidence on the risk side than the structural-opportunity side, not because the risks are larger, but because the risks are more measurable. Second, the framework does not bridge structural opportunity to listed-company equity returns. Even a hypothetically Favorable structural picture would not prove that the opportunity converts into earnings growth and shareholder returns. The ideal additional indicator is India's forward earnings growth premium versus EM ex-India; it is not included because clean forward-estimate data is not available from public sources (Bloomberg/FactSet-gated). The missing earnings bridge is the primary extension if a fuller version of this framework is built with paid data access.

---

## Notable Finding

Rolling 12-month INDA–EEM correlation averaged ~0.76 over the full window. India moves closely with the broad EM herd, which weakens the diversification argument sometimes made for an India-only allocation.

---

## Charts

![Cumulative Return](outputs/figures/01_cumulative_return.png)

![Volatility and Max Drawdown](outputs/figures/02_vol_drawdown.png)

![Rolling Correlation](outputs/figures/03_rolling_correlation.png)

![Verdict Card](outputs/figures/04_verdict_card.png)
