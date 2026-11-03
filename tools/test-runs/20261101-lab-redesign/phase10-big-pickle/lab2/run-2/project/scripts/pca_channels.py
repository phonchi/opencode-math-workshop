import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

data = np.genfromtxt("data/line_channels.csv", delimiter=",", names=True)
cols = list(data.dtype.names)
X = np.column_stack([data[c] for c in cols])

Xz = StandardScaler().fit_transform(X)

pca = PCA()
scores = pca.fit_transform(Xz)
evr = pca.explained_variance_ratio_
eig = pca.explained_variance_

np.set_printoptions(precision=4, suppress=True)
print("channel  " + "  ".join(f"PC{i+1:<5d}" for i in range(len(cols))))
for j, c in enumerate(cols):
    print(f"{c:<8s} " + "  ".join(f"{v:+.3f}" for v in pca.components_[:, j]))

print("\nexplained variance ratio:")
for i, (e, r) in enumerate(zip(eig, evr), 1):
    print(f"PC{i:<2d} eigenvalue={e:.4f}  evr={r:.4f}  cumulative={evr[:i].sum():.4f}")

n_kaiser = int((eig > 1).sum())
n_80 = int(np.searchsorted(np.cumsum(evr), 0.80) + 1)
n_90 = int(np.searchsorted(np.cumsum(evr), 0.90) + 1)
print(f"\nKaiser (eigenvalue>1): {n_kaiser}")
print(f"80% variance: {n_80}, 90% variance: {n_90}")

# Scree plot
fig, ax = plt.subplots(figsize=(7, 4.5))
pcs = np.arange(1, len(cols) + 1)
ax.plot(pcs, evr, "o-", color="#2c6e9b")
ax.bar(pcs, evr, alpha=0.25, color="#2c6e9b")
ax.axhline(1 / len(cols), color="gray", ls="--", lw=1, label="Kaiser threshold (1/p)")
ax.set_xticks(pcs)
ax.set_xlabel("Principal component")
ax.set_ylabel("Explained variance ratio")
ax.set_title("Scree plot of line sensor channels")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figs/pca_scree.png", dpi=150)

# Cumulative variance
fig, ax = plt.subplots(figsize=(7, 4.5))
cum = np.cumsum(evr)
ax.plot(pcs, cum, "o-", color="#b5523b")
ax.axhline(0.80, color="gray", ls="--", lw=1)
ax.axhline(0.90, color="gray", ls=":", lw=1)
ax.text(len(cols), 0.805, "80%", ha="right", va="bottom", fontsize=9)
ax.text(len(cols), 0.905, "90%", ha="right", va="bottom", fontsize=9)
ax.set_xticks(pcs)
ax.set_ylim(0, 1.02)
ax.set_xlabel("Number of components")
ax.set_ylabel("Cumulative explained variance")
ax.set_title("Cumulative explained variance")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figs/pca_cumulative.png", dpi=150)

# Loadings heatmap
fig, ax = plt.subplots(figsize=(6.5, 6))
im = ax.imshow(pca.components_.T, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(cols)))
ax.set_xticklabels([f"PC{i+1}" for i in range(len(cols))], rotation=45, ha="right")
ax.set_yticks(range(len(cols)))
ax.set_yticklabels(cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j, i, f"{pca.components_[j, i]:+.2f}", ha="center", va="center", fontsize=7)
ax.set_title("PCA loadings (standardized data)")
fig.colorbar(im, ax=ax, shrink=0.8, label="loading")
fig.tight_layout()
fig.savefig("figs/pca_loadings.png", dpi=150)

# Biplot PC1-PC2
fig, ax = plt.subplots(figsize=(7.5, 6))
ax.scatter(scores[:, 0], scores[:, 1], s=10, alpha=0.35, color="#2c6e9b")
scale = 3.0
for j, c in enumerate(cols):
    ax.arrow(0, 0, pca.components_[0, j] * scale, pca.components_[1, j] * scale,
             color="#b5523b", head_width=0.08, length_includes_head=True, alpha=0.8)
    ax.text(pca.components_[0, j] * scale * 1.12, pca.components_[1, j] * scale * 1.12,
            c, color="#b5523b", fontsize=8, ha="center", va="center")
ax.axhline(0, color="gray", lw=0.6)
ax.axvline(0, color="gray", lw=0.6)
ax.set_xlabel(f"PC1 ({evr[0]:.1%})")
ax.set_ylabel(f"PC2 ({evr[1]:.1%})")
ax.set_title("PCA biplot (PC1 vs PC2)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figs/pca_biplot.png", dpi=150)
