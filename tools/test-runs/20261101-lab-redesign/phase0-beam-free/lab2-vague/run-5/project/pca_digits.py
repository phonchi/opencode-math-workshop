"""手刻 PCA on sklearn digits，取前 10 個主成分，並與 sklearn PCA 驗證。"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

# 1. 資料
digits = load_digits()
X = digits.data.astype(float)  # (n, 64)
y = digits.target
n, d = X.shape

# 2. 手刻 PCA
mean = X.mean(axis=0)
Xc = X - mean

# SVD: Xc = U S Vt ; 主成分方向 = Vt 的前 k 列
U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
k = 10
components = Vt[:k]                      # (k, d)
explained_variance = (s[:k] ** 2) / (n - 1)
total_var = (s ** 2).sum() / (n - 1)
explained_variance_ratio = explained_variance / total_var

# transform
X_proj = Xc @ components.T                # (n, k)

# 3. sklearn PCA 驗證
sk = PCA(n_components=k)
X_sk = sk.fit_transform(X)

# 比對 component 方向（允許 sign flip）
cos = np.abs(components @ sk.components_.T)
diag = np.diag(cos)
print("component 方向 |cos| 對角線:", np.round(diag, 6))
print("max off-diag:", np.round(cos - np.diag(diag), 6).max())
print("explained_variance_ratio 手刻:", np.round(explained_variance_ratio, 6))
print("explained_variance_ratio sklearn:", np.round(sk.explained_variance_ratio_, 6))
print("ratio diff max:", np.abs(explained_variance_ratio - sk.explained_variance_ratio_).max())

# transform 比對（允許 sign flip）
corr = np.array([np.corrcoef(X_proj[:, i], X_sk[:, i])[0, 1] for i in range(k)])
print("transform corr (abs):", np.round(np.abs(corr), 6))

# 重建誤差
X_recon = X_proj @ components + mean
X_recon_sk = sk.inverse_transform(X_sk)
print("recon MSE 手刻:", np.mean((X - X_recon) ** 2))
print("recon MSE sklearn:", np.mean((X - X_recon_sk) ** 2))

# 4. 圖：前兩個主成分散佈
fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(X_proj[:, 0], X_proj[:, 1], c=y, cmap="tab10", s=8, alpha=0.7)
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
ax.set_title("Digits PCA (handcrafted) - first 2 components")
plt.colorbar(sc, ax=ax, label="digit")
fig.tight_layout()
fig.savefig("figs/pca_digits.png", dpi=150)
plt.close(fig)
print("saved figs/pca_digits.png")
print("components shape:", components.shape)
print("X_proj shape:", X_proj.shape)
