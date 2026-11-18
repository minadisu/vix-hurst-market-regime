# Running the research scripts

The three source scripts were uploaded from the original research files with only their hard-coded Windows input/output paths adapted to the repository layout. Research logic was **not corrected or validated** in this commit.

## Python environment

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Execution

```bash
python src/01_main_spx_vix_hurst_empirical.py
python src/02_strategy_application.py
python src/03_gold_oil_extension_optional.py
```

The main and strategy scripts use `data/raw/spx.csv`. Gold/oil extensions use `data/raw/GLD.csv` and `data/raw/USO.csv`. The original programs download `VIXCLS`, `GVZCLS` and `OVXCLS` on execution from FRED, so an internet connection is required despite local copies of GVZCLS and OVXCLS.

Outputs are directed to `outputs/main_empirical`, `outputs/strategy` and `outputs/gold_oil`. These output directories are ignored by Git.

## Important limitations

- The uploaded scripts passed a **syntax check** only; end-to-end execution and replication of the published coursework tables have **not** been verified.
- Group comparisons employ Welch t-tests on overlapping forward horizons, potentially understating uncertainty. The regressions use HAC standard errors, but this does not resolve all signal-selection concerns.
- `future_max_drawdown` measures the minimum return relative to the signal-date price, **not** the conventional within-window peak-to-trough maximum drawdown.
- The scripts were not redesigned for strict out-of-sample evaluation or alternative Hurst estimates.
- Please check license/redistribution terms for raw market data before changing the repository from private to public.
