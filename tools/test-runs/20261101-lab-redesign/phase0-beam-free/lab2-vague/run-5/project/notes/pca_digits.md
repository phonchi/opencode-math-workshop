# 手刻 PCA：sklearn digits 前 10 主成分

使用 `sklearn.datasets.load_digits`（1797 筆、64 維），以 `np.linalg.svd` 手刻 PCA，取前 $k=10$ 個主成分。

步驟：中心化 $X_c=X-\bar X$，SVD $X_c=USV^\top$，主成分方向為 $V^\top$ 前 $k$ 列；投影 $Z=X_c W$。

驗證（與 `sklearn.decomposition.PCA(n_components=10)` 比對）：
- component 方向 $|\cos|$ 對角線全為 1，離對角最大 0
- explained variance ratio 最大差 $2.36\times10^{-16}$
- 投影相關係數絕對值全為 1
- 重建 MSE 相同（4.9143）

圖：`figs/pca_digits.png`。
