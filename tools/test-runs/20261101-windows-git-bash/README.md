# Windows Git Bash 實測（2026-11-01）

環境：繁中 Windows（OEM code page 950）、OpenCode 1.19.5、Windows PowerShell 5.1、Git for Windows 2.54.0。
腳本在 `probes/`。除 `probe*.ps1` 走 `opencode serve` 的 shell API 外，`gb2.ps1`、`gb4.ps1` 在實際 mintty 視窗操作 TUI。

| 項目 | 結果 |
|---|---|
| PowerShell 下的 `!` | OpenCode 以 `powershell.EXE -NoProfile` 執行；輸出 big5，錯誤訊息亂碼 |
| `opencode-windows-encoding@5.0.0` | 有載入，Shell 模式沒有處理紀錄，未改善 |
| `chcp 65001`、`"shell":"cmd"` | 無效 |
| 從 Git Bash 啟動、不設定 `shell` | 自動使用 bash，`ls -la` 正常 |
| OpenCode TUI 在 mintty | 可啟動；Ctrl+V 可貼上中文 |
| Git Bash 提示字元貼上 | Ctrl+V、Shift+Insert 都可用 |
| Git Bash，未設 `PYTHONUTF8` | `uv run python` 印中文仍亂碼（cp950） |
| Git Bash ＋ `PYTHONUTF8=1`（以 `export` 設定） | TUI `!` 與提示字元都印出「中文」 |
| Git Bash 內 `winget --version`、`setx` | 可用（只跑版本查詢與暫時變數，已刪除） |

## 講師手動驗收（2026-11-01）
講師回報：依教材步驟設定 `setx PYTHONUTF8 1` 並重開 Git Bash 後，在 OpenCode 內由 AI 以 `bash` 工具執行並核准 `uv run python -c "print(chr(0x4e2d)+chr(0x6587))"`，印出「中文」。

## 未實測
- 乾淨 Windows 上從官方 exe 安裝 Git。
- macOS 的 Git 安裝流程。

後續 Windows 安裝改用官方腳本，實測見 `tools/test-runs/20261101-git-bash-no-winget/README.md`。
