"""用多個內部指標決定 sklearn digits 的最佳群數。"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
)

RNG = 42
digits = load_digits()
X_raw, y = digits.data, digits.target

# 影像資料標準化到 0-1 後再做 PCA，保留 95% 變異
X = StandardScaler().fit_transform(X_raw)
pca = PCA(n_components=0.95, random_state=RNG).fit(X)
Xp = pca.transform(X)
print(f"PCA components: {pca.n_components_}")

ks = list(range(2, 21))
res = {m: {"sil": [], "ch": [], "db": [], "ari": [], "nmi": []} for m in ("kmeans", "ward")}

for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=RNG).fit_predict(Xp)
    ward = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xp)
    for name, lab in (("kmeans", km), ("ward", ward)):
        r = res[name]
        r["sil"].append(silhouette_score(Xp, lab))
        r["ch"].append(calinski_harabasz_score(Xp, lab))
        r["db"].append(davies_bouldin_score(Xp, lab))
        r["ari"].append(adjusted_rand_score(y, lab))
        r["nmi"].append(normalized_mutual_info_score(y, lab))

hdr = f"{'k':>3} | {'sil_km':>7} {'sil_ward':>8} | {'CH_km':>8} {'CH_ward':>8} | {'DB_km':>6} {'DB_ward':>7} | {'ARI_km':>6} {'ARI_ward':>8} | {'NMI_km':>6} {'NMI_ward':>8}"
print(hdr)
print("-" * len(hdr))
for i, k in enumerate(ks):
    print(
        f"{k:>3} | {res['kmeans']['sil'][i]:>7.3f} {res['ward']['sil'][i]:>8.3f} | "
        f"{res['kmeans']['ch'][i]:>8.0f} {res['ward']['ch'][i]:>8.0f} | "
        f"{res['kmeans']['db'][i]:>6.3f} {res['ward']['db'][i]:>7.3f} | "
        f"{res['kmeans']['ari'][i]:>6.3f} {res['ward']['ari'][i]:>8.3f} | "
        f"{res['kmeans']['nmi'][i]:>6.3f} {res['ward']['nmi'][i]:>8.3f}"
    )

for name in ("kmeans", "ward"):
    r = res[name]
    print(
        f"\n{name}: best silhouette k={ks[int(np.argmax(r['sil']))]}, "
        f"best CH k={ks[int(np.argmax(r['ch']))]}, "
        f"best DB k={ks[int(np.argmin(r['db']))]}, "
        f"best ARI k={ks[int(np.argmax(r['ari']))]}"
    )

fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
panels = [("sil", "Silhouette (higher=better)"), ("ch", "Calinski-Harabasz (higher=better)"), ("db", "Davies-Bouldin (lower=better)")]
for ax, (key, title) in zip(axes, panels):
    for name, style in (("kmeans", "o-"), ("ward", "s--")):
        ax.plot(ks, res[name][key], style, label=name)
    ax.axvline(10, color="gray", ls=":", lw=1)
    ax.set_title(title)
    ax.set_xlabel("k")
    ax.legend()
fig.suptitle("sklearn digits: cluster-count selection (PCA 95% var)")
fig.tight_layout()
fig.savefig("figs/digits_k_selection.png", dpi=150)
print("saved figs/digits_k_selection.png")
