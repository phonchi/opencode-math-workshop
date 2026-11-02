# 手刻 Logistic 迴歸（digits 3 vs 8）：推導、驗證與「兩個模型怎麼算一樣」

程式：`logistic_digits38.py`；圖：`figs/logistic_digits38_comparison.png`。

## 1. 問題設定

- 資料：`sklearn.datasets.load_digits`，只取 3 和 8，共 $n_{total}=357$ 張 $8\times 8$ 影像，像素值 $0\sim16$。
- 前處理：$x \leftarrow x/16 \in [0,1]$（**兩邊用同一份縮放後資料**，這是「規格相同」的一部分）。
- 標籤：$y=1$ 代表數字 8（正類），$y=0$ 代表數字 3。
- 切分：`train_test_split(test_size=0.25, random_state=42, stratify=y)` → 267 訓練 / 90 測試。
- 把 bias 併進參數：$\tilde{x}=(x,1)\in\mathbb{R}^{65}$，$\theta=(w,b)$，$w\in\mathbb{R}^{64}$。
- 有 10 個像素恆為 0（邊框），會讓 Hessian 奇異（後面 Newton 用最小範數解處理）。

## 2. 模型與推導

### 2.1 模型

假設 $y\mid x \sim \text{Bernoulli}$，成功機率用線性函數過 sigmoid：

$$
P(y=1\mid x)=\hat{p}=\sigma(z),\qquad z=w^\top x+b,\qquad \sigma(z)=\frac{1}{1+e^{-z}} .
$$

### 2.2 從最大概似推出交叉熵

單一樣本的概似與對數概似：

$$
P(y_i\mid x_i;\theta)=\hat{p}_i^{\,y_i}(1-\hat{p}_i)^{1-y_i},
\qquad
\log P = y_i\log\hat{p}_i+(1-y_i)\log(1-\hat{p}_i).
$$

全體資料的對數概似是各項相加；最大概似（MLE）等價於最小化「負對數概似」，取平均即二元交叉熵（BCE）：

$$
\ell(\theta)=-\frac{1}{n}\sum_{i=1}^n\Big[y_i\log\hat{p}_i+(1-y_i)\log(1-\hat{p}_i)\Big].
$$

### 2.3 梯度

對單一樣本用鏈鎖法則。先備兩條：

$$
\frac{\partial \hat{p}_i}{\partial z_i}=\hat{p}_i(1-\hat{p}_i),\qquad
\frac{\partial z_i}{\partial w}=x_i .
$$

對 $\hat p_i$ 微分 BCE 的單項：

$$
\frac{\partial \ell_i}{\partial \hat{p}_i}=-\frac{y_i}{\hat{p}_i}+\frac{1-y_i}{1-\hat{p}_i}.
$$

兩者相乘（sigmoid 的導數剛好把分母清乾淨）：

$$
\frac{\partial \ell_i}{\partial z_i}
=\Big(-\frac{y_i}{\hat{p}_i}+\frac{1-y_i}{1-\hat{p}_i}\Big)\hat{p}_i(1-\hat{p}_i)
=-(1-y_i)\hat{p}_i+y_i(1-\hat{p}_i)
=\hat{p}_i-y_i .
$$

堆疊成矩陣形式（$\hat{y}=\sigma(Xw+b\,\mathbf{1})$）：

$$
\nabla_w \ell=\frac{1}{n}X^\top(\hat{y}-y),
\qquad
\frac{\partial \ell}{\partial b}=\frac{1}{n}\mathbf{1}^\top(\hat{y}-y).
$$

**殘差形式 $\hat p - y$ 就是 logistic 迴歸好算又好手刻的原因。**

### 2.4 Hessian 與凸性

$$
\nabla^2\ell=\frac{1}{n}X^\top\operatorname{diag}\big(\hat{p}_i(1-\hat{p}_i)\big)X\succeq 0 .
$$

所以 BCE 是凸函數；若 $X$ 的行滿秩（沒有常數/零特徵、且加了正則），則**嚴格凸、最小解唯一**。這一條是後面「怎麼判斷兩個模型一樣」的理論核心。

## 3. 兩個手刻求解器

### 3.1 梯度下降

$$
\theta_{k+1}=\theta_k-\eta\nabla\ell(\theta_k).
$$

因為 $\hat p_i(1-\hat p_i)\le 1/4$，梯度是 Lipschitz 的，常數

$$
L=\frac{\lambda_{\max}(X^\top X)}{4n}+\lambda
\quad\Rightarrow\quad
\eta=\frac{1}{L}\ \text{保證收斂}.
$$

實驗中 $\eta=1/L$ 跑了 72,769 次迭代到 $\|\nabla\|<10^{-9}$。

### 3.2 Newton 法（＝IRLS）

$$
\theta_{k+1}=\theta_k-\big(\nabla^2\ell(\theta_k)\big)^{-1}\nabla\ell(\theta_k).
$$

二次收斂，8 次迭代就到 $\|\nabla\|\sim10^{-12}$。因為有 10 個全 0 特徵，Hessian 奇異，程式用 `np.linalg.lstsq` 取最小範數解（零方向上參數不動）。另加回溯線搜尋保險。

## 4. Phase A：先踩一次陷阱——可分離資料沒有 MLE

把 sklearn 設成 `C=np.inf`（無正則）與自己的無正則 Newton 比較，結果：

| | train loss | $\lVert\theta\rVert$ | test acc | test logloss | test AUC |
|---|---|---|---|---|---|
| 手刻 Newton（無正則） | $1.0\times10^{-12}$ | **1611** | 0.9667 | **0.885** | 0.981 |
| sklearn（C=inf） | $1.2\times10^{-10}$ | **93.6** | 0.9889 | 0.0177 | 1.000 |

- 訓練集在 64 維裡是**線性可分離**的（loss 可以壓到 $\sim10^{-12}$）。此時無正則化的 MLE **不存在**：$w$ 沿「最大間隔方向」趨近無窮大，loss 趨近 0 但沒有有限的最優點。
- 兩個 solver 只是停在同一條發散路徑上的不同位置：係數相對誤差 $1.7\times10^{1}$、$\max_i|\Delta p_i|=1.0$、硬預測不一致 2.2%。
- 更有趣的是 Newton 跑得比較「遠」，係數很大 → 機率過度自信 → 一張測試錯樣本的 logloss 就把整體炸到 0.885。**train loss 比較小，模型反而更差。**
- 教訓：最佳解不存在時，「兩個模型一樣嗎」是偽命題，先確認解存在再談。

## 5. Phase B：給兩邊完全相同的目標（L2 正則的對應關係）

sklearn `LogisticRegression(penalty='l2', C=C)` 實際最小化（$y'\in\{-1,+1\}$、intercept 不正則）：

$$
O(w,b)=\frac{1}{2}\lVert w\rVert^2+C\sum_{i=1}^n\log\!\big(1+e^{-z_i'}\big),\qquad z_i'=(2y_i-1)(w^\top x_i+b).
$$

其中 $\log(1+e^{-z'})$ 就是我們的 BCE 單項（換底恆等式），所以 $O$ 與 BCE 只差「sum vs mean、係數擺哪」。目標乘正常數不變 minimizer，兩邊同除 $Cn$：

$$
\frac{O}{Cn}
=\underbrace{\frac{1}{n}\sum_i \mathrm{BCE}_i}_{\text{我的 }\ell}
+\frac{\lambda}{2}\lVert w\rVert^2,
\qquad
\boxed{\lambda=\frac{1}{C\,n}} .
$$

$C=1$、$n=267$ → $\lambda=3.745\times10^{-3}$，bias 不正則。加了 $\frac{\lambda}{2}\lVert w\rVert^2$ 之後目標是**強凸**的，解唯一。

### Phase B 結果

| | train loss | $\lVert\nabla\rVert$ | test acc | test logloss | test AUC |
|---|---|---|---|---|---|
| 手刻 GD | 0.1101270 | $1.0\times10^{-9}$ | 0.9778 | 0.077503 | 1.000 |
| 手刻 Newton | 0.1101270 | $1.7\times10^{-15}$ | 0.9778 | 0.077503 | 1.000 |
| sklearn（lbfgs, C=1） | 0.1101270 | $2.4\times10^{-8}$ | 0.9778 | 0.077503 | 1.000 |

一致度（相對於 sklearn）：

| | 相對係數誤差 | $\max\lvert\Delta\theta\rvert$ | $\max_i\lvert\Delta p_i\rvert$（測試集） | 硬預測不一致 |
|---|---|---|---|---|
| GD | $3.4\times10^{-7}$ | $8.6\times10^{-7}$ | $1.6\times10^{-7}$ | 0 |
| Newton | $5.3\times10^{-7}$ | $2.4\times10^{-6}$ | $1.7\times10^{-7}$ | 0 |

關鍵交叉驗證：把 **sklearn 的解**代進**我寫的目標函數**，梯度範數 $=2.4\times10^{-8}\approx 0$。即：sklearn 解的正是我寫的這個問題，而且兩邊都站在同一個唯一最優點上。誤差停在 $10^{-7}$ 級是因為 lbfgs 的收斂容差與浮點順序，屬正常現象。

## 6. 怎麼判斷兩個模型「一樣」？

建議按三層檢查，缺一不可：

**第一層：規格相同（先決條件）**
- 同一份訓練資料、同一組特徵與縮放。
- 同一個 loss（BCE）、同一種正則化與強度、是否正則 bias。
- 同一參數化與類別編碼方向：sklearn 的 `coef_` 對應 `classes_[1]`（這裡是 8），自寫時 $y=1$ 也要定義成 8，否則符號整個相反、係數看起來「差很多」其實只是鏡像。
- **最容易踩的雷：sklearn 用 sum、自寫常用 mean**，強度要換算 $\lambda = 1/(C n)$，不然正則強度差了 $n$ 倍。

**第二層：解存在且唯一（理論保證）**
- 目標強凸（L2 正則 + 滿秩）→ 全域最優解唯一 → 「兩邊都收斂到全域最優」就**必然**是同一個模型，係數吻合不是巧合而是必然。
- 反例即 Phase A：可分離資料 + 無正則 → 解不存在 → 無從比較，任何「誤差」都只是停在不同位置。

**第三層：數值驗證（由強到弱）**
1. 交叉最優性：把對方的解代入自己的目標函數算梯度，$\lVert\nabla\rVert\approx0$（本例 $2.4\times10^{-8}$）——這是最強的證據，證明「對方在解我的問題，而且解到了」。
2. 係數：相對誤差 $\lVert\theta_1-\theta_2\rVert/\lVert\theta_2\rVert$（本例 $\sim5\times10^{-7}$）。
3. 預測機率：$\max_i\lvert p_1(x_i)-p_2(x_i)\rvert$（本例 $\sim1.7\times10^{-7}$）——比看指標嚴格，比看硬標籤有意義（機率一樣，硬標籤才會一樣）。
4. 硬預測不一致率 $=0$，且 accuracy / logloss / AUC 完全相同。
5. 訓練目標值收斂到同一個數（本例 0.1101270）。

**實務注意**
- 不同 optimizer（lbfgs vs GD/Newton）、不同停止條件、不同浮點加總順序，不可能位元級相同；$10^{-5}\sim10^{-6}$ 的相對誤差就算「同一個模型」。
- 比較前先確認 sklearn 自己有收斂：看 `n_iter_`、有沒有 ConvergenceWarning，必要時調大 `max_iter`、縮小 `tol`。sklearn 沒收斂時係數會不同，但若離最優不遠，預測可能看起來差不多——這正是為什麼要同時檢查第三層的 1–3 項而不是只看 acc。
- 純看「accuracy 一樣」**不能**說兩個模型一樣：Phase A 裡兩個係數差 17 倍的模型 accuracy 也只差一點點。

## 7. 檔案

- `logistic_digits38.py`：Phase A/B 全流程，重跑 `uv run python logistic_digits38.py` 可重現所有數字。
- `figs/logistic_digits38_comparison.png`：GD 收斂曲線、測試集機率散佈圖（貼 $y=x$）、係數散佈圖（貼 $y=x$）。
