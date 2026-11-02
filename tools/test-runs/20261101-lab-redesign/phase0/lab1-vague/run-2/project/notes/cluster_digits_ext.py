from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
import numpy as np

X, y = load_digits(return_X_y=True)

reps = {
    "scaled_pca90": PCA(n_components=0.90, random_state=0).fit_transform(
        StandardScaler().fit_transform(X)),
    "raw_pca30": PCA(n_components=30, random_state=0).fit_transform(X),
    "raw_pca2": PCA(n_components=2, random_state=0).fit_transform(X),
}

ks = list(range(2, 41))
print("silhouette by representation")
print("k   " + "  ".join(f"{n:>13}" for n in reps))
for k in ks:
    row = []
    for name, Xr in reps.items():
        lab = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(Xr)
        row.append(silhouette_score(Xr, lab) if len(set(lab)) > 1 else np.nan)
    print(f"{k:<3} " + "  ".join(f"{v:>13.4f}" for v in row))

for name, Xr in reps.items():
    best = None
    for k in range(2, 41):
        lab = KMeans(n_clusters=k, n_init=20, random_state=0).fit_predict(Xr)
        s = silhouette_score(Xr, lab)
        a = adjusted_rand_score(y, lab)
        if best is None or s > best[1]:
            best = (k, s, a)
    print(f"{name}: silhouette-best k={best[0]} (sil={best[1]:.4f}, ARI={best[2]:.4f})")

print("\nARI/purity at k=9..13 (scaled_pca90)")
Xr = reps["scaled_pca90"]
for k in range(9, 14):
    lab = KMeans(n_clusters=k, n_init=20, random_state=0).fit_predict(Xr)
    pur = []
    for c in range(k):
        m = lab == c
        if m.sum():
            pur.append(np.bincount(y[m], minlength=10).max() / m.sum())
    print(f"k={k}: ARI={adjusted_rand_score(y, lab):.4f} purity="
          f"{np.average(pur, weights=np.bincount(lab, minlength=k)):.4f}")
