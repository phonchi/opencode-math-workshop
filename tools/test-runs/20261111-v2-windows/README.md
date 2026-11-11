# OpenCode V2 在原生 Windows（Git Bash）的實測 — 2026-11-11

環境：Windows 11、Git for Windows 的 Git Bash（由 WSL 呼叫 `C:\Program Files\Git\bin\bash.exe -l`，互動部分在 Herdr 分頁內執行 Windows 版 opencode），OpenCode v2.2.7，模型 opencode/big-pickle。使用者的全域 `~/.config/opencode/cli.json` 已啟用 `@rashidrazak/opencode-status-line`。

## 結果
| 項目 | 結果 | 證據 |
|---|---|---|
| `touch ~/.bash_profile` + `curl -fsSL https://opencode.ai/v2/install \| bash`（隔離 HOME） | 成功，安裝到 `~/.opencode/bin/opencode.exe`，PATH 寫進 `.bash_profile`，另附 `opencode2.cmd` | `install/run.log` |
| 學生專案：下載三份 CSV、`uv sync`（含 pandas 3.1.1）、測試一 | `環境 OK` | `project-setup/run.log` |
| V1 寫法的 `opencode.json`（`permission`、`agent.plan.permission`） | V2 讀得懂，`opencode debug config` 顯示自動轉成 `permissions`／`agents` | `project-setup/run.log` |
| 測試二 `opencode run "…主成分分析"` | 繁中一句話回答 | `selftest/run.log` |
| 測試三不加 `--auto` | 自動拒絕，訊息改為 `This non-interactive run cannot ask the user for permission, so the request was rejected.` | `selftest/no-auto-full.log` |
| 測試三加 `--auto` | 寫 hello.py、`uv run python hello.py`，約 15 秒 | `selftest/run.log` |
| 切換 Build/Plan | **Shift+Tab**（底部提示 `shift+tab agents`）；`Tab` 沒有作用 | 互動 |
| 斜線指令 | `/new`、`/models`、`/connect`、`/sessions`、`/exit`、`/init`、`/editor` 都在；外掛提供 `/tps` | 互動 |
| `/new` | 在畫面頂端開一個新的 session 分頁 | 互動 |
| 權限對話框 | `△ Permission required`，選項 `Allow once  Always allow  Reject`；Reject 後這一輪中斷 | 互動 |
| Esc | 第一次顯示 `esc again to interrupt`，第二次才中斷 | 互動 |
| `!` Shell 模式 | 可用，底部 `esc exit shell mode` | 互動 |
| 快捷鍵 | `ctrl+x n` 新 session、`ctrl+x l` 切換、`ctrl+x c` 壓縮、`ctrl+x e` 編輯器、`ctrl+j` 換行、`ctrl+p` 指令面板 | 互動 |
| `@AGENT` 補檔名 | 補成 AGENTS.md | 互動 |
| 側邊欄／底部 | 右側 `Context … % used`；底部 `6.4K (3%)`；status-line 另起一行顯示 context、cache、速度、經過時間 | 互動 |
| Plan 模式 + AGENTS.md 一次一題規則 | big-pickle 用 V2 的選單一次問一題、附建議答案，問 3 題後列計畫與「我打算替你做的決定」；全程約 6 分鐘。它一開始把 723 列誤認為 723 家店，第二題才由學生糾正 | `tui/lab1-plan-grill-screen.txt` |
| Plan 模式要求執行 ls | 改用讀檔工具列出檔案，沒有用 shell | 互動 |
| `/connect` Google、NVIDIA；`/models` 搜 flash lite | 選單與 V1 相同，有 Gemini 3.5 Flash Lite | 互動 |

## 未測
- macOS。
- 全新 Windows 帳號從零安裝 Git for Windows（本機已裝）。
- 全班同時使用的免費額度。

## 狀態列外掛（補充）
- 課前頁那段 `mkdir -p ~/.config/opencode` + `cat > ~/.config/opencode/cli.json <<'EOF'` 在 Git Bash 執行正常（`statusline/run.log`）。
- Windows 版 `opencode.exe` 讀的是 `USERPROFILE` 底下的 `.config/opencode`，不跟著 Git Bash 改寫的 `HOME` 走：把暫存 HOME 的 cli.json 改成空清單，`opencode plugin list` 仍列出外掛。學生的 Git Bash 預設 `~` 就是 `C:\Users\<名字>`，兩者一致。
- 使用者實際的 `C:\Users\User\.config\opencode\cli.json` 只有這一個外掛；互動時 `/tps` 與底部狀態列都出現，外掛版本 1.2.0。
