import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits

K = 10

X, y = load_digits(return_X_y=True)
n, d = X.shape
mean = X.mean(axis=0)
Xc = X - mean

U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
V = Vt[:K]
Z = Xc @ V.T
eigvals = S[:K] ** 2 / (n - 1)
total_var = Xc.var(axis=0, ddof=1).sum()
evr = eigvals / total_var

pca = PCA(n_components=K).fit(X)
Z_sk = pca.transform(X)

sign = np.sign((V * pca.components_).sum(axis=1))
sign[sign == 0] = 1

checks = []

def check(name, ok):
    checks.append((name, bool(ok)))

check("explained_variance_ 相符", np.allclose(eigvals, pca.explained_variance_, atol=1e-8))
check("explained_variance_ratio_ 相符", np.allclose(evr, pca.explained_variance_ratio_, atol=1e-8))
check("components_ 相符（允許差正負號）", np.allclose(V * sign[:, None], pca.components_, atol=1e-8))
check("投影座標 Z = transform(X)", np.allclose(Z * sign, Z_sk, atol=1e-8))
check("主成分為單範正交 V Vᵀ = I", np.allclose(V @ V.T, np.eye(K), atol=1e-10))
check("投影均值為 0", np.allclose(Z.mean(axis=0), 0.0, atol=1e-10))
check("投影變異數 = 特徵值", np.allclose(Z.var(axis=0, ddof=1), eigvals, atol=1e-8))

X_rec = Z @ V + mean
X_rec_sk = pca.inverse_transform(Z_sk)
mse_hand = ((X - X_rec) ** 2).mean()
mse_sk = ((X - X_rec_sk) ** 2).mean()
check("10 成分重建誤差一致", np.isclose(mse_hand, mse_sk, atol=1e-8))
check("重建誤差 = (n-1)/n × 剩餘特徵值之和 / d",
      np.isclose(mse_hand, (n - 1) / n * (total_var - eigvals.sum()) / d, atol=1e-8))

C = Xc.T @ Xc / (n - 1)
evals_all, evecs_all = np.linalg.eigh(C)
evals_top = evals_all[::-1][:K]
evecs_top = evecs_all[:, ::-1][:, :K].T
sign2 = np.sign((evecs_top * V).sum(axis=1))
sign2[sign2 == 0] = 1
check("協方差 eigh 與 SVD 特徵值一致", np.allclose(evals_top, eigvals, atol=1e-6))
check("協方差 eigh 與 SVD 特徵向量一致", np.allclose(evecs_top * sign2[:, None], V, atol=1e-6))

print(f"digits 資料：n={n}, d={d}，取前 {K} 個主成分\n")
print(f"{'PC':>4} {'手刻 EVR':>12} {'sklearn EVR':>14}")
for i in range(K):
    print(f"{i + 1:>4} {evr[i]:>11.4%} {pca.explained_variance_ratio_[i]:>14.4%}")
print(f"{'累計':>4} {evr.sum():>11.4%} {pca.explained_variance_ratio_.sum():>14.4%}\n")

for name, ok in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
assert all(ok for _, ok in checks), "有驗證未通過"
print(f"\n共 {len(checks)} 項驗證全數通過；重建 MSE = {mse_hand:.4f}")

fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
idx = np.arange(1, K + 1)

ax = axes[0, 0]
ax.bar(idx, evr * 100, color="#4878cf", label="hand-coded (SVD)")
ax.plot(idx, pca.explained_variance_ratio_ * 100, "ko", ms=5, label="sklearn PCA")
ax2 = ax.twinx()
ax2.plot(idx, np.cumsum(evr) * 100, "r.-", label="cumulative")
ax2.set_ylabel("cumulative EVR (%)", color="r")
ax2.set_ylim(0, 100)
ax.set_xlabel("principal component")
ax.set_ylabel("explained variance ratio (%)")
ax.set_title("Scree: hand-coded vs sklearn")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="center right", fontsize=8)

ax = axes[0, 1]
sc = ax.scatter(Z[:, 0], Z[:, 1], c=y, cmap="tab10", s=10, alpha=0.8)
fig.colorbar(sc, ax=ax, ticks=range(10), label="digit")
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_title("Projection onto first 2 PCs (hand-coded)")

ax = axes[1, 0]
for j, c in zip([0, 1], ["#4878cf", "#d65f5f"]):
    ax.scatter(Z_sk[:, j], Z[:, j], s=8, alpha=0.5, color=c, label=f"PC{j + 1}")
lims = [Z_sk.min(), Z_sk.max()]
ax.plot(lims, lims, "k--", lw=1, label="y = x")
ax.set_xlabel("sklearn coordinate")
ax.set_ylabel("hand-coded coordinate")
ax.set_title("Projected coordinates agree (up to sign)")
ax.legend(fontsize=8)

ax = axes[1, 1]
gap = np.full((8, 2), np.nan)
img = np.hstack([X[0].reshape(8, 8), gap, X_rec[0].reshape(8, 8)])
ax.imshow(img, cmap="gray_r", vmin=0, vmax=16)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(f"sample 0: original | reconstructed ({K} PCs, MSE={((X[0] - X_rec[0]) ** 2).mean():.2f})")

fig.suptitle("Hand-coded PCA on sklearn digits (n=1797, d=64)")
fig.tight_layout()
fig.savefig("figs/pca_digits_check.png", dpi=150, bbox_inches="tight")
plt.close(fig)
