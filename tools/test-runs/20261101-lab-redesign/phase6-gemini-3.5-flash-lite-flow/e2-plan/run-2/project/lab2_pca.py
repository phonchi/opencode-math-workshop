import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def main():
    # 載入 digits 資料集
    X, _ = load_digits(return_X_y=True)
    n_samples, n_features = X.shape
    n_components = 10

    # ==========================================
    # 1. 資料預處理與中心化檢查
    # ==========================================
    # 手刻中心化
    mu_my = np.mean(X, axis=0)
    X_centered_my = X - mu_my

    # scikit-learn 中心化 (PCA 內部會自動減去 mean_)
    pca_sk = PCA(n_components=n_components, svd_solver='full')
    pca_sk.fit(X)
    mu_sk = pca_sk.mean_

    mean_diff = np.max(np.abs(mu_my - mu_sk))
    data_centered_diff = np.max(np.abs(X_centered_my - (X - mu_sk)))
    
    pass_1 = (mean_diff < 1e-12) and (data_centered_diff < 1e-12)
    print("【檢查 1：資料預處理與中心化檢查】")
    print(f"  平均值最大絕對差值: {mean_diff:.2e} (容差: 1e-12)")
    print(f"  中心化資料最大絕對差值: {data_centered_diff:.2e} (容差: 1e-12)")
    print(f"  結果: {'PASS' if pass_1 else 'FAIL'}\n")

    # ==========================================
    # 2. 特徵值 / 解釋變異數檢查
    # ==========================================
    # 手刻 PCA: 共變異數矩陣 (Unbiased sample covariance: ddof=1)
    cov_matrix = np.cov(X_centered_my, rowvar=False, ddof=1)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # eigh 預設由小到大排序，需反轉成由大到小
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # 取前 10 個
    evals_my = eigenvalues[:n_components]
    
    # scikit-learn 解釋變異數 (explained_variance_)
    evals_sk = pca_sk.explained_variance_

    evals_diff = np.max(np.abs(evals_my - evals_sk))
    evals_rtol = np.max(np.abs((evals_my - evals_sk) / (evals_sk + 1e-15)))

    pass_2 = (evals_diff < 1e-5) and (evals_rtol < 1e-5)
    print("【檢查 2：特徵值 / 解釋變異數檢查】")
    print(f"  手刻前 10 個特徵值: {evals_my[:3]} ...")
    print(f"  SKLearn 前 10 個特徵值: {evals_sk[:3]} ...")
    print(f"  最大絕對差值: {evals_diff:.2e} (容差: 1e-5)")
    print(f"  最大相對差值: {evals_rtol:.2e} (容差: 1e-5)")
    print(f"  結果: {'PASS' if pass_2 else 'FAIL'}\n")

    # ==========================================
    # 3. 主成分 / 投影矩陣檢查
    # ==========================================
    # 手刻主成分 (n_components, n_features)
    components_my = eigenvectors[:, :n_components].T
    components_sk = pca_sk.components_

    # 處理正負號對齊 (Sign alignment: 確保每行首個非零元素或內積符號一致)
    for i in range(n_components):
        if np.dot(components_my[i], components_sk[i]) < 0:
            components_my[i] *= -1

    comp_diff = np.max(np.abs(components_my - components_sk))
    pass_3 = comp_diff < 1e-5
    print("【檢查 3：主成分 / 投影矩陣檢查】")
    print(f"  主成分最大絕對差值 (正負號對齊後): {comp_diff:.2e} (容差: 1e-5)")
    print(f"  結果: {'PASS' if pass_3 else 'FAIL'}\n")

    # ==========================================
    # 4. 降維投影結果檢查
    # ==========================================
    X_transformed_my = np.dot(X_centered_my, components_my.T)
    X_transformed_sk = pca_sk.transform(X)

    trans_diff = np.max(np.abs(X_transformed_my - X_transformed_sk))
    pass_4 = trans_diff < 1e-4
    print("【檢查 4：降維投影結果檢查】")
    print(f"  投影結果最大絕對差值: {trans_diff:.2e} (容差: 1e-4)")
    print(f"  結果: {'PASS' if pass_4 else 'FAIL'}\n")

    # ==========================================
    # 5. 資料重建與重建誤差檢查
    # ==========================================
    X_reconstructed_my = np.dot(X_transformed_my, components_my) + mu_my
    X_reconstructed_sk = pca_sk.inverse_transform(X_transformed_sk)

    recon_diff = np.max(np.abs(X_reconstructed_my - X_reconstructed_sk))
    recon_mse = np.mean((X_reconstructed_my - X_reconstructed_sk) ** 2)

    pass_5 = (recon_diff < 1e-4) and (recon_mse < 1e-8)
    print("【檢查 5：資料重建與重建誤差檢查】")
    print(f"  重建資料最大絕對差值: {recon_diff:.2e} (容差: 1e-4)")
    print(f"  重建資料 MSE: {recon_mse:.2e} (容差: 1e-8)")
    print(f"  結果: {'PASS' if pass_5 else 'FAIL'}\n")

if __name__ == '__main__':
    main()
