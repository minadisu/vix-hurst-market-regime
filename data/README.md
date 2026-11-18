# Data | 数据说明

This directory contains the five CSV files supplied for the research. Values and observation ordering have been retained, and filenames are normalized for the project. / 本目录保存用户提供的五份 CSV，保留数据内容及原始排序，仅统一了文件名。

| File / 文件 | Series / 数据 | Available dates / 文件日期范围 | Format / 格式 |
|---|---|---|---|
| `spx.csv` | S&P 500 OHLCV / 标普500价格及成交量 | 2000-01-03 → 2025-12-31 | Ascending dates / 日期升序 |
| `GLD.csv` | Gold ETF / 黄金ETF | 2009-01-02 → 2025-12-31 | Descending dates, formatted fields / 降序，部分字段带格式 |
| `USO.csv` | Oil ETF / 原油ETF | 2009-01-02 → 2025-12-31 | Descending dates, formatted fields / 降序，部分字段带格式 |
| `GVZCLS.csv` | Gold volatility index / 黄金隐含波动率指数 | 2008-07-01 → 2025-12-31 | Some missing observations / 存在缺失观测 |
| `OVXCLS.csv` | Oil volatility index / 原油隐含波动率指数 | 2008-01-02 → 2025-12-31 | Some missing observations / 存在缺失观测 |

## Usage | 使用方式

The supplied data extend into 2025; the empirical scripts select dates **no later than 2024-12-31**. The primary S&P 500 study uses observations from 2000 onward; GLD/USO extensions from 2009 onward. / 上传数据覆盖至2025年，但现有脚本设定的研究截止日为2024-12-31；主实证从2000年开始，跨资产扩展从2009年开始。

**VIXCLS is not included as a local CSV.** As coded, the main and strategy scripts download VIXCLS from FRED when executed. The gold/oil script also fetches GVZCLS and OVXCLS from FRED online rather than reading their uploaded local copies. / 本地没有VIXCLS文件；主实证和策略脚本运行时从FRED获取VIXCLS，黄金原油脚本也会联网读取GVZCLS和OVXCLS，而非直接使用这里的副本。

## Provenance & permissions | 来源与授权

These are user-supplied research inputs. Their precise upstream price adjustment conventions and redistribution permissions have **not been independently verified**. This directory should not be copied into a public repository without checking the original providers' terms and data quality. / 以上文件由研究者提供，上游价格复权口径和再分发授权尚未独立核实。公开仓库前需确认原始数据供应商许可并复核数据质量。

For execution details see [reproducibility guide](../docs/reproducibility.md). / 运行方法见[复现指南](../docs/reproducibility.md)。
