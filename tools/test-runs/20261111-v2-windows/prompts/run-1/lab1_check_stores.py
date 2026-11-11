# -*- coding: utf-8 -*-
"""lab1_check_stores.py — 用店別紀錄（data/shops_daily_store.csv）驗證選 k。

做的事：
1. 與 lab1_cluster.py 完全相同的前處理（丟 std=0 欄位、StandardScaler、
   KMeans k=2..12、random_state=0、n_init=10），確保群和剛才一致。
2. 對每個 k 算 ARI（Adjusted Rand Index，對照店別標籤）。
3. 對建議的 k=9（店型手冊）與 k=10（客訴回查）列出「每一群裡各家店幾天」
   的交叉表。

注意：兩個 CSV 都沒有列 ID，這裡假設「第 i 列對第 i 列」對齊；
若對齊錯了，ARI 會接近 0，可視為間接檢查。
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

CSV_MAIN = "data/shops_daily.csv"
CSV_STORE = "data/shops_daily_store.csv"
K_RANGE = range(2, 13)
CHECK_K = [9, 10]  # A 的建議 9、B 的建議 10


def main():
    df = pd.read_csv(CSV_MAIN)
    stores = pd.read_csv(CSV_STORE)["store"]
    assert len(df) == len(stores), "兩個檔案列數不一致，無法逐列對齊"
    print(f"資料 {len(df)} 列；店別共 {stores.nunique()} 家：")
    print(stores.value_counts().sort_index().to_string(), "\n")

    # --- 和 lab1_cluster.py 相同的前處理與分群 ---
    drop_cols = [c for c in df.columns if df[c].std() == 0]
    X = StandardScaler().fit_transform(df.drop(columns=drop_cols))

    labels_by_k = {}
    print("各 k 的 ARI（對照店別）：")
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=0, n_init=10)
        labels_by_k[k] = km.fit_predict(X)
        ari = adjusted_rand_score(stores, labels_by_k[k])
        print(f"  k = {k:>2} : ARI = {ari:.4f}")

    # --- 建議 k 的交叉表：每一群裡各家店幾天 ---
    for k in CHECK_K:
        labels = labels_by_k[k]
        ct = pd.crosstab(labels, stores)  # 列=群，欄=店
        ct.columns.name = "店"
        ct.index.name = "群"
        ct = ct.reindex(columns=sorted(stores.unique()))  # 店編號排序
        ct["合計"] = ct.sum(axis=1)
        ct["店家數"] = (ct.iloc[:, :-1] > 0).sum(axis=1)
        print(f"\nk = {k}：每一群包含各家店的天數")
        print(ct.to_string())
        # 每群的主要店佔比（純度）
        purity = ct.iloc[:, :-2].max(axis=1) / ct["合計"]
        print(f"各群純度（最大單店佔比）：")
        for g in ct.index:
            print(f"  群 {g}：{purity[g]:.3f}")


if __name__ == "__main__":
    main()
