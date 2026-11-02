import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

class ManualPCA:
    def __init__(self, n_components=10):
        self.n_components = n_components
        self.mean_ = None
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None

    def fit(self, X):
        X = np.array(X, dtype=float)
        N, D = X.shape
        # 1. 均值中心化
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_

        # 2. 使用 SVD 分解進行 PCA
        # X_centered = U * S * Vt
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        # 3. 取前 n_components 個主成分
        self.components_ = Vt[:self.n_components, :]
        
        # 4. 計算解釋變異量 (Explained Variance) 與比例
        # 樣本協方差矩陣的特徵值為 S^2 / (N - 1)
        self.explained_variance_ = (S ** 2) / (N - 1)
        total_var = np.sum(S ** 2) / (N - 1)
        self.explained_variance_ratio_ = self.explained_variance_[:self.n_components] / total_var
        self.explained_variance_ = self.explained_variance_[:self.n_components]

        return self

    def transform(self, X):
        X = np.array(X, dtype=float)
        X_centered = X - self.mean_
        # 投影到主成分空間
        return np.dot(X_centered, self.components_.T)

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

def main():
    # 載入 digits 資料集
    digits = load_digits()
    X = digits.data
    y = digits.target

    n_comp = 10

    # 手刻 PCA
    manual_pca = ManualPCA(n_components=n_comp)
    X_manual = manual_pca.fit_transform(X)

    # Sklearn PCA
    sklearn_pca = SklearnPCA(n_components=n_comp)
    X_sklearn = sklearn_pca.fit_transform(X)

    print("=== 資料集形狀 ===")
    print(f"原始資料形狀: {X.shape}")
    print(f"降維後資料形狀 (手刻): {X_manual.shape}")
    print(f"降維後資料形狀 (Sklearn): {X_sklearn.shape}")

    # 驗證解釋變異量比例 (Explained Variance Ratio)
    print("\n=== 解釋變異量比例 (前 10 個主成分) ===")
    print("手刻:", manual_pca.explained_variance_ratio_)
    print("Sklearn:", sklearn_pca.explained_variance_ratio_)
    
    var_diff = np.max(np.abs(manual_pca.explained_variance_ratio_ - sklearn_pca.explained_variance_ratio_))
    print(f"解釋變異量比例最大絕對誤差: {var_diff:.2e}")
    assert var_diff < 1e-10, "解釋變異量比例不符！"

    # 驗證主成分 (考慮正負號模糊性：SVD/特徵值分解的正負號可能相反)
    # 我們可以透過校正正負號或比對投影結果的絕對值/相關性來確認
    # 或是對每個主成分檢查 dot product 的絕對值是否接近 1
    comp_manual = manual_pca.components_
    comp_sklearn = sklearn_pca.components_

    print("\n=== 主成分 (Components) 驗證 ===")
    for i in range(n_comp):
        dot_val = np.dot(comp_manual[i], comp_sklearn[i])
        # 考慮正負號，絕對值應接近 1.0
        print(f"PC{i+1} 內積值 (點積): {dot_val:.4f} (絕對值: {np.abs(dot_val):.4f})")
        assert np.abs(np.abs(dot_val) - 1.0) < 1e-5, f"第 {i+1} 個主成分方向不符！"

    print("\n驗證成功！手刻 PCA 的前 10 個主成分與 sklearn 完全一致（考慮正負號）符號方向。")

    # 繪製視覺化圖表並存至 figs/
    import os
    os.makedirs("figs", exist_ok=True)
    os.makedirs("notes", exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 畫前兩個主成分的散布圖
    scatter = axes[0].scatter(X_manual[:, 0], X_manual[:, 1], c=y, cmap='tab10', alpha=0.7, s=15)
    axes[0].set_title("Manual PCA (PC1 vs PC2)")
    axes[0].set_xlabel("Principal Component 1")
    axes[0].set_ylabel("Principal Component 2")
    fig.colorbar(scatter, ax=axes[0], label='Digit Class')

    # 畫累積解釋變異量比例
    cum_var_manual = np.cumsum(manual_pca.explained_variance_ratio_)
    cum_var_sklearn = np.cumsum(sklearn_pca.explained_variance_ratio_)
    axes[1].plot(range(1, n_comp + 1), cum_var_manual, 'bo-', label='Manual PCA', markersize=6)
    axes[1].plot(range(1, n_comp + 1), cum_var_sklearn, 'r--', label='Sklearn PCA', markersize=6)
    axes[1].set_title("Cumulative Explained Variance Ratio")
    axes[1].set_xlabel("Number of Components")
    axes[1].set_ylabel("Cumulative Explained Variance Ratio")
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("figs/pca_digits_comparison.png", dpi=300)
    plt.close()
    print("圖表已成功儲存至 figs/pca_digits_comparison.png")

if __name__ == "__main__":
    main()
