import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def main():
    # 1. 載入 digits 資料集
    digits = load_digits()
    X = digits.data
    n_samples, n_features = X.shape
    n_components = 10

    # 2. Sklearn PCA (svd_solver='full')
    pca_sk = PCA(n_components=n_components, svd_solver='full')
    X_transformed_sk = pca_sk.fit_transform(X)
    X_reconstructed_sk = pca_sk.inverse_transform(X_transformed_sk)

    # 3. 手刻 PCA (使用 numpy.eigh)
    # 中心化
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean

    # 計算樣本共變異數矩陣 C = (1 / (n_samples - 1)) * X_centered.T @ X_centered
    cov_matrix = np.cov(X_centered, rowvar=False)

    # eigh 計算特徵值與特徵向量 (eigh 回傳的特徵值是由小到大排序)
    eigenvalues_full, eigenvectors_full = np.linalg.eigh(cov_matrix)

    # 排序由大到小，取前 10 個
    sorted_idx = np.argsort(eigenvalues_full)[::-1]
    eigenvalues_manual = eigenvalues_full[sorted_idx][:n_components]
    # eigenvectors_full 各行對應特徵向量，形狀為 (n_features, n_features)
    # 轉置後讓每一列對應一個主成分，形狀為 (n_components, n_features)
    components_manual = eigenvectors_full[:, sorted_idx][:, :n_components].T

    # 投影資料: X_transformed = X_centered @ components_manual.T
    X_transformed_manual = X_centered @ components_manual.T

    # 4. 正負號對齊 (Sign alignment) 處理特徵向量與投影資料的正負號多義性
    # 比較 sklearn components_ 與 manual components_
    aligned_components_manual = np.copy(components_manual)
    aligned_transformed_manual = np.copy(X_transformed_manual)

    for i in range(n_components):
        # 若內積小於 0，將特徵向量與投影值反號
        if np.dot(pca_sk.components_[i], aligned_components_manual[i]) < 0:
            aligned_components_manual[i] *= -1
            aligned_transformed_manual[:, i] *= -1

    # 重建資料: X_reconstructed = X_transformed_manual @ components_manual + X_mean
    X_reconstructed_manual = aligned_transformed_manual @ aligned_components_manual + X_mean

    # --- 檢查 1: 解釋變異數 / 特徵值 (Eigenvalues) ---
    ev_sk = pca_sk.explained_variance_
    max_ev_diff = np.max(np.abs(ev_sk - eigenvalues_manual))
    tol_ev = 1e-5
    pass_ev = max_ev_diff <= tol_ev

    # --- 檢查 2: 主成分方向 / 特徵向量 (Components) ---
    comp_sk = pca_sk.components_
    max_comp_diff = np.max(np.abs(comp_sk - aligned_components_manual))
    tol_comp = 1e-5
    pass_comp = max_comp_diff <= tol_comp

    # --- 檢查 3: 降維投影資料 (Projected Data / Transform) ---
    max_proj_diff = np.max(np.abs(X_transformed_sk - aligned_transformed_manual))
    tol_proj = 1e-5
    pass_proj = max_proj_diff <= tol_proj

    # --- 檢查 4: 資料重建誤差 (Reconstruction / Inverse Transform) ---
    mse_sk = np.mean((X - X_reconstructed_sk) ** 2)
    mse_manual = np.mean((X - X_reconstructed_manual) ** 2)
    mse_diff = np.abs(mse_sk - mse_manual)
    tol_recon = 1e-10
    pass_recon = mse_diff <= tol_recon

    # --- 印出結果 ---
    print("=" * 60)
    print("PCA 手刻實作與 Sklearn (svd_solver='full') 比對結果")
    print("=" * 60)

    print(f"1. 解釋變異數 / 特徵值 (Eigenvalues):")
    print(f"   - 最大絕對誤差: {max_ev_diff:.2e} (容差: {tol_ev})")
    print(f"   - 狀態: {'PASS' if pass_ev else 'FAIL'}")

    print(f"\n2. 主成分方向 / 特徵向量 (Components):")
    print(f"   - 最大絕對誤差: {max_comp_diff:.2e} (容差: {tol_comp})")
    print(f"   - 狀態: {'PASS' if pass_comp else 'FAIL'}")

    print(f"\n3. 降維投影資料 (Projected Data / Transform):")
    print(f"   - 最大絕對誤差: {max_proj_diff:.2e} (容差: {tol_proj})")
    print(f"   - 狀態: {'PASS' if pass_proj else 'FAIL'}")

    print(f"\n4. 資料重建誤差 (Reconstruction / Inverse Transform):")
    print(f"   - Sklearn MSE: {mse_sk:.6e}")
    print(f"   - 手刻 MSE:   {mse_manual:.6e}")
    print(f"   - MSE 差值:    {mse_diff:.2e} (容差: {tol_recon})")
    print(f"   - 狀態: {'PASS' if pass_recon else 'FAIL'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
