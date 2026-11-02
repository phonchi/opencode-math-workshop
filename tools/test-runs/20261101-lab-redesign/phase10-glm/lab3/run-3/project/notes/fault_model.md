# 產線故障預測模型筆記

## 資料
- `data/line_faults.csv`：900 筆，6 個感測特徵 + `fault` 標籤（正例 71 筆，約 7.9%）。
- `record_id` 只是編號，不當特徵。
- `data/line_modes.csv` 是未標記資料（723 筆），且分布和訓練資料有偏移（speed_rpm 到 2012，訓練資料最大 1676），直接套模型要小心。

## 方法
- 8:2 分層切 train/test，5-fold 交叉驗證。
- 比較 Logistic Regression（standardize + class_weight=balanced）與 Random Forest。

## 結果
| 模型 | CV AP | CV AUC |
|---|---|---|
| LogReg | 0.669 ± 0.113 | 0.954 |
| RandomForest | 0.473 ± 0.073 | 0.913 |

LogReg 較穩。RF 在 test set（AP=0.602）threshold 0.5 時：
- precision 0.714、recall 0.556（18 個故障抓到 10 個）。
- threshold 0.3 時 recall 升到 0.778，precision 掉到 0.538。

重要特徵：`temp_c`（最重要，重要性 0.44）、`vibration_mm_s`、`pressure_kpa`。

## 圖
- `figs/fault_pr_curve.png`：兩模型 PR 曲線。
- `figs/fault_importance.png`：RF 特徵重要性。

## 能不能上線？
**可以有限度上線，但不能全自動。**
- 正例太少（71 筆），CV AP 波動大（±0.11），估計不準。
- recall 只有 5–8 成，漏抓故障的代價高，建議用低 threshold（約 0.3）做「預警」而非自動停機。
- `line_modes.csv` 的操作區間超出訓練分布，新模式下需先收集標籤再重訓。
- 建議：上線時輸出機率分級（低/中/高風險），人員複核；持續累積標籤後重訓。
