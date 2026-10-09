# 工作坊教學圖

以 `starter/.venv/bin/python tools/make_figs.py --out assets/figures --evidence-dir tools/test-runs/20261009-site-refine/figures` 重建。
套件版本、資料與來源 hash、實際指令、參數及逐列核對結果見 `provenance.json` 與 evidence 目錄的 `run.log`。三組圖皆提供桌機與 `-mobile` 手機版 PNG／SVG，兩版使用相同資料。手機版以較少刻度和較大字呈現；digits 改為兩列五張。原始資料附於同目錄。

- **digits-samples**：digits 資料集每個標籤的第一筆樣本；索引從 0 開始，記於 JSON。這是輸入資料示意，並非模型產生的影像。顯示範圍固定為 0 到 16。
- **lab1-k-selection**：未縮放的 1797×64 原始像素，k=2..12、random_state=0、n_init=10；上下兩圖分別呈現群內距離平方和與 silhouette。全資料、每次分群標籤及指標均保存。9 是本次搜尋的 silhouette 最高值；10 是數字標籤數，兩者回答不同問題。這不保證其他版本、初始化或資料有相同排序。
- **lab3-gradient-error**：既有範例表的七個步長，線只連接資料點。門檻為最大絕對誤差 1e-8；沒有補入 1e-8 步長的資料，也沒有重新訓練或執行梯度檢查。這是 historical displayed example，不是新跑的 Lab 3 結果；誤差趨勢不能當成所有函數或資料的通則。

英文字軸避免依賴額外字型；圖說可沿用以上繁體中文說明。Lab 3 原表節錄與全部圖的 montage 存於 evidence 目錄。
