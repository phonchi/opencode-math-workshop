# 手刻 PCA (Principal Component Analysis) 與 Digits 資料集驗證筆記

本篇筆記記錄如何使用 NumPy 從零開始手刻主成分分析（PCA），並以 `sklearn.datasets.load_digits` 資料集進行前 10 個主成分的降維與正確性驗證。

## 一、 PCA 數學原理與步驟

主成分分析（PCA）是一種無監督的降維技術，旨在找到一組正交軸，使投影後的資料變異數最大化。

### 1. 資料中心化 (Centering)
給定資料矩陣 $X \in \mathbb{R}^{N \times D}$（$N$ 個樣本，$D$ 個特徵），首先計算每個特徵的均值向量 $\mu \in \mathbb{R}^{D}$：
$$\mu = \frac{1}{N} \sum_{i=1}^{N} X_i$$

將資料進行中心化：
$$X_{\text{centered}} = X - \mu$$

### 2. 奇異值分解 (SVD) 或協方差矩陣特徵值分解
對中心化後的資料矩陣 $X_{\text{centered}}$ 進行奇異值分解（SVD）：
$$X_{\text{centered}} = U \Sigma V^T$$

其中：
- $U \in \mathbb{R}^{N \times N}$ 是左奇異向量矩陣。
- $\Sigma \in \mathbb{R}^{N \times D}$ 是包含奇異值 $\sigma_i$ 的對角矩陣。
- $V^T \in \mathbb{R}^{D \times D}$ 是右奇異向量矩陣，其列（rows）即為**主成分方向（Principal Components / Loadings）**。

樣本協方差矩陣 $C$ 定義為：
$$C = \frac{1}{N-1} X_{\text{centered}}^T X_{\text{centered}}$$

透過 SVD，協方差矩陣的特徵值 $\lambda_i$ 與奇異值 $\sigma_i$ 的關係為：
$$\lambda_i = \frac{\sigma_i^2}{N-1}$$

### 3. 取前 $K$ 個主成分與投影
選取 $V^T$ 的前 $K$ 個列向量（$K = 10$），組成 $W_K \in \mathbb{R}^{K \times D}$。
資料投影到低維空間的公式為：
$$X_{\text{proj}} = X_{\text{centered}} W_K^T$$

---

## 二、 程式碼實現與驗證結果

我們使用 Python 的 `numpy` 實作 `ManualPCA` 類別，並與 `sklearn.decomposition.PCA` 進行對比驗證。

### 驗證重點：
1. **解釋變異量比例 (Explained Variance Ratio)**：手刻結果與 `sklearn` 完全一致（最大絕對誤差約為 $2.36 \times 10^{-16}$）。
2. **主成分方向 (Components)**：經內積檢驗，各主成分方向的絕對值內積均為 $1.0$，符合正交基底定義（正負號模糊性屬於正常現象）。

---

## 三、 視覺化結果

降維後的結果與累積解釋變異量比例圖已儲存至：
- `figs/pca_digits_comparison.png`
