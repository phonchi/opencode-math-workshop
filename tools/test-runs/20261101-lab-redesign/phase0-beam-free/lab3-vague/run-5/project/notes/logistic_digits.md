# 手刻 Logistic 迴歸：Digits 3 vs 8

## 1. 資料
使用 `sklearn.datasets.load_digits()`，取標籤 3 與 8，轉為二元分類：
$y_i=1$ 表示數字 8，$y_i=0$ 表示數字 3。特徵 $x_i\in\mathbb{R}^{64}$ 為 8×8 像素。

## 2. 模型
$$p_i = P(y_i=1\mid x_i)=\sigma(w^\top x_i+b),\quad \sigma(z)=\frac{1}{1+e^{-z}}.$$

## 3. 推導

### 負對數概似（最小化目標）
$$J(w,b)=-\sum_i\bigl[y_i\log p_i+(1-y_i)\log(1-p_i)\bigr]+\frac{1}{2C}\|w\|_2^2$$
（$C$ 與 sklearn 一致，截距 $b$ 不正則化。）

### 梯度
令 $z_i=w^\top x_i+b$，$\sigma'(z)=\sigma(z)(1-\sigma(z))$。由 $\partial p_i/\partial w=(p_i-y_i?)$ 推得：
$$\nabla_w J = \sum_i (p_i-y_i)x_i + \frac{1}{C}w,\qquad
\nabla_b J = \sum_i (p_i-y_i).$$
（sklearn 實作採樣本平均，等價於上式除以 $n$。）

### Hessian
$$H = \begin{pmatrix} X^\top \operatorname{diag}(p_i(1-p_i))X + \frac{1}{C}I & X^\top p(1-p)\\ p(1-p)^\top X & \sum_i p_i(1-p_i)\end{pmatrix}.$$

### Newton-Raphson 更新
$$\theta \leftarrow \theta - H^{-1}\nabla J,\qquad \theta=(w,b).$$
重複至 $\|\Delta\theta\|$ 足夠小。常數特徵（零變異）的係數固定為 0。

## 4. 實作與比較
手刻使用 Newton-Raphson（IRLS），與 `sklearn.linear_model.LogisticRegression(C=1, solver='newton-cg')` 比較：

- 係數最大絕對差 $\approx 3.2\times10^{-15}$
- 截距絕對差 $\approx 3.9\times10^{-14}$
- 預測機率最大絕對差 $\approx 2.4\times10^{-16}$
- 類別預測一致率 $=100\%$
- Accuracy 與 log-loss 一致

與預設 `lbfgs` solver 比較：係數差 $\approx 4.6\times10^{-6}$、機率差 $\approx 3.3\times10^{-7}$，但預測一致率仍 $100\%$（lbfgs 未完全收斂到 Newton 解）。

## 5. 如何判斷兩個模型「一樣」
1. **超參數一致**：相同 $C$、正則化類型、是否含截距、特徵前處理。
2. **參數接近**：$\|w_{\text{hand}}-w_{\text{sk}}\|_\infty$ 與 $|b_{\text{hand}}-b_{\text{sk}}|$ 小於容差（如 $10^{-6}$）。
3. **輸出一致**：$\max_i |p_{\text{hand}}(x_i)-p_{\text{sk}}(x_i)|$ 小；類別預測一致率 $=1$。
4. **指標一致**：accuracy、log-loss 等差異在數值誤差內。
5. **注意不可識別性**：若資料線性可分，MLE 不存在、係數可漂向無窮；此時只能比較預測/機率，不能比係數。正則化可避免此問題。
6. **特徵對齊**：相同欄位順序、相同縮放；類別標籤對應（0/1）需一致。

結論：在相同正則化與特徵下，手刻 Newton 解與 sklearn newton-cg 解在數值精度內一致，視為同一模型。