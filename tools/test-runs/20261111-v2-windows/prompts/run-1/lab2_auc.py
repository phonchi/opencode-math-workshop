# -*- coding: utf-8 -*-
"""lab2_auc.py — 訂單資料 PCA 保留 3/4/5 個主成分的客訴辨識 AUC 比較。

流程：
1. 讀 data/orders.csv 當特徵、data/orders_complaint.csv 當標籤（只拿來評分，不進特徵）。
2. Pipeline = StandardScaler -> PCA(k) -> LogisticRegression，
   用 5 折分層交叉驗證；scaler 和 PCA 只用該折的訓練資料 fit（防洩漏）。
3. AUC 用折外（out-of-fold）預測機率，整份資料一次算 roc_auc_score。
4. 累積變異 = 各訓練折 PCA 的 explained_variance_ratio_ 總和之平均。
5. 印出 k = 3、4、5 的累積變異與 AUC，並檢查撤回條件
   （AUC(5) - AUC(4) > 0.02 即「4 個比 5 個低超過 0.02」）。
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X_CSV = "data/orders.csv"
Y_CSV = "data/orders_complaint.csv"
K_LIST = [3, 4, 5]
N_SPLITS = 5
RANDOM_STATE = 0
MAX_ITER = 1000
RETRACT_GAP = 0.02  # 撤回門檻：AUC(5) - AUC(4) 超過 0.02 才算數


def main():
    X = pd.read_csv(X_CSV)
    y = pd.read_csv(Y_CSV)["complaint"]
    assert len(X) == len(y), "orders.csv 和 orders_complaint.csv 列數不一致"
    print(f"資料：{X.shape[0]} 列 x {X.shape[1]} 個特徵欄位")
    print(f"客訴陽性：{int(y.sum())} 筆（{y.mean():.1%}）")

    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    header = f"{'主成分數':>6} | {'累積變異（5折平均）':>18} | {'AUC（折外）':>10}"
    print("\n" + header)
    print("-" * len(header))

    results = {}
    for k in K_LIST:
        pipe = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("pca", PCA(n_components=k)),
                ("clf", LogisticRegression(max_iter=MAX_ITER)),
            ]
        )
        oof_proba = np.zeros(len(y))
        cum_vars = []
        for train_idx, test_idx in cv.split(X, y):
            # scaler、PCA、logistic 都只看這折的訓練資料
            pipe.fit(X.iloc[train_idx], y.iloc[train_idx])
            oof_proba[test_idx] = pipe.predict_proba(X.iloc[test_idx])[:, 1]
            cum_vars.append(pipe.named_steps["pca"].explained_variance_ratio_.sum())
        auc = roc_auc_score(y, oof_proba)
        results[k] = (float(np.mean(cum_vars)), auc)
        print(f"{k:>6} | {np.mean(cum_vars):>17.4%} | {auc:>10.4f}")

    # --- 撤回條件檢查（只報數字，不改主張） ---
    auc4, auc5 = results[4][1], results[5][1]
    gap = auc5 - auc4
    print(f"\nAUC(4 個) = {auc4:.4f}")
    print(f"AUC(5 個) = {auc5:.4f}")
    print(f"AUC(5) - AUC(4) = {gap:.4f}（門檻 {RETRACT_GAP}）")
    if gap > RETRACT_GAP:
        print("4 個主成分的 AUC 比 5 個低超過 0.02 -> 撤回條件成立。")
    else:
        print("4 個主成分的 AUC 沒有比 5 個低超過 0.02 -> 撤回條件不成立。")


if __name__ == "__main__":
    main()
