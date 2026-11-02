import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

# 1. 載入資料
digits = load_digits()
X = digits.data.astype(float)
n_samples, n_features = X.shape
print(f"X shape: {X.shape}")

# 2. 手刻 PCA（基於 SVD）
k = 10
X_mean = X.mean(axis=0)
Xc = X - X_mean  # 中心化

# SVD: Xc = U S V^T
U, s, Vt = np.linalg.svd(Xc, full_matrices=False)

# 主成分方向（每列一個主成分，shape (k, n_features)）
components_hand = Vt[:k]

# 奇異值 -> eigenvalues of covariance (除以 n_samples-1)
eigvals = (s ** 2) / (n_samples - 1)
explained_variance_hand = eigvals[:k]
explained_variance_ratio_hand = explained_variance_hand / eigvals.sum()

# 投影 (n_samples, k)
X_transformed_hand = Xc @ components_hand.T

# 3. 用 sklearn PCA 驗證
pca = PCA(n_components=k, svd_solver="full")
X_transformed_sk = pca.fit_transform(X)

# 4. 比較
# component 方向：cosine similarity 絕對值（符號可能相反）
cos = np.array([
    np.abs(np.dot(components_hand[i], pca.components_[i])
           / (np.linalg.norm(components_hand[i]) * np.linalg.norm(pca.components_[i])))
    for i in range(k)
])
print("cos |hand vs sklearn| per component:", np.round(cos, 6))
print("all components aligned (|cos|≈1):", np.allclose(cos, 1.0))

# explained variance ratio
print("explained_variance_ratio hand :", np.round(explained_variance_ratio_hand, 6))
print("explained_variance_ratio sk  :", np.round(pca.explained_variance_ratio_, 6))
print("EVR close:", np.allclose(explained_variance_ratio_hand, pca.explained_variance_ratio_))

# transform 結果（符號對齊後比）
# 以 sklearn 為準，允許整列符號翻轉
maxdiff = 0.0
for i in range(k):
    a = X_transformed_hand[:, i]
    b = X_transformed_sk[:, i]
    # 選符號使差最小
    diff = min(np.max(np.abs(a - b)), np.max(np.abs(a + b)))
    maxdiff = max(maxdiff, diff)
print("max transform diff (after sign align):", maxdiff)
print("transform close:", maxdiff < 1e-8)

# 重建誤差
X_recon = X_transformed_hand @ components_hand + X_mean
recon_err = np.mean((X - X_recon) ** 2)
print("reconstruction MSE (10 comps):", recon_err)

# assertions
assert np.allclose(cos, 1.0), "components not aligned"
assert np.allclose(explained_variance_ratio_hand, pca.explained_variance_ratio_), "EVR mismatch"
assert maxdiff < 1e-8, "transform mismatch"
print("\nPCA 手刻驗證通過 ✔")
