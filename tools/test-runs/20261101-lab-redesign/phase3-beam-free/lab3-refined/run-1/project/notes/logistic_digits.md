# 手刻 Logistic 迴歸：digits 3 vs 8

## 推導

對樣本 $x \in \mathbb{R}^d$，模型輸出

$$
p = \sigma(w^\top x + b),\quad \sigma(z)=\frac{1}{1+e^{-z}}.
$$

二元交叉熵（平均）為

$$
\mathcal L = -\frac1n\sum_{i=1}^n \left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
$$

為避免資料可分離時 MLE 係數發散，並與 sklearn 預設一致，加入 L2 正則化（$C=1$）：

$$
J = \mathcal L + \frac{1}{2n}\|w\|_2^2 .
$$

梯度：

$$
\frac{\partial J}{\partial w}
= \frac1n\left(X^\top(p-y)+w\right),\qquad
\frac{\partial J}{\partial b}
= \frac1n \mathbf{1}^\top(p-y).
$$

批次梯度下降更新：

$$
w \leftarrow w-\eta\frac{\partial J}{\partial w},\qquad
b \leftarrow b-\eta\frac{\partial J}{\partial b}.
$$

## 實作與比較

- 資料：`sklearn.datasets.load_digits`，只取標籤 3 與 8，$y=1$ 表示 8。
- 特徵標準化（`StandardScaler`），train/test split `test_size=0.3`、`random_state=42`。
- 手刻：gradient descent，$\eta=0.5$，收斂條件 loss 變化 $<10^{-14}$。
- sklearn：`LogisticRegression(l1_ratio=0, C=1.0, solver='lbfgs', tol=1e-12)`。

結果（test set）：

| 指標 | 手刻 | sklearn |
|---|---|---|
| accuracy | 1.0 | 1.0 |
| prediction agreement | 1.0 | |
| max prob diff | $1.1\times10^{-6}$ | |
| max $\|w_{\text{hand}}-w_{\text{sk}}\|_\infty$ | $1.6\times10^{-6}$ | |
| $|b_{\text{hand}}-b_{\text{sk}}|$ | $3.3\times10^{-6}$ | |
| $\operatorname{corr}(w_{\text{hand}},w_{\text{sk}})$ | $1.0$ | |

圖檔：`figs/logistic_loss.png`、`figs/logistic_coef.png`。

## 如何判斷兩個模型「一樣」

1. 前處理一致：相同 scaling、相同 train/test split。
2. 預測一致：train/test 上預測標籤 agreement = 1（或 ≥ 0.99）。
3. 機率接近：$\max |p_{\text{hand}}-p_{\text{sk}}|$ 在 $10^{-5}$ 以內。
4. 指標一致：accuracy / confusion matrix 相同。
5. 係數接近：$\max |w_{\text{hand}}-w_{\text{sk}}|$ 在 $10^{-5}$ 以內，且 $\operatorname{corr}\approx 1$。
6. 注意：若不加正則化且資料可分離，MLE 係數會發散，不同 solver 停在不同尺度，此時不能用係數大小判斷，只能用預測/機率/決策邊界判斷。
