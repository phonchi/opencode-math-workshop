# 產線感測資料 PCA 主成分數與故障監控 AUC 評估筆記

## 實驗設定
- **資料來源**：`data/line_channels.csv`（產線感測資料）與 `data/line_channels_fault.csv`（故障標籤，僅用於評估）。
- **交叉驗證**：採用 5 折交叉驗證（StratifiedKFold）。
- **前處理與 PCA**：標準化（StandardScaler）與主成分分析（PCA）嚴格僅在每一折的訓練集（Training Fold）進行擬合（Fit），再對測試集（Test Fold）進行轉換（Transform）。
- **評估指標**：故障辨識 AUC（Area Under ROC Curve），涵蓋非監督式監控指標（Hotelling's $T^2$ 統計量）以及監督式分類器（Logistic Regression 預測機率）。

## 實驗結果
- **$K = 3$**：
  - Hotelling's $T^2$ AUC：$0.4551 \pm 0.0854$
  - Logistic Regression AUC：$0.5659 \pm 0.0977$
- **$K = 4$**：
  - Hotelling's $T^2$ AUC：$0.9797 \pm 0.0180$
  - Logistic Regression AUC：$1.0000 \pm 0.0000$
- **$K = 5$**：
  - Hotelling's $T^2$ AUC：$0.9716 \pm 0.0181$
  - Logistic Regression AUC：$1.0000 \pm 0.0000$

## 結論
在 $K = 4$ 時，無論是以 Hotelling's $T^2$ 進行非監督式故障監控，或以羅吉斯迴歸（Logistic Regression）進行故障辨識，AUC 皆已達到非常高的水準（$T^2$ 達 $0.98$、分類器達 $1.00$）。
且相較於 $K = 5$，$K = 4$ 的 AUC 並無明顯偏低（甚至略高於 $K = 5$ 或維持相同高水準）。因此，主張 **4 個主成分就夠** 的說法**成立**。
