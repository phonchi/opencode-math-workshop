import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def main():
    # 1. 載入 digits 資料集
    digits = load_digits()
    X = digits.data
    y = digits.target
    n_samples, n_features = X.shape
    print(f"資料集形狀 (X): {X.shape}")

    # 2. 手刻 PCA 步驟
    # 步驟 2.1: 資料中心化 (Center the data)
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean

    # 步驟 2.2: 使用 SVD (Singular Value Decomposition) 分解中心化矩陣
    # X_centered = U * S * Vt
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

    # 步驟 2.3: 選取前 10 個主成分 (Principal Components)
    n_components = 10
    manual_components = Vt[:n_components]

    # 步驟 2.4: 計算投影後的資料 (Scores / Transformed data)
    manual_transformed = X_centered @ manual_components.T

    # 步驟 2.5: 計算解釋變異量比例 (Explained Variance Ratio)
    # 樣本共變異數矩陣的特徵值可透過奇異值 S 計算：lambda = S^2 / (n_samples - 1)
    eigenvalues = (S ** 2) / (n_samples - 1)
    manual_explained_variance = eigenvalues[:n_components]
    manual_total_var = np.sum(eigenvalues)
    manual_explained_variance_ratio = manual_explained_variance / manual_total_var

    # 3. 使用 sklearn.decomposition.PCA 進行驗證
    pca = PCA(n_components=n_components)
    sklearn_transformed = pca.fit_transform(X)
    sklearn_components = pca.components_
    sklearn_explained_variance_ratio = pca.explained_variance_ratio_

    # 4. 處理正負號模糊性 (Sign Ambiguity)
    # 特徵向量乘以 -1 仍為特徵向量，需調整正負號以便進行數值比對
    for i in range(n_components):
        if np.dot(manual_components[i], sklearn_components[i]) < 0:
            manual_components[i] *= -1
            manual_transformed[:, i] *= -1

    # 5. 數值驗證與誤差計算
    comp_diff = np.max(np.abs(manual_components - sklearn_components))
    trans_diff = np.max(np.abs(manual_transformed - sklearn_transformed))
    ratio_diff = np.max(np.abs(manual_explained_variance_ratio - sklearn_explained_variance_ratio))

    print("--- 驗證結果 ---")
    print(f"主成分 (Components) 最大誤差: {comp_diff:.2e}")
    print(f"投影資料 (Transformed) 最大誤差: {trans_diff:.2e}")
    print(f"解釋變異量比例 (Variance Ratio) 最大誤差: {ratio_diff:.2e}")

    assert comp_diff < 1e-10, "主成分比對失敗！"
    assert trans_diff < 1e-10, "投影資料比對失敗！"
    assert ratio_diff < 1e-10, "解釋變異量比例比對失敗！"
    print("驗證成功！手刻 PCA 結果與 sklearn 完全一致。")

    # 6. 繪製圖表並存至 figs/
    os.makedirs("figs", exist_ok=True)
    os.makedirs("notes", exist_ok=True)

    plt.figure(figsize=(8, 5))
    cumulative_variance_ratio = np.cumsum(sklearn_explained_variance_ratio)
    plt.plot(range(1, n_components + 1), cumulative_variance_ratio, marker='o', linestyle='-', color='b')
    plt.title('PCA Cumulative Explained Variance Ratio (Digits Dataset)')
    plt.xlabel('Number of Principal Components')
    plt.ylabel('Cumulative Explained Variance Ratio')
    plt.grid(True)
    plt.ylim(0, 1.05)
    
    fig_path = "/home/phonchi/.cache/oc-lab-redesign/runs/phase6-gemini-3.5-flash-lite-flow/e1-vague-table-3/project/figs/pca_digits_variance.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"圖表已儲存至: {fig_path}")

if __name__ == "__main__":
    main()
