# Research Brief

**Title:** *Identifying Risk-Recovery Regimes in the S&P 500 with VIX Dynamics and the DFA-Hurst Exponent*  
**Status:** Preliminary undergraduate empirical research; not a published or peer-reviewed paper.

## Abstract

**English.** This study examines whether the persistence of changes in option-implied volatility provides incremental information about equity-market risk recovery. We estimate a rolling detrended fluctuation analysis (DFA) exponent on daily changes in log(VIX), with a 90-trading-day main window, and combine it with S&P 500 trend and VIX-state indicators. Using daily observations in 2000–2024, the research explores conditional signals, forward 22- and 60-trading-day market outcomes, and nested regression specifications. In the bear-market subsample, reported adjusted R² for 60-day forward S&P 500 returns increases from 11.01% under traditional-plus-VIX controls (M2) to 17.55% when VIX-Hurst variables are added (M3). Supplementary allocation and cross-asset exercises illustrate possible applications but do not validate a tradable forecasting rule. Results remain in sample and require more stringent dependence-aware inference and out-of-sample testing.

## Research question

Does a measure of **volatility persistence** add information beyond conventional equity-market and VIX level/direction variables *conditional on weak equity-market states*? The study is **not** designed as a universal bottom-finding model.

## Data & model design 

| Component | Specification |
|---|---|
| Main period | 2000–2024 daily observations |
| Equity series | S&P 500 price level; returns, moving-average gaps, trailing volatility and drawdowns |
| Volatility series | VIX level, rolling quantiles and 5/22-day changes |
| Persistence | DFA slope on Δlog(VIX), 45/60/90/120-day rolling windows; main 90-day |
| Core regime | S&P 500 < MA200; VIX > trailing 252-day Q80; VIX 5-day change < 0; Hurst(90d) > 0.5 |
| Outcomes | 22/60-day forward returns, VIX changes, realized volatility, downside-path measure, recovery classifications |
| Nested models | M1: market factors; M2: M1 + VIX measures; M3: M2 + VIX-Hurst terms |

The `mdd_fwd` variable in the supplied scripts measures the *minimum future return relative to the starting price*; it is not the standard peak-to-trough maximum drawdown.

## Selected results

1. **Hurst distribution:** The reported 90-day DFA-Hurst mean is **0.5402** across 5,978 retained observations; **64.84%** exceed 0.5.
2. **Core state frequency:** The bear/high-VIX/falling-VIX/high-Hurst state occurs on **170 days (2.84%)**; the high/rising-VIX counterpart occurs on **225 days (3.76%)**. 
3. **Nested model fit:** In the bear subsample, 60-day forward equity returns have adjusted R² of **11.01% for M2** and **17.55% for M3**; AIC improves from **−2881.91** to **−3008.35**. 
4. **Descriptive group differences:** The core signal's reported mean 60-day forward log return is **5.15%**, compared with **−0.62%** for *other bear-market days*. This comparison is **not a matched high- versus low-Hurst experiment** and uses overlapping observations.
5. **Application illustration / 应用示例:** The dynamic strategy has a reported annualized return of **3.91%**, volatility of **10.83%** and maximum drawdown of **−34.43%**, versus buy-and-hold **6.43%**, **19.29%**, and **−56.78%**. The lower volatility comes alongside lower return/exposure; this is not evidence of alpha.
See [reported tables](../results/tables/) and [nine figures](../results/figures/).

## Interpretation & next checks 

The main contribution is a **conditional state-identification question** and a structured M1–M3 empirical comparison. Limitations are substantive, not simply presentation details:

- Compare **Hurst > 0.5 vs. Hurst ≤ 0.5** within the *same* bear/high-VIX/falling-VIX state to isolate incremental Hurst information.
- Account for serial dependence and overlapping future windows (HAC/event-level tests/block bootstrap, as appropriate). OLS employs HAC, but the reported Welch group tests do not. 
- Implement chronologically separated out-of-sample evaluation and stronger benchmark models; avoid tuning thresholds on the full test set.
- Test alternate Hurst windows/estimators and practical assumptions; distinguish downside relative to signal price from peak-to-trough drawdown. 

**No full thesis PDF is provided here.** This is a standalone research overview linked to code and reported outputs, not a substitute for journal review. 
