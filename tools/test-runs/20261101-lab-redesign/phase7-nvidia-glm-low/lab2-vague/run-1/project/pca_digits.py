import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X = load_digits().data
Xc = X - X.mean(axis=0)

# 手刻 PCA：covariance eigendecomposition
cov = Xc.T @ Xc / (X.shape[0] - 1)
eigvals, eigvecs = np.linalg.eigh(cov)
idx = np.argsort(eigvals)[::-1][:10]
W = eigvecs[:, idx]              # 10 個主成分（每行一個）
Z = Xc @ W                       # 投影

# 對照 sklearn
pca = PCA(n_components=10)
Z_ref = pca.fit_transform(X)

total_var = (Xc ** 2).sum() / (X.shape[0] - 1)
print("explained variance ratio:", np.round(eigvals[idx] / total_var, 4))
print("explained variance ratio (sklearn):", np.round(pca.explained_variance_ratio_, 4))

# 比較：投影結果可能差一個符號（特徵向量方向不唯一）
sign_fix = np.sign(np.sum(Z * Z_ref, axis=0))
sign_fix[sign_fix == 0] = 1
Z_aligned = Z * sign_fix
print("max |Z - Z_ref| after sign fix:", np.abs(Z_aligned - Z_ref).max())
print("explained variance ratio allclose:", np.allclose(eigvals[idx] / total_var, pca.explained_variance_ratio_))
assert np.allclose(Z_aligned, Z_ref, atol=1e-8)
print("OK: 手刻 PCA 與 sklearn 一致")
