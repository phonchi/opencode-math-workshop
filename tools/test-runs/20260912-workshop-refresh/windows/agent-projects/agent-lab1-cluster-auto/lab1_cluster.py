import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.metrics import silhouette_score

k_min, k_max = 2, 12
random_state = 0

X = load_digits().data

Ks = []
inertias = []
silhouettes = []

for k in range(k_min, k_max + 1):
    km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)
    Ks.append(k)
    inertias.append(km.inertia_)
    silhouettes.append(sil)
    print(f"k={k:2d}  inertia={km.inertia_:12.2f}  silhouette={sil:.6f}")

best_k = Ks[silhouettes.index(max(silhouettes))]
print(f"\nSilhouette 最高的 k = {best_k} (silhouette={max(silhouettes):.6f})")

fig, ax = plt.subplots(1, 2, figsize=(12, 4))

ax[0].plot(Ks, inertias, marker="o")
ax[0].set_xlabel("k")
ax[0].set_ylabel("Inertia")
ax[0].set_title("k-means inertia vs k")
ax[0].set_xticks(Ks)

ax[1].plot(Ks, silhouettes, marker="o", color="tab:orange")
ax[1].set_xlabel("k")
ax[1].set_ylabel("Silhouette score")
ax[1].set_title("Silhouette score vs k")
ax[1].set_xticks(Ks)

plt.tight_layout()
plt.savefig("figs/lab1_k_selection.png", dpi=150)