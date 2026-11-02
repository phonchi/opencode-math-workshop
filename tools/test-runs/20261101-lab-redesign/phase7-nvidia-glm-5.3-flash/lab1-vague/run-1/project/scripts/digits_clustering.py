"""評估 sklearn digits 資料集的最佳分群數（k）。

比較兩種表示法：
- raw：StandardScaler 標準化後的原始 64 維
- pca：標準化後再 PCA 保留 95% 變異（40 維）

指標：
- 內部指標：silhouette、Calinski-Harabasz、Davies-Bouldin
- 外部驗證：對照真實標籤（0-9 共 10 類）的 ARI
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for f in ["Noto Sans CJK TC", "Droid Sans Fallback"]:
    try:
        font_manager.findfont(f, fallback_to_default=False)
        plt.rcParams["font.family"] = [f]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    adjusted_rand_score,
)

digits = load_digits()
X, y = digits.data, digits.target
X_raw = StandardScaler().fit_transform(X)
X_pca = PCA(n_components=0.95, random_state=42).fit_transform(X_raw)
print(f"raw: {X_raw.shape[1]} 維, pca(95%): {X_pca.shape[1]} 維, n={len(X)}, 真實類別數=10")

ks = range(2, 21)
spaces = {"raw": X_raw, "pca": X_pca}
results = {name: {"sil": [], "ch": [], "db": [], "ari": [], "inertia": []}
           for name in spaces}

for name, Xs in spaces.items():
    for k in ks:
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        labels = km.fit_predict(Xs)
        r = results[name]
        r["sil"].append(silhouette_score(Xs, labels))
        r["ch"].append(calinski_harabasz_score(Xs, labels))
        r["db"].append(davies_bouldin_score(Xs, labels))
        r["ari"].append(adjusted_rand_score(y, labels))
        r["inertia"].append(km.inertia_)

print("\n== 每個指標的最適 k ==")
print(f"{'指標':<18}{'raw':>6}{'pca':>6}")
for metric, better in [("sil", "max"), ("ch", "max"), ("db", "min"), ("ari", "max")]:
    row = []
    for name in spaces:
        arr = np.array(results[name][metric])
        idx = int(np.argmax(arr)) if better == "max" else int(np.argmin(arr))
        row.append(f"k={list(ks)[idx]} ({arr[idx]:.3f})")
    print(f"{metric:<18}{row[0]:>22}{row[1]:>22}")

print("\n== ARI 明細（對照真實 10 類）==")
print(" k  |  raw ARI |  pca ARI")
for i, k in enumerate(ks):
    print(f"{k:3d} |  {results['raw']['ari'][i]:.4f}  |  {results['pca']['ari'][i]:.4f}")

# 畫圖
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
colors = {"raw": "tab:blue", "pca": "tab:red"}
titles = {
    "sil": "Silhouette（越大越好）",
    "ch": "Calinski-Harabasz（越大越好）",
    "db": "Davies-Bouldin（越小越好）",
    "inertia": "Inertia（找 elbow）",
    "ari": "ARI 對照真實標籤（越大越好）",
}
for ax, metric in zip(axes.flat[:5], ["sil", "ch", "db", "inertia", "ari"]):
    for name in spaces:
        ax.plot(list(ks), results[name][metric], "o-", ms=3,
                color=colors[name], label=name, alpha=0.8)
    ax.axvline(10, color="gray", ls=":", lw=1)
    ax.text(10.1, ax.get_ylim()[1] * 0.97, "k=10 (真實類別數)",
            fontsize=8, color="gray", va="top")
    ax.set_xlabel("k"); ax.set_ylabel(metric)
    ax.set_title(titles[metric]); ax.grid(alpha=0.3); ax.legend()

# PCA 前兩主軸 + k=10 分群結果
km10 = KMeans(n_clusters=10, n_init=20, random_state=42).fit(X_pca)
ax = axes.flat[5]
for c in range(10):
    m = km10.labels_ == c
    ax.scatter(X_pca[m, 0], X_pca[m, 1], s=6, alpha=0.5, label=f"c{c}")
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
ax.set_title("KMeans k=10（pca 空間，前兩主軸）")
ax.legend(fontsize=7, markerscale=2)

fig.suptitle("sklearn digits 最佳分群數分析（raw 64 維 vs PCA 40 維）", fontsize=14)
fig.tight_layout()
fig.savefig("figs/digits_cluster_k_selection.png", dpi=150)
print("\n圖已存到 figs/digits_cluster_k_selection.png")
