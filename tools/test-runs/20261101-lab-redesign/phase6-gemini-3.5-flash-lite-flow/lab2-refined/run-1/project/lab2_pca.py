import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def run_pca(bug_type="none"):
    digits = load_digits()
    X = digits.data  # shape: (1797, 64)
    n_samples, n_features = X.shape
    n_components = 10

    # 1. 中心化
    if bug_type == "no_center":
        X_centered = X
    else:
        X_mean = np.mean(X, axis=0)
        X_centered = X - X_mean

    # 2. 共變異數矩陣
    if bug_type == "denom_n":
        cov_matrix = np.dot(X_centered.T, X_centered) / n_samples
    else:
        cov_matrix = np.dot(X_centered.T, X_centered) / (n_samples - 1)

    # 3. eigh 計算特徵值與特徵向量
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # 4. 排序
    sorted_idx = np.argsort(eigenvalues)[::-1]
    eigenvalues_sorted = eigenvalues[sorted_idx]
    eigenvectors_sorted = eigenvectors[:, sorted_idx]

    # 5. 取前 10 個主成分
    top_eigenvalues = eigenvalues_sorted[:n_components]

    if bug_type == "rows":
        # 錯誤：直接取 evecs 的前 10 列作為主成分
        manual_components = eigenvectors_sorted[:n_components, :]
        manual_transformed = np.dot(X_centered, manual_components.T)
    else:
        top_eigenvectors = eigenvectors_sorted[:, :n_components]
        manual_components = top_eigenvectors.T
        manual_transformed = np.dot(X_centered, top_eigenvectors)

    # 6. 解釋變異數比率分母
    if bug_type == "ratio_topk":
        total_var = np.sum(top_eigenvalues)
    else:
        total_var = np.sum(eigenvalues_sorted)
    
    # 避免除以零
    if total_var == 0:
        manual_explained_variance_ratio = np.zeros(n_components)
    else:
        manual_explained_variance_ratio = top_eigenvalues / total_var

    return manual_components, manual_transformed, manual_explained_variance_ratio, top_eigenvalues

def main():
    digits = load_digits()
    X = digits.data

    # sklearn PCA 對照組
    n_components = 10
    pca = PCA(n_components=n_components)
    sklearn_transformed = pca.fit_transform(X)
    sklearn_components = pca.components_
    sklearn_explained_variance_ratio = pca.explained_variance_ratio_
    sklearn_eigenvalues = pca.explained_variance_

    bug_types = ["none", "ratio_topk", "denom_n", "no_center", "rows"]
    check_names = [
        "主成分方向 (components_)",
        "降維投影資料 (transform)",
        "解釋變異數比率 (ratio_)",
        "特徵值 (explained_var_)"
    ]
    tolerances = [1e-5, 1e-4, 1e-5, 1e-5]

    results = {}

    for b in bug_types:
        m_comp, m_trans, m_ratio, m_eval = run_pca(b)

        # 正負號對齊 (若非 rows 且維度正確)
        if b != "rows" and m_comp.shape == sklearn_components.shape:
            for i in range(n_components):
                if np.dot(m_comp[i], sklearn_components[i]) < 0:
                    m_comp[i] *= -1
                    m_trans[:, i] *= -1

        # 計算各項誤差
        if m_comp.shape == sklearn_components.shape:
            err_comp = np.max(np.abs(m_comp - sklearn_components))
        else:
            err_comp = float('inf')

        if m_trans.shape == sklearn_transformed.shape:
            err_trans = np.max(np.abs(m_trans - sklearn_transformed))
        else:
            err_trans = float('inf')

        if m_ratio.shape == sklearn_explained_variance_ratio.shape:
            err_ratio = np.max(np.abs(m_ratio - sklearn_explained_variance_ratio))
        else:
            err_ratio = float('inf')

        if m_eval.shape == sklearn_eigenvalues.shape:
            err_eval = np.max(np.abs(m_eval - sklearn_eigenvalues))
        else:
            err_eval = float('inf')

        results[b] = [err_comp, err_trans, err_ratio, err_eval]

    # 印出檢查 × 錯誤 表格
    print("=== 檢查 × 錯誤 評估表 ===")
    header = f"{'檢查項目':<30} | " + " | ".join([f"{b:<12}" for b in bug_types])
    print(header)
    print("-" * len(header))

    for i, c_name in enumerate(check_names):
        tol = tolerances[i]
        row_str = f"{c_name:<30} | "
        cells = []
        for b in bug_types:
            val = results[b][i]
            passed = val < tol
            status = "PASS" if passed else "FAIL"
            cells.append(f"{val:.2e} ({status})")
        row_str += " | ".join([f"{cell:<12}" for cell in cells])
        print(row_str)

if __name__ == "__main__":
    main()
