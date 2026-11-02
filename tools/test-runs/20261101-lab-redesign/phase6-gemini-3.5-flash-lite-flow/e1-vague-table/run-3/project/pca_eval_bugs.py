import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def run_pca_with_bug(bug_type="none"):
    digits = load_digits()
    X = digits.data
    n_samples, n_features = X.shape
    n_components = 10

    # 1. 中心化與 bug 處理
    if bug_type == "no_center":
        X_centered = X.copy()
    else:
        X_mean = np.mean(X, axis=0)
        X_centered = X - X_mean

    # 2. SVD 分解
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

    # 3. 取主成分 (Components)
    if bug_type == "rows":
        # Bug: 取矩陣的前 10 列，不是前 10 個特徵向量
        manual_components = X_centered[:n_components].copy()
    else:
        manual_components = Vt[:n_components].copy()

    # 4. 投影資料 (Transformed)
    manual_transformed = X_centered @ manual_components.T

    # 5. 解釋變異量比例 (Variance Ratio)
    if bug_type == "denom_n":
        eigenvalues = (S ** 2) / n_samples
    else:
        eigenvalues = (S ** 2) / (n_samples - 1)

    manual_explained_variance = eigenvalues[:n_components]

    if bug_type == "ratio_topk":
        # Bug: 比例分母只用前 10 個特徵值的和
        manual_total_var = np.sum(eigenvalues[:n_components])
    else:
        manual_total_var = np.sum(eigenvalues)

    manual_explained_variance_ratio = manual_explained_variance / manual_total_var

    # 6. sklearn PCA 基準
    pca = PCA(n_components=n_components)
    sklearn_transformed = pca.fit_transform(X)
    sklearn_components = pca.components_
    sklearn_explained_variance_ratio = pca.explained_variance_ratio_

    # 7. 處理正負號模糊性 (僅當 components 正常時有意義，若 bug="rows" 則直接比對)
    if bug_type != "rows":
        for i in range(n_components):
            if np.dot(manual_components[i], sklearn_components[i]) < 0:
                manual_components[i] *= -1
                manual_transformed[:, i] *= -1

    # 8. 原始檢查與門檻 (Threshold = 1e-10)
    threshold = 1e-10

    comp_diff = np.max(np.abs(manual_components - sklearn_components))
    trans_diff = np.max(np.abs(manual_transformed - sklearn_transformed))
    ratio_diff = np.max(np.abs(manual_explained_variance_ratio - sklearn_explained_variance_ratio))

    return {
        "comp_diff": comp_diff,
        "comp_pass": comp_diff < threshold,
        "trans_diff": trans_diff,
        "trans_pass": trans_diff < threshold,
        "ratio_diff": ratio_diff,
        "ratio_pass": ratio_diff < threshold,
    }

def main():
    bugs = ["none", "ratio_topk", "denom_n", "no_center", "rows"]
    results = {}

    for b in bugs:
        results[b] = run_pca_with_bug(b)

    # 建立「檢查 × 錯誤」表
    print("| 檢查項目 / 錯誤類型 | " + " | ".join(bugs) + " |")
    print("|:---|---" + "|---" * len(bugs) + "|")

    checks = [
        ("主成分 (Components)", "comp_diff", "comp_pass"),
        ("投影資料 (Transformed)", "trans_diff", "trans_pass"),
        ("解釋變異量比例 (Ratio)", "ratio_diff", "ratio_pass"),
    ]

    for check_name, diff_key, pass_key in checks:
        row_str = f"| {check_name} |"
        for b in bugs:
            val = results[b][diff_key]
            status = "PASS" if results[b][pass_key] else "FAIL"
            row_str += f" {val:.2e} ({status}) |"
        print(row_str)

if __name__ == "__main__":
    main()
