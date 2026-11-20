# Reproducibility & usage 

## 1. Scope

The source code was copied from the three original study scripts. For the directory reorganization, only the **input and output path definitions** are changed; statistical methods, trading rules and numerical procedures are intentionally unchanged.

| Script | Role | Generated output |
|---|---|---|
| `src/01_main_spx_vix_hurst_empirical.py` | Main S&P 500/VIX-Hurst empirical tests | `outputs/main_empirical/` |
| `src/02_strategy_application.py` | Supplementary S&P 500 strategy tests | `outputs/strategy/` |
| `src/03_gold_oil_extension_optional.py` | Optional gold/oil analysis | `outputs/gold_oil/` |

## 2. Setup

From the repository root (Python 3 recommended)：

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the virtual environment first if needed. Dependencies include NumPy, pandas, SciPy, statsmodels and Matplotlib. The file lists packages, **not tested/frozen exact versions**.

## 3. Input data 

- `data/spx.csv`: S&P 500 historical levels
- `data/GLD.csv`, `data/USO.csv`: gold/oil ETF prices 
- `data/GVZCLS.csv`, `data/OVXCLS.csv`: local uploaded reference series
**FRED requests in the existing code:** `VIXCLS` for scripts 01/02, and `GVZCLS`/`OVXCLS` for script 03. Even though local GVZCLS/OVXCLS files are included, **script 03 currently downloads those series afresh**; no local fallback is implemented.
  
Uploaded CSVs may extend through 2025, but scripts are configured with `END_DATE = "2024-12-31"`. Main study begins in 2000; the asset-extension code begins in 2009.

## 4. Run 

```bash
python src/01_main_spx_vix_hurst_empirical.py
python src/02_strategy_application.py
python src/03_gold_oil_extension_optional.py
```

The programs write CSVs and figures into subfolders of `outputs/`, which Git ignores. Previously supplied *reported* tables/figures are stored under `results/`. Do not overwrite them with new run outputs without checking sample/data/version differences.

## 5. Verification status

- **Available:** Source scripts, five uploaded CSVs, reported Tables 1–7 and Figures 1–9. 
- **Checked:** Files present in the repository and path substitutions for the new directory layout; source-code syntax only.
- **Not yet checked:** Complete end-to-end execution with FRED data, numerical reproduction of all output tables and figures, exact dependency versions, or an out-of-sample forecast test.
### Known methodological cautions

1. **Overlapping forward 22/60-day outcomes.** Group comparisons use ordinary Welch t-tests and may understate uncertainty; the regressions explicitly use HAC covariance with 22/60 lags. 
2. **No isolated Hurst control group.** Composite-signal days are compared with other bear-state days, not conditionally matched Hurst≤0.5 days. 
3. **In-sample analysis only.** Model AIC/adjusted R² differences do not prove out-of-sample predictive value. 
4. **Drawdown definition.** Forward `mdd_fwd` is the minimum cumulative return relative to the initial signal-day price; distinguish it from the usual within-window peak-to-trough maximum drawdown.
5. **Strategy comparability.** S&P 500 index-level backtests, cash weights, cost assumptions and different average exposures limit investability and return comparisons.

### Sharing

Market data may have redistribution restrictions, and journal policies on prior dissemination vary. Keep raw data and any complete thesis private until these questions are resolved; a separate public showcase can omit restricted inputs and the full thesis.
