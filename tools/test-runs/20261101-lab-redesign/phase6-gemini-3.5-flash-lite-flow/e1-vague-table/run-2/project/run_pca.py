import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

class HandcraftedPCA:
    def __init__(self, n_components=10):
        self.n_components = n_components
        self.mean = None
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        
    def fit(self, X):
        n_samples, n_features = X.shape
        # 1. 中心化 (Center the data)
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean
        
        # 2. 使用 SVD 分解 (Singular Value Decomposition)
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        
        # 3. 計算特徵值與解釋變異數 (Calculate eigenvalues / variance)
        eigenvalues = (S ** 2) / (n_samples - 1)
        total_variance = np.sum(eigenvalues)
        
        self.explained_variance_ = eigenvalues[:self.n_components]
        self.explained_variance_ratio_ = self.explained_variance_ / total_variance
        
        # 4. 取前 n_components 個主成分 (Top k components)
        self.components_ = Vt[:self.n_components, :]
        
        return self
        
    def transform(self, X):
        X_centered = X - self.mean
        return np.dot(X_centered, self.components_.T)
        
    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

def main():
    # 載入 Digits 資料集
    digits = load_digits()
    X = digits.data
    y = digits.target
    print(f"資料集形狀 (Data shape): {X.shape}")
    
    # 手刻 PCA (前 10 個主成分)
    n_comp = 10
    my_pca = HandcraftedPCA(n_components=n_comp)
    X_projected_my = my_pca.fit_transform(X)
    
    # Sklearn PCA 對照
    sk_pca = SklearnPCA(n_components=n_comp)
    X_projected_sk = sk_pca.fit_transform(X)
    
    print(f"手刻降維後形狀 (Handcrafted projected shape): {X_projected_my.shape}")
    print(f"Sklearn 降維後形狀 (Sklearn projected shape): {X_projected_sk.shape}")
    
    # 確認正確性
    print("\n--- 解釋變異數比例比較 (Explained Variance Ratio Comparison) ---")
    print("手刻 (Handcrafted):", np.round(my_pca.explained_variance_ratio_, 4))
    print("Sklearn:        ", np.round(sk_pca.explained_variance_ratio_, 4))
    
    ratio_diff = np.max(np.abs(my_pca.explained_variance_ratio_ - sk_pca.explained_variance_ratio_))
    print(f"解釋變異數比例最大差值 (Max diff in explained variance ratio): {ratio_diff:.2e}")
    assert ratio_diff < 1e-7, "解釋變異數比例不符！"
    
    # 對齊符號後比較投影值與主成分
    components_my = my_pca.components_.copy()
    projected_my = X_projected_my.copy()
    for i in range(n_comp):
        if np.dot(components_my[i], sk_pca.components_[i]) < 0:
            components_my[i] *= -1
            projected_my[:, i] *= -1
            
    comp_diff = np.max(np.abs(components_my - sk_pca.components_))
    proj_diff = np.max(np.abs(projected_my - X_projected_sk))
    print(f"主成分權重最大差值 (Max diff in components after sign alignment): {comp_diff:.2e}")
    print(f"投影資料最大差值 (Max diff in projected data after sign alignment): {proj_diff:.2e}")
    
    assert comp_diff < 1e-7, "主成分權重不符！"
    assert proj_diff < 1e-5, "投影資料不符！"
    print("\n>>> 驗證成功：手刻 PCA 結果與 scikit-learn PCA 完全一致！ <<<\n")
    
    # 計算全部主成分的累積解釋變異數
    full_pca = HandcraftedPCA(n_components=X.shape[1])
    full_pca.fit(X)
    cum_var = np.cumsum(full_pca.explained_variance_ratio_)
    
    # 繪製圖表
    import os
    os.makedirs("figs", exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    scatter = axes[0].scatter(projected_my[:, 0], projected_my[:, 1], c=y, cmap='tab10', alpha=0.7, s=15)
    axes[0].set_title("Digits PCA (PC1 vs PC2)")
    axes[0].set_xlabel("Principal Component 1")
    axes[0].set_ylabel("Principal Component 2")
    fig.colorbar(scatter, ax=axes[0], label='Digit Class')
    
    axes[1].plot(range(1, len(cum_var) + 1), cum_var, marker='o', linestyle='-', color='b')
    axes[1].axhline(y=cum_var[9], color='r', linestyle='--', label=f'Top 10 components ({cum_var[9]*100:.1f}%)')
    axes[1].set_title("Cumulative Explained Variance Ratio")
    axes[1].set_xlabel("Number of Components")
    axes[1].set_ylabel("Cumulative Explained Variance")
    axes[1].grid(True)
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig("figs/pca_digits.png", dpi=300)
    print("圖檔已儲存至 figs/pca_digits.png")
    
    # 寫入筆記 notes/pca_digits.md
    os.makedirs("notes", exist_ok=True)
    top10_pct = cum_var[9] * 100
    samples_count = X.shape[0]
    features_count = X.shape[1]
    
    note_content = (
        "# 手刻 PCA 與 sklearn digits 資料集分析筆記\n\n"
        "本篇筆記記錄如何從零實作 PCA（主成分分析）並應用於 `sklearn.datasets.load_digits` 資料集，"
        "同時透過 scikit-learn 的 `PCA` 驗證其數學正確性。\n\n"
        "## 1. PCA 數學原理\n\n"
        "PCA 的目標是將高維度資料 $X \\in \\mathbb{R}^{n \\times p}$ 投影到低維度子空間 $\\mathbb{R}^{n \\times k}$，"
        "同時最大化投影後的變異數。\n\n"
        "1. **資料中心化 (Centering)**：\n"
        "   $$\\mathbf{X}_{centered} = \\mathbf{X} - \\mu$$\n"
        "   其中 $\\mu$ 為每個特徵的平均值。\n\n"
        "2. **奇異值分解 (Singular Value Decomposition, SVD)**：\n"
        "   對中心化後的矩陣進行 SVD：\n"
        "   $$\\mathbf{X}_{centered} = \\mathbf{U} \\boldsymbol{\\Sigma} \\mathbf{V}^T$$\n"
        "   其中 $\\mathbf{V}^T$ 的各列即為主成分方向（即樣本共變異數矩陣的特徵向量）。\n\n"
        "3. **解釋變異數比例 (Explained Variance Ratio)**：\n"
        "   第 $i$ 個主成分的變異數為：\n"
        "   $$\\lambda_i = \\frac{S_i^2}{n - 1}$$\n"
        "   其解釋變異數比例為：\n"
        "   $$\\text{Ratio}_i = \frac{\\lambda_i}{\\sum_{j} \\lambda_j}$$\n\n"
        "4. **資料投影 (Projection)**：\n"
        "   取前 $k$ 個主成分 $\\mathbf{V}_k$，將資料投影至低維空間：\n"
        "   $$\\mathbf{X}_{projected} = \\mathbf{X}_{centered} \\mathbf{V}_k^T$$\n\n"
        "## 2. 實驗結果與驗證\n\n"
        f"- 資料集樣本數：{samples_count}，特徵數：{features_count}\n"
        f"- 提取主成分數量：$k = {n_comp}$\n"
        f"- 前 10 個主成分累積解釋變異數比例：**{top10_pct:.2f}%**\n"
        "- 經比對，手刻實作的解釋變異數比例與 sklearn PCA 最大誤差小於 `1e-7`，投影資料與主成分向量在符號對齊後亦完全吻合。\n\n"
        "## 3. 視覺化圖表\n"
        "- 產生的 PCA 投影與累積變異數圖表已儲存至 `figs/pca_digits.png`。\n"
    )
    
    with open("notes/pca_digits.md", "w", encoding="utf-8") as f:
        f.write(note_content)
    print("筆記已寫入 notes/pca_digits.md")

if __name__ == "__main__":
    main()
