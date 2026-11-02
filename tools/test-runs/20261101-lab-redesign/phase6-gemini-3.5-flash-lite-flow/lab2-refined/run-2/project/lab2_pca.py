import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

def run_pca(X, bug="none", n_components=10):
    n_samples, n_features = X.shape
    
    # 1. 中心化 (Bug: no_center)
    if bug == "no_center":
        X_c = X.copy()
    else:
        X_mean = np.mean(X, axis=0)
        X_c = X - X_mean

    # 2. 共變異數矩陣分母 (Bug: denom_n)
    if bug == "denom_n":
        cov_denom = n_samples
    else:
        cov_denom = n_samples - 1

    cov_matrix = (X_c.T @ X_c) / cov_denom

    # 3. 特徵分解
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # 4. 排序 (由大到小)
    sorted_idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sorted_idx]
    eigenvectors = eigenvectors[:, sorted_idx]

    # 5. 取前 10 個主成分
    hand_eigenvalues = eigenvalues[:n_components]

    # Bug: rows (用 evecs[:K] 取列，而不是取欄)
    if bug == "rows":
        hand_components = eigenvectors[:n_components, :]  # shape: (10, n_features), but wrong rows
        hand_transformed = X_c @ hand_components.T
    else:
        hand_components = eigenvectors[:, :n_components].T  # shape: (10, n_features)
        hand_transformed = X_c @ eigenvectors[:, :n_components]  # shape: (n_samples, 10)

    # 6. 解釋變異比例分母 (Bug: ratio_topk)
    if bug == "ratio_topk":
        total_variance = np.sum(hand_eigenvalues)
    else:
        total_variance = np.sum(eigenvalues)

    hand_evr = hand_eigenvalues / total_variance

    return hand_eigenvalues, hand_evr, hand_components, hand_transformed

def main():
    print("=== PCA 驗證與錯誤模式 (Checks × Bugs) 分析表 ===")
    
    digits = load_digits()
    X = digits.data
    n_components = 10

    # Sklearn PCA 對照組
    sk_pca = SklearnPCA(n_components=n_components)
    sk_transformed = sk_pca.fit_transform(X)
    sk_eigenvalues = sk_pca.explained_variance_
    sk_evr = sk_pca.explained_variance_ratio_
    sk_components = sk_pca.components_

    checks_def = [
        ("特徵值 (Eigenvalues)", lambda h_e, h_evr, h_comp, h_trans: (h_e, sk_eigenvalues, 1e-5, 1e-5)),
        ("解釋變異比例 (EVR)", lambda h_e, h_evr, h_comp, h_trans: (h_evr, sk_evr, 1e-5, 1e-5)),
        ("主成分向量 (Components)", lambda h_e, h_evr, h_comp, h_trans: (align_components(h_comp, sk_components)[0], sk_components, 1e-5, 1e-5)),
        ("投影資料 (Transformed)", lambda h_e, h_evr, h_comp, h_trans: (align_components(h_comp, sk_components)[1], sk_transformed, 1e-4, 1e-4)),
    ]

    bugs = ["none", "ratio_topk", "denom_n", "no_center", "rows"]

    # 儲存結果矩陣: results[check_idx][bug_idx] = (status_str, max_diff)
    table_data = {}

    for check_name, get_vals in checks_def:
        table_data[check_name] = {}
        for bug in bugs:
            h_e, h_evr, h_comp, h_trans = run_pca(X, bug=bug, n_components=n_components)
            # 針對 rows bug，當轉型或資料維度報錯時進行保護
            try:
                hand_val, ref_val, atol, rtol = get_vals(h_e, h_evr, h_comp, h_trans)
                max_diff = np.max(np.abs(hand_val - ref_val))
                passed = np.allclose(hand_val, ref_val, atol=atol, rtol=rtol)
                status = "PASS" if passed else "FAIL"
            except Exception as e:
                max_diff = float('nan')
                status = "FAIL"

            table_data[check_name][bug] = (status, max_diff)

    # 印出表格
    print("\n" + "="*110)
    header = f"{'檢查項目':<26} | " + " | ".join([f"{b:<14}" for b in bugs])
    print(header)
    print("-" * len(header))

    for check_name, _ in checks_def:
        row_str = f"{check_name:<26} | "
        cells = []
        for bug in bugs:
            status, max_diff = table_data[check_name][bug]
            if np.isnan(max_diff):
                cell = f"{status} (err)"
            else:
                cell = f"{status} ({max_diff:.1e})"
            cells.append(f"{cell:<14}")
        row_str += " | ".join(cells)
        print(row_str)
    print("="*110)

def align_components(hand_comp, sk_comp):
    # 符號對齊輔助函數
    hc = hand_comp.copy()
    # 假設 shape 是 (10, n_features)
    # 由於 rows bug 可能導致 shape 不符，先做檢查
    if hc.shape != sk_comp.shape:
        # 如果 shape 不一樣，構造一個全錯的 dummy 以免 crash
        return hc, np.zeros((1797, 10))
    
    digits = load_digits().data
    X_mean = np.mean(digits, axis=0)
    X_c = digits - X_mean
    
    ht = X_c @ hc.T
    for i in range(hc.shape[0]):
        if np.dot(hc[i], sk_comp[i]) < 0:
            hc[i] *= -1
            ht[:, i] *= -1
    return hc, ht

if __name__ == "__main__":
    main()
