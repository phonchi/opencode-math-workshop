import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def main():
    # Load digits dataset
    digits = load_digits()
    X = digits.data

    n_samples, n_features = X.shape
    n_components = 10

    # --- Hand-coded PCA using numpy.eigh ---
    # 1. Mean centering
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean

    # 2. Covariance matrix (unbiased sample covariance, dividing by n_samples - 1)
    cov_matrix = np.dot(X_centered.T, X_centered) / (n_samples - 1)

    # 3. Eigendecomposition using eigh (since cov_matrix is symmetric)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # 4. Sort eigenvalues and eigenvectors in descending order
    sorted_indices = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sorted_indices]
    eigenvectors = eigenvectors[:, sorted_indices]

    # Take top n_components
    custom_eigenvalues = eigenvalues[:n_components]
    # eigenvectors columns are principal axes, shape (n_features, n_components)
    # sklearn components_ has shape (n_components, n_features), so transpose custom eigenvectors
    custom_components = eigenvectors[:, :n_components].T

    # Total variance for explained variance ratio
    total_variance = np.sum(eigenvalues)
    custom_explained_variance_ratio = custom_eigenvalues / total_variance

    # Transformed data (scores)
    custom_transformed = np.dot(X_centered, eigenvectors[:, :n_components])

    # --- sklearn PCA reference ---
    pca_ref = PCA(n_components=n_components, svd_solver='full')
    sklearn_transformed = pca_ref.fit_transform(X)
    sklearn_eigenvalues = pca_ref.explained_variance_
    sklearn_components = pca_ref.components_
    sklearn_explained_variance_ratio = pca_ref.explained_variance_ratio_

    # --- Checks & Tolerances ---
    results = []

    # Check 1: Eigenvalues / Explained Variance
    # Tolerance: atol=1e-5, rtol=1e-5
    eval_diff = np.abs(custom_eigenvalues - sklearn_eigenvalues)
    eval_pass = np.allclose(custom_eigenvalues, sklearn_eigenvalues, atol=1e-5, rtol=1e-5)
    results.append(("1. 特徵值 (Eigenvalues)", eval_pass, f"Max diff: {np.max(eval_diff):.2e}"))

    # Check 2: Principal Axes / Components
    # Sign ambiguity correction: align signs so dot product >= 0
    aligned_custom_components = np.copy(custom_components)
    for i in range(n_components):
        if np.dot(aligned_custom_components[i], sklearn_components[i]) < 0:
            aligned_custom_components[i] *= -1
    comp_diff = np.abs(aligned_custom_components - sklearn_components)
    # Tolerance: cosine similarity or elementwise atol/rtol
    cos_sim = np.array([np.dot(aligned_custom_components[i], sklearn_components[i]) / 
                        (np.linalg.norm(aligned_custom_components[i]) * np.linalg.norm(sklearn_components[i]))
                        for i in range(n_components)])
    comp_pass = np.all(cos_sim > 1 - 1e-6) and np.allclose(aligned_custom_components, sklearn_components, atol=1e-5, rtol=1e-5)
    results.append(("2. 特徵向量 (Principal Components)", comp_pass, f"Min cosine sim: {np.min(cos_sim):.7f}, Max diff: {np.max(comp_diff):.2e}"))

    # Check 3: Transformed Data / Scores
    # Align transformed data sign if component sign was flipped
    aligned_custom_transformed = np.copy(custom_transformed)
    for i in range(n_components):
        if np.dot(aligned_custom_components[i], sklearn_components[i]) < 0: # note: we already aligned components, but let's be safe
            pass
    # If custom_components were flipped, custom_transformed needs to be flipped accordingly
    # Wait, custom_transformed = X_centered @ eigenvectors[:, :n_components], and custom_components = eigenvectors[:, :n_components].T
    # So custom_transformed[:, i] corresponds to X_centered @ eigenvectors[:, i]. 
    # If we flipped aligned_custom_components[i], we should flip aligned_custom_transformed[:, i] as well if needed, 
    # or check against sklearn_transformed where sign matches sklearn_components.
    # Actually, sklearn_transformed[:, i] = X_centered @ sklearn_components[i].T.
    # Let's check alignment of transformed data directly:
    aligned_custom_transformed_checked = np.copy(custom_transformed)
    for i in range(n_components):
        if np.mean(aligned_custom_transformed_checked[:, i] * sklearn_transformed[:, i]) < 0:
            aligned_custom_transformed_checked[:, i] *= -1

    trans_diff = np.abs(aligned_custom_transformed_checked - sklearn_transformed)
    trans_pass = np.allclose(aligned_custom_transformed_checked, sklearn_transformed, atol=1e-4, rtol=1e-4)
    results.append(("3. 投影資料 (Transformed Data)", trans_pass, f"Max diff: {np.max(trans_diff):.2e}"))

    # Check 4: Explained Variance Ratio
    # Tolerance: atol=1e-5, rtol=1e-5
    evr_diff = np.abs(custom_explained_variance_ratio - sklearn_explained_variance_ratio)
    evr_pass = np.allclose(custom_explained_variance_ratio, sklearn_explained_variance_ratio, atol=1e-5, rtol=1e-5)
    results.append(("4. 解釋變異數比例 (Explained Variance Ratio)", evr_pass, f"Max diff: {np.max(evr_diff):.2e}"))

    # Print results
    print("=== PCA 實作與對照結果 ===")
    for name, passed, details in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name} -> {details}")

if __name__ == "__main__":
    main()
