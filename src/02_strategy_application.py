# -*- coding: utf-8 -*-
"""
02_strategy_application.py

VIX-Hurst 状态信号的策略应用检验。

定位：论文附加应用，不作为主实证。
输出：策略绩效表、年度收益、年度最大回撤、净值图、回撤图、仓位图。
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 0. 参数设置
# ============================================================

SPX_PATH = str(Path(__file__).resolve().parents[1] / "data" / "spx.csv")
OUTPUT_DIR = str(Path(__file__).resolve().parents[1] / "outputs" / "strategy")

START_DATE = "2000-01-01"
END_DATE = "2024-12-31"
MAIN_HURST_COL = "hurst_dfa_ret_90"
TRADING_COST = 0.0005

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. 数据与指标函数
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
    data[price_col] = data[price_col].astype(str).str.replace(",", "", regex=False)
    data[price_col] = pd.to_numeric(data[price_col], errors="coerce")
    s = data.set_index("Date")[price_col].sort_index().dropna()
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
    date_col = "observation_date" if "observation_date" in data.columns else "DATE"
    data[date_col] = pd.to_datetime(data[date_col])
    data[series_id] = pd.to_numeric(data[series_id], errors="coerce")
    s = data.set_index(date_col)[series_id].sort_index().dropna()
    s.name = name
    return s


def hurst_dfa(x, min_scale=5, max_scale=22, n_scales=8):
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
    scales = np.unique(np.floor(np.logspace(np.log10(min_scale), np.log10(max_scale), n_scales)).astype(int))
    flucts, valid_scales = [], []
    for scale in scales:
        n_segments = n // scale
        if n_segments < 2:
            continue
        rms_list = []
        for i in range(n_segments):
            segment = y[i * scale:(i + 1) * scale]
            t = np.arange(scale)
            coeffs = np.polyfit(t, segment, 1)
            residual = segment - np.polyval(coeffs, t)
            rms = np.sqrt(np.mean(residual ** 2))
            if np.isfinite(rms) and rms > 0:
                rms_list.append(rms)
        if rms_list:
            flucts.append(np.mean(rms_list))
            valid_scales.append(scale)
    if len(flucts) < 3:
        return np.nan
    slope, _ = np.polyfit(np.log(valid_scales), np.log(flucts), 1)
    return slope

# ============================================================
# 2. 构造策略数据
# ============================================================

def build_strategy_data():
    spx = read_price_file(SPX_PATH, "spx").loc[START_DATE:END_DATE]
    vix = read_fred_series("VIXCLS", "vix", START_DATE, END_DATE)
    df = pd.concat([spx, vix], axis=1, sort=True).dropna()

    df["spx_ret"] = np.log(df["spx"] / df["spx"].shift(1))
    df["log_vix"] = np.log(df["vix"])
    df["dlog_vix"] = df["log_vix"].diff()

    df["hurst_dfa_ret_90"] = df["dlog_vix"].rolling(90).apply(
        lambda x: hurst_dfa(x, min_scale=5, max_scale=22, n_scales=8), raw=False
    )
    df["hurst_dfa_ret_120"] = df["dlog_vix"].rolling(120).apply(
        lambda x: hurst_dfa(x, min_scale=5, max_scale=30, n_scales=8), raw=False
    )
    df["hurst_main"] = df[MAIN_HURST_COL]

    df["spx_ma200"] = df["spx"].rolling(200).mean()
    df["bull"] = (df["spx"] > df["spx_ma200"]).astype(int)
    df["bear"] = (df["spx"] < df["spx_ma200"]).astype(int)

    df["vix_q20"] = df["vix"].rolling(252).quantile(0.20)
    df["vix_q80"] = df["vix"].rolling(252).quantile(0.80)
    df["vix_low"] = (df["vix"] < df["vix_q20"]).astype(int)
    df["vix_high"] = (df["vix"] > df["vix_q80"]).astype(int)

    df["vix_change_5d"] = np.log(df["vix"] / df["vix"].shift(5))
    df["vix_up"] = (df["vix_change_5d"] > 0).astype(int)
    df["vix_down"] = (df["vix_change_5d"] < 0).astype(int)
    df["hurst_high_05"] = (df["hurst_main"] > 0.5).astype(int)

    df["bear_highvix_down_hhigh"] = (
        (df["bear"] == 1) & (df["vix_high"] == 1) & (df["vix_down"] == 1) & (df["hurst_high_05"] == 1)
    ).astype(int)
    df["bear_highvix_up_hhigh"] = (
        (df["bear"] == 1) & (df["vix_high"] == 1) & (df["vix_up"] == 1) & (df["hurst_high_05"] == 1)
    ).astype(int)
    df["bull_lowvix_hhigh"] = (
        (df["bull"] == 1) & (df["vix_low"] == 1) & (df["hurst_high_05"] == 1)
    ).astype(int)

    return df

# ============================================================
# 3. 回测函数
# ============================================================

def calculate_strategy_returns(data, position_col, ret_col="spx_ret", cost=0.0005):
    pos = data[position_col].copy()
    pos_lag = pos.shift(1).fillna(0)
    turnover = pos.diff().abs().fillna(0)
    return pos_lag * data[ret_col] - turnover * cost


def max_drawdown(nav):
    running_max = nav.cummax()
    return (nav / running_max - 1).min()


def annualized_return(nav, periods_per_year=252):
    total_return = nav.iloc[-1] / nav.iloc[0] - 1
    n_days = len(nav)
    return (1 + total_return) ** (periods_per_year / n_days) - 1


def annualized_volatility(ret, periods_per_year=252):
    return ret.std() * np.sqrt(periods_per_year)


def sharpe_ratio(ret, periods_per_year=252):
    ann_ret = ret.mean() * periods_per_year
    ann_vol = ret.std() * np.sqrt(periods_per_year)
    return np.nan if ann_vol == 0 else ann_ret / ann_vol


def calmar_ratio(nav):
    mdd = abs(max_drawdown(nav))
    return np.nan if mdd == 0 else annualized_return(nav) / mdd


def performance_summary(data, strategy_name, pos_col):
    ret = data[f"{strategy_name}_ret"].dropna()
    nav = data[f"{strategy_name}_nav"].dropna()
    pos = data[pos_col].dropna()
    turnover = pos.diff().abs().fillna(0)
    return {
        "strategy": strategy_name,
        "start": nav.index.min(),
        "end": nav.index.max(),
        "total_return": nav.iloc[-1] / nav.iloc[0] - 1,
        "annual_return": annualized_return(nav),
        "annual_volatility": annualized_volatility(ret),
        "sharpe_ratio": sharpe_ratio(ret),
        "max_drawdown": max_drawdown(nav),
        "calmar_ratio": calmar_ratio(nav),
        "avg_position": pos.mean(),
        "turnover_sum": turnover.sum(),
        "num_position_changes": int((turnover > 0).sum())
    }

# ============================================================
# 4. 主程序
# ============================================================

def main():
    df = build_strategy_data()
    bt = df.dropna(subset=["spx_ret", "hurst_main", "spx_ma200", "vix_q20", "vix_q80"]).copy()

    bt["pos_buy_hold"] = 1.0
    bt["pos_A_repair_only"] = np.where(bt["bear_highvix_down_hhigh"] == 1, 1.0, 0.0)

    bt["pos_B_dynamic"] = 0.50
    bt.loc[bt["bull_lowvix_hhigh"] == 1, "pos_B_dynamic"] = 1.00
    bt.loc[bt["bear_highvix_down_hhigh"] == 1, "pos_B_dynamic"] = 0.70

    bt["pos_C_risk_control"] = 0.50
    bt.loc[bt["bull_lowvix_hhigh"] == 1, "pos_C_risk_control"] = 1.00
    bt.loc[bt["bear_highvix_down_hhigh"] == 1, "pos_C_risk_control"] = 0.70
    bt.loc[bt["bear_highvix_up_hhigh"] == 1, "pos_C_risk_control"] = 0.00

    strategy_map = {
        "Buy_Hold": "pos_buy_hold",
        "A_Repair_Only": "pos_A_repair_only",
        "B_Dynamic": "pos_B_dynamic",
        "C_Risk_Control": "pos_C_risk_control"
    }

    rows = []
    for name, pos_col in strategy_map.items():
        bt[f"{name}_ret"] = calculate_strategy_returns(bt, pos_col, cost=TRADING_COST)
        bt[f"{name}_nav"] = np.exp(bt[f"{name}_ret"].cumsum())
        rows.append(performance_summary(bt, name, pos_col))

    perf = pd.DataFrame(rows)
    perf.round(4).to_csv(Path(OUTPUT_DIR) / "Table7_strategy_performance.csv", index=False, encoding="utf-8-sig")

    annual_returns = pd.DataFrame({
        name: bt[f"{name}_ret"].groupby(bt.index.year).sum().apply(np.exp) - 1
        for name in strategy_map
    })
    annual_returns.round(4).to_csv(Path(OUTPUT_DIR) / "strategy_annual_returns.csv", encoding="utf-8-sig")

    annual_mdd = {}
    for name in strategy_map:
        values = []
        for year, group in bt.groupby(bt.index.year):
            nav = group[f"{name}_nav"] / group[f"{name}_nav"].iloc[0]
            values.append({"year": year, name: max_drawdown(nav)})
        annual_mdd[name] = pd.DataFrame(values).set_index("year")[name]
    annual_mdd = pd.DataFrame(annual_mdd)
    annual_mdd.round(4).to_csv(Path(OUTPUT_DIR) / "strategy_annual_mdd.csv", encoding="utf-8-sig")

    signal_summary = pd.DataFrame({
        "signal": ["bear_highvix_down_hhigh", "bear_highvix_up_hhigh", "bull_lowvix_hhigh"],
        "signal_days": [
            int(bt["bear_highvix_down_hhigh"].sum()),
            int(bt["bear_highvix_up_hhigh"].sum()),
            int(bt["bull_lowvix_hhigh"].sum())
        ],
        "signal_ratio": [
            bt["bear_highvix_down_hhigh"].mean(),
            bt["bear_highvix_up_hhigh"].mean(),
            bt["bull_lowvix_hhigh"].mean()
        ]
    })
    signal_summary.round(4).to_csv(Path(OUTPUT_DIR) / "strategy_signal_summary.csv", index=False, encoding="utf-8-sig")

    bt.to_csv(Path(OUTPUT_DIR) / "strategy_backtest_full_data.csv", encoding="utf-8-sig")

    # 净值图
    plt.figure(figsize=(14, 7))
    for name in strategy_map:
        plt.plot(bt.index, bt[f"{name}_nav"], label=name)
    plt.title("Strategy Net Asset Value")
    plt.xlabel("Date")
    plt.ylabel("NAV")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(Path(OUTPUT_DIR) / "Figure5_strategy_nav.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 回撤图
    plt.figure(figsize=(14, 7))
    for name in strategy_map:
        nav = bt[f"{name}_nav"]
        dd = nav / nav.cummax() - 1
        plt.plot(bt.index, dd, label=name)
    plt.title("Strategy Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(Path(OUTPUT_DIR) / "Figure6_strategy_drawdown.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 仓位图
    plt.figure(figsize=(14, 6))
    plt.plot(bt.index, bt["pos_B_dynamic"], label="B_Dynamic")
    plt.plot(bt.index, bt["pos_C_risk_control"], label="C_Risk_Control")
    plt.title("Dynamic Strategy Positions")
    plt.xlabel("Date")
    plt.ylabel("Position")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(Path(OUTPUT_DIR) / "Figure7_strategy_positions.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Finished. Results saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()