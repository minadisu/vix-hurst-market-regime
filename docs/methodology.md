# Methodology and validation roadmap

## Construction

Let `x_t = log(VIX_t) - log(VIX_{t-1})`. Estimate its DFA-Hurst exponent with rolling windows of 45, 60, 90 and 120 trading days. The original analysis uses 90 days as the primary window and 120 days as a sensitivity comparison.

Weak market: `S&P 500 close < MA200`. Elevated VIX: above the trailing 252-day 80th percentile. VIX-down: negative trailing 5-day VIX change. Candidate state: the conjunction of weak market, elevated and declining VIX, and `H_90 > 0.5`.

Outcomes considered: forward 22/60-day S&P 500 log return, log VIX change, annualized realized volatility, worst forward price relative to signal date, and loose/strict definitions of risk recovery.

## Critical checks before submission

1. Compare high- and low-Hurst groups **conditional on the same weak market / high VIX / falling VIX state** to isolate the Hurst contribution.
2. Apply dependence-robust inference to overlapping 22/60-day targets (e.g., appropriate HAC or block bootstrap); report effective event counts.
3. Conduct strictly time-ordered expanding-window or rolling-window out-of-sample tests, using parameters selected only from the training period.
4. Test window lengths, cutoff choices, alternative Hurst estimators and finite-sample uncertainty.
5. Evaluate classification with appropriate metrics and comparator models; report practical gains, not solely in-sample R²/AIC.
6. Compare dynamic positions to appropriate matched-volatility / matched-exposure baselines including fees and execution constraints.
7. Verify numerical presentation, including the corrected P-value for the bear-sample 60-day maximum drawdown Hurst level effect (appendix reports `0.0291`).

## Caveat on drawdown terminology

The coursework uses the minimum forward cumulative return relative to the signal-date price and labels it maximum drawdown. Standard peak-to-trough drawdown over the horizon is a different statistic; these definitions should be separated in future revisions.
