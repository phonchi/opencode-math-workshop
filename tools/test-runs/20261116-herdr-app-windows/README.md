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

## Agent 互相派工（2026-11-16 晚間至 11-17）

用 `hc` 在講師的 core 開背景終端機，送出學生會貼的提示詞。權限詢問由測試腳本代按 Allow once，遇到 `hc keys` 則選 Reject。用的模型是 big-pickle，測試專案放在 `Documents\herdr-a2a-test`，內容是 Lab 3 的參考程式，加上故意寫錯的 `notes/logistic.md`（抓到 12、漏掉 1，與 decision.md 的 11 矛盾；「不能證明什麼」一段混入「保證」句）。測完已刪除。逐行輸出在 `run.log`、`a2a-e2e.log`、`a2a-guide*.log`。`hc --skill`、OpenCode V2 help 與 herdr-app 指令清單在 `hc-docs/` 和 `herdr-app-commands.txt`。

| 項目 | 結果 |
|---|---|
| OpenCode 的 bash 工具 | Windows 上用 Git Bash，繼承 `HC_TERMINAL_ID`，`hc`、`opencode` 都找得到 |
| 子 agent 回報 | 以 `<hc from="t16 review">…</hc>` 打進主 agent 的輸入框，並自動送出；主 agent 會接著整理 |
| 父子關係 | 子終端機的 `parent` 是主 agent；主 agent 結束時子 agent 一起結束 |
| 指定指令的提示詞（A2A-6） | 能完成派工與回報，但主 agent 曾用 `hc keys` 替 reviewer 按下同意 |
| 共用背景服務（A2A-7、A2A-9） | OpenCode V2 預設連同一個背景服務，終端機會回報服務裡所有 session 的狀態。主 agent 等權限時，reviewer 也顯示 blocked，`hc send` 被拒。被 kill 的 session 若卡在權限詢問，之後在同一資料夾開的 OpenCode 一啟動就是 blocked。後者在 OpenCode 裡切到該 session 選 Reject 就清掉（`opencode service restart` 被本機權限規則擋下，沒有使用）。`--standalone` 可以隔開狀態（A2A-8） |
| **guide 風格提示詞（A2A-11，章節採用）** | 只叫主 agent 讀 `~/.config/herdr-app/AGENTS.md` 與 `hc --skill`，再用自然語言請它開 reviewer。主 agent 自己查 `opencode --help`，用 `hc run --bg --name review … opencode --prompt "…"` 開 reviewer；約 4 分 40 秒收到回報，兩個植入錯誤都被抓到。補問時，主 agent 把問題寫成檔案交給 reviewer，再讀它的畫面回答；最後依「收工」指示 `hc kill`、`hc rm`。全程約 15 分鐘、16 次權限詢問，主 agent context 用到 34%。沒有出現狀態互相干擾 |
| A2A-10（guide 風格前一次） | 主 agent 先試 `opencode "<任務>"` 失敗：V2 把位置參數當資料夾，出現 ENAMETOOLONG；之後自己改成先開再送。reviewer 卡在權限，主 agent 依指示沒有代按、請使用者處理。測試腳本漏抓子終端機，所以沒走完 |

未測：學生機器的 Windows PATH 沒有 `.opencode\bin` 時，主 agent 直接 `hc run … opencode` 會不會找不到程式。講師機器剛好有，測不出差別。章節的常見問題列了對應說法。
