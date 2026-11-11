# -*- coding: utf-8 -*-
"""lab1_check_stores.py

用 data/shops_daily_store.csv 的店別，回頭檢查 lab1_cluster.py 建議的群數
（A 店型手冊 = 9 群、B 客訴回查 = 10 群）。這支只做驗證，不改變建議。

檢查項目：
1. k = 2..12 每個 k 的 ARI（adjusted Rand index，與店別比對，1.0 = 完全一致）。
2. k=9 與 k=10 各印出「每一群 × 每家店」的天數交叉表，以及每群的主要店與純度。

前處理與 lab1_cluster.py 完全相同：
丟掉標準差為 0 的欄位 → z-score 標準化 → KMeans(random_state=0, n_init=10)。
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

DATA_PATH = "data/shops_daily.csv"
STORE_PATH = "data/shops_daily_store.csv"
RECOMMENDED = {"k=9（A 店型手冊）": 9, "k=10（B 客訴回查）": 10}


def main():
    df = pd.read_csv(DATA_PATH)
    stores = pd.read_csv(STORE_PATH)["store"]
    assert len(df) == len(stores), "兩個檔案列數不一致，無法逐列對齊"

    std = df.std(numeric_only=True)
    kept = std[std > 0].index.tolist()
    X = StandardScaler().fit_transform(df[kept])

    print(f"筆數 {len(df)}、店家數 {stores.nunique()}")
    print(f"各店天數: {stores.value_counts().sort_index().to_dict()}")
    print()

    # 1) ARI 曲線（順便看建議的 k 在哪個位置）
    print(f"{'k':>3} {'ARI':>7}")
    print("-" * 12)
    for k in range(2, 13):
        labels = KMeans(n_clusters=k, random_state=0, n_init=10).fit_predict(X)
        ari = adjusted_rand_score(stores, labels)
        mark = ""
        if k == 9:
            mark = "  <- 建議 A（手冊）"
        elif k == 10:
            mark = "  <- 建議 B（客訴）"
        print(f"{k:>3} {ari:>7.4f}{mark}")

    # 2) 建議的兩個 k：交叉表 + 每群純度
    for name, k in RECOMMENDED.items():
        labels = KMeans(n_clusters=k, random_state=0, n_init=10).fit_predict(X)
        ari = adjusted_rand_score(stores, labels)
        print(f"\n=== {name}，ARI = {ari:.4f}：每群包含各家店幾天 ===")

        tab = pd.crosstab(labels, stores)  # 列 = 群，欄 = 店
        tab["合計"] = tab.sum(axis=1)
        # 依「主要店編號」排序，方便對照
        dom = tab.drop(columns="合計").idxmax(axis=1)
        tab = tab.loc[dom.sort_values().index]
        tab.index.name = "群"

        days = tab.drop(columns="合計")
        for c in tab.index:
            main_store = days.loc[c].idxmax()
            n_main = days.loc[c, main_store]
            total = tab.loc[c, "合計"]
            others = {s: int(v) for s, v in days.loc[c][days.loc[c] > 0].items() if s != main_store}
            extra = f"；混入 {others}" if others else ""
            print(
                f"  群 {c}: 主要店 {main_store}，{n_main}/{total} 天"
                f"（純度 {n_main / total:.1%}）{extra}"
            )
        overall = days.max(axis=1).sum() / len(df)
        print(f"  整體純度（每群最大店天數加總 / 全部）: {overall:.1%}")
        print()
        print(tab.to_string())


if __name__ == "__main__":
    main()
