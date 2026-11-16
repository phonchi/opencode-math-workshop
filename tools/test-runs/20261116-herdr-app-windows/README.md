# Herdr 桌面 app 在 Windows 的實測 — 2026-11-16

目的：驗證 `content/herdr.md` 的 Windows 步驟。用 herdr-core 的 `hc`（由 WSL 呼叫 Windows 版 `hc.exe`）在講師既有的 core 開背景終端機，不操作 GUI。

- 環境：Windows，herdr-app 0.1.15、hc 0.1.20。
- 講師的 `%APPDATA%\herdr-core\config.toml` 已有 `shell = ['C:\Program Files\Git\bin\bash.exe', '--login', '-i']`。
- 測試專案：starter（不含 `.venv`）複製到 `C:\Users\User\AppData\Local\Temp\herdr-app-test\ai-math-lab`。
- 注意：講師的 Windows 使用者 PATH 已含 `C:\Users\User\.opencode\bin`，與全新安裝的學生不同。11/11 實測顯示安裝程式只寫 `.bash_profile`，見 `../20261111-v2-windows/`。

完整輸出在 `run.log`。

## 結果

| 項目 | 結果 |
|---|---|
| T1：不指定程式時，core 開的預設 shell | 依 `config.toml` 開出 `bash.exe --login -i`。opencode v2.2.7（`~/.opencode/bin`）與 uv 0.13.6 都找得到 |
| T1b：Herdr 開的 bash 是否讀 `.bash_profile` | `shopt login_shell` 為 on；`.bash_profile` 的 `export PATH=/c/Users/User/.opencode/bin:$PATH` 讓它排在 PATH 第 2 位，Windows PATH 帶進來的同一路徑在第 31 位，證明 profile 有被讀到。學生的 opencode 只登記在 `.bash_profile`，這個設定照樣找得到 |
| T2：在 Git Bash 裡 `cd` 後，core 記錄的 cwd | 不會更新，`hc get` 的 cwd 停在啟動時的資料夾，與 issue #5958 相符。從 C:\ 啟動、`cd` 進專案的終端機也一樣 |
| T3：OpenCode 的 OSC 7501 狀態 | 啟動後 `idle`；送出寫檔任務後依序是 `working` → `blocked`（權限詢問）→ Enter 選 Allow once → `working` → `idle`。core 從未收到 `done`，`notes/herdr-test.md` 內容正確（見 `herdr-test.md.output`） |
| T5：中文輸出 | `PYTHONUTF8=1`，`uv run --no-project python -c "print('中文輸出測試')"` 輸出正常 |
| T6：寫入 `config.toml` 的指令 | 用假的 `APPDATA` 測 `mkdir -p` 加 `cat >`。跑兩次後檔案仍只有一行，`tomllib` 解析成 `['C:\\Program Files\\Git\\bin\\bash.exe', '--login', '-i']` |
| 清理 | 測試用的 t8、t9 已 kill 並 rm，暫存專案已刪除。講師原本的 t4、t5、t7 沒有動 |

## 未測，需要在 GUI 確認

- 預設按鍵改查 `herdr-app/defaults/keys.json` 與 `keys.macos.json`：往右切開是 `ctrl-shift-o`／`cmd-d`，設定是 `ctrl-,`／`cmd-,`，貼上是 `ctrl-shift-v`、`shift-insert`／`cmd-v`。按鍵是否實際生效、設定裡 Privacy 的位置，沒有在 GUI 確認。
- 側欄實際顯示的文字：做完後是 Done 還是 Idle。core 只收到 `idle`，Done 可能是 app 依「沒看過」另外標示的。
- 關掉視窗再打開後，窗格與 OpenCode 對話都還在。官方 README 有寫，但這次沒有在 GUI 實測。
- 從 Git Bash 執行 `powershell -c "irm …/install.ps1 | iex"` 安裝。講師已經裝好，為了不動到正在跑的 core，這次沒有重裝。只讀過 `install.ps1`：它安裝 app、加開始選單與使用者 PATH，沒有 core 時再裝 core；不會自動打開 app，也不寫 `config.toml`。
- `+` 選單直接啟動 agent 時的 PATH。講師的 Windows 使用者 PATH 已含 `.opencode\bin`，無法代表學生的情況。

## 旁證

`hc ls` 列出講師自己在 app 開的分頁 t4、t5、t7，三個都是 `bash.exe`，cwd 都停在 `C:\Users\User`，其中一個 space 名稱是 `~`。可見 app 的分頁也套用 `config.toml` 的 shell，#5958 的現象在 app 裡同樣存在。
