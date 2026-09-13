import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

N_COMPONENTS = 10

digits = load_digits()
X = digits.data
n_samples, n_features = X.shape


def my_pca_topk(X, k):
    """手刻 PCA：只許用 numpy。中心化 -> 共變異數矩陣 -> eigh -> 排序 -> 取前 k。"""
    X_centered = X - X.mean(axis=0)
    cov = (X_centered.T @ X_centered) / (n_samples - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)

    order = np.argsort(eigvals)[::-1]
    top = order[:k]
    components = eigvecs[:, top].T
    explained_variance = eigvals[top]

    # 對齊 sklearn 的 sign convention（svd_flip, u_based_decision=False）：
    # 每個主成分在"絕對值最大"那一格必須為正。
    max_idx = np.argmax(np.abs(components), axis=1)
    signs = np.sign(components[np.arange(k), max_idx])
    components = components * signs[:, None]

    return components, explained_variance


components_hand, var_hand = my_pca_topk(X, N_COMPONENTS)

ref = PCA(n_components=N_COMPONENTS, svd_solver="full", random_state=0)
ref.fit(X)

components_sk, var_sk = ref.components_, ref.explained_variance_

print(f"資料形狀: X{n_features} 維 x {n_samples} 個樣本\n")

# 1. 特徵值本身（explained_variance_）
print("=== 1. 特徵值 (explained_variance_) 比對 ===")
for i in range(N_COMPONENTS):
    print(f"  PC{i+1:2d}  手刻={var_hand[i]:12.6f}   sklearn={var_sk[i]:12.6f}")
max_diff_var = np.max(np.abs(var_hand - var_sk))
print(f"  最大絕對差 = {max_diff_var:.6e}  ->  {max_diff_var < 1e-10}")

# 2. 解釋變異比例
print("\n=== 2. 解釋變異比例 (explained_variance_ratio_) 比對 ===")
ratio_hand = var_hand / var_hand.sum()
ratio_sk = var_sk / var_sk.sum()
for i in range(N_COMPONENTS):
    print(f"  PC{i+1:2d}  手刻={ratio_hand[i]:.8f}   sklearn={ratio_sk[i]:.8f}")
print(f"  累計比例(前10) = {ratio_hand.sum():.6f}")
max_diff_ratio = np.max(np.abs(ratio_hand - ratio_sk))
print(f"  最大絕對差 = {max_diff_ratio:.6e}  ->  {max_diff_ratio < 1e-10}")

# 3. 方向與正負號
print("\n=== 3. 方向與正負號 比對 ===")
align = np.sum(np.sign(components_hand) * np.sign(components_sk), axis=1)
dot = np.abs(np.sum(components_hand * components_sk, axis=1))
idx = np.argmax(np.abs(components_sk), axis=1)
for i in range(N_COMPONENTS):
    ag = "同向" if align[i] > 0 else "反向"
    print(f"  PC{i+1:2d}  |內積|={dot[i]:.8f}  正負號對齊={ag}  max|位置|符號(手刻/sklearn)={np.sign(components_hand[i,idx[i]]):+.0f}/{np.sign(components_sk[i,idx[i]]):+.0f}")
max_dot_err = np.max(1 - dot)
print(f"  最大(1-|內積|) = {max_dot_err:.6e}  ->  {max_dot_err < 1e-8}")

# 4. 正交性：手刻的主成分彼此正交
print("\n=== 4. 手刻主成分正交性 ===")
gram = components_hand @ components_hand.T
print(f"  Gram matrix 第 1 列 = {np.round(gram[0], 4)}")
off = np.abs(gram - np.eye(N_COMPONENTS))
print(f"  最大非對角元素(|C C^T - I|) = {np.max(off):.6e}  ->  {np.max(off) < 1e-10}")

# 5. 重建誤差
print("\n=== 5. 重建誤差 比對 ===")
Xc = X - X.mean(axis=0)
recon_hand = Xc @ components_hand.T @ components_hand + X.mean(axis=0)
recon_sk = ref.inverse_transform(ref.transform(X))
err_hand = np.linalg.norm(X - recon_hand)
err_sk = np.linalg.norm(X - recon_sk)
diff_er = np.linalg.norm(recon_hand - recon_sk)
print(f"  手刻重建誤差 ||X - X_hat||  = {err_hand:.8f}")
print(f"  sklearn 重建誤差 ||X - X_hat|| = {err_sk:.8f}")
print(f"  兩者重建結果差 ||Xhat_hand - Xhat_sk|| = {diff_er:.6e}  ->  {diff_er < 1e-8}")