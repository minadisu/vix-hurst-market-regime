VIX-Hurst 论文代码
文件说明：

1. 01_main_spx_vix_hurst_empirical.py
   主论文实证代码。
   研究 S&P 500 熊市修复阶段中，VIX-Hurst 是否在传统变量和 VIX 变量之外具有增量识别价值。
   输出论文主表和主图。

2. 02_strategy_application.py
   策略应用检验代码。
   不作为主实证，只用于论文应用部分或附录。
   输出策略绩效、年度收益、年度最大回撤、净值图、回撤图和仓位图。

3. 03_gold_oil_extension_optional.py
   黄金和原油扩展检验代码。
   需要桌面有 gld.csv 和 uso.csv。

运行顺序：
1. 先运行 01_main_spx_vix_hurst_empirical.py。
2. 策略部分需要时运行 02_strategy_application.py。
3. 黄金原油扩展需要时运行 03_gold_oil_extension_optional.py。

注意：
- 需要本地有 spx.csv。
- 主代码会自动从 FRED 下载 VIXCLS。
- 输出路径可在每个文件顶部的 OUTPUT_DIR 中修改。