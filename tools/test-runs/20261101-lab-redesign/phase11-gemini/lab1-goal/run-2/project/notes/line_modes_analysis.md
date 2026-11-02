# 產線感測讀數分群分析筆記

## 決定事項 (Decisions Made)
1. **特徵標準化 (Feature Scaling)**: 使用 `StandardScaler` 將 8 個感測器特徵進行標準化，避免不同特徵尺度差異（如溫度、壓力、轉速等）影響距離計算。
2. **分群演算法 (Clustering Algorithm)**: 採用 `KMeans` 演算法，設定 `random_state=42` 以確保結果可重現。
3. **評估指標 (Evaluation Metrics)**: 
   - **Silhouette Score**: 評估分群凝聚度與分離度。
   - **Adjusted Rand Index (ARI)**: 以 `data/line_modes_batches.csv` 的真實 10 批次標籤作為稽核標準，評估分群結果與真實批次的一致性。
4. **目標導向選擇**: 結合使用者的核心需求（追蹤批次、不同批次不能合併、已知總計 10 批），以 ARI 作為最終決策的核心依據。

## 實驗結果 (Results)
- **$k = 9$**:
  - Silhouette Score = `0.7943`
  - ARI = `0.8811`
- **$k = 10$**:
  - Silhouette Score = `0.7252`
  - ARI = `0.9902`

## 結論 (Conclusion)
雖然 $k=9$ 的 Silhouette 稍高，但 $k=10$ 的 ARI 高達 `0.9902`（幾乎完全對應真實 10 批次）。由於用途要求「不同批次不能合併」，必須確保每群對應一個獨立批次，因此**應使用 $k = 10$**。
