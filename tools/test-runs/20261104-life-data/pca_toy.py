"""Lab 2 動畫用的 60 筆示範訂單：距離與騎乘時間高度相關；5 筆客訴是「比同距離的訂單慢很多」。另印 11 欄資料的解釋變異比例。"""
import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from pathlib import Path
rng = np.random.default_rng(11)
n = 60
dist = np.round(rng.uniform(0.5, 4.0, n), 2)
c = np.zeros(n, int); c[rng.choice(n, 5, replace=False)] = 1
ride = np.round(3 + 3.2 * dist + 0.7 * rng.normal(size=n) + c * 4.5, 1)
X = np.column_stack([dist, ride])
for name, A in [("std", StandardScaler().fit_transform(X)), ("meters", np.column_stack([dist * 1000, ride]))]:
    p = PCA(2).fit(A); z = p.transform(A)
    print(name, "ratio", p.explained_variance_ratio_.round(4), "comp", p.components_.round(3))
    print("  PC2 complaint mean", z[c == 1, 1].mean().round(2), "others range", z[c == 0, 1].min().round(2), z[c == 0, 1].max().round(2))
print(json.dumps([[float(a), float(b), int(k)] for a, b, k in zip(dist, ride, c)], separators=(",", ":")))
D = Path(__file__).resolve().parents[3] / "assets/data"
Z = StandardScaler().fit_transform(np.genfromtxt(D / "orders.csv", delimiter=",", skip_header=1))
print("orders ratio", PCA().fit(Z).explained_variance_ratio_.round(4).tolist())
