"""sklearn digits 手刻 PCA：先實作 PCA、取前 10 主成分，再驗證結果是否正確。"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

K = 10

digits = load_digits()
X, y = digits.data, digits.target
n_samples, n_features = X.shape

mean = X.mean(axis=0)
Xc = X - mean

cov = np.cov(Xc.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
order = np.argsort(eigenvalues)[::-1]
top = order[:K]
eigenvalues_k = eigenvalues[top]
components_k = eigenvectors[:, top].T

Z = Xc @ components_k.T
total_var = eigenvalues.sum()
explained_variance_k = eigenvalues[top]
explained_ratio_k = explained_variance_k / total_var

U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
svd_eigenvalues = S ** 2 / (n_samples - 1)
svd_components_k = Vt[:K]

sk = PCA(n_components=K)
Z_sk = sk.fit_transform(X)
sk_components = sk.components_
sk_explained = sk.explained_variance_
sk_ratio = sk.explained_variance_ratio_


def align_signs(M):
    M = np.array(M, dtype=float, copy=True)
    for i in range(M.shape[0]):
        j = int(np.argmax(np.abs(M[i])))
        if M[i, j] < 0:
            M[i] = -M[i]
    return M


comp_k_aligned = align_signs(components_k)
sk_aligned = align_signs(sk_components)
max_comp_diff = float(np.max(np.abs(comp_k_aligned - sk_aligned)))

flips = np.array([
    1.0 if components_k[i, int(np.argmax(np.abs(components_k[i])))] > 0 else -1.0
    for i in range(K)
])
Z_aligned = Z * flips
max_proj_diff = float(np.max(np.abs(Z_aligned - Z_sk)))

checks = {}
checks["SVD 與 EIG 本質值一致"] = bool(
    np.allclose(np.sort(svd_eigenvalues)[::-1], np.sort(eigenvalues)[::-1], atol=1e-8)
)
checks["SVD 與 EIG 主成分一致（絕對值）"] = bool(np.allclose(
    np.abs(svd_components_k), np.abs(components_k), atol=1e-8
))
checks["本質值與 sklearn 一致"] = bool(np.allclose(eigenvalues_k, sk_explained, atol=1e-8))
checks["解釋方差比與 sklearn 一致"] = bool(np.allclose(explained_ratio_k, sk_ratio, atol=1e-8))
checks["主成分與 sklearn 一致"] = bool(np.allclose(comp_k_aligned, sk_aligned, atol=1e-7))
checks["投影結果與 sklearn 一致"] = bool(np.max(np.abs(Z_aligned - Z_sk)) < 1e-7)

X_recon = Z @ components_k + mean
resid_sq = float(np.sum((X - X_recon) ** 2))
checks["重建誤差等於剩餘方差"] = bool(
    np.isclose(resid_sq, (n_samples - 1) * (total_var - explained_variance_k.sum()), rtol=1e-6)
)

print(f"資料集：digits（樣本 {n_samples} x 特徵 {n_features}）")
print(f"前 {K} 個主成分：")
for i in range(K):
    print(
        f"  PC{i + 1}：本質值 {eigenvalues_k[i]:.4f}，解釋方差比 {explained_ratio_k[i]:.4%}"
    )
print(f"累積解釋方差（前 {K} 個）：{np.sum(explained_ratio_k):.4%}")
print(f"手刻主成分與 sklearn 主成分最大差異：{max_comp_diff:.3e}")
print(f"手刻投影與 sklearn 投影最大差異：{max_proj_diff:.3e}")

for name, ok in checks.items():
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")

if not all(checks.values()):
    raise RuntimeError("手刻 PCA 驗證失敗")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].bar(range(1, K + 1), explained_ratio_k, color="steelblue")
axes[0].set_xticks(range(1, K + 1))
axes[0].set_xlabel("Component")
axes[0].set_ylabel("Explained Variance Ratio")
axes[0].set_title(f"Top {K} Components Explained Variance")

Z_plot = Z_aligned[:, :2]
sc = axes[1].scatter(
    Z_plot[:, 0], Z_plot[:, 1], c=y, cmap="tab10", s=12, alpha=0.8
)
axes[1].set_xlabel(f"PC1 (Explained Variance Ratio: {explained_ratio_k[0]:.2%})")
axes[1].set_ylabel(f"PC2 (Explained Variance Ratio: {explained_ratio_k[1]:.2%})")
axes[1].set_title("First 2 Principal Components")

plt.tight_layout()
plt.savefig("figs/pca_digits.png")
plt.close()
print("圖片已存到 figs/pca_digits.png")
