# 手刻 PCA：sklearn digits 前 10 主成分

程式：`pca_digits.py`，圖：`figs/pca_digits_check.png`。

## 推導

對資料 $X \in \mathbb{R}^{n \times d}$ 先中心化得 $X_c = X - \bar{x}$。PCA 要找單位向量 $w$ 使投影變異數 $w^\top C w$ 最大，其中協方差矩陣

$$C = \frac{1}{n-1} X_c^\top X_c.$$

拉格朗日乘子法 $\mathcal{L} = w^\top C w - \lambda(w^\top w - 1)$ 對 $w$ 微分得 $Cw = \lambda w$，故主成分就是 $C$ 的特徵向量，變異數就是特徵值。

實作上不直接算 $C$，改用 SVD 比較穩定：

$$X_c = U \Sigma V^\top \;\Rightarrow\; V$ 的前 $K$ 列為主成分、投影 $Z = X_c V_K^\top$、特徵值 $\lambda_j = \sigma_j^2 / (n-1).$$

## 手刻作法

1. 中心化：`Xc = X - X.mean(axis=0)`
2. `U, S, Vt = np.linalg.svd(Xc, full_matrices=False)`
3. 取 `V = Vt[:10]`，投影 `Z = Xc @ V.T`
4. 解釋變異比例 $\text{EVR}_j = \lambda_j / \sum_k \lambda_k$

## 驗證結果（對照 `sklearn.decomposition.PCA(n_components=10)`）

11 項檢查全數通過（atol $10^{-8}$）：

| 檢查 | 結果 |
| --- | --- |
| `explained_variance_` / `explained_variance_ratio_` 相符 | PASS |
| `components_` 相符（允許差一個正負號） | PASS |
| 投影座標 $Z$ = `transform(X)`（允許差正負號） | PASS |
| 主成分單範正交 $VV^\top = I$ | PASS |
| 投影均值 $=0$、投影各軸變異數 $=\lambda_j$ | PASS |
| 10 成分重建誤差 = sklearn 重建誤差，且 $= \frac{n-1}{n}\cdot\frac{\text{總變異} - \sum_{j\le K}\lambda_j}{d}$ | PASS |
| 另用 `np.linalg.eigh(C)` 算特徵值／向量，與 SVD 一致 | PASS |

EVR：PC1 $14.89\%$、PC2 $13.62\%$、PC3 $11.79\%$ … 前 10 主成分累計 $73.82\%$，重建 MSE $\approx 4.91$。

## 注意事項

- **符號不唯一**：$v$ 與 $-v$ 都是合法主成分，sklearn 與手刻版本可能差正負號（圖中 PC1 落在 $y=-x$、PC2 落在 $y=x$），比較時要先對齊符號。
- **MSE 的 $n-1$ 因子**：sklearn 變異數用 $1/(n-1)$，逐元素 MSE 是 $1/n$，兩者換算差 $(n-1)/n$。
- 數值上偏好 SVD 而非顯式形成 $C$ 再特徵分解，條件數較好。
