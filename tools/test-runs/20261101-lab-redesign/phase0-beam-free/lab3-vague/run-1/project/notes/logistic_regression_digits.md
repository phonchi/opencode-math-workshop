# 手刻 Logistic 迴歸：digits 3 vs 8

## 1. 問題設定

使用 `sklearn.datasets.load_digits`，篩選標籤為 3 與 8 的樣本，轉成二元分類
$y\in\{0,1\}$（3 → 0，8 → 1）。共 $n=357$ 筆，每筆 $p=64$ 個像素特徵。

## 2. 模型

$$
p_i = P(y_i=1\mid x_i) = \sigma(z_i),\quad z_i = w^\top x_i + b,\quad
\sigma(z)=\frac{1}{1+e^{-z}}.
$$

## 3. 推導：損失函數

獨立 Bernoulli 假設下的負對數概似（binary cross entropy）：

$$
\ell_i = -\big[y_i\log p_i + (1-y_i)\log(1-p_i)\big],
\qquad
L(w,b)=\frac1n\sum_{i=1}^n \ell_i.
$$

為與 sklearn 預設 `C=1.0` 對齊，加入 L2 正則化：

$$
J(w,b)=\frac1n\sum_i \ell_i + \frac{1}{2Cn}\|w\|_2^2
$$

（intercept $b$ 不正則化）。

## 4. 推導：梯度

利用 $\partial p_i/\partial z_i = p_i(1-p_i)$：

$$
\frac{\partial J}{\partial w}
= \frac1n\sum_i (p_i-y_i)x_i + \frac{1}{Cn}w,
\qquad
\frac{\partial J}{\partial b}
= \frac1n\sum_i (p_i-y_i).
$$

Batch gradient descent 更新：$w\leftarrow w-\eta \nabla_w J$，$b\leftarrow b-\eta \nabla_b J$。

## 5. 推導：Hessian 與 Newton (IRLS)

$$
H_{ww}=\frac1n\sum_i p_i(1-p_i)x_ix_i^\top + \frac{1}{Cn}I,\quad
H_{wb}=\frac1n\sum_i p_i(1-p_i)x_i,\quad
H_{bb}=\frac1n\sum_i p_i(1-p_i).
$$

Newton 更新：$\theta\leftarrow \theta-H^{-1}\nabla J$，其中 $\theta=(w,b)$。本實作最終模型採用此法，14 次迭代即收斂。

## 6. 實作細節

- 10 個像素在 3/8 子集中為常數（標準差 0），其係數不可識別；手刻與 sklearn 皆將其係數設為 0。
- 正則化強度換算：$\lambda = 1/(Cn)$，使目標函數與 sklearn 一致。

## 7. 與 sklearn 比較結果

| 指標 | 數值 |
|---|---|
| 係數 cosine 相似度 | 0.9999999992 |
| 係數最大絕對差異 | $4.57\times10^{-6}$ |
| intercept 差異 | $2.60\times10^{-4}$ |
| 全資料 accuracy (兩者) | 1.000000 |
| 預測一致率 | 1.000000 |
| 機率 RMSE | $4.42\times10^{-8}$ |
| 機率 Pearson r | 1.0000000000 |
| 測試集 accuracy (兩者) | 0.986111 |

結論：手刻 (Newton/IRLS) 與 sklearn 的係數、機率、預測皆一致到數值誤差等級，確認實作正確。

## 8. 如何判斷兩個模型「一樣」

1. 不要只比係數是否逐位元相等：優化器、tolerance、特徵縮放、正則化換算、不可識別特徵都會造成微小差異；在可分資料上 MLE 更是不唯一。
2. 比預測：labels 一致率、accuracy、confusion matrix 應完全或幾乎一致。
3. 比機率：預測機率的 RMSE / 最大絕對誤差應在 $10^{-6}$ 以內，Pearson r ≈ 1。
4. 比係數方向：cosine 相似度接近 1、相對誤差在 tolerance（例如 $10^{-3}$）內；允許 intercept 有 $10^{-3}$ 級差異。
5. 確保比較條件一致：相同資料、相同 train/test split、相同前處理（標準化）、相同正則化 (`C`)、相同 random_state；以 hold-out 或 cross-validation 的指標作為最終依據。
6. 實務上以「預測等價」而非「參數等價」判定：若兩模型在新資料上的預測與機率皆一致，即可視為同一模型。
EOF
echo done