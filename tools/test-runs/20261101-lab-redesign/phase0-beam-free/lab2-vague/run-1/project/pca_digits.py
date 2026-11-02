"""手刻 PCA：sklearn digits，取前 10 個主成分，並與 sklearn PCA 驗證。"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

# 1. 資料
X, y = load_digits(return_X_y=True)
n_samples, n_features = X.shape
print(f"X shape: {X.shape}")

# 2. 手刻 PCA（以 SVD 實作，等價於 eig on covariance）
def pca_handmade(X, n_components):
    # 中心化
    mean = X.mean(axis=0)
    Xc = X - mean
    # SVD：Xc = U S V^T
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    components = Vt[:n_components]          # 主成分方向 (n_components, n_features)
    # 投影
    X_proj = Xc @ components.T              # (n_samples, n_components)
    # explained variance（ddof=1，與 sklearn 一致）
    explained_variance = (s ** 2) / (n_samples - 1)
    total_var = explained_variance.sum()
    explained_variance_ratio = explained_variance / total_var
    return mean, components, X_proj, explained_variance[:n_components], explained_variance_ratio[:n_components]

mean, components, X_proj, ev, evr = pca_handmade(X, 10)
print("手刻 explained_variance_ratio (前10):", np.round(evr, 6))
print("累積:", round(evr.sum(), 6))

# 3. sklearn PCA 驗證
sk = PCA(n_components=10)
X_sk = sk.fit_transform(X)
print("sklearn explained_variance_ratio (前10):", np.round(sk.explained_variance_ratio_, 6))
print("sklearn 累積:", round(sk.explained_variance_ratio_.sum(), 6))

# 4. 驗證：成分方向（符號不固定，比絕對值）
# 對齊符號
def align_sign(a, b):
    # a, b: (n, d) -> 使每欄相關為正
    out = a.copy()
    for j in range(a.shape[1]):
        if np.dot(a[:, j], b[:, j]) < 0:
            out[:, j] = -a[:, j]
    return out

comp_aligned = align_sign(components.T, sk.components_.T)  # (features, 10)
maxdiff_comp = np.abs(comp_aligned - sk.components_.T).max()
print("成分最大差異 (對齊符號後):", maxdiff_comp)

proj_aligned = align_sign(X_proj, X_sk)
maxdiff_proj = np.abs(proj_aligned - X_sk).max()
print("投影最大差異 (對齊符號後):", maxdiff_proj)

# explained variance ratio 差異
print("EVR 最大差異:", np.abs(evr - sk.explained_variance_ratio_).max())

# 重建誤差
X_recon = X_proj @ components + mean
recon_err = np.linalg.norm(X - X_recon) / np.linalg.norm(X - X.mean(0))
print("重建相對誤差:", recon_err)
X_recon_sk = sk.inverse_transform(X_sk)
print("sklearn 重建相對誤差:", np.linalg.norm(X - X_recon_sk) / np.linalg.norm(X - X.mean(0)))

# 正交性檢查
print("成分正交性 (C C^T - I) max:", np.abs(components @ components.T - np.eye(10)).max())
print("投影中心化 (mean abs):", np.abs(X_proj.mean(0)).max())

# 判定
tol = 1e-9
ok = (maxdiff_comp < 1e-6 and maxdiff_proj < 1e-6 and
      np.abs(evr - sk.explained_variance_ratio_).max() < 1e-9)
print("驗證結果:", "PASS" if ok else "FAIL")
