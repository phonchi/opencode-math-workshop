# Windows 不靠 winget 安裝（2026-11-01）

環境：繁中 Windows、Git for Windows 2.54.0、OpenCode 1.19.5、uv 0.13.6。先以 winget 移除 opencode 與 uv，再於 Git Bash 執行官方安裝腳本。

| 安裝前動作 | 結果 |
|---|---|
| 無設定檔 | opencode 腳本回報 `No config file found`；重開後找不到 `opencode`，uv 正常（`install.log`） |
| `touch ~/.bashrc` | uv 另建 `.profile`，登入 shell 不讀 `.bashrc`，找不到 `opencode`（`variants.log`） |
| `touch ~/.bash_profile` | 兩者都找得到，沒有 Git Bash 警告（`variants.log`） |

`install-with-bashrc.log` 的 `uv NOT FOUND` 是測試造成的假象：安裝用的 shell 已帶上一輪 PATH，uv 腳本因此略過設定。

## 完整流程（`flow.log`、`flow-tui.png`）
以 explorer 開啟 `git-bash.exe`（MINGW64），操作皆在 mintty 視窗：`uv sync`、`setx PYTHONUTF8 1`、重開後變數為 1、匯入全部套件並印出「環境 OK」、OpenCode TUI 以 `!` 跑 `uv`、`which` 與 Python 中文、`opencode run` 取得回應。

## `PYTHONUTF8`（`last-checks-2.log`）
Git Bash 視窗直接輸出時，未設定也能顯示中文。輸出經過管線（OpenCode 接收輸出的方式）時，未設定為 cp950，設定後為 UTF-8，所以教材保留 `setx PYTHONUTF8 1`。

## 補救指令（`last-checks-2.log`）
模擬忘記先 `touch`、只有 `.profile` 的家目錄，追加 `PATH` 到 `~/.bash_profile` 後，`opencode` 與 `uv` 都找得到。

## 講師手動驗收（2026-11-01）
講師回報：在官方腳本安裝、使用者層級 `PYTHONUTF8=1` 的環境下，從 Git Bash 啟動 OpenCode，由 AI 以 `bash` 工具執行並核准 `uv run python -c "print(chr(0x4e2d)+chr(0x6587))"`，印出「中文」。

## Ctrl+V 貼上
講師手動操作時，在 `git-bash.exe` 視窗的 OpenCode 按 `Ctrl+V` 貼不上，標題變成 `Windows PowerShell`。讀 1.19.5 執行檔：`Ctrl+V` 先啟動 `powershell.exe` 查圖片，再呼叫 `fallbacks/windows/clipboard_${an}.exe` 讀文字，錯誤被吞掉；執行檔內找不到 `clipboard_x86_64`（工具缺失為推論，未直接執行驗證）。

講師加上 `KeyFunctions=C+v:paste` 與 `ShootFoot=on`（mintty 官方文件的寫法）到 `~/.minttyrc` 並重開後回報：`Ctrl+V` 可以貼上。先前以 SendKeys 模擬可貼上的原因未完全釐清，模擬按鍵的結果不能代表實體按鍵。

## 未實測
- 乾淨 Windows 上從官方 exe 安裝 Git。
- 全新帳號；本機已有 uv 下載的 Python 與快取。
