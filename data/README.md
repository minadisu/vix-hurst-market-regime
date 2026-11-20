# Data

This directory contains the five CSV files supplied for the research. Values and observation ordering have been retained, and filenames are normalized for the project.

| File | Series | Available dates | Format |
|---|---|---|---|
| `spx.csv` | S&P 500 OHLCV | 2000-01-03 → 2025-12-31 | Ascending dates |
| `GLD.csv` | Gold ETF | 2009-01-02 → 2025-12-31 | Descending dates, formatted fields |
| `USO.csv` | Oil ETF | 2009-01-02 → 2025-12-31 | Descending dates, formatted fields |
| `GVZCLS.csv` | Gold volatility index | 2008-07-01 → 2025-12-31 | Some missing observations |
| `OVXCLS.csv` | Oil volatility index | 2008-01-02 → 2025-12-31 | Some missing observations |

## Usage

The supplied data extend into 2025; the empirical scripts select dates **no later than 2024-12-31**. The primary S&P 500 study uses observations from 2000 onward; GLD/USO extensions from 2009 onward.

**VIXCLS is not included as a local CSV.** As coded, the main and strategy scripts download VIXCLS from FRED when executed. The gold/oil script also fetches GVZCLS and OVXCLS from FRED online rather than reading their uploaded local copies.

## Provenance & permissions

These are user-supplied research inputs. Their precise upstream price adjustment conventions and redistribution permissions have **not been independently verified**. This directory should not be copied into a public repository without checking the original providers' terms and data quality. 

For execution details see [reproducibility guide](../docs/reproducibility.md).(../docs/reproducibility.md)。
