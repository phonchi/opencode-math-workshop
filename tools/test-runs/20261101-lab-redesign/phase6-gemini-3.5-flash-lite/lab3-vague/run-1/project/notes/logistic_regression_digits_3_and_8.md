# Digits 3 與 8 之 Logistic 迴歸手刻實作與數學推導

本筆記記錄使用 scikit-learn 的 `digits` 資料集（僅取數字 3 與 8）進行二元分類的 Logistic 迴歸手刻實作、完整數學推導，以及與 `sklearn.linear_model.LogisticRegression` 的對比驗證方法。

---

## 一、 數學推導 (Mathematical Derivation)

### 1. 模型設定 (Model Formulation)
給定特徵向量 $x \in \mathbb{R}^d$，我們加入偏置項（bias）$b$，並定義擴增特徵向量 $\tilde{x} = [1, x^T]^T \in \mathbb{R}^{d+1}$ 以及擴增權重向量 $w = [b, w_1, w_2, \dots, w_d]^T \in \mathbb{R}^{d+1}$。

Logistic 迴歸利用 Sigmoid 函數將線性組合 $z = w^T \tilde{x}$ 對應到 $(0, 1)$ 區間，代表樣本屬於正類（$y=1$，在此例中為數字 8）的預測機率 $\hat{y}$：

$$\hat{y} = \sigma(z) = \frac{1}{1 + e^{-z}} = \frac{1}{1 + e^{-w^T \tilde{x}}}$$

其中 Sigmoid 函數具有以下重要性質（便於求導）：
$$\sigma'(z) = \sigma(z)(1 - \sigma(z)) = \hat{y}(1 - \hat{y})$$

### 2. 損失函數 (Cost / Loss Function)
對於 $N$ 個樣本 $(x^{(1)}, y^{(1)}), (x^{(2)}, y^{(2)}), \dots, (x^{(N)}, y^{(N)})$，其中標籤 $y^{(i)} \in \{0, 1\}$，我們使用二元交叉熵損失（Binary Cross Entropy Loss / Log Loss）：

$$L(w) = -\frac{1}{N} \sum_{i=1}^N \left[ y^{(i)} \log(\hat{y}^{(i)}) + (1 - y^{(i)}) \log(1 - \hat{y}^{(i)}) \right]$$

### 3. 梯度推導 (Gradient Derivation)
我們希望透過梯度下降法最小化損失函數 $L(w)$。根據鏈鎖律（Chain Rule），損失函數對權重向量 $w$ 的梯度為：

$$\nabla_w L(w) = \frac{\partial L}{\partial w} = \frac{\partial L}{\partial \hat{y}} \cdot \frac{\partial \hat{y}}{\partial z} \cdot \frac{\partial z}{\partial w}$$

逐項計算：
1. **損失對預測機率的偏微分**：
   $$\frac{\partial L}{\partial \hat{y}} = -\frac{1}{N} \sum_{i=1}^N \left( \frac{y^{(i)}}{\hat{y}^{(i)}} - \frac{1 - y^{(i)}}{1 - \hat{y}^{(i)}} \right) = -\frac{1}{N} \sum_{i=1}^N \frac{y^{(i)} - \hat{y}^{(i)}}{\hat{y}^{(i)}(1 - \hat{y}^{(i)})}$$

2. **預測機率對線性組合 $z$ 的偏微分**：
   $$\frac{\partial \hat{y}}{\partial z} = \hat{y}(1 - \hat{y})$$

3. **線性組合 $z$ 對權重 $w$ 的偏微分**：
   $$\frac{\partial z}{\partial w} = \tilde{x}$$

將三者相乘並加總（以矩陣形式表示）：
$$\nabla_w L(w) = \frac{1}{N} \tilde{X}^T (\hat{y} - y)$$

其中：
- $\tilde{X} \in \mathbb{R}^{N \times (d+1)}$ 是包含截距項（第一欄為全 1）的設計矩陣。
- $\hat{y} \in \mathbb{R}^{N}$ 是預測機率向量。
- $y \in \mathbb{R}^{N}$ 是真實標籤向量。

### 4. 最佳化更新 (Gradient Descent Update)
透過梯度下降法，反覆更新權重：
$$w^{(t+1)} = w^{(t)} - \alpha \nabla_w L(w^{(t)})$$
其中 $\alpha$ 為學習率（learning rate）。

---

## 二、 如何判斷手刻模型與 sklearn 模型「一樣」？

要確認手刻的 Logistic 迴歸與 `sklearn.linear_model.LogisticRegression` 模型完全一致，需從以下四個維度進行嚴格檢驗：

1. **參數對齊（Weights & Bias Alignment）**：
   - 確保 sklearn 模型設定為**無正則化**（`penalty=None` 或 `C=1e10`）且不使用額外懲罰項。
   - 比較兩者的權重向量 $w$ 與偏置 $b$：計算歐式距離 $\|w_{\text{hand}} - w_{\text{sklearn}}\|_2 < \epsilon$（當優化收斂時，數值誤差應小於 $10^{-4}$ 甚至更低）。

2. **預測機率一致性（Predicted Probabilities）**：
   - 對同一組測試集輸入 $X_{\text{test}}$，計算兩者輸出的預測機率 $\hat{y}_{\text{hand}}$ 與 $\hat{y}_{\text{sklearn}}$。
   - 檢驗最大絕對誤差 $\max(|\hat{y}_{\text{hand}} - \hat{y}_{\text{sklearn}}|) < 10^{-4}$。

3. **預測分類與指標一致性（Predictions & Metrics）**：
   - 以 $0.5$ 為閾值轉換為二元類別，兩者的預測標籤、準確率（Accuracy）、精確率、召回率與 F1-score 必須完全相同。

4. **損失函數值一致性（Loss Value）**：
   - 在相同資料集上計算的 Log Loss 數值應當對齊（小數點後四位以上相同）。
