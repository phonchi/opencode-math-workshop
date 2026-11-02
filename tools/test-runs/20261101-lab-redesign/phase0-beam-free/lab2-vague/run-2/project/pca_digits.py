"""手刻 PCA on sklearn digits, 取前 10 主成分，並與 sklearn PCA 驗證。"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

digits = load_digits()
X = digits.data.astype(float)
n_samples, n_features = X.shape

# --- 手刻 PCA (SVD) ---
Xc = X - X.mean(axis=0)                       # 中心化
U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
k = 10
components = Vt[:k]                           # (k, n_features) 主成分方向
explained_variance = (s[:k] ** 2) / (n_samples - 1)
total_var = np.var(X, axis=0, ddof=1).sum()
explained_variance_ratio = explained_variance / total_var
X_transformed = Xc @ components.T             # (n_samples, k)

# --- sklearn PCA ---
sk = PCA(n_components=k, svd_solver="full")
sk.fit(X)
sk_transformed = sk.transform(X)

# --- 驗證 ---
# 1. explained variance ratio
evr_diff = np.max(np.abs(explained_variance_ratio - sk.explained_variance_ratio_))
# 2. components (up to sign)
comp_diff = 0.0
for i in range(k):
    # 對齊 sign
    a = components[i]
    b = sk.components_[i]
    sign = np.sign(np.dot(a, b)) or 1.0
    comp_diff = max(comp_diff, np.max(np.abs(a - sign * b)))
# 3. transformed (up to sign per component)
trans_diff = 0.0
for i in range(k):
    a = X_transformed[:, i]
    b = sk_transformed[:, i]
    sign = np.sign(np.dot(a, b)) or 1.0
    trans_diff = max(trans_diff, np.max(np.abs(a - sign * b)))

print("shape X:", X.shape)
print("前 10 explained_variance_ratio (手刻):", np.round(explained_variance_ratio, 6))
print("前 10 explained_variance_ratio (sklearn):", np.round(sk.explained_variance_ratio_, 6))
print("max |evr diff|:", evr_diff)
print("max |component diff| (sign-aligned):", comp_diff)
print("max |transform diff| (sign-aligned):", trans_diff)
print("cumulative explained variance (10 PCs):", explained_variance_ratio.sum())

assert evr_diff < 1e-10, "explained variance ratio 不符"
assert comp_diff < 1e-10, "components 不符"
assert trans_diff < 1e-10, "transformed 不符"
print("OK: 手刻 PCA 與 sklearn PCA 一致（前 10 主成分）")
