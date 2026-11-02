# 手刻 PCA 與 sklearn 驗證筆記

本篇筆記記錄如何使用 Python 與 NumPy 從零開始實作主成分分析 (Principal Component Analysis, PCA)，並以 scikit-learn 的 `sklearn.datasets.load_digits` 資料集與 `sklearn.decomposition.PCA` 進行對照驗證。

## 1. PCA 數學原理

給定資料矩陣 $X \in \mathbb{R}^{N \times D}$，其中 $N$ 為樣本數，$D$ 為特徵維度（在 digits 資料集中 $N=1797, D=64$）。

### 步驟一：資料中心化 (Zero-mean Centering)
計算每個特徵的平均值 $\mu \in \mathbb{R}^{D}$：
$$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$

將資料減去平均值：
$$X_{\text{centered}} = X - \mu$$

### 步驟二：奇異值分解 (Singular Value Decomposition, SVD)
對中心化後的資料矩陣進行 SVD：
$$X_{\text{centered}} = U S V^T$$

其中：
- $U \in \mathbb{R}^{N \times N}$ 為左奇異向量矩陣。
- $S \in \mathbb{R}^{N \times D}$ 為奇異值對角矩陣。
- $V^T \in \mathbb{R}^{D \times D}$ 為右奇異向量矩陣，其各列 (rows) 即為正交的主成分 (Principal Components)。

### 步驟三：選取前 $K$ 個主成分
取 $V^T$ 的前 $K$ 行（在此實作中 $K=10$）：
$$W_K = V[:K, :] \in \mathbb{R}^{K \times D}$$

### 步驟四：資料投影 (Transform)
將中心化資料投影到低維空間：
$$X_{\text{transformed}} = X_{\text{centered}} W_K^T = X_{\text{centered}} \cdot V[:K, :]^T$$

### 步驟五：解釋變異量 (Explained Variance)
每個主成分對應的變異量為：
$$\sigma_i^2 = \frac{S_i^2}{N - 1}$$

累積解釋變異比例為：
$$\text{Ratio}_k = \frac{\sum_{i=1}^{k} S_i^2}{\sum_{j=1}^{D} S_j^2}$$

---

## 2. 驗證結果

與 `sklearn.decomposition.PCA(n_components=10)` 進行比較，經正負號對齊 (Sign Alignment) 後：
- **Mean**：完全一致 (`True`)
- **Components**：完全一致 (`True`)
- **Transformed Data**：完全一致 (`True`)
- **Explained Variance**：完全一致 (`True`)

相關累積解釋變異比例圖已儲存至 `figs/pca_explained_variance.png`。
