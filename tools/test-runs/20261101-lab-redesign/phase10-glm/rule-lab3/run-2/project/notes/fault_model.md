# 產線故障預測模型筆記

## 資料
- `data/line_faults.csv`：900 筆、6 個感測特徵、正例（fault=1）僅 71 筆（7.9%），無缺失值。
- `record_id` 僅為編號，訓練時移除。
- 檢視過 `data/line_channels.csv`（11 通道感測、無標籤）與 `data/line_modes.csv`（firmware_ver、sample_period_s 全為常數），對訓練沒有幫助，未使用。

## 方法
- 5-fold Stratified CV（out-of-fold 評估），比較 LogisticRegression（標準化 + class_weight=balanced）與 RandomForest。
- 因故障偵測漏報代價高，threshold 以 recall ≥ 0.9 為前提挑 precision 最高者。

## 結果（out-of-fold）
| 模型 | PR-AUC | ROC-AUC |
|---|---|---|
| LogisticRegression | **0.711** | **0.959** |
| RandomForest | 0.544 | 0.935 |

最佳模型：LogisticRegression，threshold ≈ 0.56
- TP=65、FP=84、FN=6、TN=745
- recall = 0.915、precision = 0.436、誤報率 ≈ 10%

## 結論：可以小規模上線（輔助警報），不建議全自動停機
- recall 0.92 代表約 92% 的故障可被提前抓到，但 precision 0.44 代表每抓到 1 次真故障會伴隨約 1.3 次誤報（整體誤報率約 10%）。
- 適合當「預警系統」提醒人員巡檢；若誤報成本高，可調高 threshold 換較低誤報（但漏報會增加）。

## 圖
- `figs/pr_curve.png`、`figs/feature_importance.png`

## 改善方向
- 正例只有 71 筆，收集更多故障樣本最能提升 precision。
- 可加入時間序列特徵（滑動窗均值/變化率），目前只用了單點快照。
