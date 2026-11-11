# -*- coding: utf-8 -*-
"""lab1_cluster.py

對 data/shops_daily.csv 做 k-means 分群（不知道店別），
用 silhouette / Calinski-Harabasz / Davies-Bouldin 三個內部指標選 k。

前置處理：
1. 丟掉標準差為 0 的欄位（對分群沒有資訊，標準化後還會變 NaN/0）。
2. 其餘欄位做 z-score 標準化（各欄尺度差很大：營收上萬、share 大約 0.3）。

k = 2..12，KMeans(random_state=0, n_init=10)。
圖存 figs/lab1_k_selection.png。
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Windows 上沒有 CJK 字型的話，中文會變成方框
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

DATA_PATH = "data/shops_daily.csv"
FIG_PATH = "figs/lab1_k_selection.png"
K_RANGE = range(2, 13)


def load_features():
    df = pd.read_csv(DATA_PATH)

    # 丟掉標準差為 0 的欄位
    std = df.std(numeric_only=True)
    dropped = std[std == 0].index.tolist()
    kept = [c for c in df.columns if c not in dropped]

    X = StandardScaler().fit_transform(df[kept])
    return df, X, dropped, kept


def main():
    df, X, dropped, kept = load_features()
    print(f"資料筆數: {len(df)}")
    print(f"丟掉的欄位（標準差 = 0）: {dropped}")
    print(f"保留並標準化的欄位: {kept}")
    print()

    results = []
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=0, n_init=10)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
        db = davies_bouldin_score(X, labels)
        sizes = np.bincount(labels, minlength=k)
        results.append(
            {"k": k, "silhouette": sil, "ch": ch, "db": db, "sizes": sizes.tolist()}
        )

    # 印出表格
    header = (
        f"{'k':>3} {'silhouette':>11} {'CH':>8} {'DB':>6}  各群筆數"
    )
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['k']:>3} {r['silhouette']:>11.4f} {r['ch']:>8.1f} "
            f"{r['db']:>6.3f}  {r['sizes']}"
        )

    best_sil = max(results, key=lambda r: r["silhouette"])
    best_ch = max(results, key=lambda r: r["ch"])
    best_db = min(results, key=lambda r: r["db"])
    print()
    print(f"silhouette 最高（越大越好）: k={best_sil['k']} ({best_sil['silhouette']:.4f})")
    print(f"Calinski-Harabasz 最高（越大越好）: k={best_ch['k']} ({best_ch['ch']:.1f})")
    print(f"Davies-Bouldin 最低（越小越好）: k={best_db['k']} ({best_db['db']:.3f})")

    # ---- 輔助診斷（回答手冊／客訴兩種用途的 k 用）----
    # 1) 各群內部 RMS（每點到自己群質心的距離）：某群特別大 → 裡面可能藏了兩家店。
    # 2) k=10 質心兩兩距離：看最小那對和其他對差多少（近似雙胞胎店）。
    from itertools import combinations

    for kk in (9, 10):
        km = KMeans(n_clusters=kk, random_state=0, n_init=10).fit(X)
        rms = [
            round(float(np.sqrt(((X[km.labels_ == c] - km.cluster_centers_[c]) ** 2).sum(axis=1).mean())), 3)
            for c in range(kk)
        ]
        pair_d = sorted(
            round(float(np.linalg.norm(km.cluster_centers_[i] - km.cluster_centers_[j])), 3)
            for i, j in combinations(range(kk), 2)
        )
        print(f"\n[k={kk}] 各群內部 RMS: {rms}")
        if kk == 10:
            print(f"[k=10] 質心間距離最小 3 對: {pair_d[:3]}，中位數: {pair_d[len(pair_d) // 2]}")

    # 畫圖：三個指標各自一個子圖（尺度不同，不硬疊在同一軸）
    ks = [r["k"] for r in results]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)

    panels = [
        ("silhouette", "Silhouette（越大越好）", max, "tab:blue"),
        ("ch", "Calinski-Harabasz（越大越好）", max, "tab:orange"),
        ("db", "Davies-Bouldin（越小越好）", min, "tab:green"),
    ]
    for ax, (key, title, best_fn, color) in zip(axes, panels):
        vals = [r[key] for r in results]
        ax.plot(ks, vals, marker="o", color=color)
        bk = best_fn(results, key=lambda r: r[key])["k"]
        bv = next(r[key] for r in results if r["k"] == bk)
        ax.scatter([bk], [bv], color="red", zorder=5, label=f"最佳 k={bk}")
        ax.set_title(title)
        ax.set_xlabel("k（群數）")
        ax.set_xticks(list(K_RANGE))
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.suptitle("k-means 分群：k 的選擇（三個內部指標，不看店別）")
    fig.tight_layout(rect=(0, 0, 1, 0.94))

    os.makedirs(os.path.dirname(FIG_PATH), exist_ok=True)
    fig.savefig(FIG_PATH, dpi=150)
    print(f"\n圖已存到 {FIG_PATH}")


if __name__ == "__main__":
    main()
