# 新版 prompt 實測：原生 Windows、OpenCode v2.2.7、big-pickle（2026-11-11）

`run_prompts.sh` 在 Git Bash 執行，每輪從乾淨學生專案開始，依教材順序 `opencode run --auto` 各步 prompt（`-c` 表示接續上一段）。揭曉檔在對應步驟前才放進 `data/`。各步完整輸出在 `run-1/`、`run-2/`，耗時在 `progress.log`。

注意：這兩輪用的是審閱前的 prompt 版本。之後依審閱改過的地方有：Lab 2 標籤說明改成「不要放進 PCA，只用來訓練分類器和算 AUC」；Lab 1 切回 Build 時的範圍收小句；參考 prompt 補上 W 的形狀。

| 步驟 | run-1 | run-2 | 結果 |
|---|---|---|---|
| Lab 1 參考 prompt | 220 s | 173 s | 兩輪都比較 silhouette／CH／DB，A 答 9、B 答 10，並列出決定；沒有讀店別檔 |
| Lab 1 店別核對（`-c`） | 60 s | 58 s | 兩輪都算出 k=10 ARI 0.990、只有 3 天分錯，維持原建議 |
| Lab 2 AUC | 78 s | 91 s | 3／4／5 個主成分 AUC 約 0.53–0.59／1.000／1.000；撤回條件不成立，沒改主張 |
| Lab 2 手刻＋驗證 | 145 s | 554 s | 自己寫 8／10 項檢查，全部 PASS，印出數值與門檻 |
| Lab 2 錯誤表（`-c`） | 702 s | 1154 s | 兩輪都抓到全部 4 種錯誤；正交檢查整列 PASS。run-2 有 3 次 `Timed out waiting for response headers` 重試 |
| Lab 3 門檻表 | 90 s | 144 s | 兩輪都列五個門檻、沒有替我們選；run-1 自己決定把超過 40 封的截到前 40 高 |

教學上的觀察：
- Lab 2 錯誤表那一步耗時最長，教材已提醒「常常超過 10 分鐘，等的時候先讀參考結果」。
- run-1 的 Lab 3 自己加了「截到前 40 高」的規則，是「它替你做的決定」的好例子。
- Plan 模式問答（另見 `../tui/lab1-plan-grill-screen.txt`）約 6 分鐘，它列出的計畫比 Lab 1 需要的大，教材因此加了收小範圍的句子。
