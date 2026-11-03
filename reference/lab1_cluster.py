"""Lab 1 參考程式：同一份分店營業資料，前處理不同，silhouette 選出的 k 就不同。

shops_daily.csv 是為工作坊設計的合成資料。分店標籤只在揭曉時使用，選 k 時不看。
"""
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).resolve().parents[1] / "assets" / "data"
X = np.genfromtxt(DATA / "shops_daily.csv", delimiter=",", skip_header=1)
store = np.genfromtxt(DATA / "reveal" / "shops_daily_store.csv", delimiter=",", skip_header=1)
print(f"資料形狀 X={X.shape}；標準差為 0 的欄位索引 = {np.flatnonzero(X.std(0) == 0).tolist()}")


def sweep(Z):
    out = {}
    for k in range(2, 13):
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Z)
        out[k] = (km.inertia_, silhouette_score(Z, km.labels_), adjusted_rand_score(store, km.labels_))
    return out


raw = sweep(X)
std = sweep(StandardScaler().fit_transform(X))
print(f"{'k':>3} {'原始 silhouette':>16} {'原始 ARI':>9} {'標準化 silhouette':>18} {'標準化 ARI':>11}")
for k in raw:
    print(f"{k:>3} {raw[k][1]:>16.4f} {raw[k][2]:>9.3f} {std[k][1]:>18.4f} {std[k][2]:>11.3f}")
print("原始尺度 silhouette 最高的 k =", max(raw, key=lambda k: raw[k][1]))
print("標準化後 silhouette 最高的 k =", max(std, key=lambda k: std[k][1]))
