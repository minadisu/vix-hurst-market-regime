# -*- coding: utf-8 -*-
"""
03_gold_oil_extension_optional.py

黄金、原油扩展检验。该文件为可选附录，不作为主论文实证。

Gold: GLD + GVZCLS
Oil : USO + OVXCLS

输出：
- Appendix_gold_oil_signal_summary.csv
- Appendix_gold_oil_group_test.csv
- Appendix_gold_oil_strategy_performance.csv
- Figure8_gold_oil_nav.png
- Figure9_gold_oil_drawdown.png
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# 0. 参数设置
# ============================================================

GLD_PATH = str(Path(__file__).resolve().parents[1] / "数据" / "GLD.csv")
USO_PATH = str(Path(__file__).resolve().parents[1] / "数据" / "USO.csv")
OUTPUT_DIR = str(Path(__file__).resolve().parents[1] / "代码" / "输出结果" / "黄金原油")

START_DATE = "2009-01-01"
END_DATE = "2024-12-31"
FORWARD_WINDOWS = [5, 10, 22, 60]
TRADING_COST = 0.0005

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. 数据函数
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


def future_max_drawdown(prices, window):
    result = []
    arr = prices.values
    for i in range(len(arr)):
        if i + window >= len(arr):
            result.append(np.nan)
            continue
        future_path = arr[i:i + window + 1]
        start_price = future_path[0]
        result.append((future_path / start_price - 1).min())
    return pd.Series(result, index=prices.index)

# ============================================================
# 2. 构造单资产数据
# ============================================================

def build_asset_dataset(price, iv, asset_name):
    df = pd.concat([price, iv], axis=1, sort=True).dropna()
    df.columns = ["price", "iv"]
    df = df.loc[START_DATE:END_DATE].copy()

    df["ret"] = np.log(df["price"] / df["price"].shift(1))
    df["log_iv"] = np.log(df["iv"])
    df["dlog_iv"] = df["log_iv"].diff()

    df["hurst_dfa_ret_90"] = df["dlog_iv"].rolling(90).apply(
        lambda x: hurst_dfa(x, min_scale=5, max_scale=22, n_scales=8), raw=False
    )
    df["hurst_main"] = df["hurst_dfa_ret_90"]

    df["ma200"] = df["price"].rolling(200).mean()
    df["bull"] = (df["price"] > df["ma200"]).astype(int)
    df["bear"] = (df["price"] < df["ma200"]).astype(int)
    df["iv_q20"] = df["iv"].rolling(252).quantile(0.20)
    df["iv_q80"] = df["iv"].rolling(252).quantile(0.80)
    df["iv_low"] = (df["iv"] < df["iv_q20"]).astype(int)
    df["iv_high"] = (df["iv"] > df["iv_q80"]).astype(int)
    df["iv_change_5d"] = np.log(df["iv"] / df["iv"].shift(5))
    df["iv_up"] = (df["iv_change_5d"] > 0).astype(int)
    df["iv_down"] = (df["iv_change_5d"] < 0).astype(int)
    df["hurst_high_05"] = (df["hurst_main"] > 0.5).astype(int)

    df["panic_repair"] = ((df["bear"] == 1) & (df["iv_high"] == 1) & (df["iv_down"] == 1) & (df["hurst_high_05"] == 1)).astype(int)
    df["panic_worsen"] = ((df["bear"] == 1) & (df["iv_high"] == 1) & (df["iv_up"] == 1) & (df["hurst_high_05"] == 1)).astype(int)
    df["lowvol_persist"] = ((df["bull"] == 1) & (df["iv_low"] == 1) & (df["hurst_high_05"] == 1)).astype(int)

    for k in FORWARD_WINDOWS:
        df[f"fwd_ret_{k}d"] = np.log(df["price"].shift(-k) / df["price"])
        df[f"rv_fwd_{k}d"] = df["ret"].shift(-k).rolling(k).std() * np.sqrt(252)
        df[f"mdd_fwd_{k}d"] = future_max_drawdown(df["price"], k)

    df["asset"] = asset_name
    return df


def group_test(data, signal_col, y_col):
    signal_group = data.loc[data[signal_col] == 1, y_col].dropna()
    other_group = data.loc[data[signal_col] == 0, y_col].dropna()
    if len(signal_group) < 2 or len(other_group) < 2:
        return None
    t_stat, p_value = stats.ttest_ind(signal_group, other_group, equal_var=False, nan_policy="omit")
    return {
        "signal": signal_col,
        "target": y_col,
        "signal_mean": signal_group.mean(),
        "other_mean": other_group.mean(),
        "difference": signal_group.mean() - other_group.mean(),
        "signal_count": len(signal_group),
        "other_count": len(other_group),
        "t_stat": t_stat,
        "p_value": p_value
    }

# ============================================================
# 3. 回测函数
# ============================================================

def calculate_strategy_returns(data, position_col, ret_col="ret", cost=0.0005):
    pos = data[position_col].copy()
    return pos.shift(1).fillna(0) * data[ret_col] - pos.diff().abs().fillna(0) * cost


def max_drawdown(nav):
    return (nav / nav.cummax() - 1).min()


def annualized_return(nav):
    total_return = nav.iloc[-1] / nav.iloc[0] - 1
    return (1 + total_return) ** (252 / len(nav)) - 1


def annualized_volatility(ret):
    return ret.std() * np.sqrt(252)


def sharpe_ratio(ret):
    vol = annualized_volatility(ret)
    return np.nan if vol == 0 else ret.mean() * 252 / vol


def run_asset_backtest(df, asset_name):
    bt = df.dropna(subset=["ret", "hurst_main", "ma200", "iv_q20", "iv_q80"]).copy()
    bt["pos_buy_hold"] = 1.0
    bt["pos_A_repair_only"] = np.where(bt["panic_repair"] == 1, 1.0, 0.0)
    bt["pos_B_dynamic"] = 0.50
    bt.loc[bt["lowvol_persist"] == 1, "pos_B_dynamic"] = 1.00
    bt.loc[bt["panic_repair"] == 1, "pos_B_dynamic"] = 0.70
    bt["pos_C_risk_control"] = 0.50
    bt.loc[bt["lowvol_persist"] == 1, "pos_C_risk_control"] = 1.00
    bt.loc[bt["panic_repair"] == 1, "pos_C_risk_control"] = 0.70
    bt.loc[bt["panic_worsen"] == 1, "pos_C_risk_control"] = 0.00

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
        ret = bt[f"{name}_ret"].dropna()
        nav = bt[f"{name}_nav"].dropna()
        rows.append({
            "asset": asset_name,
            "strategy": name,
            "total_return": nav.iloc[-1] / nav.iloc[0] - 1,
            "annual_return": annualized_return(nav),
            "annual_volatility": annualized_volatility(ret),
            "sharpe_ratio": sharpe_ratio(ret),
            "max_drawdown": max_drawdown(nav),
            "avg_position": bt[pos_col].mean()
        })
    return bt, pd.DataFrame(rows)

# ============================================================
# 4. 主程序
# ============================================================

def main():
    gold = build_asset_dataset(
        read_price_file(GLD_PATH, "gold").loc[START_DATE:END_DATE],
        read_fred_series("GVZCLS", "gvz", START_DATE, END_DATE),
        "gold"
    )
    oil = build_asset_dataset(
        read_price_file(USO_PATH, "oil").loc[START_DATE:END_DATE],
        read_fred_series("OVXCLS", "ovx", START_DATE, END_DATE),
        "oil"
    )

    asset_data = {"gold": gold, "oil": oil}
    signals = ["panic_repair", "panic_worsen", "lowvol_persist"]

    signal_rows = []
    group_rows = []
    perf_rows = []
    bt_data = {}

    for asset, data in asset_data.items():
        test_df = data.dropna().copy()
        for sig in signals:
            signal_rows.append({
                "asset": asset,
                "signal": sig,
                "signal_days": int(test_df[sig].sum()),
                "signal_ratio": test_df[sig].mean()
            })
            for k in FORWARD_WINDOWS:
                for target in [f"fwd_ret_{k}d", f"rv_fwd_{k}d", f"mdd_fwd_{k}d"]:
                    res = group_test(test_df, sig, target)
                    if res is not None:
                        res["asset"] = asset
                        group_rows.append(res)
        bt, perf = run_asset_backtest(data, asset)
        bt_data[asset] = bt
        perf_rows.append(perf)

    signal_summary = pd.DataFrame(signal_rows)
    group_table = pd.DataFrame(group_rows)
    performance = pd.concat(perf_rows, ignore_index=True)

    signal_summary.round(4).to_csv(Path(OUTPUT_DIR) / "Appendix_gold_oil_signal_summary.csv", index=False, encoding="utf-8-sig")
    group_table.round(4).to_csv(Path(OUTPUT_DIR) / "Appendix_gold_oil_group_test.csv", index=False, encoding="utf-8-sig")
    performance.round(4).to_csv(Path(OUTPUT_DIR) / "Appendix_gold_oil_strategy_performance.csv", index=False, encoding="utf-8-sig")

    # NAV figure
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    for ax, asset in zip(axes, ["gold", "oil"]):
        bt = bt_data[asset]
        for name in ["Buy_Hold", "A_Repair_Only", "B_Dynamic", "C_Risk_Control"]:
            ax.plot(bt.index, bt[f"{name}_nav"], label=name)
        ax.set_title(f"{asset.upper()} Strategy NAV")
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    plt.savefig(Path(OUTPUT_DIR) / "Figure8_gold_oil_nav.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Drawdown figure
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    for ax, asset in zip(axes, ["gold", "oil"]):
        bt = bt_data[asset]
        for name in ["Buy_Hold", "A_Repair_Only", "B_Dynamic", "C_Risk_Control"]:
            nav = bt[f"{name}_nav"]
            dd = nav / nav.cummax() - 1
            ax.plot(bt.index, dd, label=name)
        ax.set_title(f"{asset.upper()} Strategy Drawdown")
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    plt.savefig(Path(OUTPUT_DIR) / "Figure9_gold_oil_drawdown.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Finished. Results saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()