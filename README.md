# 隐含波动率信息与股票市场风险修复识别

**VIX-Hurst Market Regime Identification** · 私人研究仓库

本仓库按原始项目的「代码 / 论文 / 数据」三部分整理，以便管理论文写作、实证程序和数据，不将辅助文档分散到多个顶层目录。

## 目录

- **[代码](代码/)**：三份 Python 研究脚本、原始代码说明、环境依赖及「输出结果」。输出结果目前包含论文表1—表7的 CSV 导出和图表清单。
- **[论文](论文/)**：为原始 `main`（正文）和 `appendix`（附录）保留目录，附研究方法备注。原文件夹中的写作源文件尚未收到；`Paper_Tables.xlsx` 原件和含个人信息的完整课程报告 PDF 暂未提交仓库。
- **[数据](数据/)**：S&P 500、GLD、USO、GVZCLS 和 OVXCLS 的 CSV 数据，保持原始字段与顺序。

## 执行

```bash
pip install -r 代码/requirements.txt
python 代码/01_main_spx_vix_hurst_empirical.py
python 代码/02_strategy_application.py
python 代码/03_gold_oil_extension_optional.py
```

三份脚本在运行时通过 FRED 下载隐含波动率序列，包括 VIXCLS。生成的文件将保存在「代码/输出结果」中对应的子文件夹；详见「代码/运行说明.md」。

**研究状态：** 表格和图形为已有的样本内结果，尚未完成全流程独立复现与样本外验证。22/60日目标变量存在重叠窗口问题，分组显著性解释需谨慎。暂不宜将成果称为经过验证的预测模型。

本仓库当前为 Private。若准备公开或投稿，需先核实市场数据的再分发授权、个人信息及期刊政策。
