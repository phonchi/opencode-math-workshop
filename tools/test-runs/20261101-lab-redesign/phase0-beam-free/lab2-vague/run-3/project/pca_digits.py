"""手刻 PCA（sklearn digits，取前 10 個主成分）並與 sklearn.PCA 驗證。"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

# 1. 資料
digits = load_digits()
X = digits.data.astype(float)          # (1797, 64)
y = digits.target

# 2. 手刻 PCA
n_samples, n_features = X.shape
mean = X.mean(axis=0)
Xc = X - mean

# SVD：Xc = U Σ V^T，主成分方向為 V 的列（右奇異向量）
U, s, Vt = np.linalg.svd(Xc, full_matrices=False)

k = 10
components = Vt[:k]                   # (10, 64)
explained_variance = (s[:k] ** 2) / (n_samples - 1)
total_var = (s ** 2).sum() / (n_samples - 1)
explained_variance_ratio = explained_variance / total_var
X_transformed = Xc @ components.T     # (1797, 10)

# 重建
X_reconstructed = X_transformed @ components + mean
recon_mse = np.mean((X - X_reconstructed) ** 2)

# 3. 與 sklearn PCA 比對
sk = PCA(n_components=k, svd_solver="full")
X_sk = sk.fit_transform(X)

# components：方向可能 sign flip，比對絕對 cosine
cos = np.abs(np.sum(components * sk.components_, axis=1))
# transformed：可能 sign flip，比對絕對相關
corr = np.abs(np.corrcoef(X_transformed.T, X_sk.T)[:k, k:]).diagonal()

print("explained_variance_ratio (mine):", np.round(explained_variance_ratio, 6))
print("explained_variance_ratio (sk)  :", np.round(sk.explained_variance_ratio_, 6))
print("|cos(components)|              :", np.round(cos, 6))
print("|corr(transformed)|           :", np.round(corr, 6))
print("reconstruction MSE            :", recon_mse)
print("cumulative var (mine)         :", round(explained_variance_ratio.sum(), 6))

# 4. 圖：scree + 前兩個 PC 散佈
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(range(1, k + 1), explained_variance_ratio, color="steelblue")
axes[0].plot(range(1, k + 1), np.cumsum(explained_variance_ratio), "ro-")
axes[0].set_xlabel("主成分")
axes[0].set_ylabel("解釋變異比例")
axes[0].set_title("Digits PCA 前 10 主成分")

sc = axes[1].scatter(X_transformed[:, 0], X_transformed[:, 1], c=y, cmap="tab10", s=8, alpha=0.7)
axes[1].set_xlabel("PC1")
axes[1].set_ylabel("PC2")
axes[1].set_title("前兩主成分散佈")
fig.colorbar(sc, ax=axes[1])
fig.tight_layout()
fig.savefig("figs/pca_digits.png", dpi=150)
print("saved figs/pca_digits.png")
plt.close(fig)
