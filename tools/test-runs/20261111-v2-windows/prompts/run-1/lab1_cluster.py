# -*- coding: utf-8 -*-
"""lab1_cluster.py — 分店日營業紀錄 k-means 分群（不看店別）。

流程：
1. 讀 data/shops_daily.csv（不含任何店別檔）。
2. 拿掉標準差為 0 的欄位（本資料為 open_hours、menu_version）。
3. StandardScaler 標準化。
4. KMeans k = 2..12，random_state=0、n_init=10。
5. 用 silhouette、Calinski-Harabasz、Davies-Bouldin 三個不看店別的指標比較，
   並印出每個 k 的各群筆數。
6. 圖存 figs/lab1_k_selection.png。
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

CSV_PATH = "data/shops_daily.csv"
K_RANGE = range(2, 13)
RANDOM_STATE = 0
N_INIT = 10
OUT_FIG = "figs/lab1_k_selection.png"

# Windows 上的中文字型（微軟正黑體），找不到就退回預設字型
plt.rcParams["font.family"] = ["Microsoft JhengHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"資料：{df.shape[0]} 列 x {df.shape[1]} 欄")

    # --- 1. 拿掉標準差為 0 的欄位 ---
    drop_cols = [c for c in df.columns if df[c].std() == 0]
    print(f"丟掉的欄位（std = 0）：{drop_cols}")
    X_df = df.drop(columns=drop_cols)
    print(f"保留欄位（{X_df.shape[1]} 個）：{list(X_df.columns)}")

    # --- 2. 標準化 ---
    X = StandardScaler().fit_transform(X_df)

    # --- 3. 對每個 k 跑 k-means 並算三個指標 ---
    ks, sizes_all = [], []
    sils, chs, dbs = [], [], []
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
        labels = km.fit_predict(X)
        sizes = np.bincount(labels, minlength=k)
        sil = silhouette_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
        db = davies_bouldin_score(X, labels)
        ks.append(k)
        sizes_all.append(sizes)
        sils.append(sil)
        chs.append(ch)
        dbs.append(db)

    # --- 4. 印出結果表（含各群筆數） ---
    print("\n各 k 的指標與各群筆數：")
    header = f"{'k':>3} | {'silhouette':>10} | {'CH':>8} | {'DB':>6} | 各群筆數"
    print(header)
    print("-" * len(header))
    for k, sil, ch, db, sizes in zip(ks, sils, chs, dbs, sizes_all):
        size_str = ",".join(str(s) for s in sorted(sizes, reverse=True))
        print(f"{k:>3} | {sil:>10.4f} | {ch:>8.1f} | {db:>6.3f} | {size_str}")

    best_sil_k = ks[int(np.argmax(sils))]
    best_ch_k = ks[int(np.argmax(chs))]
    best_db_k = ks[int(np.argmin(dbs))]
    print(f"\nsilhouette 最大：k = {best_sil_k}（{max(sils):.4f}）")
    print(f"Calinski-Harabasz 最大：k = {best_ch_k}（{max(chs):.1f}）")
    print(f"Davies-Bouldin 最小：k = {best_db_k}（{min(dbs):.3f}）")

    # --- 5. 畫圖：三個指標 vs k ---
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)

    def style(ax, title, note):
        ax.set_title(title)
        ax.set_xlabel("k（群數）")
        ax.set_xticks(list(K_RANGE))
        ax.grid(alpha=0.3)
        ax.text(
            0.98,
            0.03,
            note,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            color="dimgray",
        )

    ax = axes[0]
    ax.plot(ks, sils, "o-")
    ax.plot(best_sil_k, max(sils), "r*", markersize=14)
    ax.set_ylabel("silhouette")
    style(ax, "輪廓係數 silhouette", "越大越好")

    ax = axes[1]
    ax.plot(ks, chs, "o-")
    ax.plot(best_ch_k, max(chs), "r*", markersize=14)
    ax.set_ylabel("Calinski-Harabasz")
    style(ax, "Calinski-Harabasz", "越大越好")

    ax = axes[2]
    ax.plot(ks, dbs, "o-")
    ax.plot(best_db_k, min(dbs), "r*", markersize=14)
    ax.set_ylabel("Davies-Bouldin")
    style(ax, "Davies-Bouldin", "越小越好")

    fig.suptitle("k-means 選 k：三個不看店別的內部指標（紅星 = 最佳）")
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    fig.savefig(OUT_FIG, dpi=150)
    print(f"\n圖已存到 {OUT_FIG}")


if __name__ == "__main__":
    main()
