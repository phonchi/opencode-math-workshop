# 手刻 Logistic 迴歸：digits 3 vs 8

## 1. 問題設定

使用 `sklearn.datasets.load_digits()`，只取數字 3 與 8，共 357 筆（3:183, 8:174）。
每筆影像為 $8\times 8=64$ 維像素向量 $\mathbf{x}\in\mathbb{R}^{64}$，標籤
$y\in\{0,1\}$（3→0, 8→1）。切 80/20 訓練/測試。

## 2. 模型

\[
p(\mathbf{x}) = \sigma(\mathbf{w}^\top\mathbf{x}+b),\qquad
\sigma(z)=\frac{1}{1+e^{-z}}.
\]

## 3. 目標函數（與 sklearn `C=1` 一致）

以 $y'\in\{-1,+1\}$（$y'=2y-1$）寫 log-loss：

\[
J(\mathbf{w},b)=\frac12\|\mathbf{w}\|^2
+ C\sum_{i=1}^n \log\!\bigl(1+e^{-y'_i z_i}\bigr),\quad z_i=\mathbf{w}^\top\mathbf{x}_i+b.
\]

正則只作用在 $\mathbf{w}$，$b$ 不正則。

## 4. 推導

令 $p_i=\sigma(z_i)$。由 $\sigma'(z)=\sigma(z)(1-\sigma(z))$，

\[
\frac{\partial J}{\partial \mathbf{w}}
= \mathbf{w} + C\sum_i (p_i-y_i)\mathbf{x}_i
= \mathbf{w}+C\,\mathbf{X}^\top(\mathbf{p}-\mathbf{y}),
\]

\[
\frac{\partial J}{\partial b}
= C\sum_i (p_i-y_i).
\]

Hessian（Gauss-Newton）：

\[
\mathbf{H}_{\mathbf{ww}} = C\,\mathbf{X}^\top\operatorname{diag}\bigl(p_i(1-p_i)\bigr)\mathbf{X}+\mathbf{I},\quad
\mathbf{H}_{\mathbf{wb}} = C\,\mathbf{X}^\top\bigl(p_i(1-p_i)\bigr),\quad
H_{bb}=C\sum_i p_i(1-p_i).
\]

Newton 更新：

\[
\begin{bmatrix}\mathbf{w}\\ b\end{bmatrix}
\leftarrow
\begin{bmatrix}\mathbf{w}\\ b\end{bmatrix}
-
\mathbf{H}^{-1}
\begin{bmatrix}\nabla_{\mathbf{w}}J\\ \nabla_b J\end{bmatrix}.
\]

## 5. 實作

見 `logistic_digits.py`：`HandLogistic` 類別以 Newton (IRLS) 解上述系統，
收斂容差 `tol=1e-12`。

## 6. 與 sklearn 比較

| 指標 | 手刻 | sklearn (newton-cholesky, tol=1e-12) |
|---|---|---|
| 係數 max abs diff | $6.7\times10^{-14}$ | — |
| intercept diff | $2.6\times10^{-13}$ | — |
| 預測機率 max abs diff | $7.4\times10^{-14}$ | — |
| 測試準確率 | 1.0000 | 1.0000 |

- `np.allclose(coef, rtol=1e-10)` → True；`np.allclose(proba)` → True；預測標籤完全一致。
- 訓練集殘差 $\sum(p_i-y_i)\approx -9.5\times10^{-16}$、梯度範數 $\approx 5.6\times10^{-14}$，確認已到最優點。

sklearn 預設 (`lbfgs, tol=1e-4`) 會提早停，係數差 $\sim 5\times10^{-2}$、機率差 $\sim 2\times10^{-2}$，
但預測標籤與準確率仍相同。

## 7. 如何判斷兩個模型「一樣」

1. **最優點等價**：兩者的目標函數相同且都收斂到最優點（訓練殘差 $\sum(p_i-y_i)\approx 0$、梯度範數 $\approx 0$）。
2. **係數/截距**：`np.allclose(w1, w2, rtol=1e-8)` 且 intercept allclose。
3. **輸出等價**：測試集預測機率 `np.allclose(p1, p2, rtol=1e-8)`，以及 `np.array_equal(pred1, pred2)`。
4. **效能**：訓練/測試準確率相同。
5. **注意容差**：sklearn 預設 `tol=1e-4` 只是提早停，係數會差但決策不變；要「真正一樣」應把 `tol` 調緊或比較預測而非係數。切勿只看準確率（不同模型可同分），應同時看機率與係數。
