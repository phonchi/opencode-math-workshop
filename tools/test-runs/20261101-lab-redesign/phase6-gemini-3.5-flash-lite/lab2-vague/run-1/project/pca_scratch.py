import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

def main():
    # 1. 載入 digits 資料集
    digits = load_digits()
    X = digits.data
    y = digits.target
    print(f"資料集形狀: {X.shape}")

    # 2. 手刻 PCA (透過 SVD)
    # 步驟 A: 資料中心化 (Zero-mean centering)
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean

    # 步驟 B: Singular Value Decomposition (SVD)
    # X_centered = U * S * Vt
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

    # 步驟 C: 取前 10 個主成分
    n_components = 10
    components_scratch = Vt[:n_components]
    
    # 投影到前 10 個主成分
    X_transformed_scratch = X_centered @ components_scratch.T

    # 計算解釋變異量 (Explained Variance)
    explained_variance_scratch = (S ** 2) / (X.shape[0] - 1)
    explained_variance_ratio_scratch = (S ** 2) / np.sum(S ** 2)

    # 3. 使用 scikit-learn PCA 進行對照
    pca_sklearn = PCA(n_components=n_components)
    X_transformed_sklearn = pca_sklearn.fit_transform(X)

    # 4. 驗證結果正確性
    # 考慮特徵向量的正負號模糊性 (Sign ambiguity)，進行對齊
    for i in range(n_components):
        if np.dot(components_scratch[i], pca_sklearn.components_[i]) < 0:
            components_scratch[i] *= -1
            X_transformed_scratch[:, i] *= -1

    # 檢查均值
    print("檢查 Mean 是否一致:", np.allclose(X_mean, pca_sklearn.mean_))
    # 檢查主成分
    print("檢查主成分 (Components) 是否一致:", np.allclose(components_scratch, pca_sklearn.components_))
    # 檢查降維後的資料 (Transform)
    print("檢查投影資料 (Transform) 是否一致:", np.allclose(X_transformed_scratch, X_transformed_sklearn))
    # 檢查解釋變異量
    print("檢查解釋變異量 (Explained Variance) 是否一致:", np.allclose(explained_variance_scratch[:n_components], pca_sklearn.explained_variance_))
    print("檢查解釋變異量比例 (Explained Variance Ratio) 是否一致:", np.allclose(explained_variance_ratio_scratch[:n_components], pca_sklearn.explained_variance_ratio_))

    # 5. 繪製前 10 個主成分的累積解釋變異比例圖，並存至 figs/
    import os
    os.makedirs("figs", exist_ok=True)
    os.makedirs("notes", exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(np.cumsum(explained_variance_ratio_scratch), marker='o', linestyle='-', color='b')
    plt.xlabel('Number of Components')
    plt.ylabel('Cumulative Explained Variance Ratio')
    plt.title('PCA Cumulative Explained Variance Ratio on Digits Dataset')
    plt.grid(True)
    plt.savefig('figs/pca_explained_variance.png')
    plt.close()
    print("圖檔已儲存至 figs/pca_explained_variance.png")

if __name__ == "__main__":
    main()
