"""補充驗證：
1. cosine 距離（L2 正規化後 KMeans）是否讓指標在 k=10 出現明確峰值
2. k=10 時各群與真實數字的對應純度（contingency）
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.stats import mode

digits = load_digits()
X, y = digits.data, digits.target

X_std = StandardScaler().fit_transform(X)
X_cos = normalize(X_std)  # L2 正規化 -> 歐氏距離單調等價於 cosine 距離
X_pca = PCA(n_components=0.95, random_state=42).fit_transform(X_std)

print("== cosine（L2 正規化）空間的 silhouette 與 ARI ==")
print(" k  |  silhouette |  ARI")
best = []
for k in range(2, 21):
    km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(X_cos)
    s = silhouette_score(X_cos, km.labels_)
    a = adjusted_rand_score(y, km.labels_)
    best.append((k, s, a))
    print(f"{k:3d} |   {s:.4f}    |  {a:.4f}")
best_k_sil = max(best, key=lambda t: t[1])
print(f"silhouette 峰值: k={best_k_sil[0]} (score={best_k_sil[1]:.4f})")

print("\n== k=10 時各群對應的數字與純度（cosine 空間）==")
km = KMeans(n_clusters=10, n_init=20, random_state=42).fit(X_cos)
labels = km.labels_
for c in range(10):
    mask = labels == c
    true_vals = y[mask]
    top = np.bincount(true_vals, minlength=10).argmax()
    purity = (true_vals == top).mean()
    counts = np.bincount(true_vals, minlength=10)
    others = {d: n for d, n in enumerate(counts) if n > 0 and d != top}
    print(f"cluster {c:2d} -> 數字 {top}（純度 {purity:.0%}, n={mask.sum()}）混入: {others}")

print(f"\nk=10 cosine 空間 ARI = {adjusted_rand_score(y, labels):.4f}")
