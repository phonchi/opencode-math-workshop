"""比較 PCA 保留 3 / 4 / 5 個主成分時，客訴預警的 5 折交叉驗證 AUC。

資料：
- data/orders.csv            特徵（800 筆 × 11 個數值欄位）
- data/orders_complaint.csv  客訴標籤（與 orders.csv 同順序，僅用於檢查/評估）

流程：每一折只在訓練資料上 fit StandardScaler 與 PCA（避免資料洩漏），
logistic 迴歸在折外的預測機率最後合併算一個 AUC。
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path("data")
N_COMPONENTS_LIST = [3, 4, 5]
N_SPLITS = 5
RANDOM_STATE = 42


def main() -> None:
    X = pd.read_csv(DATA_DIR / "orders.csv")
    y = pd.read_csv(DATA_DIR / "orders_complaint.csv")["complaint"].to_numpy()

    # 標籤不平衡（約 7.5% 客訴），用分層抽樣；三種主成分數共用同一組折
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    # 每折的 out-of-fold 預測機率與（訓練折 PCA 的）累積變異
    oof_proba = {n: np.zeros(len(y)) for n in N_COMPONENTS_LIST}
    cum_var = {n: [] for n in N_COMPONENTS_LIST}

    for train_idx, test_idx in cv.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]

        # 標準化與 PCA 只用訓練折 fit，再轉換測試折
        scaler = StandardScaler().fit(X_train)
        X_train_s = scaler.transform(X_train)
        X_test_s = scaler.transform(X_test)

        # 一次 fit 到最大需要的 5 個主成分；主成分有巢狀性，
        # 前 k 個不受之後取幾個影響，所以可以直接切片取 3 / 4 / 5
        pca = PCA(n_components=max(N_COMPONENTS_LIST)).fit(X_train_s)
        Z_train = pca.transform(X_train_s)
        Z_test = pca.transform(X_test_s)

        for n in N_COMPONENTS_LIST:
            cum_var[n].append(pca.explained_variance_ratio_[:n].sum())
            clf = LogisticRegression(max_iter=1000)
            clf.fit(Z_train[:, :n], y[train_idx])
            oof_proba[n][test_idx] = clf.predict_proba(Z_test[:, :n])[:, 1]

    print(f"資料：{X.shape[0]} 筆、{X.shape[1]} 個特徵；客訴 {int(y.sum())} 筆（{y.mean():.1%}）")
    print(f"交叉驗證：分層 {N_SPLITS} 折（shuffle=True, random_state={RANDOM_STATE}）")
    print(f"（累積變異 = 各訓練折 PCA 的前 n 個 explained_variance_ratio_ 之和，5 折平均）\n")
    print(f"{'主成分':>4}  {'累積變異':>10}  {'AUC':>8}")
    aucs = {}
    for n in N_COMPONENTS_LIST:
        aucs[n] = roc_auc_score(y, oof_proba[n])
        print(f"{n:>4}  {np.mean(cum_var[n]):>10.4f}  {aucs[n]:>8.4f}")

    # 依你的主張（4 個夠用；比 5 個低超過 0.02 就撤回）印出差值，結論留給你
    print(f"\nAUC(5) - AUC(4) = {aucs[5] - aucs[4]:.4f}（你的門檻：超過 0.02 才撤回）")


if __name__ == "__main__":
    main()
