# 手刻主成分分析 (PCA) 與 digits 資料集驗證筆記

本筆記記錄如何從零開始（手刻）實作主成分分析（Principal Component Analysis, PCA），並使用 `scikit-learn` 的 `digits` 資料集與官方 `sklearn.decomposition.PCA` 進行數值驗證。

## 1. PCA 數學原理

主成分分析是一種非監督式的線性降維技術，旨在尋找資料變異數最大的正交方向（主成分）。

### 步驟一：資料中心化 (Centering)
給定資料矩陣 $X \in \mathbb{R}^{N \times D}$（$N$ 個樣本，$D$ 個特徵），首先計算每個特徵的平均值向量 $\mu \in \mathbb{R}^{D}$：
$$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$

將資料減去平均值，得到中心化後的資料 $X_c$：
$$X_c = X - \mathbf{1}\mu^T$$

### 步驟二：奇異值分解 (Singular Value Decomposition, SVD)
對中心化矩陣 $X_c$ 進行 SVD 分解：
$$X_c = U \Sigma V^T$$

其中：
- $U \in \mathbb{R}^{N \times N}$ 是左奇異向量矩陣。
- $\Sigma \in \mathbb{R}^{N \times D}$ 是對角矩陣，對角線上的元素為奇異值 $\sigma_i$。
- $V^T \in \mathbb{R}^{D \times D}$ 是右奇異向量矩陣，其列向量（Rows）即為主成分方向（即共變異數矩陣的特徵向量）。

### 步驟三：投影與降維
選取前 $k$ 個主成分（即 $V^T$ 的前 $k$ 列，記為 $V_k^T \in \mathbb{R}^{k \times D}$），將資料投影到低維空間：
$$X_{\text{reduced}} = X_c V_k^T$$

### 步驟四：解釋變異數比例 (Explained Variance Ratio)
樣本共變異數矩陣的特徵值 $\lambda_i$ 與奇異值 $\sigma_i$ 的關係為：
$$\lambda_i = \frac{\sigma_i^2}{N - 1}$$

第 $i$ 個主成分的解釋變異數比例為：
$$\text{Ratio}_i = \frac{\lambda_i}{\sum_{j=1}^{D} \lambda_j}$$

---

## 2. 程式碼實作與驗證

我們使用 Python 的 `numpy` 與 `scikit-learn` 實作上述步驟，並與 `sklearn.decomposition.PCA(n_components=10)` 進行對比。

- 手刻實作程式碼位於 `pca_digits.py`。
- 執行指令：`uv run python pca_digits.py`

## 3. 實驗結果與結論

- **主成分最大誤差** $< 10^{-10}$
- **投影資料最大誤差** $< 10^{-10}$
- **解釋變異數比例最大誤差** $< 10^{-10}$

這證明了手刻 PCA 的數學推導與實作完全正確，且與 Scikit-Learn 內建的 PCA 模組結果高度吻合。
累積解釋變異數比例圖已儲存至 `figs/pca_digits_variance.png`。
