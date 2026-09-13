import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.metrics import silhouette_score

digits = load_digits()
X = digits.data

k_range = range(2, 13)
inertias = []
silhouettes = []

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
    labels = kmeans.fit_predict(X)
    inertia = kmeans.inertia_
    sil = silhouette_score(X, labels)
    inertias.append(inertia)
    silhouettes.append(sil)
    print(f"k={k:2d}  inertia={inertia:12.2f}  silhouette={sil:.4f}")

best_k = k_range[0]
for k, sil in zip(k_range, silhouettes):
    if sil > silhouettes[k_range.index(best_k)]:
        best_k = k
print(f"\n最高的 silhouette 出現在 k = {best_k}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(list(k_range), inertias, marker="o")
axes[0].set_xlabel("k")
axes[0].set_ylabel("inertia")
axes[0].set_title("inertia vs k")
axes[1].plot(list(k_range), silhouettes, marker="o")
axes[1].axvline(best_k, color="r", linestyle="--", alpha=0.5)
axes[1].set_xlabel("k")
axes[1].set_ylabel("silhouette score")
axes[1].set_title("silhouette vs k")
fig.tight_layout()
fig.savefig("figs/lab1_k_selection.png", dpi=150)