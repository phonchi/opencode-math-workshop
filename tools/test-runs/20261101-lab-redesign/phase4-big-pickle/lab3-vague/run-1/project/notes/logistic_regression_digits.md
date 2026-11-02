# 手刻 Logistic Regression：digits 3 vs 8

這份筆記搭配 `logreg_digits.py`。目標是從最大概似估計（MLE）推導 logistic regression，用 NumPy 手刻最佳化，再和 `sklearn.linear_model.LogisticRegression` 對照，最後討論「怎麼判斷兩個模型一樣」。

## 1. 實驗設定

- 資料：`sklearn.datasets.load_digits()`，只取數字 3 與 8。
- 標籤：令 $y=1$ 代表數字 8，$y=0$ 代表數字 3。
- 特徵：64 維像素強度。用訓練集 fit `StandardScaler`，再套用到訓練集與測試集。
- 切分：`train_test_split(test_size=0.3, stratify=y, random_state=42)`。
- 規模：訓練 249 筆、測試 108 筆、特徵 64 維；訓練集中數字 8 的比例為 0.486。

標準化只改變參數化，不改變模型族。若把標準化後的係數換算回原始尺度，預測會完全一樣；因此跨前處理比較係數前，必須先做換算。

## 2. 模型

對第 $i$ 筆資料 $\mathbf{x}_i\in\mathbb{R}^d$，加入截距後 $\tilde{\mathbf{x}}_i=(1,\mathbf{x}_i^\top)^\top$，參數 $\mathbf{w}=(b,\mathbf{v}^\top)^\top$，其中 $b$ 是截距、$\mathbf{v}$ 是特徵權重。

定義線性分數（logit）

$$
z_i=\mathbf{w}^\top\tilde{\mathbf{x}}_i=b+\mathbf{v}^\top\mathbf{x}_i.
$$

用 sigmoid 把實數映射到機率：

$$
p_i=P(y_i=1\mid\mathbf{x}_i)=\sigma(z_i)=\frac{1}{1+e^{-z_i}}.
$$

等價地，

$$
\log\frac{p_i}{1-p_i}=z_i,
$$

所以 logistic regression 是「假設對數勝算（log odds）是 $\mathbf{x}$ 的線性函數」。決策邊界是 $z_i=0$，也就是 $p_i=0.5$。

## 3. 最大概似估計（MLE）

給定 $y_i\in\{0,1\}$，概似函數為

$$
P(y_i\mid\mathbf{x}_i)=p_i^{y_i}(1-p_i)^{1-y_i}.
$$

所有樣本獨立之下，

$$
L(\mathbf{w})=\prod_{i=1}^n p_i^{y_i}(1-p_i)^{1-y_i}.
$$

取負對數，得到 negative log-likelihood（NLL）：

$$
\operatorname{NLL}(\mathbf{w})
=-\sum_{i=1}^n\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
$$

利用 $\log p_i=-\log(1+e^{-z_i})$ 與 $\log(1-p_i)=-z_i-\log(1+e^{-z_i})$ 的整理，可寫成數值穩定的形式

$$
\ell_i(\mathbf{w})=\log(1+e^{z_i})-y_i z_i.
$$

本實作用平均 NLL，並加上 L2 懲罰（截距不懲罰）：

$$
J_\lambda(\mathbf{w})
=\frac{1}{n}\sum_{i=1}^n\left[\log(1+e^{z_i})-y_i z_i\right]
+\frac{\lambda}{2}\|\mathbf{v}\|_2^2.
$$

當 $\lambda=0$ 就是純 MLE。除以 $n$ 只是把損失尺度固定，最適解不變。

## 4. 梯度與 Hessian

先對 $z_i$ 微分：

$$
\frac{\partial \ell_i}{\partial z_i}
=\frac{e^{z_i}}{1+e^{z_i}}-y_i
=\sigma(z_i)-y_i
=p_i-y_i.
$$

因此對權重 $\mathbf{v}$ 與截距 $b$：

$$
\nabla_{\mathbf{v}}J_\lambda
=\frac{1}{n}\sum_{i=1}^n(p_i-y_i)\mathbf{x}_i+\lambda\mathbf{v},
\qquad
\frac{\partial J_\lambda}{\partial b}
=\frac{1}{n}\sum_{i=1}^n(p_i-y_i).
$$

用增廣矩陣 $X\in\mathbb{R}^{n\times(d+1)}$、$\mathbf{p}=(p_1,\dots,p_n)^\top$、$\mathbf{y}=(y_1,\dots,y_n)^\top$，可寫成

$$
\nabla J_\lambda
=\frac{1}{n}X^\top(\mathbf{p}-\mathbf{y})
+\lambda\begin{pmatrix}0\\ \mathbf{v}\end{pmatrix}.
$$

再微分一次。因為

$$
\frac{\partial p_i}{\partial z_i}=p_i(1-p_i),
$$

所以

$$
\nabla^2 J_\lambda
=\frac{1}{n}X^\top S X
+\lambda\begin{pmatrix}0&0\\0&I_d\end{pmatrix},
\qquad
S=\operatorname{diag}\bigl(p_1(1-p_1),\dots,p_n(1-p_n)\bigr).
$$

$S$ 是半正定，L2 懲罰也是半正定，所以 $J_\lambda$ 是凸函數。當 $\lambda>0$ 且資料有變異時，Hessian 正定，最適解唯一。當 $\lambda=0$ 時，若資料線性可分，NLL 的下確界是 0 但達不到，MLE 不存在（係數會趨向無窮大）。

## 5. 最佳化

### 5.1 梯度下降（GD）

$$
\mathbf{w}_{t+1}
=\mathbf{w}_t-\eta\nabla J_\lambda(\mathbf{w}_t).
$$

GD 每步只用到一階梯度，收斂是線性的；步長 $\eta$ 太大會震盪，太小會很慢。本實作先把特徵標準化，再用 $\eta=1.0$。

### 5.2 Newton / IRLS

對 $J_\lambda$ 在 $\mathbf{w}_t$ 做二次近似：

$$
J_\lambda(\mathbf{w}_t+\Delta)
\approx J_\lambda(\mathbf{w}_t)
+\nabla J_\lambda^\top\Delta
+\frac{1}{2}\Delta^\top\nabla^2J_\lambda\Delta.
$$

對 $\Delta$ 微分設為零，得到 Newton 方向

$$
\nabla^2J_\lambda\,\Delta=-\nabla J_\lambda
\quad\Longrightarrow\quad
\Delta=-(\nabla^2J_\lambda)^{-1}\nabla J_\lambda,
$$

更新為

$$
\mathbf{w}_{t+1}=\mathbf{w}_t-\left(\nabla^2J_\lambda\right)^{-1}\nabla J_\lambda.
$$

因為目標函數凸，Newton 法在附近有二次收斂；本實作加上 backtracking line search，確保每次更新都讓目標函數下降。實測 Newton 約 9 步就到達梯度範數 $3.3\times10^{-15}$，GD 則需要 5896 步才到 $10^{-12}$。

## 6. 和 sklearn 的正則化對應

`sklearn.linear_model.LogisticRegression` 的 L2 目標函數（`solver='lbfgs'`、`fit_intercept=True`）可寫成

$$
J_{\text{sk}}
=\frac{1}{2}\|\mathbf{v}\|_2^2
+C\sum_{i=1}^n\ell_i(\mathbf{w}),
$$

截距不懲罰。兩邊同除以 $nC$：

$$
\frac{1}{nC}J_{\text{sk}}
=\frac{1}{2nC}\|\mathbf{v}\|_2^2
+\frac{1}{n}\sum_{i=1}^n\ell_i(\mathbf{w}).
$$

和本實作的 $J_\lambda$ 比較，得到

$$
\boxed{\lambda=\frac{1}{nC}}.
$$

因此：

- 要和 sklearn 預設 `C=1.0` 對照，手刻模型取 $\lambda=1/(n\cdot 1)$。
- 要和無正則化 MLE 對照，取 $\lambda=0$，sklearn 則取 `C=np.inf`。
- 若懲罰的是平均損失而不是總損失，係數對應會不同；這是最常見的「看起來一樣但其實正則化強度不同」陷阱。

本實驗的數字：

| 比較 | `max abs Δw` | `max abs Δp`（test） | 預測不同 | 判定 |
|---|---:|---:|---:|---|
| L2, `C=1`（主對照） | $2.39\times10^{-7}$ | $1.47\times10^{-7}$ | 0/108 | 數值上同一個模型 |
| 手刻 GD 解 L2 vs sklearn | $2.39\times10^{-7}$ | $1.47\times10^{-7}$ | 0/108 | 同一個最適解 |
| PCA 3 維、無正則化 MLE | $3.29\times10^{-9}$ | $4.54\times10^{-9}$ | 0/108 | 同一個 MLE |
| 64 維、無正則化 MLE | $1.42\times10^{1}$ | $1.00$ | 3/108 | 不可比較（MLE 不存在） |

L2 主對照的目標函數值：手刻 $0.031575885023$，sklearn $0.031575885023$，差距 $2.05\times10^{-15}$。測試集兩者都是 108/108 正確。

## 7. 為什麼無正則化的 64 維版本對不上？

這不是實作錯，而是問題本身沒有唯一解。3 與 8 在 64 維像素空間中線性可分，訓練集可以被完全切開，於是 NLL 的下確界 0 可以任意逼近但達不到。不同最佳化器會在係數不同的地方停下來：

- 手刻 Newton：$\|\mathbf{v}\|=45.28$，訓練 NLL $6.0\times10^{-13}$。
- sklearn lbfgs：$\|\mathbf{v}\|=30.66$，訓練 NLL $1.6\times10^{-12}$。

兩者的訓練損失都幾乎是 0，也都完美分開訓練集，但係數與測試預測不同（3/108 筆不同）。在線性可分資料上，談「唯一的 MLE」沒有意義；必須加正則化、降維，或改用其他有唯一解的估計方式。

為了單獨驗證 $\lambda=0$ 的實作，我額外用 PCA 降到 3 維，讓資料不再線性可分，此時 MLE 存在。手刻與 sklearn 的係數差距 $3.29\times10^{-9}$、機率差距 $4.54\times10^{-9}$，預測 0/108 不同，測試準確率同為 0.9630。

## 8. 怎麼判斷兩個模型「一樣」？

### 8.1 先確認是同一個數學問題

以下任一項不同，就不該期待係數一樣：

- 資料切分、隨機種子、標籤定義（$y=1$ 是 3 還是 8）。
- 特徵前處理（原始像素、標準化、PCA）。
- 是否含截距。
- 損失函數與正則化（L1/L2/無）、正則化強度（`C` 與 $\lambda$ 的換算）。
- 類別權重、最佳化容忍度。

如果標籤定義相反，係數會整體變號；如果特徵做過標準化，係數要換算：

$$
\mathbf{v}_{\text{raw}}=\frac{\mathbf{v}_{\text{std}}}{\boldsymbol{\sigma}},
\qquad
b_{\text{raw}}=b_{\text{std}}-\sum_{j=1}^d\frac{v_{\text{std},j}\,\mu_j}{\sigma_j}.
$$

換算後再比，才有意義。

### 8.2 數值等價：比「預測」比「係數」更可靠

建議依序檢查：

1. **平穩條件**：$\|\nabla J(\mathbf{w})\|$ 是否接近 0。若沒有，模型根本還沒收斂。
2. **目標函數值**：$|J_{\text{hand}}-J_{\text{sk}}|$ 是否在浮點誤差等級。
3. **預測差異**：在同一份資料上比較
   $$
   \max_i|\Delta z_i|,\qquad
   \max_i|\Delta p_i|,\qquad
   \#\{i:\hat y_i^{\text{hand}}\ne\hat y_i^{\text{sk}}\}.
   $$
   這是最不受參數化影響的判準。實務上可用例如 $\max|\Delta p|<10^{-6}$ 且標籤差異 0 筆，當作「數值上同一個模型」。
4. **係數差異**：只有在模型可辨識、且兩邊參數化相同時才有意義。係數尺度可能很大，建議同時看絕對差與相對差。若資料線性可分或模型有對稱性，係數不唯一，係數差不能拿來判定對錯。

本實驗的 L2 對照在 $\max|\Delta p|=1.47\times10^{-7}$、標籤差異 0/108、目標函數差 $2\times10^{-15}$ 的水準，因此可以說手刻實作與 sklearn 解的是同一個最佳化問題，且都收斂到同一個最適解（在最佳化器容忍度內）。

### 8.3 統計等價：如果要比「表現一樣」

如果是不同訓練樣本、不同初始化，或只是要主張兩個模型泛化表現相同，不能只看準確率小數點後幾位。應該：

- 報告測試指標的信賴區間（bootstrap）。
- 對同一批測試樣本用 McNemar 檢定比較預測是否配對不同。
- 對 AUC 用 DeLong 檢定或 bootstrap。
- 比較 log-loss 與機率校準，而不只比 0/1 預測。
- 事先定義「實務上可接受」的容差；不同應用對 $\Delta p$ 的容忍度不同。

「準確率一樣」不代表模型一樣；反過來，「係數不同」也不代表預測不同。判斷時要把「同一個數學模型」、「同一個最適解」、「統計表現等價」三件事分開。

## 9. 圖

![收斂曲線](../figs/logreg_convergence.png)

![係數與測試機率對照](../figs/logreg_coef_compare.png)

![PCA 投影下的決策邊界](../figs/logreg_pca_boundary.png)

注意最後一張圖只是把 64 維線性邊界投影到前兩個主成分，並把其他主成分固定在平均值，屬於視覺化近似，不是完整的 2D 邊界。

## 10. 重現方式

```bash
uv run python logreg_digits.py
```

腳本會印出上方所有比較數字，並把三張圖存到 `figs/`。
