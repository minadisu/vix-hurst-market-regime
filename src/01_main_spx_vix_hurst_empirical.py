# -*- coding: utf-8 -*-
"""
01_main_spx_vix_hurst_empirical.py

S&P 500 熊市修复阶段识别：传统市场变量 + VIX变量 + VIX-Hurst变量。

运行前准备：
1. 将 spx.csv 放在 SPX_PATH 指定位置；
2. 代码会自动从 FRED 下载 VIXCLS；
3. 输出结果会保存在 OUTPUT_DIR 下，包括论文表格和图片。

核心输出：
- Table1_hurst_descriptive.csv
- Table2_signal_summary.csv
- Table3_group_test_core.csv
- Table4_ols_full_sample_60d.csv
- Table5_ols_bear_sample_60d.csv
- Table6_hurst_significant_coefficients.csv
- Figure1_spx_vix_hurst_signals.png
- Figure2_hurst_windows.png
- Figure3_signal_yearly_distribution.png
- Figure4_model_aic_comparison_60d.png
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm

# ============================================================
# 0. 参数设置
# ============================================================

SPX_PATH = str(Path(__file__).resolve().parents[1] / "data" / "spx.csv")
OUTPUT_DIR = str(Path(__file__).resolve().parents[1] / "outputs" / "main_empirical")

START_DATE = "2000-01-01"
END_DATE = "2024-12-31"
FORWARD_WINDOWS = [22, 60]
MAIN_HURST_COL = "hurst_dfa_ret_90"

ROUND_DIGITS = 4

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. 数据读取函数
# ============================================================

def read_price_file(path, name):
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到文件：{path}")

    data = pd.read_csv(path)

    if "Date" not in data.columns:
        raise ValueError(f"{name} 文件中必须有 Date 列。")

    data["Date"] = pd.to_datetime(data["Date"])

    if "Adj Close" in data.columns:
        price_col = "Adj Close"
    elif "Close" in data.columns:
        price_col = "Close"
    elif "Price" in data.columns:
        price_col = "Price"
    else:
        raise ValueError(f"{name} 文件中必须有 Adj Close、Close 或 Price 列。")

    data[price_col] = (
        data[price_col]
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    data[price_col] = pd.to_numeric(data[price_col], errors="coerce")

    s = data.set_index("Date")[price_col].copy()
    s = s.sort_index().dropna()
    s.name = name
    return s


def read_fred_series(series_id, name, start_date, end_date):
    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}"
        f"&cosd={start_date}"
        f"&coed={end_date}"
    )
    data = pd.read_csv(url)

    if "observation_date" in data.columns:
        date_col = "observation_date"
    elif "DATE" in data.columns:
        date_col = "DATE"
    else:
        raise ValueError(f"{series_id} 数据中找不到日期列。")

    if series_id not in data.columns:
        raise ValueError(f"{series_id} 数据中找不到数值列。")

    data[date_col] = pd.to_datetime(data[date_col])
    data[series_id] = pd.to_numeric(data[series_id], errors="coerce")

    s = data.set_index(date_col)[series_id].copy()
    s = s.sort_index().dropna()
    s.name = name
    return s

# ============================================================
# 2. 指标函数
# ============================================================

def hurst_dfa(x, min_scale=5, max_scale=22, n_scales=8):
    """DFA scaling exponent, used as Hurst-like measure of Δlog(VIX)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 30:
        return np.nan
    if max_scale is None:
        max_scale = n // 4
    if max_scale <= min_scale + 2:
        return np.nan

    y = np.cumsum(x - np.mean(x))
    scales = np.unique(
        np.floor(np.logspace(np.log10(min_scale), np.log10(max_scale), n_scales)).astype(int)
    )

    flucts = []
    valid_scales = []
    for scale in scales:
        n_segments = n // scale
        if n_segments < 2:
            continue

        rms_list = []
        for i in range(n_segments):
            segment = y[i * scale:(i + 1) * scale]
            t = np.arange(scale)
            coeffs = np.polyfit(t, segment, 1)
            trend = np.polyval(coeffs, t)
            residual = segment - trend
            rms = np.sqrt(np.mean(residual ** 2))
            if np.isfinite(rms) and rms > 0:
                rms_list.append(rms)

        if rms_list:
            flucts.append(np.mean(rms_list))
            valid_scales.append(scale)

    flucts = np.asarray(flucts)
    valid_scales = np.asarray(valid_scales)
    if len(flucts) < 3:
        return np.nan

    slope, _ = np.polyfit(np.log(valid_scales), np.log(flucts), 1)
    return slope


def future_max_drawdown(prices, window):
    result = []
    arr = prices.values
    for i in range(len(arr)):
        if i + window >= len(arr):
            result.append(np.nan)
            continue
        future_path = arr[i:i + window + 1]
        start_price = future_path[0]
        drawdowns = future_path / start_price - 1
        result.append(drawdowns.min())
    return pd.Series(result, index=prices.index)

# ============================================================
# 3. 构造数据集
# ============================================================

def build_dataset():
    spx = read_price_file(SPX_PATH, "spx").loc[START_DATE:END_DATE]
    vix = read_fred_series("VIXCLS", "vix", START_DATE, END_DATE)

    df = pd.concat([spx, vix], axis=1, sort=True).dropna()

    # 基础收益与未来变量
    df["spx_ret"] = np.log(df["spx"] / df["spx"].shift(1))
    df["vix_ret"] = np.log(df["vix"] / df["vix"].shift(1))

    for k in FORWARD_WINDOWS:
        df[f"spx_fwd_ret_{k}d"] = np.log(df["spx"].shift(-k) / df["spx"])
        df[f"vix_fwd_change_{k}d"] = np.log(df["vix"].shift(-k) / df["vix"])
        df[f"rv_fwd_{k}d"] = df["spx_ret"].shift(-k).rolling(k).std() * np.sqrt(252)
        df[f"mdd_fwd_{k}d"] = future_max_drawdown(df["spx"], k)

    # 第一层：传统市场变量
    df["ret_1m"] = np.log(df["spx"] / df["spx"].shift(22))
    df["ret_3m"] = np.log(df["spx"] / df["spx"].shift(63))
    df["ret_6m"] = np.log(df["spx"] / df["spx"].shift(126))
    df["rv_1m"] = df["spx_ret"].rolling(22).std() * np.sqrt(252)
    df["rv_3m"] = df["spx_ret"].rolling(63).std() * np.sqrt(252)
    df["ma200"] = df["spx"].rolling(200).mean()
    df["ma50"] = df["spx"].rolling(50).mean()
    df["ma200_gap"] = df["spx"] / df["ma200"] - 1
    df["ma50_gap"] = df["spx"] / df["ma50"] - 1
    df["bull"] = (df["spx"] > df["ma200"]).astype(int)
    df["bear"] = (df["spx"] < df["ma200"]).astype(int)
    df["rolling_peak_3m"] = df["spx"].rolling(63).max()
    df["drawdown_from_3m_peak"] = df["spx"] / df["rolling_peak_3m"] - 1
    df["rolling_peak_6m"] = df["spx"].rolling(126).max()
    df["drawdown_from_6m_peak"] = df["spx"] / df["rolling_peak_6m"] - 1

    # 第二层：VIX变量
    df["log_vix"] = np.log(df["vix"])
    df["dlog_vix"] = df["log_vix"].diff()
    df["vix_change_5d"] = np.log(df["vix"] / df["vix"].shift(5))
    df["vix_change_22d"] = np.log(df["vix"] / df["vix"].shift(22))
    df["vix_up_5d"] = (df["vix_change_5d"] > 0).astype(int)
    df["vix_down_5d"] = (df["vix_change_5d"] < 0).astype(int)
    df["vix_q20"] = df["vix"].rolling(252).quantile(0.20)
    df["vix_q80"] = df["vix"].rolling(252).quantile(0.80)
    df["vix_q90"] = df["vix"].rolling(252).quantile(0.90)
    df["vix_low"] = (df["vix"] < df["vix_q20"]).astype(int)
    df["vix_high"] = (df["vix"] > df["vix_q80"]).astype(int)
    df["vix_extreme"] = (df["vix"] > df["vix_q90"]).astype(int)
    df["vix_z"] = (df["vix"] - df["vix"].rolling(252).mean()) / df["vix"].rolling(252).std()
    df["vix_high_down"] = ((df["vix_high"] == 1) & (df["vix_down_5d"] == 1)).astype(int)
    df["vix_high_up"] = ((df["vix_high"] == 1) & (df["vix_up_5d"] == 1)).astype(int)

    # 第三层：VIX-Hurst变量
    df["hurst_dfa_ret_45"] = df["dlog_vix"].rolling(45).apply(
        lambda x: hurst_dfa(x, min_scale=4, max_scale=12, n_scales=6), raw=False
    )
    df["hurst_dfa_ret_60"] = df["dlog_vix"].rolling(60).apply(
        lambda x: hurst_dfa(x, min_scale=4, max_scale=15, n_scales=7), raw=False
    )
    df["hurst_dfa_ret_90"] = df["dlog_vix"].rolling(90).apply(
        lambda x: hurst_dfa(x, min_scale=5, max_scale=22, n_scales=8), raw=False
    )
    df["hurst_dfa_ret_120"] = df["dlog_vix"].rolling(120).apply(
        lambda x: hurst_dfa(x, min_scale=5, max_scale=30, n_scales=8), raw=False
    )
    df["hurst_main"] = df[MAIN_HURST_COL]
    df["hurst_high_05"] = (df["hurst_main"] > 0.5).astype(int)
    df["hurst_low_05"] = (df["hurst_main"] < 0.5).astype(int)
    df["hurst_change_5d"] = df["hurst_main"] - df["hurst_main"].shift(5)
    df["hurst_decline"] = (df["hurst_change_5d"] < 0).astype(int)

    # 核心组合信号
    df["bear_vix_high_down_hhigh"] = (
        (df["bear"] == 1) &
        (df["vix_high"] == 1) &
        (df["vix_down_5d"] == 1) &
        (df["hurst_high_05"] == 1)
    ).astype(int)
    df["bear_vix_high_up_hhigh"] = (
        (df["bear"] == 1) &
        (df["vix_high"] == 1) &
        (df["vix_up_5d"] == 1) &
        (df["hurst_high_05"] == 1)
    ).astype(int)
    df["vix_high_down_hhigh"] = (
        (df["vix_high"] == 1) &
        (df["vix_down_5d"] == 1) &
        (df["hurst_high_05"] == 1)
    ).astype(int)
    df["vix_high_up_hhigh"] = (
        (df["vix_high"] == 1) &
        (df["vix_up_5d"] == 1) &
        (df["hurst_high_05"] == 1)
    ).astype(int)

    # 修复状态目标变量
    for k in FORWARD_WINDOWS:
        df[f"recovery_loose_{k}d"] = (
            (df[f"spx_fwd_ret_{k}d"] > 0) &
            (df[f"vix_fwd_change_{k}d"] < 0)
        ).astype(int)
        df[f"recovery_strict_{k}d"] = (
            (df[f"spx_fwd_ret_{k}d"] > 0) &
            (df[f"vix_fwd_change_{k}d"] < 0) &
            (df[f"mdd_fwd_{k}d"] > -0.05)
        ).astype(int)
        df[f"risk_ease_{k}d"] = (
            (df[f"vix_fwd_change_{k}d"] < 0) &
            (df[f"rv_fwd_{k}d"] < df["rv_3m"])
        ).astype(int)

    test_df = df.dropna().copy()
    return df, test_df

# ============================================================
# 4. 分组检验与回归
# ============================================================

def group_test(data, signal_col, y_col, control_state=None):
    signal_group = data.loc[data[signal_col] == 1, y_col].dropna()
    if control_state is None:
        other_group = data.loc[data[signal_col] == 0, y_col].dropna()
    else:
        other_group = data.loc[
            (data[signal_col] == 0) & (data[control_state] == 1), y_col
        ].dropna()

    if len(signal_group) < 2 or len(other_group) < 2:
        return {
            "signal": signal_col, "target": y_col, "control_state": control_state,
            "signal_mean": np.nan, "other_mean": np.nan, "difference": np.nan,
            "signal_count": len(signal_group), "other_count": len(other_group),
            "t_stat": np.nan, "p_value": np.nan
        }

    t_stat, p_value = stats.ttest_ind(signal_group, other_group, equal_var=False, nan_policy="omit")
    return {
        "signal": signal_col,
        "target": y_col,
        "control_state": control_state,
        "signal_mean": signal_group.mean(),
        "other_mean": other_group.mean(),
        "difference": signal_group.mean() - other_group.mean(),
        "signal_count": len(signal_group),
        "other_count": len(other_group),
        "t_stat": t_stat,
        "p_value": p_value
    }


def run_ols_model(data, y_col, x_cols, hac_lags):
    reg_data = data[[y_col] + x_cols].dropna().copy()
    y = reg_data[y_col]
    X = sm.add_constant(reg_data[x_cols])
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    return model

# ============================================================
# 5. 表格输出
# ============================================================

def save_table(df, filename, round_digits=ROUND_DIGITS):
    out = df.copy()
    numeric_cols = out.select_dtypes(include=[np.number]).columns
    out[numeric_cols] = out[numeric_cols].round(round_digits)
    out.to_csv(Path(OUTPUT_DIR) / filename, index=False, encoding="utf-8-sig")


def make_tables(test_df):
    # 表1：Hurst描述性统计
    hurst_cols = ["hurst_dfa_ret_45", "hurst_dfa_ret_60", "hurst_dfa_ret_90", "hurst_dfa_ret_120"]
    rows = []
    for col in hurst_cols:
        s = test_df[col].dropna()
        d = s.describe(percentiles=[0.25, 0.5, 0.75]).to_dict()
        rows.append({
            "variable": col,
            "count": d["count"], "mean": d["mean"], "std": d["std"], "min": d["min"],
            "p25": d["25%"], "median": d["50%"], "p75": d["75%"], "max": d["max"],
            "share_gt_0.5": (s > 0.5).mean(),
            "share_lt_0.5": (s < 0.5).mean()
        })
    table1 = pd.DataFrame(rows)
    save_table(table1, "Table1_hurst_descriptive.csv")

    # 表2：核心信号统计
    signal_cols = [
        "vix_high_down", "vix_high_up", "bear_vix_high_down_hhigh",
        "bear_vix_high_up_hhigh", "vix_high_down_hhigh", "vix_high_up_hhigh"
    ]
    rows = []
    for col in signal_cols:
        temp = test_df[test_df[col] == 1]
        yearly = temp.groupby(temp.index.year).size()
        yearly_str = "; ".join([f"{int(y)}:{int(v)}" for y, v in yearly.items()])
        rows.append({
            "signal": col,
            "signal_days": int(test_df[col].sum()),
            "signal_ratio": test_df[col].mean(),
            "yearly_distribution": yearly_str
        })
    table2 = pd.DataFrame(rows)
    save_table(table2, "Table2_signal_summary.csv")

    # 表3：核心分组检验
    group_targets = []
    for k in FORWARD_WINDOWS:
        group_targets.extend([
            f"spx_fwd_ret_{k}d", f"vix_fwd_change_{k}d", f"rv_fwd_{k}d", f"mdd_fwd_{k}d",
            f"recovery_loose_{k}d", f"recovery_strict_{k}d", f"risk_ease_{k}d"
        ])
    group_results = []
    for sig in signal_cols:
        control = "bear" if sig.startswith("bear") else None
        for target in group_targets:
            group_results.append(group_test(test_df, sig, target, control_state=control))
    group_table = pd.DataFrame(group_results)
    save_table(group_table, "Full_group_test_results.csv")

    core_signals = ["vix_high_down", "bear_vix_high_down_hhigh", "bear_vix_high_up_hhigh"]
    core_targets = [
        "spx_fwd_ret_22d", "vix_fwd_change_22d", "rv_fwd_22d", "mdd_fwd_22d",
        "spx_fwd_ret_60d", "vix_fwd_change_60d", "rv_fwd_60d", "mdd_fwd_60d",
        "recovery_loose_60d", "recovery_strict_60d", "risk_ease_60d"
    ]
    table3 = group_table[group_table["signal"].isin(core_signals) & group_table["target"].isin(core_targets)].copy()
    save_table(table3, "Table3_group_test_core.csv")

    # OLS模型设定
    traditional_vars = [
        "ret_1m", "ret_3m", "ret_6m", "rv_1m", "rv_3m", "ma200_gap", "ma50_gap",
        "drawdown_from_3m_peak", "drawdown_from_6m_peak", "bear"
    ]
    vix_vars = ["vix_z", "vix_change_5d", "vix_change_22d", "vix_high", "vix_high_down", "vix_high_up"]
    hurst_vars = [
        "hurst_main", "hurst_change_5d", "hurst_high_05", "hurst_decline",
        "bear_vix_high_down_hhigh", "bear_vix_high_up_hhigh"
    ]
    model_specs = {
        "M1_traditional": traditional_vars,
        "M2_traditional_vix": traditional_vars + vix_vars,
        "M3_traditional_vix_hurst": traditional_vars + vix_vars + hurst_vars
    }
    ols_targets = []
    for k in FORWARD_WINDOWS:
        ols_targets.extend([
            f"spx_fwd_ret_{k}d", f"vix_fwd_change_{k}d", f"rv_fwd_{k}d", f"mdd_fwd_{k}d",
            f"recovery_loose_{k}d", f"recovery_strict_{k}d", f"risk_ease_{k}d"
        ])

    def run_model_set(data, sample_name):
        model_rows = []
        coef_rows = []
        for y_col in ols_targets:
            hac_lags = 22 if "22d" in y_col else 60
            for model_name, x_cols in model_specs.items():
                if sample_name == "bear_only":
                    x_cols = [x for x in x_cols if x != "bear"]
                model = run_ols_model(data, y_col, x_cols, hac_lags)
                model_rows.append({
                    "sample": sample_name,
                    "target": y_col,
                    "model": model_name,
                    "nobs": int(model.nobs),
                    "r_squared": model.rsquared,
                    "adj_r_squared": model.rsquared_adj,
                    "aic": model.aic,
                    "bic": model.bic
                })
                for var in hurst_vars:
                    if var in model.params.index:
                        coef_rows.append({
                            "sample": sample_name,
                            "target": y_col,
                            "model": model_name,
                            "variable": var,
                            "coef": model.params[var],
                            "t_value": model.tvalues[var],
                            "p_value": model.pvalues[var],
                            "nobs": int(model.nobs),
                            "r_squared": model.rsquared,
                            "adj_r_squared": model.rsquared_adj
                        })
        return pd.DataFrame(model_rows), pd.DataFrame(coef_rows)

    model_compare_full, hurst_coef_full = run_model_set(test_df, "full_sample")
    bear_df = test_df[test_df["bear"] == 1].copy()
    model_compare_bear, hurst_coef_bear = run_model_set(bear_df, "bear_only")

    save_table(model_compare_full, "Full_ols_model_comparison.csv")
    save_table(hurst_coef_full, "Full_hurst_coefficients.csv")
    save_table(model_compare_bear, "Full_bear_only_ols_model_comparison.csv")
    save_table(hurst_coef_bear, "Full_bear_only_hurst_coefficients.csv")

    table4 = model_compare_full[model_compare_full["target"].str.contains("60d")].copy()
    save_table(table4, "Table4_ols_full_sample_60d.csv")

    table5 = model_compare_bear[model_compare_bear["target"].str.contains("60d")].copy()
    save_table(table5, "Table5_ols_bear_sample_60d.csv")

    sig_coef = pd.concat([hurst_coef_full, hurst_coef_bear], axis=0, ignore_index=True)
    sig_coef = sig_coef[sig_coef["p_value"] < 0.05].copy()
    # 论文表只保留核心变量，避免过长
    core_hurst_vars = [
        "hurst_main", "hurst_change_5d", "hurst_high_05",
        "bear_vix_high_down_hhigh", "bear_vix_high_up_hhigh"
    ]
    table6 = sig_coef[sig_coef["variable"].isin(core_hurst_vars)].copy()
    save_table(table6, "Table6_hurst_significant_coefficients.csv")

    return {
        "table1": table1, "table2": table2, "group_table": group_table,
        "model_compare_full": model_compare_full, "model_compare_bear": model_compare_bear,
        "hurst_coef_full": hurst_coef_full, "hurst_coef_bear": hurst_coef_bear
    }

# ============================================================
# 6. 图片输出
# ============================================================

def save_fig(path):
    plt.tight_layout()
    plt.savefig(Path(OUTPUT_DIR) / path, dpi=300, bbox_inches="tight")
    plt.close()


def make_figures(test_df, tables):
    # Figure 1: SPX / VIX / Hurst / core signals
    fig = plt.figure(figsize=(14, 12))
    ax1 = plt.subplot(4, 1, 1)
    ax1.plot(test_df.index, test_df["spx"], label="S&P 500")
    ax1.plot(test_df.index, test_df["ma200"], linestyle="--", label="200-day MA")
    ax1.set_title("S&P 500, VIX and VIX-Hurst")
    ax1.legend()
    ax1.grid(True)

    ax2 = plt.subplot(4, 1, 2, sharex=ax1)
    ax2.plot(test_df.index, test_df["vix"], label="VIX")
    ax2.plot(test_df.index, test_df["vix_q80"], linestyle="--", label="VIX 252d Q80")
    ax2.plot(test_df.index, test_df["vix_q20"], linestyle="--", label="VIX 252d Q20")
    ax2.legend()
    ax2.grid(True)

    ax3 = plt.subplot(4, 1, 3, sharex=ax1)
    ax3.plot(test_df.index, test_df["hurst_main"], label="90-day DFA-Hurst of Δlog(VIX)")
    ax3.axhline(0.5, linestyle=":", label="H = 0.5")
    ax3.legend()
    ax3.grid(True)

    ax4 = plt.subplot(4, 1, 4, sharex=ax1)
    ax4.plot(test_df.index, test_df["bear_vix_high_down_hhigh"], label="Bear + High VIX + VIX Down + Hurst High")
    ax4.plot(test_df.index, test_df["bear_vix_high_up_hhigh"], label="Bear + High VIX + VIX Up + Hurst High")
    ax4.legend()
    ax4.grid(True)
    save_fig("Figure1_spx_vix_hurst_signals.png")

    # Figure 2: Hurst windows
    plt.figure(figsize=(14, 6))
    for col in ["hurst_dfa_ret_45", "hurst_dfa_ret_60", "hurst_dfa_ret_90", "hurst_dfa_ret_120"]:
        plt.plot(test_df.index, test_df[col], label=col)
    plt.axhline(0.5, linestyle="--", label="H = 0.5")
    plt.title("DFA-Hurst of Δlog(VIX) with Different Rolling Windows")
    plt.xlabel("Date")
    plt.ylabel("DFA-Hurst")
    plt.legend()
    plt.grid(True)
    save_fig("Figure2_hurst_windows.png")

    # Figure 3: yearly distribution of core signals
    core = ["bear_vix_high_down_hhigh", "bear_vix_high_up_hhigh"]
    yearly = pd.DataFrame({sig: test_df[test_df[sig] == 1].groupby(test_df[test_df[sig] == 1].index.year).size() for sig in core}).fillna(0)
    yearly.plot(kind="bar", figsize=(14, 6))
    plt.title("Yearly Distribution of Core VIX-Hurst Signals")
    plt.xlabel("Year")
    plt.ylabel("Signal days")
    plt.grid(True)
    save_fig("Figure3_signal_yearly_distribution.png")

    # Figure 4: 60d AIC comparison, full and bear-only
    full_60 = tables["model_compare_full"][tables["model_compare_full"]["target"].str.contains("60d")]
    bear_60 = tables["model_compare_bear"][tables["model_compare_bear"]["target"].str.contains("60d")]
    key_targets = ["spx_fwd_ret_60d", "vix_fwd_change_60d", "rv_fwd_60d", "mdd_fwd_60d"]
    full_60 = full_60[full_60["target"].isin(key_targets)]
    bear_60 = bear_60[bear_60["target"].isin(key_targets)]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    full_pivot = full_60.pivot(index="target", columns="model", values="aic")
    full_pivot.plot(kind="bar", ax=axes[0])
    axes[0].set_title("Full Sample: AIC Comparison for 60-day Targets")
    axes[0].set_ylabel("AIC")
    axes[0].grid(True)

    bear_pivot = bear_60.pivot(index="target", columns="model", values="aic")
    bear_pivot.plot(kind="bar", ax=axes[1])
    axes[1].set_title("Bear-Only Sample: AIC Comparison for 60-day Targets")
    axes[1].set_ylabel("AIC")
    axes[1].grid(True)
    save_fig("Figure4_model_aic_comparison_60d.png")

# ============================================================
# 7. 主程序
# ============================================================

def main():
    raw_df, test_df = build_dataset()
    raw_df.to_csv(Path(OUTPUT_DIR) / "raw_spx_vix_with_variables.csv", encoding="utf-8-sig")
    test_df.to_csv(Path(OUTPUT_DIR) / "analysis_sample.csv", encoding="utf-8-sig")

    print("Analysis sample:", test_df.index.min(), "to", test_df.index.max(), "shape=", test_df.shape)

    tables = make_tables(test_df)
    make_figures(test_df, tables)

    print("\nFinished. Results saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()