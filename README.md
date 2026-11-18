# VIX-Hurst Market Regime Identification

**Research status:** Preliminary empirical study; not peer reviewed. Statistical robustness and out-of-sample validation remain incomplete.

## Overview

This project investigates whether the persistence of changes in option-implied volatility, measured by a rolling detrended fluctuation analysis (DFA) Hurst exponent on daily log changes in the CBOE VIX, offers incremental information for identifying potential risk-recovery regimes in the S&P 500 during weak market conditions.

The core candidate signal combines four conditions:

1. S&P 500 below its 200-day moving average;
2. VIX above its rolling 252-trading-day 80th percentile;
3. VIX decreased over the preceding five trading days;
4. The 90-day DFA-Hurst estimate of changes in log(VIX) exceeds 0.5.

The empirical study covers **2000–2024** and considers forward 22- and 60-trading-day outcomes.

## Methods and preliminary findings

- Compare traditional market covariates (M1), traditional plus VIX measures (M2), and additional VIX-Hurst measures (M3).
- Assess forward returns, VIX changes, realized volatility, drawdowns, and risk-recovery conditions.
- Illustrative in-sample result: for 60-day S&P 500 returns in the bear-state subsample, the reported adjusted R² increases from **11.01% (M2)** to **17.55% (M3)**.
- Both high-and-declining and high-and-rising VIX signals with high Hurst show subsequent recovery patterns; results do **not** establish a unique directional signal.
- Strategy and gold/oil analyses are supplementary exploratory applications, not evidence of proven trading profitability.

**Limitations:** The original coursework uses overlapping forward windows and has not yet implemented the necessary robust statistical inference and out-of-sample checks. These preliminary in-sample associations should not be interpreted as causal effects or validated predictive performance.

## Repository contents

- `figures/`: figures from the research analysis (descriptive, regression comparison, strategy diagnostics, and cross-asset supplements).
- `results/Paper_Tables.xlsx`: preliminary result tables.
- `results/figure_list.csv`: figure index.
- `docs/methodology.md`: methodological summary and validation priorities.

**Reproduction note:** Executable research scripts and data download pipelines are **not yet included**, so this repository is currently a research-results archive rather than a fully reproducible pipeline. Add verified source code and dependency versions before describing it as reproducible.

## Data provenance

- S&P 500 historical levels: Yahoo Finance, as described in the associated coursework.
- VIX levels: Cboe, as described in the associated coursework.
- Gold and oil extensions: GLD/GVZ and USO/OVX respectively.

Raw market data are not redistributed here. Please consult providers' licenses and terms of use.

## Publication status

This repository is initially intended for **private** research organization. The full coursework PDF (which contains student information) is deliberately omitted. Before making a public version, check any target journal's preprint, code-sharing and anonymity policies and review the files for sensitive information.
