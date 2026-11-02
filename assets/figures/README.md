# 工作坊教學圖

以 `starter/.venv/bin/python tools/make_figs.py --out assets/figures --evidence-dir tools/test-runs/20261101-lab-redesign/figures` 重建。資料由 `tools/make_line_data.py` 產生，是講師設計的合成資料。

- **line-preview**：`line_modes.csv` 前 40 筆標準化後的熱圖，只示意資料樣貌。
- **lab1-k-selection**：原始尺度與標準化各掃 k=2..12（random_state=0、n_init=10）的 silhouette，以及揭曉後與 10 個批次比對的 ARI。

結果只適用於這份資料，不代表其他資料有相同排序。
