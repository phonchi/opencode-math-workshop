# 產線故障預測模型筆記

## 資料
- `data/line_faults.csv`：900 筆、6 個感測特徵、`fault` 標籤。
- 類別極度不平衡：故障 71 筆（約 7.9%）、正常 829 筆。
- 無缺失值；`record_id` 不作為特徵。

## 作法
- `RandomForestClassifier(n_estimators=500, class_weight="balanced")`
- 8:2 分層切分 train/test（test 225 筆），train 上做 5-fold 分層 CV。
- 程式碼：`train_fault_model.py`；圖：`figs/fault_model_eval.png`

## 結果
- CV ROC-AUC：$0.913 \pm 0.026$，CV average precision：$0.468 \pm 0.069$
- Holdout（threshold = 0.5）：故障類 precision 0.714、recall 0.556；漏掉 18 筆故障中的 8 筆。
- 重要特徵：以 `vibration_mm_s`、`temp_c` 為主（見 feature importance 圖）。

## Threshold 取捨（holdout）
| threshold | precision | recall | 警報數 |
|---|---|---|---|
| 0.2 | 0.357 | 0.833 | 42 |
| 0.3 | 0.519 | 0.778 | 27 |
| 0.5 | 0.714 | 0.556 | 14 |

## 上線結論
**可以「輔助監控」上線，不建議全自動停機。**
- 優點：AUC 0.91 顯示訊號確實存在，低 threshold 時可抓到 8 成故障。
- 限制：樣本太少（故障僅 71 筆），precision-recall 波動大；每 100 次警報約 3~5 成是誤報（依 threshold 而定）。
- 建議：threshold 設 0.3 左右當預警（recall 0.78），警報交由人員複查；累積更多標籤後再重新訓練、評估是否升級為自動停機。
