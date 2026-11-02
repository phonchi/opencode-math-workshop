# 手刻 Logistic 迴歸：digits 3 vs 8

## 1. 資料與前處理

使用 `sklearn.datasets.load_digits()`，篩選標籤為 3 與 8 的樣本，令

$$y_i = \begin{cases} 0 & \text{若數字為 3}\\ 1 & \text{若數字為 8}\end{cases}$$

特徵為 $8\times 8=64$ 維像素。為讓梯度下降穩定，對訓練集做標準化

$$\tilde{x}_{ij} = \frac{x_{ij}-\mu_j}{\sigma_j}$$

（$\mu_j,\sigma_j$ 只用訓練集估計，再套用到測試集）。

## 2. 模型

$$P(y=1\mid x)=\sigma(w^\top \tilde{x}+b),\qquad 
\sigma(z)=\frac{1}{1+e^{-z}}.$$

## 3. 推導：損失與梯度

對單一樣本的對數概似

$$\log P(y\mid x)= y\log p + (1-y)\log(1-p),\quad p=\sigma(w^\top \tilde{x}+b).$$

全資料平均負對數概似（資料項）

$$J_{\text{data}}(w,b)= -\frac{1}{n}\sum_{i=1}^n \left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].$$

為與 `sklearn` 預設（`C=1.0`，L2）對齊，加入正則項（截距不正則）

$$J(w,b)=J_{\text{data}}(w,b)+\frac{1}{2Cn}\|w\|^2.$$

梯度（利用 $\sigma'(z)=\sigma(z)(1-\sigma(z))$）：

$$\frac{\partial J}{\partial w}= \frac{1}{n}X^\top(p-y)+\frac{1}{Cn}w,\qquad
\frac{\partial J}{\partial b}= \frac{1}{n}\sum_{i=1}^n (p_i-y_i).$$

更新規則（全批次梯度下降）：

$$w \leftarrow w-\eta\frac{\partial J}{\partial w},\qquad
b \leftarrow b-\eta\frac{\partial J}{\partial b}.$$

迭代至 $|J_{t}-J_{t-1}|<\text{tol}$（本實作 $\text{tol}=10^{-12}$）。

## 4. 與 sklearn 比較

`sklearn.linear_model.LogisticRegression(C=1.0, solver='lbfgs')` 解的是同一個凸最佳化問題。結果：

| 指標 | 手刻 | sklearn |
|---|---|---|
| 訓練準確率 | 1.000 | 1.000 |
| 測試準確率 | 1.000 | 1.000 |
| 測試 log-loss | 0.02770 | 0.02770 |
| 預測一致率 | 1.000 | — |
| max \|p_hand − p_sk\| (test) | $5.1\times 10^{-5}$ | — |
| 係數 Pearson 相關 | $0.999999997$ | — |
| max \|w_hand − w_sk\| | $1.7\times 10^{-4}$ | — |
| cosine(w_hand, w_sk) | $0.999999997$ | — |

圖檔：`figs/logistic_loss.png`、`figs/logistic_coef.png`、`figs/logistic_proba.png`。

結論：手刻實作與 sklearn 解同一凸問題，係數與機率在數值容差內一致，確認實作正確。

## 5. 如何判斷「兩個模型一樣」

不要只看準確率（太粗，易掩蓋差異）。建議由嚴到鬆依序檢查：

1. **預測一致率**：$\frac{1}{m}\sum \mathbf{1}[\hat y^{\text{hand}}_i=\hat y^{\text{sk}}_i]$，應 = 1。
2. **機率差**：$\max_i |p^{\text{hand}}_i-p^{\text{sk}}_i|$ 與平均差，應 $<10^{-4}$（或 $<10^{-5}$）。
3. **損失**：log-loss 差應 $<10^{-4}$。
4. **係數對齊**：Pearson 相關與 cosine 應 $>0.9999$，$\max_i |w^{\text{hand}}_i-w^{\text{sk}}_i|$ 小。
5. **混淆矩陣 / ROC-AUC**：應完全相同或極接近。

同時需控制實驗設定一致：前處理（標準化）、正則化強度（`C`/`lambda`）、是否正則化截距、solver 與收斂條件（`tol`、`max_iter`）、隨機種子、train/test 切分。任一不同都會讓「是否相同」的判斷失真。

注意：若資料線性可分且**不加正則化**，MLE 無有限解（係數趨向無限大），此時只能比較預測/機率與收斂軌跡，不能比較係數大小；要比較係數必須固定正則化。另外，「預測相同」不等於「模型相同」——不同參數可能給出相同分類；真正相同需機率與參數都對齊。
