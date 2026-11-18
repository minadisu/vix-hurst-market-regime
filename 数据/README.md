# Raw market data (user supplied)

These files are archived as received from the user, with original column formats and observation ordering preserved. Names were normalized for repository paths; file values were not cleaned or recalculated.

| File | Dataset | Observed coverage in upload | Notes |
|---|---|---|---|
| spx.csv | S&P 500 OHLCV | 2000-01-03 to 2025-12-31 | Date ascending |
| GLD.csv | GLD price, OHLC, volume and change | 2009-01-02 to 2025-12-31 | Date descending; CSV uses formatted fields |
| USO.csv | USO price, OHLC, volume and change | 2009-01-02 to 2025-12-31 | Date descending; CSV uses formatted fields |
| GVZCLS.csv | GVZ volatility index | 2008-07-01 to 2025-12-31 | Includes blank observations |
| OVXCLS.csv | OVX volatility index | 2008-01-02 to 2025-12-31 | Includes blank observations |

**Important:** The uploaded files extend through 2025, while the coursework paper reports a 2000–2024 main-sample period. Do not attribute these uploads to the paper's exact estimation sample without recreating its filtering.

**Missing dataset:** A VIX history file was not among this batch. Main VIX-Hurst computations require VIX observations in addition to the S&P 500 levels.

**Reproducibility and rights:** Raw CSV files may be subject to original providers' terms. This repository is private; review data redistribution rights before making it public. No assumptions are made about the source or adjustment conventions of every file.
