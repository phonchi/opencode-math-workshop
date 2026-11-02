import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.utils.extmath import svd_flip

# 資料
digits = load_digits()
X = digits.data.astype(np.float64)
n_samples, n_features = X.shape
k = 10

# 手刻 PCA：np.linalg.eigh
mean_hand = X.mean(axis=0)
Xc = X - mean_hand
cov = (Xc.T @ Xc) / (n_samples - 1)
eigvals, eigvecs = np.linalg.eigh(cov)
order = np.argsort(eigvals)[::-1]
eigvals = eigvals[order]
eigvecs = eigvecs[:, order]

components_hand = eigvecs[:, :k].T.copy()
ev_hand = eigvals[:k].copy()
evr_hand = eigvals[:k] / eigvals.sum()

# sklearn svd_flip 符號慣例對齊
U_hand = (Xc @ eigvecs[:, :k]) / np.sqrt((n_samples - 1) * np.clip(ev_hand, 1e-30, None))
U_hand, components_hand_t = svd_flip(U_hand, components_hand, u_based_decision=False)
components_hand = components_hand_t
X_hand = (X - mean_hand) @ components_hand.T

# sklearn 對照組
pca = PCA(n_components=k, svd_solver="full")
X_sklearn = pca.fit_transform(X)

def ok(cond):
    return "PASS" if bool(cond) else "FAIL"

# 1. 中心化向量
d_mean = np.max(np.abs(mean_hand - pca.mean_))
print(f"1 mean_ max_abs_diff={d_mean:.3e} {ok(d_mean <= 1e-12)}")

# 2. explained variance (eigenvalues)
d_ev = np.max(np.abs(ev_hand - pca.explained_variance_))
print(f"2 explained_variance max_abs_diff={d_ev:.3e} {ok(np.allclose(ev_hand, pca.explained_variance_, rtol=1e-7, atol=1e-10))}")

# 3. 主成分方向
cos = np.abs(np.sum(components_hand * pca.components_, axis=1))
min_cos = float(cos.min())
proj_hand = components_hand.T @ components_hand
proj_sklearn = pca.components_.T @ pca.components_
d_proj = np.linalg.norm(proj_hand - proj_sklearn, ord="fro")
print(f"3 components min_abs_cosine={min_cos:.10f} proj_fro_diff={d_proj:.3e} {ok((min_cos >= 1 - 1e-8) and (d_proj <= 1e-8))}")

# 4. 降維結果
d_X = np.max(np.abs(X_hand - X_sklearn))
print(f"4 transform max_abs_diff={d_X:.3e} {ok(np.allclose(X_hand, X_sklearn, rtol=1e-7, atol=1e-8))}")

# 5. 重構誤差
X_recon_hand = X_hand @ components_hand + mean_hand
rel_recon = np.linalg.norm(X - X_recon_hand, ord="fro") / np.linalg.norm(X, ord="fro")
X_recon_sklearn = pca.inverse_transform(X_sklearn)
d_recon = np.max(np.abs(X_recon_hand - X_recon_sklearn))
print(f"5 reconstruction rel_fro_vs_original={rel_recon:.3e} max_abs_diff_vs_sklearn={d_recon:.3e} {ok(np.allclose(X_recon_hand, X_recon_sklearn, rtol=1e-7, atol=1e-8))}")

# 6. explained variance ratio
d_ratio = np.max(np.abs(evr_hand - pca.explained_variance_ratio_))
print(f"6 explained_variance_ratio max_abs_diff={d_ratio:.3e} {ok(np.allclose(evr_hand, pca.explained_variance_ratio_, rtol=1e-7, atol=1e-10))}")

# 7. 正交性
orth = np.linalg.norm(components_hand @ components_hand.T - np.eye(k), ord="fro")
print(f"7 orthogonality fro_diff={orth:.3e} {ok(orth <= 1e-12)}")

# 8. 形狀/數量
shape_ok = (components_hand.shape == (k, n_features)) and (X_hand.shape == (n_samples, k))
print(f"8 shapes components={components_hand.shape} transform={X_hand.shape} {ok(shape_ok)}")
