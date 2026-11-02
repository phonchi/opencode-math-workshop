import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score,
    adjusted_rand_score, normalized_mutual_info_score,
)

RNG = 42
digits = load_digits()
X, y_true = digits.data, digits.target
X_scaled = StandardScaler().fit_transform(X)

ks = list(range(2, 16))
inertia, sil, ch, db, ari, nmi = [], [], [], [], [], []

for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=RNG)
    labels = km.fit_predict(X_scaled)
    inertia.append(km.inertia_)
    sil.append(silhouette_score(X_scaled, labels, sample_size=1000, random_state=RNG))
    ch.append(calinski_harabasz_score(X_scaled, labels))
    db.append(davies_bouldin_score(X_scaled, labels))
    ari.append(adjusted_rand_score(y_true, labels))
    nmi.append(normalized_mutual_info_score(y_true, labels))
    print(f"k={k:2d} inertia={km.inertia_:9.1f} sil={sil[-1]:.4f} "
          f"CH={ch[-1]:8.1f} DB={db[-1]:.4f} ARI={ari[-1]:.4f} NMI={nmi[-1]:.4f}")

print("\n最佳（以各指標）：")
print(f"silhouette 最大 -> k={ks[int(np.argmax(sil))]}")
print(f"CH 最大         -> k={ks[int(np.argmax(ch))]}")
print(f"DB 最小         -> k={ks[int(np.argmin(db))]}")
print(f"ARI 最大        -> k={ks[int(np.argmax(ari))]}")

# 肘部法：以相鄰 inertia 降幅判斷
drops = -np.diff(inertia)
print("\ninertia 降幅：")
for k, d in zip(ks[1:], drops):
    print(f"  {k-1}->{k}: {d:.1f}")

# 視覺化
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes[0, 0].plot(ks, inertia, "o-"); axes[0, 0].set_title("Elbow (inertia)")
axes[0, 0].set_xlabel("k"); axes[0, 0].set_ylabel("inertia")
axes[0, 1].plot(ks, sil, "o-"); axes[0, 1].set_title("Silhouette (higher=better)")
axes[0, 1].set_xlabel("k")
axes[0, 2].plot(ks, ch, "o-"); axes[0, 2].set_title("Calinski-Harabasz (higher=better)")
axes[0, 2].set_xlabel("k")
axes[1, 0].plot(ks, db, "o-"); axes[1, 0].set_title("Davies-Bouldin (lower=better)")
axes[1, 0].set_xlabel("k")
axes[1, 1].plot(ks, ari, "o-", label="ARI"); axes[1, 1].plot(ks, nmi, "s-", label="NMI")
axes[1, 1].set_title("Against true digit labels"); axes[1, 1].legend(); axes[1, 1].set_xlabel("k")
for k in ks:
    axes[1, 1].axvline(k, color="gray", alpha=0.05)
pca = PCA(n_components=2, random_state=RNG)
Xp = pca.fit_transform(X_scaled)
sc = axes[1, 2].scatter(Xp[:, 0], Xp[:, 1], c=y_true, cmap="tab10", s=8)
axes[1, 2].set_title("PCA (colored by true digit)")
fig.tight_layout()
fig.savefig("figs/digits_cluster_diagnostics.png", dpi=150)
print("\n圖已存：figs/digits_cluster_diagnostics.png")
