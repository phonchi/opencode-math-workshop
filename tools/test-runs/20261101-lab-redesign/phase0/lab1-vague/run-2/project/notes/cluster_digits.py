from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (silhouette_score, calinski_harabasz_score,
                             davies_bouldin_score, adjusted_rand_score)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RANDOM_STATE = 0
X, y = load_digits(return_X_y=True)
Xs = StandardScaler().fit_transform(X)
Xp = PCA(n_components=0.90, random_state=RANDOM_STATE).fit_transform(Xs)

ks = list(range(2, 21))
inertia, sil, ch, db, ari, acc_like = [], [], [], [], [], []

for k in ks:
    km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE).fit(Xp)
    lab = km.labels_
    inertia.append(km.inertia_)
    sil.append(silhouette_score(Xp, lab))
    ch.append(calinski_harabasz_score(Xp, lab))
    db.append(davies_bouldin_score(Xp, lab))
    ari.append(adjusted_rand_score(y, lab))
    # 每個 cluster 對應到的最多數真實類別比例（純度）
    purities = []
    for c in range(k):
        m = lab == c
        if m.sum() > 0:
            purities.append(np.bincount(y[m], minlength=10).max() / m.sum())
    acc_like.append(np.average(purities, weights=np.bincount(lab, minlength=k)))

print("PCA dims:", Xp.shape[1])
print(f"{'k':>3} {'inertia':>10} {'sil':>7} {'CH':>8} {'DB':>7} {'ARI':>7} {'purity':>7}")
for i, k in enumerate(ks):
    print(f"{k:>3} {inertia[i]:>10.1f} {sil[i]:>7.4f} {ch[i]:>8.1f} "
          f"{db[i]:>7.4f} {ari[i]:>7.4f} {acc_like[i]:>7.4f}")

best_sil = ks[int(np.argmax(sil))]
print("best k by silhouette:", best_sil)
print("best k by CH:", ks[int(np.argmax(ch))])

fig, axes = plt.subplots(2, 2, figsize=(10, 7))
axes[0, 0].plot(ks, inertia, "o-"); axes[0, 0].set_title("Inertia (elbow)")
axes[0, 1].plot(ks, sil, "o-"); axes[0, 1].set_title("Silhouette")
axes[1, 0].plot(ks, ch, "o-"); axes[1, 0].set_title("Calinski-Harabasz")
axes[1, 1].plot(ks, ari, "o-"); axes[1, 1].set_title("ARI vs true labels")
for ax in axes.flat:
    ax.set_xlabel("k"); ax.grid(alpha=.3)
fig.tight_layout()
fig.savefig("figs/digits_cluster_metrics.png", dpi=150)
print("saved figs/digits_cluster_metrics.png")

km = KMeans(n_clusters=best_sil, n_init=20, random_state=RANDOM_STATE).fit(Xp)
cross = np.zeros((best_sil, 10), int)
for c, t in zip(km.labels_, y):
    cross[c, t] += 1
print("confusion (cluster x digit) for k =", best_sil)
print(cross)
