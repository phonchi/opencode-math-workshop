"""Lab 1 動畫用的 60 筆示範資料：4 家店，第 A、B 家同站兩出口幾乎一樣。印出可貼進 JS 的陣列與檢查。"""
import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
rng = np.random.default_rng(7)
spec = [(42000, 6.0), (42600, 6.5), (42300, 10.6), (52000, 7.2)]  # A、B 同站兩出口；C 等很久；D 營業額高
X, s = [], []
for i, (r, w) in enumerate(spec):
    X.append(np.column_stack([r + 1300 * rng.normal(size=15), w + 0.55 * rng.normal(size=15)])); s += [i] * 15
X = np.vstack(X); s = np.array(s)
X[:, 0] = np.round(X[:, 0], -1); X[:, 1] = np.round(X[:, 1], 1)
for name, Z in [("raw", X), ("std", StandardScaler().fit_transform(X))]:
    sc = {k: silhouette_score(Z, KMeans(k, n_init=10, random_state=0).fit_predict(Z)) for k in range(2, 6)}
    print(name, {k: round(v, 3) for k, v in sc.items()}, "best", max(sc, key=sc.get))
print(json.dumps([[int(a), float(b), int(c)] for (a, b), c in zip(X, s)], separators=(",", ":")))
