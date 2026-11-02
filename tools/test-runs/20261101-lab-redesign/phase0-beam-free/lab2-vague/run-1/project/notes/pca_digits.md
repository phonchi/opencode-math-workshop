# 手刻 PCA（sklearn digits，前 10 主成分）

- 資料：`load_digits()`，$X\in\mathbb{R}^{1797\times 64}$。
- 手刻：中心化 $X_c=X-\bar X$，SVD $X_c=U\Sigma V^\top$，取 $V_{:,1:10}$ 為主成分；投影 $Z=X_c V_{:,1:10}$。
- 前 10 主成分累積解釋變異比：$0.738227$。
- 驗證：與 `sklearn.decomposition.PCA(n_components=10)` 對齊符號後，成分最大差異 $3.5\times10^{-15}$、投影最大差異 $3.2\times10^{-13}$、EVR 最大差異 $2.6\times10^{-16}$，重建相對誤差一致 ($0.5116$)。判定 **PASS**。
