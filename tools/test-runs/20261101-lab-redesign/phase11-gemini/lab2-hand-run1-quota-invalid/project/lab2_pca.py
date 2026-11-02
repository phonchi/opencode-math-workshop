import numpy as np
from sklearn.decomposition import PCA

def main():
    # 1. 載入資料
    data_path = "data/line_channels.csv"
    data = np.loadtxt(data_path, delimiter=",", skiprows=1)
    n_samples, n_features = data.shape
    print(f"資料形狀 (Samples, Features): {data.shape}")

    # 2. 每欄先除以標準差但不減平均 (ddof=0)
    std = np.std(data, axis=0, ddof=0)
    X_scaled = data / std

    # 3. 手刻 PCA (使用 numpy.linalg.eigh)
    # 中心化留給 PCA 本身
    mean = np.mean(X_scaled, axis=0)
    X_centered = X_scaled - mean

    # 計算共變異數矩陣 (樣本共變異數 ddof=1)
    cov = np.dot(X_centered.T, X_centered) / (n_samples - 1)

    # 只能用 numpy 的 eigh 進行特徵值分解
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # 降序排序特徵值與特徵向量
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # 取前 4 個主成分
    k = 4
    evals_top4 = eigenvalues[:k]
    evecs_top4 = eigenvectors[:, :k] # shape (n_features, k)
    my_components = evecs_top4.T     # shape (k, n_features)

    # 手刻投影資料 (分數)
    my_transformed = X_centered @ evecs_top4

    # 4. Scikit-learn PCA (svd_solver='full') 作為對照組
    pca_sk = PCA(n_components=k, svd_solver='full')
    X_trans_sk = pca_sk.fit_transform(X_scaled)

    # 處理特徵向量/投影符號對齊 (由於正交子空間符號不唯一)
    for i in range(k):
        if np.corrcoef(my_transformed[:, i], X_trans_sk[:, i])[0, 1] < 0:
            my_transformed[:, i] *= -1
            my_components[i] *= -1

    # 5. 驗證與比對 (列出實際數值與 PASS/FAIL)
    print("=" * 60)
    print("PCA 手刻實作與對照組 (scikit-learn svd_solver='full') 驗證結果:")
    print("=" * 60)

    # 檢查 1: 特徵值 (解釋變異數 Explained Variance)
    sk_ev = pca_sk.explained_variance_
    match_ev = np.allclose(evals_top4, sk_ev, atol=1e-5)
    print(f"[檢查 1] 特徵值 (Explained Variance):")
    print(f"  手刻數值: {evals_top4}")
    print(f"  對照組  : {sk_ev}")
    print(f"  狀態    : {'PASS' if match_ev else 'FAIL'}\n")

    # 檢查 2: 解釋變異數比例 (Explained Variance Ratio)
    total_var = np.sum(eigenvalues)
    evals_ratio = evals_top4 / total_var
    sk_ratio = pca_sk.explained_variance_ratio_
    match_ratio = np.allclose(evals_ratio, sk_ratio, atol=1e-5)
    print(f"[檢查 2] 解釋變異數比例 (Explained Variance Ratio):")
    print(f"  手刻數值: {evals_ratio}")
    print(f"  對照組  : {sk_ratio}")
    print(f"  狀態    : {'PASS' if match_ratio else 'FAIL'}\n")

    # 檢查 3: 單值 (Singular Values)
    my_sv = np.sqrt(eigenvalues * (n_samples - 1))[:k]
    sk_sv = pca_sk.singular_values_
    match_sv = np.allclose(my_sv, sk_sv, atol=1e-5)
    print(f"[檢查 3] 單值 (Singular Values):")
    print(f"  手刻數值: {my_sv}")
    print(f"  對照組  : {sk_sv}")
    print(f"  狀態    : {'PASS' if match_sv else 'FAIL'}\n")

    # 檢查 4: 主成分載荷向量 (Components)
    match_comp = np.allclose(my_components, pca_sk.components_, atol=1e-5)
    print(f"[檢查 4] 主成分載荷向量 (Components):")
    print(f"  手刻前 2 維 (部分展示):\n{my_components[:, :2]}")
    print(f"  對照組前 2 維 (部分展示):\n{pca_sk.components_[:, :2]}")
    print(f"  狀態    : {'PASS' if match_comp else 'FAIL'}\n")

    # 檢查 5: 降維投影資料 (Transformed Data / Scores)
    match_trans = np.allclose(my_transformed, X_trans_sk, atol=1e-4)
    print(f"[檢查 5] 降維投影資料 (Transformed Data):")
    print(f"  手刻前 5 筆前 2 維:\n{my_transformed[:5, :2]}")
    print(f"  對照組前 5 筆前 2 維:\n{X_trans_sk[:5, :2]}")
    print(f"  狀態    : {'PASS' if match_trans else 'FAIL'}\n")

    all_passed = match_ev and match_ratio and match_sv and match_comp and match_trans
    print("=" * 60)
    print(f"總結: {'所有檢查均 PASS' if all_passed else '部分檢查 FAIL'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
