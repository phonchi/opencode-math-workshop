# -*- coding: utf-8 -*-
"""lab3_loans_threshold.py

用 data/loans.csv（900 筆）訓練 logistic 迴歸預測逾期，
對 data/loans_new_batch.csv（300 筆）算 P(逾期)，再列出
門檻 0.5 / 0.3 / 0.2 / 0.1 / 0.05 的「提醒數／抓到／漏掉／白提醒」。

我替你做的每個決定（完整清單見 notes/lab3_loans_decisions.md）：
1. 丟掉 case_no（你的指示）；其餘 6 個數值欄位全部當特徵，不篩選、不合成新欄位。
2. 兩檔都無遺漏值、無重複列 → 不插補、不刪列。
3. 特徵做標準化（StandardScaler 只用訓練檔 fit，新批套同一轉換）。
4. LogisticRegression 用 sklearn 預設（L2、C=1.0、lbfgs），僅 max_iter=1000，不調參。
5. 不做 class_weight／重取樣：機率維持訓練檔盛行率的校準。
6. 提醒準則：P(逾期) ≥ 門檻就寄信（含等於）。
7. 門檻由你挑；本腳本只印數字與預算檢查（300 筆 ≤ 40 封），不替你選。

模型式：P(overdue=1 | x) = σ(β₀ + Σⱼ βⱼ zⱼ)，z = 標準化後的特徵。
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

TRAIN_PATH = Path("data") / "loans.csv"
NEW_PATH = Path("data") / "loans_new_batch.csv"
FIG_PATH = Path("figs") / "lab3_threshold_tradeoff.png"

THRESHOLDS = [0.5, 0.3, 0.2, 0.1, 0.05]
MAIL_CAP = 40          # 你的預算：每 300 筆最多寄 40 封
NEW_BATCH_SIZE = 300   # 新一批實際筆數（用來對照預算）
N_SPLITS = 5
RANDOM_STATE = 42


def disp_len(s: str) -> int:
    """終端機顯示寬度（CJK 全形算 2、其他算 1），只為了表格對齊。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def disp_pad(s: str, width: int) -> str:
    """補空格到指定顯示寬度（只為了表格對齊）。"""
    return s + " " * max(1, width - disp_len(s))


def make_model() -> LogisticRegression:
    """決定 4：sklearn 預設參數 + max_iter=1000（不調參）。"""
    return LogisticRegression(max_iter=1000)


def main() -> None:
    train = pd.read_csv(TRAIN_PATH)
    new = pd.read_csv(NEW_PATH)

    # ===== 資料檢查（決定 2 的依據）=====
    for name, df in [("訓練檔", train), ("新一批", new)]:
        assert not df.isna().any().any(), f"{name}有遺漏值"
        assert not df.duplicated().any(), f"{name}有重複列"
    assert not (set(train["case_no"]) & set(new["case_no"])), "case_no 跨檔重疊"

    # ===== 特徵與標籤（決定 1、3）=====
    features = [c for c in train.columns if c not in ("case_no", "overdue")]
    X_train = train[features]
    y_train = train["overdue"].to_numpy()
    X_new = new[features]
    y_new = new["overdue"].to_numpy()

    print(f"訓練檔：{len(train)} 筆，逾期 {int(y_train.sum())} 筆（{y_train.mean():.1%}）")
    print(f"新一批：{len(new)} 筆，逾期 {int(y_new.sum())} 筆（{y_new.mean():.1%}）")
    print(f"特徵（{len(features)} 個，標準化後餵模型）：{'、'.join(features)}")
    print(f"丟掉：case_no（你的指示）、overdue（只當標籤）\n")

    # ===== 交叉驗證 AUC（只看模型能不能用，不做模型選擇）=====
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    oof = np.zeros(len(y_train))
    for tr_idx, te_idx in cv.split(X_train, y_train):
        pipe = make_pipeline(StandardScaler(), make_model())
        pipe.fit(X_train.iloc[tr_idx], y_train[tr_idx])
        oof[te_idx] = pipe.predict_proba(X_train.iloc[te_idx])[:, 1]
    print(f"訓練檔 {N_SPLITS} 折分層交叉驗證 AUC（out-of-fold）：{roc_auc_score(y_train, oof):.3f}")

    # ===== 正式模型：900 筆全拿去訓練（決定 3 的 scaler 只用訓練檔 fit）=====
    scaler = StandardScaler().fit(X_train)
    model = make_model().fit(scaler.transform(X_train), y_train)
    p_train = model.predict_proba(scaler.transform(X_train))[:, 1]
    p_new = model.predict_proba(scaler.transform(X_new))[:, 1]
    print(f"訓練檔內樣本 AUC：{roc_auc_score(y_train, p_train):.3f}")
    print(f"新一批 AUC：{roc_auc_score(y_new, p_new):.3f}")
    print(
        "新一批 P(逾期) 分布：min {:.4f}／中位數 {:.4f}／90 分位 {:.4f}／max {:.4f}".format(
            p_new.min(), np.median(p_new), np.quantile(p_new, 0.9), p_new.max()
        )
    )

    # ===== 標準化尺度下的係數（模型用什麼欄位、往哪個方向）=====
    print("\n係數（標準化尺度，正號 = 該欄越大 P(逾期) 越高）：")
    for name, b in sorted(
        zip(features, model.coef_[0]), key=lambda t: -abs(t[1])
    ):
        print(f"  {disp_pad(name, 18)}{b:+.3f}")
    print(f"  {disp_pad('截距', 18)}{model.intercept_[0]:+.3f}")

    # ===== 門檻表（決定 6、7：只列數字，不選門檻）=====
    n_overdue = int(y_new.sum())
    print(f"\n== 門檻表（新一批 {len(new)} 筆，逾期共 {n_overdue} 筆；預算：{MAIL_CAP} 封/{NEW_BATCH_SIZE} 筆）==")
    header = (
        disp_pad("門檻", 8)
        + disp_pad("提醒數", 10)
        + disp_pad("抓到", 8)
        + disp_pad("漏掉", 8)
        + disp_pad("白提醒", 10)
        + disp_pad(f"提醒數 ≤ {MAIL_CAP}", 14)
    )
    print(header)
    print("-" * disp_len(header))
    rows = []
    for t in THRESHOLDS:
        send = p_new >= t                      # 準則：≥ 門檻就寄
        caught = int((send & (y_new == 1)).sum())
        missed = int((~send & (y_new == 1)).sum())
        false_alarm = int((send & (y_new == 0)).sum())
        n_send = int(send.sum())
        assert caught + missed == n_overdue
        assert caught + false_alarm == n_send
        rows.append((t, n_send, caught, missed, false_alarm))
        print(
            disp_pad(f"{t:g}", 8)
            + disp_pad(str(n_send), 10)
            + disp_pad(str(caught), 8)
            + disp_pad(str(missed), 8)
            + disp_pad(str(false_alarm), 10)
            + ("是" if n_send <= MAIL_CAP else "否（超預算）")
        )

    # ===== 圖：門檻 vs 提醒數／抓到／漏掉（figs/，不開視窗）=====
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    grid = np.geomspace(0.02, 0.6, 200)
    send_grid = [(p_new >= t).sum() for t in grid]
    caught_grid = [((p_new >= t) & (y_new == 1)).sum() for t in grid]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
    ts = [r[0] for r in rows]
    ax1.plot(grid, send_grid, color="tab:blue", label="提醒數")
    ax1.scatter(ts, [r[1] for r in rows], color="tab:blue", zorder=3)
    ax1.axhline(MAIL_CAP, color="tab:red", linestyle="--", label=f"預算上限 {MAIL_CAP} 封")
    ax1.set_xscale("log")
    ax1.set_xlabel("門檻（對數軸）")
    ax1.set_ylabel("提醒數（封）")
    ax1.set_title("門檻 vs 寄信數")
    ax1.legend()

    ax2.plot(grid, caught_grid, color="tab:green", label=f"抓到（逾期共 {n_overdue}）")
    ax2.plot(grid, n_overdue - np.array(caught_grid), color="tab:orange", label="漏掉")
    ax2.scatter(ts, [r[2] for r in rows], color="tab:green", zorder=3)
    ax2.scatter(ts, [r[3] for r in rows], color="tab:orange", zorder=3)
    ax2.set_xscale("log")
    ax2.set_xlabel("門檻（對數軸）")
    ax2.set_ylabel("筆數")
    ax2.set_title("門檻 vs 抓到／漏掉")
    ax2.legend()

    # 刻度用純文字標籤：log 軸的 mathtext 刻度會用到 U+2212，字型缺字會變成空框
    for ax in (ax1, ax2):
        ax.set_xticks(THRESHOLDS)
        ax.set_xticklabels([f"{t:g}" for t in THRESHOLDS])
        ax.minorticks_off()

    fig.suptitle("logistic 迴歸在新一批（300 筆）的門檻取捨；門檻由你挑")
    fig.tight_layout()
    fig.savefig(FIG_PATH, dpi=150)
    print(f"\n圖已存：{FIG_PATH}")


if __name__ == "__main__":
    main()
