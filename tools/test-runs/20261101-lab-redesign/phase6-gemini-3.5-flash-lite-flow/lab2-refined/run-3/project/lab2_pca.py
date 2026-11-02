import argparse
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

def run_pca(bug_type='none'):
    digits = load_digits()
    X = digits.data  # shape: (1797, 64)
    n_samples, n_features = X.shape
    n_components = 10

    # 1. 中心化
    if bug_type == 'no_center':
        X_centered = X
    else:
        mean = np.mean(X, axis=0)
        X_centered = X - mean

    # 2. 共變異數矩陣分母
    if bug_type == 'denom_n':
        cov_matrix = np.dot(X_centered.T, X_centered) / n_samples
    else:
        cov_matrix = np.dot(X_centered.T, X_centered) / (n_samples - 1)

    # 3. eigh 與排序
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # 4. 取前 10 個
    if bug_type == 'rows':
        # 錯誤：用 evecs[:K] 取列，不是取欄
        top_eigenvalues = eigenvalues[:n_components]
        top_eigenvectors = eigenvectors[:n_components, :]  # shape: (10, 64)
        W_custom = top_eigenvectors
        X_proj_custom = np.dot(X_centered, top_eigenvectors.T)
    else:
        top_eigenvalues = eigenvalues[:n_components]
        top_eigenvectors = eigenvectors[:, :n_components]  # shape: (64, 10)
        W_custom = top_eigenvectors.T
        X_proj_custom = np.dot(X_centered, top_eigenvectors)

    # 5. sklearn PCA 對照組
    sk_pca = SklearnPCA(n_components=n_components)
    X_proj_sk = sk_pca.fit_transform(X)
    W_sk = sk_pca.components_
    eval_sk = sk_pca.explained_variance_
    cum_var_sk = np.sum(sk_pca.explained_variance_ratio_)

    # 6. 解釋變異比例
    total_var = np.sum(np.var(X, axis=0, ddof=1))
    if bug_type == 'ratio_topk':
        # 錯誤：比例分母只用前 10 個特徵值的和
        cum_var_custom = np.sum(top_eigenvalues) / np.sum(top_eigenvalues)
    else:
        cum_var_custom = np.sum(top_eigenvalues) / total_var

    # 7. 對齊正負號 (針對 rows 或其他可能維度不匹配的情況做防護)
    try:
        if W_custom.shape == W_sk.shape:
            signs = np.sign(np.sum(W_custom * W_sk, axis=1, keepdims=True))
            W_custom_aligned = W_custom * signs
            X_proj_custom_aligned = X_proj_custom * signs.T
        else:
            W_custom_aligned = W_custom
            X_proj_custom_aligned = X_proj_custom
    except Exception:
        W_custom_aligned = W_custom
        X_proj_custom_aligned = X_proj_custom

    # 8. 檢查項目與門檻
    checks = []

    # 檢查一：特徵值
    try:
        diff_eval = np.max(np.abs(top_eigenvalues - eval_sk))
    except Exception:
        diff_eval = np.inf
    pass_eval = diff_eval < 1e-4
    checks.append(("特徵值", diff_eval, 1e-4, pass_eval))

    # 檢查二：主成分載荷向量 (W)
    try:
        diff_w = np.max(np.abs(W_custom_aligned - W_sk))
    except Exception:
        diff_w = np.inf
    pass_w = diff_w < 1e-4
    checks.append(("載荷向量", diff_w, 1e-4, pass_w))

    # 檢查三：降維投影資料 (X_proj)
    try:
        diff_proj = np.max(np.abs(X_proj_custom_aligned - X_proj_sk))
    except Exception:
        diff_proj = np.inf
    pass_proj = diff_proj < 1e-3
    checks.append(("投影資料", diff_proj, 1e-3, pass_proj))

    # 檢查四：累積解釋變異比例
    try:
        diff_var = np.abs(cum_var_custom - cum_var_sk)
    except Exception:
        diff_var = np.inf
    pass_var = diff_var < 1e-5
    checks.append(("累積變異比", diff_var, 1e-5, pass_var))

    return checks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bug', type=str, default='all', choices=['none', 'ratio_topk', 'denom_n', 'no_center', 'rows', 'all'])
    args = parser.parse_args()

    bugs = ['none', 'ratio_topk', 'denom_n', 'no_center', 'rows']
    if args.bug != 'all':
        bugs = [args.bug]

    check_names = ["特徵值", "載荷向量", "投影資料", "累積變異比"]
    
    # 儲存結果表: results[bug][check_idx] = (val, passed)
    results = {}
    for b in bugs:
        checks = run_pca(b)
        results[b] = checks

    print("=" * 95)
    print("【檢查 × 錯誤】對照表 (實際數值與 PASS/FAIL)")
    print("=" * 95)
    header = f"{'檢查項目':<14} | " + " | ".join([f"{b:<12}" for b in bugs])
    print(header)
    print("-" * 95)

    for i, c_name in enumerate(check_names):
        row_str = f"{c_name:<14} | "
        vals = []
        for b in bugs:
            name, val, tol, passed = results[b][i]
            status = "PASS" if passed else "FAIL"
            if np.isinf(val):
                val_str = f"inf ({status})"
            else:
                val_str = f"{val:.1e} ({status})"
            vals.append(f"{val_str:<12}")
        row_str += " | ".join(vals)
        print(row_str)
    print("=" * 95)

if __name__ == "__main__":
    main()
