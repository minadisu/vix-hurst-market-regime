# Research Brief | 研究简报

**Title / 题目:** *Identifying Risk-Recovery Regimes in the S&P 500 with VIX Dynamics and the DFA-Hurst Exponent*  
**Status / 状态:** Preliminary undergraduate empirical research; not a published or peer-reviewed paper. / 本科阶段的初步实证研究，尚未发表或经过同行评审。

## Abstract | 摘要

**English.** This study examines whether the persistence of changes in option-implied volatility provides incremental information about equity-market risk recovery. We estimate a rolling detrended fluctuation analysis (DFA) exponent on daily changes in log(VIX), with a 90-trading-day main window, and combine it with S&P 500 trend and VIX-state indicators. Using daily observations in 2000–2024, the research explores conditional signals, forward 22- and 60-trading-day market outcomes, and nested regression specifications. In the bear-market subsample, reported adjusted R² for 60-day forward S&P 500 returns increases from 11.01% under traditional-plus-VIX controls (M2) to 17.55% when VIX-Hurst variables are added (M3). Supplementary allocation and cross-asset exercises illustrate possible applications but do not validate a tradable forecasting rule. Results remain in sample and require more stringent dependence-aware inference and out-of-sample testing.

**中文。** 本研究考察隐含波动率变化的持续性，能否为股票市场风险修复状态识别提供增量信息。研究对 VIX 对数变化率估计滚动 DFA-Hurst 指数，以90个交易日为主要窗口，并结合标普500趋势和 VIX 状态构造信号。基于2000—2024年日度样本，分析未来22日与60日风险表现，并采用递进回归模型进行比较。在熊市子样本中，未来60日标普500收益模型的调整 R² 从 M2 的11.01%提高至 M3 的17.55%。仓位管理及跨资产分析仅用于应用探索，不能证明已获得可交易的预测优势。现有发现仍是样本内结果，有待依赖稳健推断和样本外验证。

## Research question | 研究问题

Does a measure of **volatility persistence** add information beyond conventional equity-market and VIX level/direction variables *conditional on weak equity-market states*? The study is **not** designed as a universal bottom-finding model.

在弱势股票市场状态下，波动率持续性指标能否补充传统市场变量及 VIX 水平、变化方向的信息？本研究不以普遍性的“抄底模型”为目标。

## Data & model design | 数据与模型设计

| Component / 环节 | Specification / 设定 |
|---|---|
| Main period / 主区间 | 2000–2024 daily observations / 2000—2024年日度数据 |
| Equity series / 股票市场 | S&P 500 price level; returns, moving-average gaps, trailing volatility and drawdowns / 标普500价格、收益、均线偏离、历史波动率与回撤 |
| Volatility series / 隐含波动率 | VIX level, rolling quantiles and 5/22-day changes / VIX水平、滚动分位和5/22日变化 |
| Persistence / 持续性 | DFA slope on Δlog(VIX), 45/60/90/120-day rolling windows; main 90-day / 对Δlog(VIX)进行DFA，90日为主窗口 |
| Core regime / 核心状态 | S&P 500 < MA200; VIX > trailing 252-day Q80; VIX 5-day change < 0; Hurst(90d) > 0.5 / 熊市、VIX高位且回落、Hurst高于0.5 |
| Outcomes / 未来指标 | 22/60-day forward returns, VIX changes, realized volatility, downside-path measure, recovery classifications / 未来收益、VIX变化、实现波动率、下行路径与修复分类 |
| Nested models / 递进模型 | M1: market factors; M2: M1 + VIX measures; M3: M2 + VIX-Hurst terms / M1传统市场变量，M2增加VIX，M3再加入Hurst信息 |

The `mdd_fwd` variable in the supplied scripts measures the *minimum future return relative to the starting price*; it is not the standard peak-to-trough maximum drawdown.

原程序中的 `mdd_fwd` 是相对信号日价格的未来最低累计收益，而不是标准的区间峰谷最大回撤，两者不能混用。

## Selected results | 代表性结果

1. **Hurst distribution / Hurst分布:** The reported 90-day DFA-Hurst mean is **0.5402** across 5,978 retained observations; **64.84%** exceed 0.5. / 90日Hurst均值0.5402，超过0.5的比例64.84%。
2. **Core state frequency / 信号频率:** The bear/high-VIX/falling-VIX/high-Hurst state occurs on **170 days (2.84%)**; the high/rising-VIX counterpart occurs on **225 days (3.76%)**. / 核心回落信号170日（2.84%），上行对应信号225日（3.76%）。
3. **Nested model fit / 模型拟合:** In the bear subsample, 60-day forward equity returns have adjusted R² of **11.01% for M2** and **17.55% for M3**; AIC improves from **−2881.91** to **−3008.35**. / 熊市子样本中加入Hurst信息后，未来60日收益率模型的样本内拟合改善。
4. **Descriptive group differences / 描述性分组差异:** The core signal's reported mean 60-day forward log return is **5.15%**, compared with **−0.62%** for *other bear-market days*. This comparison is **not a matched high- versus low-Hurst experiment** and uses overlapping observations. / 核心信号日未来60日平均对数收益为5.15%，其余熊市日为−0.62%；该比较并未固定VIX状态后单独识别Hurst效应，且存在窗口重叠。
5. **Application illustration / 应用示例:** The dynamic strategy has a reported annualized return of **3.91%**, volatility of **10.83%** and maximum drawdown of **−34.43%**, versus buy-and-hold **6.43%**, **19.29%**, and **−56.78%**. The lower volatility comes alongside lower return/exposure; this is not evidence of alpha. / 动态策略波动与回撤较低，但收益和平均仓位也较低，不能据此证明超额收益。

See [reported tables](../results/tables/) and [nine figures](../results/figures/). / 对照完整[结果表格](../results/tables/)和[研究图表](../results/figures/)。

## Interpretation & next checks | 解释与后续检验

The main contribution is a **conditional state-identification question** and a structured M1–M3 empirical comparison. Limitations are substantive, not simply presentation details:

- Compare **Hurst > 0.5 vs. Hurst ≤ 0.5** within the *same* bear/high-VIX/falling-VIX state to isolate incremental Hurst information. / 固定熊市、VIX高位和回落条件，对比高低Hurst组。
- Account for serial dependence and overlapping future windows (HAC/event-level tests/block bootstrap, as appropriate). OLS employs HAC, but the reported Welch group tests do not. / 针对重叠窗口采用适当的依赖稳健方法；OLS已有HAC，分组t检验仍需修正。
- Implement chronologically separated out-of-sample evaluation and stronger benchmark models; avoid tuning thresholds on the full test set. / 增加严格按时间划分的样本外检验和基准模型。
- Test alternate Hurst windows/estimators and practical assumptions; distinguish downside relative to signal price from peak-to-trough drawdown. / 检验窗口与估计稳健性，并严格区分回撤指标。

**No full thesis PDF is provided here.** This is a standalone research overview linked to code and reported outputs, not a substitute for journal review. / 本仓库不提供论文全文；本简报仅概述研究并关联代码与结果，不能替代期刊评审。
