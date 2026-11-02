# 產線故障預測模型評估報告

## 1. 資料概況與特性
- **資料來源**：`data/line_faults.csv`
- **樣本數**：900 筆紀錄
- **特徵欄位**：`temp_c`（溫度）、`vibration_mm_s`（振動）、`pressure_kpa`（壓力）、`flow_lpm`（流量）、`current_a`（電流）、`speed_rpm`（轉速）
- **標籤分佈**：
  - 正常 (`fault = 0`)：829 筆 (92.11%)
  - 故障 (`fault = 1`)：71 筆 (7.89%)
- **類別不平衡**：故障樣本比例約為 7.9%，屬於中度不平衡資料集。

---

## 2. 模型訓練與評估結果
我們採用了三種經典機器學習模型：**Logistic Regression (邏輯迴歸)**、**Random Forest (隨機森林)** 與 **Gradient Boosting (梯度提升樹)**。使用 5 折交叉驗證 (Stratified K-Fold) 與 80/20 保留測試集 (Holdout Test Set) 進行評估。

### 2.1 交叉驗證表現 (5-Fold CV)
- **Logistic Regression (具備 class_weight='balanced')**：
  - ROC-AUC: **0.9525**
  - F1-score: **0.5463**
  - Precision: **0.3885**
  - Recall: **0.9303**
- **Random Forest**：
  - ROC-AUC: **0.9303**
  - F1-score: **0.4943**
  - Precision: **0.5294**
  - Recall: **0.4864**
- **Gradient Boosting**：
  - ROC-AUC: **0.9345**
  - F1-score: **0.3687**
  - Precision: **0.5410**
  - Recall: **0.2939**

### 2.2 測試集表現 (Test Set, $N=180$)
- **Logistic Regression**：ROC-AUC = **0.9781**, F1 = **0.6047**, Precision = **0.4483**, Recall = **0.9286**
- **Random Forest**：ROC-AUC = **0.9348**, F1 = **0.5000**, Precision = **0.6000**, Recall = **0.4286**
- **Gradient Boosting**：ROC-AUC = **0.9380**, F1 = **0.5455**, Precision = **0.7500**, Recall = **0.4286**

---

## 3. 特徵重要性分析
透過隨機森林與邏輯迴歸的特徵權重分析，影響故障預測最重要的特徵依序為：
1. `temp_c`（溫度）：最具決定性的預測指標，溫度過高顯著增加故障機率。
2. `vibration_mm_s`（振動）：機械異常的重要表徵。
3. `pressure_kpa`（壓力）與 `speed_rpm`（轉速）。

---

## 4. 能不能上線用？（上線評估與建議）

### 結論：**可以進行「試運行（Shadow Mode / A-B Testing）」或「輔助預警」，但不建議直接進行完全自動化的硬性停機控制。**

### 原因分析：
1. **預測能力（ROC-AUC）優異**：
   模型的 ROC-AUC 達到 **0.95 ~ 0.97**，顯示模型在區分正常與故障狀態上具有極高的鑑別能力。
2. **召回率高（Recall > 92%）vs 誤報率（Precision ~ 45%）**：
   - 採用邏輯迴歸（調整權重後）的 **Recall 高達 92.86%**，能抓出絕大多數的潛在故障，非常適合工廠避免「漏報（漏掉故障導致產線損壞）」的風險。
   - 然而，其 **Precision 約 44.83%**，代表每發出兩次警報就有一次是誤報（False Positive）。若直接用於自動停機，會造成過多不必要的產線中斷。
3. **資料規模與代表性限制**：
   - 資料量偏小（僅 900 筆，其中故障僅 71 筆）。
   - 產線環境動態變化多，當前特徵可能未涵蓋所有極端工況（Edge Cases）。

### 建議落地策略：
1. **階段一：陰影模式（Shadow Mode）**
   將模型部署至系統背景運行，記錄其預警時間與實際故障的對應關係，不直接介入產線控制，藉此收集真實環境中的誤報與漏報數據。
2. **階段二：分級預警（Tiered Alerting）**
   - **黃色警戒（中低機率）**：通知維修人員進行設備巡檢（結合 `temp_c` 與 `vibration_mm_s` 檢查）。
   - **紅色警戒（高機率）**：建議排程維護或降載運行，避免無預警無預防的突發停機。
3. **持續優化**：
   隨著產線持續運作，累積更多樣本後定期重新訓練（Retraining），並引入更多即時監控特徵（如 `line_channels.csv` 的通道訊號）。
