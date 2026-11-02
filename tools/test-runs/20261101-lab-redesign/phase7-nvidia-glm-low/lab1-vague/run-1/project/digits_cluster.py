import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score

X, y = load_digits(return_X_y=True)
Xs = StandardScaler().fit_transform(X)
Xp = PCA(n_components=0.90, random_state=0).fit_transform(Xs)
print("PCA dims:", Xp.shape[1])

ks = range(2, 21)
sil = []
ari = []
for k in ks:
    lab = KMeans(n_clusters=k, n_init=20, random_state=0).fit_predict(Xp)
    sil.append(silhouette_score(Xp, lab))
    ari.append(adjusted_rand_score(y, lab))

for k, s, a in zip(ks, sil, ari):
    print(f"k={k:2d}  silhouette={s:.4f}  ARI={a:.4f}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(list(ks), sil, "o-", label="silhouette")
ax.plot(list(ks), ari, "s--", label="ARI vs true labels")
ax.set_xlabel("k")
ax.legend()
fig.savefig("figs/digits_k_selection.png", dpi=150, bbox_inches="tight")
print("saved figs/digits_k_selection.png")
