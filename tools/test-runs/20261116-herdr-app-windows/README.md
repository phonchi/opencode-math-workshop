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

## GUI 實測（講師同意後操作 app）

用 `herdr-app do <command>` 操作、`herdr-app shot` 截圖，沒有模擬按鍵。截圖在 `gui/`（含講師的機器名稱，與 2026-09-12 的紀錄相同）。

| 項目 | 結果 | 截圖 |
|---|---|---|
| 啟動 app | 第一個終端機是 Git Bash（`bash ~`）。左下角有 Settings | `gui/00-start.png` |
| 新 space | 名稱顯示 `~`；`cd` 之後窗格標題仍是 `~`（#5958） | `gui/02-newspace.png`、`gui/04-bigpickle.png` |
| `pane.split right`（講師安裝版 `keys.json` 綁在 `ctrl-shift-o`） | 新窗格開在 `C:\Users\User`，不在專案資料夾 | `gui/03-split.png` |
| 側欄 Agents | OpenCode 啟動後列在 Idle；離開 OpenCode 後從清單消失 | `gui/03-split.png`、`gui/04-bigpickle.png` |
| 等使用者回答（OpenCode 提問工具） | 側欄分組是紅色 **Needs you**，窗格右上角標 Needs you，分頁有紅點，狀態列寫 `1 needs you`。app 不用 Blocked 這個字 | `gui/07-blocked.png` |
| 看著窗格時做完 | 側欄顯示 Idle | `gui/05-blocked.png` |
| 切到別的 space 時做完 | 側欄顯示藍色 **Done**，右下角跳出 `OpenCode finished` | `gui/08-away.png` |
| 設定 | `app.settings` 打開後，左側有 Look、Machines、Alerts、Updates、Privacy | `gui/09-settings.png` |
| 關掉視窗再開 | `window.close` 後 app 的 socket 關閉，core 裡 t11（opencode）、t12 仍是 live；重開後同一個 space 的兩個窗格與對話都在 | `gui/10-reopened.png` |
| 清理 | 測試 space 已關閉，畫面切回講師原本的 `~` space；暫存專案已刪除 | `gui/11-after-cleanup.png` |

### 測試中的意外

- OpenCode 啟動時預設模型是講師最近用的「Auto · GitHub Copilot」。為了不動用講師的 Copilot 額度，用 `/models` 換成 Big Pickle。V2 沒有 `-m` 參數。
- 這次寫檔與 `ls` 都沒有跳出權限詢問。`opencode debug config` 只列出全域設定，沒有讀到暫存專案的 `opencode.json`，加了 `git init` 也一樣。T3 那次的編輯詢問可能是 V2 的預設行為，而按 Enter 選到了 Always allow。11/11 在正式專案資料夾實測時有讀到專案設定，這次的原因沒有再追。**這件事與 Herdr 無關，但值得另外確認學生專案的 `opencode.json` 有被讀到。**
- 所以改用 OpenCode 的提問工具觸發等待狀態。

## 仍未測

- 從 Git Bash 執行 `powershell -c "irm …/install.ps1 | iex"` 安裝（只讀過腳本）。
- 用全新的 Windows 帳號從頭安裝。
- 實際按下 `Ctrl+Shift+O`、`Ctrl+,` 按鍵（只確認了綁定與對應指令）。

## 旁證

`hc ls` 列出講師自己在 app 開的分頁 t4、t5、t7，三個都是 `bash.exe`，cwd 都停在 `C:\Users\User`，其中一個 space 名稱是 `~`。可見 app 的分頁也套用 `config.toml` 的 shell，#5958 的現象在 app 裡同樣存在。
