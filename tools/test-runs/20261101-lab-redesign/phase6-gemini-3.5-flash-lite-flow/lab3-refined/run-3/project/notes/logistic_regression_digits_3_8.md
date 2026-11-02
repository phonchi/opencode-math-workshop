# 手刻 Logistic 迴歸：以 Digits 資料集（數字 3 與 8）為例

本篇筆記記錄如何使用 NumPy 從零開始手刻實作 Logistic 迴歸（Logistic Regression），並以 Scikit-learn 的 `load_digits` 資料集中的數字 `3` 與 `8` 進行二元分類訓練與推導。內容包含完整的數學推導、Python 程式碼實作、與 `sklearn` 模型的對比，以及如何嚴謹地確認兩個模型是否完全一致。

---

## 一、 問題定義與資料準備

我們從 `sklearn.datasets.load_digits` 載入手寫數字資料集。每個樣本是一張 $8 \times 8$ 像素的灰階圖片，展開後為維度 $d = 64$ 的特徵向量 $x \in \mathbb{R}^{64}$。

我們篩選出標籤為 `3` 與 `8` 的樣本進行二元分類任務：
- 令標籤 $y^{(i)} = 1$ 代表數字 `8`。
- 令標籤 $y^{(i)} = 0$ 代表數字 `3`。

---

## 二、 Logistic 迴歸的數學模型與推導

### 1. 假設函數 (Hypothesis Function)

Logistic 迴歸透過 **Sigmoid 函數** 將線性組合 $z = w^T x + b$ 映射到 $(0, 1)$ 之間，代表樣本屬於正類別 ($y=1$) 的機率 $\hat{y}$：

$$z = w^T x + b = \sum_{j=1}^{d} w_j x_j + b$$

$$\hat{y} = h_w,b(x) = \sigma(z) = \frac{1}{1 + e^{-z}}$$

其中 $\sigma(z)$ 的導數具有一個非常優美的性質：

$$\frac{d\sigma(z)}{dz} = \sigma(z)(1 - \sigma(z)) = \sigma(z) - \sigma(z)^2$$

### 2. 成本函數 (Cost Function / Binary Cross-Entropy Loss)

給定 $m$ 個訓練樣本 $(x^{(i)}, y^{(i)}0$，利用最大似然估計法 (Maximum Likelihood Estimation, MLE) 可以推導出二元交叉熵損失函數（含選配的 L2 正規化項）：

$$J(w, b) = -\frac{1}{m} \sum_{i=1}^{m} \left[ y^{(i)} \log(\hat{y}^{(i)}) + (1 - y^{(i)}) \log(1 - \hat{y}^{(i)}) \right] + \frac{\lambda}{2m} \|w\|^2$$

其中 $\lambda$ 為 L2 正規化係數（對應於 sklearn 中 `C` 的倒數 $\frac{1}{C}$）。

### 3. 梯度推導 (Gradient Derivation)

我們需要計算成本函數 $J(w, b)$ 對權重向量 $w$ 與偏權值 $b$ 的偏微分。

首先計算損失對線性組合 $z^{(i)} = w^T x^{(i)} + b$ 的梯度：
$$\frac{\partial J}{\partial z^{(i)}} = \frac{\partial J}{\partial \hat{y}^{(i)}} \cdot \frac{\partial \hat{y}^{(i)}}{\partial z^{(i)}}$$

其中：
$$\frac{\partial J}{\partial \hat{y}^{(i)}} = -\frac{y^{(i)}}{\hat{y}^{(i)}} + \frac{1 - y^{(i)}}{1 - \hat{y}^{(i)}} = \frac{\hat{y}^{(i)} - y^{(i)}}{\hat{y}^{(i)}(1 - \hat{y}^{(i)})}$$

$$\frac{\partial \hat{y}^{(i)}}{\partial z^{(i)}} = \sigma(z^{(i)})(1 - \sigma(z^{(i)})) = \hat{y}^{(i)}(1 - \hat{y}^{(i)})$$

相乘後簡化得到：
$$\frac{\partial J}{\partial z^{(i)}} = \hat{y}^{(i)} - y^{(i)}$$

接著利用鏈鎖律（Chain Rule）求得對 $w_j$ 與 $b$ 的梯度：

$$\frac{\partial J}{\partial w_j} = \frac{1}{m} \sum_{i=1}^{m} (\hat{y}^{(i)} - y^{(i)}) x_j^{(i)} + \frac{\lambda}{m} w_j$$

寫成矩陣向量形式：
$$\nabla_w J = \frac{1}{m} X^T (\hat{y} - y) + \frac{\lambda}{m} w$$

$$\frac{\partial J}{\partial b} = \frac{1}{m} \sum_{i=1}^{m} (\hat{y}^{(i)} - y^{(i)})$$

---

## 三、 手刻實作與 SciPy 最佳化

為了與 `sklearn` 的 `LogisticRegression`（預設使用 L-BFGS 演算法）達到高精度的權重吻合，我們使用 `scipy.optimize.minimize` 來最小化我們的 Loss 函數，同時也支援傳統的批次梯度下降法 (Gradient Descent)。

---

## 四、 如何判斷兩個模型一樣？

要確認我們手刻的 Logistic 迴歸模型與 Scikit-learn 的模型完全一樣，可以從以下幾個維度進行嚴格檢驗：

1. **模型參數的數值一致性 (Weights & Bias Check)**：
   - 檢查權重向量 $w$ 的最大絕對誤差 ($\max |w_{\text{custom}} - w_{\text{sklearn}}|_2$) 是否小於極小閾值（如 $10^{-4}$ 或 $10^{-5}$）。
   - 檢查截距 $b$ 是否高度接近。
2. **預測機率的一致性 (Predicted Probabilities Check)**：
   - 將相同的測試集輸入兩模型，計算預測機率 $\hat{y}$ 的均方誤差 (MSE) 或最大絕對差異。
3. **預測類別與準確率一致性 (Predictions & Accuracy Check)**：
   - 決策閾值設為 $0.5$ 時，二元分類的預測標籤 (`predict`) 應完全一致，混淆矩陣與 Accuracy 應相同。
4. **決策邊界與特徵重要性視覺化 (Decision Boundary / Coefficient Heatmap)**：
   - 將 $8 \times 8$ 的權重向量 $w$ 繪製成熱力圖 (Heatmap)，觀察兩者學到的特徵權重空間分佈是否一致（例如數字 3 與 8 的特徵對比）。
