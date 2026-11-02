# 產線感測資料 PCA 主成分與故障監控 AUC 評估筆記

## 實驗目的
比較 3、4、5 個主成分 ($k=3, 4, 5$) 在故障監控中的辨識表現（AUC）。嚴格遵照前處理 (`StandardScaler`) 與降維 (`PCA`) 僅在各訓練折（Training fold）進行擬合的交叉驗證規範。

## 資料與方法
- 資料集：`data/line_channels.csv` (感測資料) 與 `data/line_channels_fault.csv` (故障標籤)。
- 交叉驗證：10 折分層交叉驗證（$10$-fold Stratified CV）。
- 模型/指標：
  1. Logistic Regression 於主成分分數（PC scores）上的預測 AUC。
  2. Hotelling's $T^2$ 統計量異常檢測 AUC。

## 實驗結果

### 1. 解釋變異數比例（Explained Variance Ratio）
- $k=3$：累積解釋變異數比例為 $69.02\%$
- $k=4$：累積解釋變異數比例為 $83.88\%$
- $k=5$：累積解釋變異數比例為 $92.95\%$

### 2. 交叉驗證 AUC 表現
- **Logistic Regression / Random Forest 於主成分分數**：
  - $k = 3$：$\text{AUC} \approx 0.51$
  - $k = 4$：$\text{AUC} = 1.0000 \pm 0.0000$
  - $k = 5$：$\text{AUC} = 1.0000 \pm 0.0000$
- **Hotelling's $T^2$ 統計量**：
  - $k = 3$：$\text{AUC} = 0.6450 \pm 0.0796$
  - $k = 4$：$\text{AUC} = 0.9804 \pm 0.0195$
  - $k = 5$：$\text{AUC} = 0.9694 \pm 0.0255$

## 結論
當主成分數 $k=4$ 時：
1. 分類器故障辨識 AUC 達到 $1.0000$，與 $k=5$ 完全相同（無顯著差異）。
2. Hotelling's $T^2$ 監控 AUC 達到 $0.9804$，甚至略高於 $k=5$（$0.9694$）。
3. 4 個主成分已足以完整捕捉故障特徵，且並未明顯低於 5 個主成分。

因此，**「4 個主成分就夠」的主張成立**。
