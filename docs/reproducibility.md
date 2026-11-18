# Reproducibility & usage | 运行与复现说明

## 1. Scope | 文件范围

The source code was copied from the three original study scripts. For the directory reorganization, only the **input and output path definitions** are changed; statistical methods, trading rules and numerical procedures are intentionally unchanged.

三份原始研究脚本已保留。此次为适应英文目录，仅调整**输入和输出路径定义**，不修改统计方法、仓位规则或数值计算逻辑。

| Script / 脚本 | Role / 用途 | Generated output / 输出 |
|---|---|---|
| `src/01_main_spx_vix_hurst_empirical.py` | Main S&P 500/VIX-Hurst empirical tests / 主实证 | `outputs/main_empirical/` |
| `src/02_strategy_application.py` | Supplementary S&P 500 strategy tests / 策略应用 | `outputs/strategy/` |
| `src/03_gold_oil_extension_optional.py` | Optional gold/oil analysis / 黄金原油扩展 | `outputs/gold_oil/` |

## 2. Setup | 环境配置

From the repository root (Python 3 recommended): / 在项目根目录执行（建议使用 Python 3）：

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the virtual environment first if needed. Dependencies include NumPy, pandas, SciPy, statsmodels and Matplotlib. The file lists packages, **not tested/frozen exact versions**.

如有需要，请先激活虚拟环境。依赖包已列在 `requirements.txt`，但尚未记录与原始论文计算完全对应的固定版本。

## 3. Input data | 输入数据

- `data/spx.csv`: S&P 500 historical levels / 标普500历史数据。
- `data/GLD.csv`, `data/USO.csv`: gold/oil ETF prices / 黄金、原油ETF价格。
- `data/GVZCLS.csv`, `data/OVXCLS.csv`: local uploaded reference series / 已上传的波动率指数数据备份。

**FRED requests in the existing code:** `VIXCLS` for scripts 01/02, and `GVZCLS`/`OVXCLS` for script 03. Even though local GVZCLS/OVXCLS files are included, **script 03 currently downloads those series afresh**; no local fallback is implemented.

**原程序运行时会访问FRED：** 01/02获取 VIXCLS，03获取 GVZCLS 和 OVXCLS。虽然仓库中已有 GVZCLS/OVXCLS 文件，原代码**并未改为本地读取或添加断网回退机制**。

Uploaded CSVs may extend through 2025, but scripts are configured with `END_DATE = "2024-12-31"`. Main study begins in 2000; the asset-extension code begins in 2009.

原始CSV可能延伸到2025年底，但脚本将主要分析截止日设置为2024-12-31；黄金和原油扩展从2009年开始。

## 4. Run | 运行命令

```bash
python src/01_main_spx_vix_hurst_empirical.py
python src/02_strategy_application.py
python src/03_gold_oil_extension_optional.py
```

The programs write CSVs and figures into subfolders of `outputs/`, which Git ignores. Previously supplied *reported* tables/figures are stored under `results/`. Do not overwrite them with new run outputs without checking sample/data/version differences.

新运行生成的CSV和图片保存在 `outputs/`，Git默认忽略。用户已提供的原始论文结果集中在 `results/`；复现时应先比对样本、数据来源及版本差异，不应直接覆盖。

## 5. Verification status | 验证状态

- **Available:** Source scripts, five uploaded CSVs, reported Tables 1–7 and Figures 1–9. / 已提供代码、五份CSV、7张表和9张图。
- **Checked:** Files present in the repository and path substitutions for the new directory layout; source-code syntax only. / 已检查文件和路径配置；此前只完成静态语法检查。
- **Not yet checked:** Complete end-to-end execution with FRED data, numerical reproduction of all output tables and figures, exact dependency versions, or an out-of-sample forecast test. / 尚未验证联网全流程运行、全部结果数值复现、精确依赖版本或样本外预测性能。

### Known methodological cautions | 已知方法局限

1. **Overlapping forward 22/60-day outcomes.** Group comparisons use ordinary Welch t-tests and may understate uncertainty; the regressions explicitly use HAC covariance with 22/60 lags. / 未来窗口重叠，分组t检验未进行相应依赖修正，OLS采用HAC标准误。
2. **No isolated Hurst control group.** Composite-signal days are compared with other bear-state days, not conditionally matched Hurst≤0.5 days. / 尚未固定传统VIX条件后比较高低Hurst组。
3. **In-sample analysis only.** Model AIC/adjusted R² differences do not prove out-of-sample predictive value. / AIC与调整R²改善不代表样本外预测改进。
4. **Drawdown definition.** Forward `mdd_fwd` is the minimum cumulative return relative to the initial signal-day price; distinguish it from the usual within-window peak-to-trough maximum drawdown. / 前瞻下行指标不是标准区间最大回撤。
5. **Strategy comparability.** S&P 500 index-level backtests, cash weights, cost assumptions and different average exposures limit investability and return comparisons. / 使用指数点位及简化的成本与仓位假设，结果不可直接作为真实投资组合绩效。

### Sharing | 公开前注意事项

Market data may have redistribution restrictions, and journal policies on prior dissemination vary. Keep raw data and any complete thesis private until these questions are resolved; a separate public showcase can omit restricted inputs and the full thesis.

市场数据可能受再分发许可限制，期刊对公开传播也有不同要求。公开展示版宜单独建立干净仓库，不复制受限数据或论文全文，也不直接公开含历史私有提交的原仓库。
