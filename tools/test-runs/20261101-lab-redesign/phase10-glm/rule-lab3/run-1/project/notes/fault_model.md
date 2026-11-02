# 產線故障預測模型筆記

## 資料
- `data/line_faults.csv`：900 筆、6 個感測特徵（temp_c、vibration_mm_s、pressure_kpa、flow_lpm、current_a、speed_rpm）、標籤 `fault`。
- 正例（故障）僅 71 筆（7.9%），屬高度不平衡資料。無缺失值。
- `record_id` 已移除，不當特徵。

## 模型
- RandomForest（400 棵，`class_weight="balanced"`），5-fold stratified CV。
- 75/25 分層切分 train/test，`random_state=42`。

## 結果
- CV：ROC-AUC 0.913 ± 0.027，AP 0.473 ± 0.073，recall 0.41、precision 0.45。
- Holdout（threshold=0.295）：故障 recall 0.78、precision 0.50，AP 0.602。
- 重要特徵：temp_c（0.44）> vibration（0.19）> pressure（0.12）。

## 能不能上線？
- **看用途**：若作為「警示/預警工具」（召回故障約 78%，代價是誤報約 7%），勉強可用於輔助人力，**不建議完全自動停機**。
- 主要風險：AP 偏低且 CV 變異大（±0.07），故障樣本太少，模型不夠穩。
- 建議先以 shadow mode 跑一段時間驗證；若能蒐集更多故障樣本或加入其他特徵（如 line_channels.csv / line_modes.csv 若可對齊），再考慮正式上線。

## 圖
- `figs/fault_model_eval.png`：PR curve 與特徵重要度。
