# 手刻 PCA 與 sklearn digits 資料集分析筆記

本篇筆記記錄如何從零實作 PCA（主成分分析）並應用於 `sklearn.datasets.load_digits` 資料集，同時透過 scikit-learn 的 `PCA` 驗證其數學正確性。

## 1. PCA 數學原理

PCA 的目標是將高維度資料 $X \in \mathbb{R}^{n \times p}$ 投影到低維度子空間 $\mathbb{R}^{n \times k}$，同時最大化投影後的變異數。

1. **資料中心化 (Centering)**：
   $$\mathbf{X}_{centered} = \mathbf{X} - \mu$$
   其中 $\mu$ 為每個特徵的平均值。

2. **奇異值分解 (Singular Value Decomposition, SVD)**：
   對中心化後的矩陣進行 SVD：
   $$\mathbf{X}_{centered} = \mathbf{U} \boldsymbol{\Sigma} \mathbf{V}^T$$
   其中 $\mathbf{V}^T$ 的各列即為主成分方向（即樣本共變異數矩陣的特徵向量）。

3. **解釋變異數比例 (Explained Variance Ratio)**：
   第 $i$ 個主成分的變異數為：
   $$\lambda_i = \frac{S_i^2}{n - 1}$$
   其解釋變異數比例為：
   $$\text{Ratio}_i = rac{\lambda_i}{\sum_{j} \lambda_j}$$

4. **資料投影 (Projection)**：
   取前 $k$ 個主成分 $\mathbf{V}_k$，將資料投影至低維空間：
   $$\mathbf{X}_{projected} = \mathbf{X}_{centered} \mathbf{V}_k^T$$

## 2. 實驗結果與驗證

- 資料集樣本數：1797，特徵數：64
- 提取主成分數量：$k = 10$
- 前 10 個主成分累積解釋變異數比例：**73.82%**
- 經比對，手刻實作的解釋變異數比例與 sklearn PCA 最大誤差小於 `1e-7`，投影資料與主成分向量在符號對齊後亦完全吻合。

## 3. 視覺化圖表
- 產生的 PCA 投影與累積變異數圖表已儲存至 `figs/pca_digits.png`。
