# 逾期預測模型評估

## 資料
- `data/loans.csv`：900 筆、71 筆逾期（7.9%），類別不平衡。
- `case_no` 為借閱編號/ID，不可作為特徵；若納入可達 AUC 0.999 / 準確率 0.993，屬資料洩漏。
- `past_ontime_pct` 有一筆 101.0，訓練前需裁切至 100。

## 模型（排除 case_no）
- Logistic Regression（class_weight=balanced），5-fold CV：
  - AUC 0.959、Average Precision 0.711
  - threshold=0.5：precision 0.406、recall 0.915、F1 0.563
  - 混淆矩陣：TP 65、FP 95、FN 6、TN 734

## 是否可上線
- 不建議直接自動決策上線。
- 可先作為「高風險借閱排序/提醒」輔助工具；逾期捕捉率高，但誤報率高（約 60% 預測逾期為誤報）。
- 上線前需：補足逾期樣本、依時間切分驗證、處理 ID 洩漏與資料品質、校準機率與閾值、監控資料漂移。
