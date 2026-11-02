# digits 3 vs 8：手刻 Logistic Regression

## 1. 理論推導

### 模型
對二元分類，我們想預測 $y \in \{0,1\}$。
定義線性組合：
$$
z = \theta_0 + \theta_1 x_1 + \cdots + \theta_n x_n = \mathbf{\theta}^T \mathbf{x}_b,\quad \mathbf{x}_b = [1, x_1, \ldots, x_n]^T
$$

透過 Sigmoid 函數將 $z$ 映射到 $(0,1)$：
$$
h_\theta(\mathbf{x}) = \sigma(z) = \frac{1}{1 + e^{-z}}, \quad \sigma'(z)=\sigma(z)(1-\sigma(z))
$$

決策規則（預設閾值 0.5）：
$$
\hat{y} = \begin{cases}
1, & h_\theta(\mathbf{x}) \ge 0.5\\
0, & otherwise
\end{cases}
\iff z \ge 0
$$

### 損失函數（Binary Cross Entropy）
對單一樣本：
$$
L(h_\theta(\mathbf{x}), y) = -\bigl[y \log h_\theta(\mathbf{x}) + (1-y)\log (1-h_\theta(\mathbf{x}))\bigr]
$$

整體代價函數（平均）：
$$
J(\theta) = -\frac{1}{m}\sum_{i=1}^{m}\bigl[y^{(i)} \log h^{(i)} + (1-y^{(i)})\log (1-h^{(i)})\bigr], \quad h^{(i)}=\sigma(\theta^T x_b^{(i)})
$$

### 梯度推導
計算 $\frac{\partial J}{\partial \theta_j}$：
$$
\frac{\partial J}{\partial \theta_j} = \frac{1}{m}\sum_{i=1}^{m} (h^{(i)} - y^{(i)}) x_j^{(i)}
$$

向量形式：
$$
\nabla_\theta J = \frac{1}{m} X_b^T (h - y), \quad h=\sigma(X_b \theta)
$$

### 梯度下降更新
$$
\theta := \theta - \alpha \nabla_\theta J
$$

## 2. 實作結果（digits 3 vs 8）

- 篩選條件：$y \in \{3,8\}$，轉換為 $y'=1$ 若 $y==8$，否則 $0$（$y==3$）
- 前處理：每個特徵標準化 $(x - \mu)/\sigma$，加入 bias 項
- 手刻：梯度下降（learning rate 0.1，最多 20000 次，tol=1e-7）
- sklearn：`LogisticRegression(solver='lbfgs', max_iter=10000)`

結果：
- 手刻 Logistic Regression 準確率：1.000000
- sklearn LogisticRegression 準確率：1.000000
- 手刻 $\theta = [\theta_0, \theta_1,\ldots]$ 前幾項不同於 sklearn 的 $[\text{intercept}, \text{coef}]$（見執行輸出）

## 3. 為何參數不同卻預測相同？

Logistic Regression 的決策邊界由 $z = \theta^T x_b = 0$ 決定。若將整個 $\theta$ 乘上任意正數 $c > 0$：
$$
(c\theta)^T x_b = c (\theta^T x_b) = 0 \iff \theta^T x_b = 0
$$
決策邊界完全相同，預測結果也相同。

此外：
- 優化器不同（手刻梯度下降 vs L-BFGS）會找到不同的「最小化 $J$」解，尤其當資料**線性可分**時，$J$ 沒有唯一的有限最小值——任何足夠大的 $\|\theta\|$ 都能讓 $J \to 0$，梯度下降會沿著能達成可分的方向不斷放大參數直到收斂條件或迭代上限。
- 正則化不同：sklearn 預設是 $L_2$ 正則化（`penalty='l2', C=1.0`），手刻實作中並**沒有**加正則項。這會導致參數尺度不同。
- 數值精度、初始化（手刻全零）等也會影響收斂路徑。

因此「模型一樣」不該用參數逐項比對，而要用**決策行為**比對。

## 4. 如何判斷兩個模型一樣？

建議用以下方式驗證（由強到弱）：

1. **預測一致性（最直接）**  
   比較 `predict` 結果：$\hat{y}_{scratch} == \hat{y}_{sklearn}$ 全部相等，且準確率相同。
   ```python
   np.allclose(y_pred_scratch, y_pred_sk)
   ```

2. **決策函數一致性**  
   比較 $z = \theta^T x_b$ 的符號，或比較預測機率：  
   - $z_{scratch}$ 與 $z_{sklearn}$ 的符號是否全部相同（$\text{sign}(z_1)=\text{sign}(z_2)$）  
   - 或 $\text{corr}(\sigma(z_{scratch}), \sigma(z_{sklearn})) \approx 1$，且 $|\sigma(z_1)-\sigma(z_2)|$ 很小  
   注意：若決策邊界相同但參數有正比例關係，$\sigma(z_1), \sigma(z_2)$ 不一定逐點相同，但分類結果相同。

3. **決策邊界等價**  
   檢查是否存在 $c > 0$ 使得 $\theta_{scratch} \approx c\, \theta_{sklearn}'$（將 sklearn 的 intercept+coef 對齊成同一向量形式）。也可以用正規化後的方向比較：  
   $\frac{\theta_{scratch}}{\|\theta_{scratch}\|} \approx \frac{\theta_{sklearn}'}{\|\theta_{sklearn}'\|}$。

4. **在訓練集外測試**  
   最關鍵：用測試集（或交叉驗證）看預測是否完全一致。

**結論**：對本例來說，兩個模型的決策行為完全一致（預測完全相同、準確率皆 1.0），因此可以說「在分類行為上等價」，即使參數向量不相等。
