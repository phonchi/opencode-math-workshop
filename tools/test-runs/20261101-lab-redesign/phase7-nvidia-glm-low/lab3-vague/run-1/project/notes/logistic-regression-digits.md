# 手刻 Logistic 迴歸（digits 3 vs 8）推導與驗證

對應程式：`logreg_digits.py`（牛頓法）。

## 1. 問題設定

從 `sklearn.datasets.load_digits` 取出 3 與 8 兩類，標籤 $y_i \in \{0,1\}$（3→0、8→1），
特徵標準化後加上常數 1 的截距欄，共 $d = 64 + 1$ 維。

## 2. 模型與推導

$$\hat{y}_i = p_i = \sigma(x_i^\top w), \qquad \sigma(z) = \frac{1}{1+e^{-z}}$$

假設 $y_i \sim \text{Bernoulli}(p_i)$，單筆資料的 log-likelihood：

$$\log P(y_i \mid x_i; w) = y_i \log p_i + (1-y_i)\log(1-p_i)$$

要最小化的是負 log-likelihood（平均）加 L2 正則化（sklearn 預設 `penalty='l2', C=1`）：

$$J(w) = -\frac{1}{n}\sum_i \left[y_i \log \sigma(x_i^\top w) + (1-y_i)\log\big(1-\sigma(x_i^\top w)\big)\right] + \frac{\lambda}{2}\|w\|^2,\quad \lambda = \frac{1}{C n}$$

**梯度**：利用 $\partial \sigma / \partial z = \sigma(1-\sigma)$，對單筆資料微分可得經典形式：

$$\frac{\partial (-\log P(y_i|x_i;w))}{\partial w} = (\sigma(x_i^\top w) - y_i)\, x_i$$

$$\nabla J(w) = \frac{1}{n} X^\top (\sigma(Xw) - y) + \lambda \tilde{w}$$

其中 $\tilde{w}$ 是把截距那維設成 0 的 $w$（**sklearn 不懲罰截距**，手刻時一定要對齊，否則係數會差很多——這是第一次實作時踩到的坑）。

**Hessian**：$\sigma''(z) = \sigma(z)(1-\sigma(z))(1-2\sigma(z))$，但對 log-loss 而言化簡後很乾淨：

$$H(w) = \frac{1}{n} X^\top \mathrm{diag}\big(p_i(1-p_i)\big) X + \lambda\, \mathrm{diag}(\tilde{1})$$

（對截距那維不加 $\lambda$。）$H$ 是正定矩陣，所以 $J$ 是凸函數、最小值唯一。

**牛頓法更新**：

$$w^{(t+1)} = w^{(t)} - H(w^{(t)})^{-1} \nabla J(w^{(t)})$$

收斂判斷：$\|\Delta w\| < 10^{-12}$ 即停。本資料 10 次迭代就收斂。

## 3. 與 sklearn 的比較結果（test 集 25%，`random_state=42`）

| 項目 | 手刻牛頓法 | sklearn |
|---|---|---|
| test accuracy | 1.0000 | 1.0000 |
| test log-loss | 0.029345 | 0.029345 |
| train NLL | 0.0124048485 | 0.0124048483 |
| $\|w_{\text{hand}} - w_{\text{sk}}\|_2$ | $1.14 \times 10^{-6}$ | — |

兩個模型的權重相關係數 = 1.00000000，等於是解到了同一個點。

## 4. 怎麼判斷「兩個模型一樣」？

只看 accuracy 不夠——accuracy 是離散指標，兩個解差很遠也可能同分。
正確的檢查順序：

1. **目標函數要先一致**：兩邊必須最小化同一個 $J$。
   - 正則化種類與強度要對齊（sklearn 預設 `l2, C=1`，手刻就要 $\lambda = 1/(Cn)$）；
   - 截距是否被正則化要對齊（sklearn 不懲罰截距）；
   - 特徵前處理要一致（都過同一個 `StandardScaler`）。
2. **係數逐項比較**：$\|w_1 - w_2\|_2$ 與 $\max|w_1 - w_2|$ 應在浮點誤差等級（$10^{-6}$ 上下）。
   光看相關係數不夠，相關係數 = 1 只代表「方向一樣、尺度可能不同」。
3. **訓練集上的目標函數值**（train NLL）：這是最關鍵的判準。兩個解都是最小化 $J$，
   所以 $J$ 值應該一致到小數點後好幾位。若一邊的 $J$ 值明顯較高，代表那個最佳化器還沒收斂，
   而不是模型不同。本次實驗兩邊 train NLL 只差 $2 \times 10^{-10}$。
4. **連續預測值**：比較兩邊的 $p_i$（或 log-loss），而不是只有 0/1 預測。
   本次兩邊 test log-loss 完全相同到顯示的小數位。

**判斷流程白話版**：先確認兩邊在「解同一道數學題」（目標函數一致）→ 再看兩邊是否「解到同一個點」（係數與 train NLL 的差在小數點後很多位）→ 最後才看預測表現。若 train NLL 差很多，先懷疑沒收斂或目標函數沒對齊（例：忘了截距不正則、或用錯 $C$ 的縮放）。
