# GitHub Copilot Auto 實跑（Windows Git Bash，2026-11-11）

環境：Windows 11、Git Bash、OpenCode v2.2.7。講師在互動 TUI 以 `/connect` → GitHub Copilot 裝置登入。`opencode models` 列出 `github-copilot/auto` 與 14 個可手選模型（講師帳號的方案沒有核對）。腳本由 WSL 經 `bash.exe -l -c` 呼叫，prompt 與 `20261111-v2-windows/prompts/run_prompts.sh` 相同，只改成 `-m github-copilot/auto` 並加上 `</dev/null`。

## 結果

| 項目 | 結果 | 證據 |
|---|---|---|
| `1+1` 試跑 | Auto 挑 `gpt-6-luna`，3 秒，cost 0.000046 美元 | `probe-auto.jsonl` |
| 第二輪全套（重啟背景服務後） | 6 步全部 rc=0，約 5.5 分鐘；34 個請求，0.0821 美元＝**8.2 credits**；Auto 挑 `gpt-6.1-terra` 21 次、`gpt-6-luna` 13 次 | `run-2-fresh-service/`、`usage.txt` |
| 第二輪品質 | Lab 2 錯誤表抓到 4 種錯；Lab 3 列 5 個門檻、不替人選；三關都列出替使用者做的決定 | `run-2-fresh-service/*.log` |
| 第一輪（舊背景服務） | Lab 1～Lab 2 AUC 正常；`lab2-hand` 兩次停在 `patch` 工具（DB 狀態 `running`，session busy），殺 client 後服務端仍 busy、服務 CPU 滿一核；`opencode service restart` 後 CPU 回到 0 | `run-1-stalled/` |
| 同 prompt、Temp 以外、`--standalone` | patch 正常，52 秒完成 | `repro-patch-on/` |
| 同上，加 `"plugins": ["-opencode.tool.patch"]` | 模型改用 `← Write`，39 秒完成，檢查全 PASS；狀態列外掛仍載入 | `repro-patch-off/` |

花費取自 session DB（`session_message.data.cost`，v2.2.7 起為 Copilot 實際收費），統計腳本 `copilot_usage.py`。

## 踩到的坑
- `opencode run` 在 stdin 不是終端機時會等 EOF；從腳本呼叫要加 `</dev/null`，否則卡住不動。
- 新資料夾第一次啟動時，Copilot 模型清單可能還沒載入，`-m github-copilot/auto` 回 `Model unavailable`；腳本加了等待與重試。
- 殺掉 `opencode run` client 不會停止服務端正在執行的工具。
- 第一輪卡住的確切原因沒有查明：第二次可能是在等第一次留下的檔案鎖（Astra 讀原始碼的推論）；重啟服務後同一步沒有再卡。

## 未測
- Copilot Free／Student 帳號（Auto 的候選模型可能不同）。
- 互動 TUI 中按 Esc 能否停止卡住的工具。
