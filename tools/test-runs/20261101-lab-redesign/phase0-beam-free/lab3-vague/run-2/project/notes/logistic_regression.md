# Logistic 迴歸手刻與 sklearn 比較：digits 3 vs 8

## 問題設定

取 `sklearn.datasets.load_digits()` 中標籤為 3 與 8 的樣本，二元分類：

- 輸入 \(x \in \mathbb{R}^{64}\)（8×8 像素攤平）
- 標籤 \(y \in \{0,1\}\)，定義 \(y=1\) 代表 8、\(y=0\) 代表 3
- 訓練/測試分割：70/30，`stratify=y`，`random_state=42`
- 特徵標準化：\( \tilde x = (x-\mu)/\sigma \)（fit 於訓練集）

## 模型

\[
p(x)=\Pr(y=1\mid x)=\sigma(w^\top \tilde x + b),\qquad
\sigma(z)=\frac{1}{1+e^{-z}}.
\]

## 推導：從 MLE 到 Log Loss

對單一樣本，Bernoulli likelihood：

\[
\Pr(y\mid x)=p^y(1-p)^{1-y}.
\]

\(n\) 筆獨立樣本的 log-likelihood：

\[
\ell(w,b)=\sum_{i=1}^n \left[ y_i \log p_i + (1-y_i)\log(1-p_i)\right].
\]

最大化 \(\ell\) 等價於最小化負 log-likelihood（log loss / cross-entropy）：

\[
J(w,b)=-\frac{1}{n}\ell(w,b)
      =-\frac{1}{n}\sum_{i=1}^n\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
\]

## 推導：梯度

令 \(z_i=w^\top \tilde x_i+b\)，\(p_i=\sigma(z_i)\)。注意 \(\sigma'(z)=\sigma(z)(1-\sigma(z))=p(1-p)\)。

\[
\frac{\partial J}{\partial w}
 = -\frac{1}{n}\sum_i \left(\frac{y_i}{p_i}-\frac{1-y_i}{1-p_i}\right)p_i(1-p_i)\tilde x_i
 = \frac{1}{n}\sum_i (p_i-y_i)\tilde x_i
 = \frac{1}{n}X^\top(p-y).
\]

\[
\frac{\partial J}{\partial b}=\frac{1}{n}\sum_i (p_i-y_i).
\]

梯度下降更新：\(w \leftarrow w-\eta \nabla_w J\)，\(b \leftarrow b-\eta \nabla_b J\)。

## 推導：Hessian 與 Newton / IRLS

\[
H_{ww}=\frac{1}{n}\sum_i p_i(1-p_i)\tilde x_i\tilde x_i^\top,\quad
H_{wb}=\frac{1}{n}\sum_i p_i(1-p_i)\tilde x_i,\quad
H_{bb}=\frac{1}{n}\sum_i p_i(1-p_i).
\]

Newton 更新 \(\beta\leftarrow \beta-H^{-1}g\)（\(\beta=[w;b]\)）二次收斂，即 IRLS。

## L2 正則化與 sklearn 的對齊

digits 3 vs 8 幾乎線性可分，未正則化的 MLE 不存在有限解（權重會發散）。故採 L2 正則化讓解唯一、可比較。

sklearn 目標（`l1_ratio=0` 即 L2，`C` 為正則強度反比）：

\[
\min_{w,b}\; \frac12\|w\|_2^2 + C\sum_{i=1}^n \log(1+e^{-y_i^* z_i}),
\quad y_i^* \in \{-1,+1\}.
\]

手刻以 mean 形式寫：

\[
J_{\text{reg}} = \frac1n\sum_i \ell_i + \frac{\lambda}{2}\|w\|_2^2.
\]

兩者 minimizer 對齊條件：\(\lambda = 1/(C n)\)。bias 不正則化（sklearn 亦然）。本實驗取 \(C=1.0\)。

正則化後的梯度/Hessian 在 \(w\) 區塊各加 \(\lambda w\) 與 \(\lambda I\)。

## 實驗結果（`logistic_digits.py`）

| 指標 | sklearn | 手刻 (Newton) |
|---|---|---|
| train acc | 1.0 | 1.0 |
| test acc | 1.0 | 1.0 |
| train log loss | 0.0126880363 | 0.0126880358 |
| test log loss | 0.0276985137 | 0.0276985201 |
| test AUC | 1.0 | 1.0 |

差異：

- \(\max |w_i^{\text{hand}}-w_i^{\text{sk}}| \approx 2.39\times10^{-7}\)
- \(\|w^{\text{hand}}-w^{\text{sk}}\|_2 \approx 6.83\times10^{-7}\)
- \(|b^{\text{hand}}-b^{\text{sk}}| \approx 2.16\times10^{-7}\)
- \(\max |p^{\text{hand}}-p^{\text{sk}}| \approx 1.47\times10^{-7}\)（test）
- 預測一致率：train/test 皆 1.0

圖：`figs/logistic_weights_proba.png`、`figs/logistic_roc.png`。

## 如何判斷兩個模型「一樣」

1. **參數對齊**：比較 \(w,b\) 的 \(\max\) 絕對差與 L2 差，設定 tolerance（例如 \(10^{-5}\) 或 \(10^{-6}\)）。浮點與 solver 差異下，\(10^{-6}\sim10^{-7}\) 已可視為相同。
2. **機率對齊**：\(\max |p_{\text{hand}}-p_{\text{sk}}|\)、RMSE、相關係數；應在 \(10^{-6}\) 以內。
3. **決策一致**：accuracy、confusion matrix、預測 label 一致率；在可分資料上皆應 1.0。
4. **校準/排序**：AUC、log loss、Brier score 應一致。
5. **功能等價測試**：對大量隨機/邊界輸入（含訓練/測試外）比對預測與機率；檢查決策邊界。
6. **控制變因**：資料分割、標準化（fit 範圍）、正則化強度（\(C\)↔\(\lambda\)）、solver、tol、max_iter、隨機種子必須一致；任一不同都可能造成差異。
7. **注意不可比的情況**：未正則化且資料可分時，MLE 不存在有限解，不同 solver 收斂到不同有限近似（權重大小不同但預測幾乎相同）——此時只能比「預測」不能比「參數」。

結論：本手刻實作（L2 對齊、Newton/IRLS）與 sklearn 在參數、機率、預測、loss 上皆在 \(10^{-6}\) 以內一致，可判定為同一模型。
