# Logistic 迴歸理論推導與 Digits (3與8) 專案筆記

## 1. 數學推導 (Mathematical Derivation)

Logistic 迴歸（Logistic Regression）是一種廣義線性模型（Generalized Linear Model），用於處理二元分類問題（Binary Classification）。

### 1.1 模型假設與 Sigmoid 函數
給定特徵向量 $\mathbf{x} \in \mathbb{R}^d$ 與偏置（Bias） $b \in \mathbb{R}$（或將其擴展為權重向量 $\mathbf{w}$ 包含截距），線性組合為：
$$z = \mathbf{w}^T \mathbf{x} + b$$

為了將線性組合的值對應到 $[0, 1]$ 之間作為機率，我們使用 Sigmoid 函數（Logistic 函數） $\sigma(z)$：
$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

模型預測正類（例如標籤 $y=1$，在此專案中代表數字 8）的條件機率為：
$$\hat{y} = P(y=1 | \mathbf{x}; \mathbf{w}, b) = \sigma(\mathbf{w}^T \mathbf{x} + b)$$
而預測負類（$y=0$，數字 3）的機率為：
$$P(y=0 | \mathbf{x}; \mathbf{w}, b) = 1 - \hat{y}$$

### 1.2 似然函數與對數似然函數 (Likelihood & Log-Likelihood)
假設樣本集 $\{(\mathbf{x}_i, y_i)\}_{i=1}^N$ 獨立同分佈（I.I.D.），其概率分佈（伯努利分佈）為：
$$P(y_i | \mathbf{x}_i; \mathbf{w}, b) = \hat{y}_i^{y_i} (1 - \hat{y}_i)^{1 - y_i}$$

整個訓練集的似然函數（Likelihood）為：
$$L(\mathbf{w}, b) = \prod_{i=1}^N \hat{y}_i^{y_i} (1 - \hat{y}_i)^{1 - y_i}$$

取自然對數得到對數似然函數（Log-Likelihood）：
$$\ell(\mathbf{w}, b) = \ln L(\mathbf{w}, b) = \sum_{i=1}^N \left[ y_i \ln \hat{y}_i + (1 - y_i) \ln (1 - \hat{y}_i) \right]$$

### 1.3 成本函數 (Cost Function / Cross-Entropy Loss)
機器學習中習慣最小化損失函數（Loss Function），因此定義平均二元交叉熵損失（Binary Cross-Entropy Loss）：
$$J(\mathbf{w}, b) = -\frac{1}{N} \ell(\mathbf{w}, b) = -\frac{1}{N} \sum_{i=1}^N \left[ y_i \ln \hat{y}_i + (1 - y_i) \ln (1 - \hat{y}_i) \right]$$

### 1.4 梯度下降法 (Gradient Descent)
為了尋找最佳的 $\mathbf{w}$ 與 $b$ 使得成本函數 $J(\mathbf{w}, b)$ 最小化，我們計算成本函數對 $\mathbf{w}$ 和 $b$ 的偏導數。

令 $\hat{y}_i = \sigma(z_i)$ 且 $z_i = \mathbf{w}^T \mathbf{x}_i + b$。
根據鏈鎖律（Chain Rule）：
$$\frac{\partial J}{\partial \mathbf{w}} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i) \mathbf{x}_i$$
$$\frac{\partial J}{\partial b} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)$$

更新規則（Gradient Descent Update）：
$$\mathbf{w} \leftarrow \mathbf{w} - \alpha \frac{\partial J}{\partial \mathbf{w}}$$
$$b \leftarrow b - \alpha \frac{\partial J}{\partial b}$$
其中 $\alpha$ 為學習率（Learning Rate）。

---

## 2. 如何判斷手刻模型與 sklearn 模型一樣？

要確認手刻模型（Scratch Implementation）與 `sklearn.linear_model.LogisticRegression` 完全一致，可以從以下幾個維度進行檢驗：

1. **參數權重與截距一致性 ($\mathbf{w}$ 與 $b$)**：
   - 當兩者使用相同的優化目標（例如：無正則化 `penalty=None` 或極大 $C$ 值，且無 L1/L2 懲罰項），其訓練出的權重向量 $\mathbf{w}$ 與截距 $b$ 應該極為接近（數值誤差在 $\approx 10^{-4}$ 或更小以內）。
2. **預測機率一致性 ($\hat{y}$)**：
   - 對於同一組測試資料 $\mathbf{X}_{\text{test}}$，兩者計算出的預測機率 $P(y=1|\mathbf{X})$ 差異（如最大絕對誤差或均方根誤差）應接近 0。
3. **預測分類結果一致性**：
   - 在相同決策閾值（通常為 0.5）下，預測出的類別標籤（0 與 1）準確率（Accuracy）與混淆矩陣（Confusion Matrix）應完全相同。
4. **損失函數數值**：
   - 在訓練結束時，兩者在訓練集上的交叉熵損失（Cross-Entropy Loss）應收斂至相同數值。
