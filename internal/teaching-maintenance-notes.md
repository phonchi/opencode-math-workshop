# 教材維護記錄：正文移出的歷史證據

本文件供講師維護使用。教學正文以操作、概念與成功判斷為主；以下保留原教材的量測、來源與驗證限制。記錄日期為 2026-09-12，不代表已重新測試新版或其他硬體。完整原始紀錄仍在 `tools/test-runs/`。

## 平台驗證的邊界

原教材與既有 handoff 記錄過 WSL2 Ubuntu 24.04 與原生 Windows 11 的 OpenCode／uv 主線操作。macOS 安裝步驟與 Windows 版 Ollama 沒有對應實測；本地 Ollama 的載入、context 及直接 API 證據，也不能代替完整 OpenCode agent 任務的成功紀錄。正文移除重複標籤，不改變這些驗證邊界。新一輪測試結果應另存 `tools/test-runs/`，不要用本文件替代實跑。

## tools/body_index.html：首頁資訊

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

<div class="meta">
    <div><b>3 小時</b><span>現場工作坊</span></div>
    <div><b>0 元</b><span>免註冊・免信用卡</span></div>
    <div><b>3 個</b><span>數學實作</span></div>
    <div><b>1 份</b><span>資料集貫穿全場</span></div>
  </div>


## tools/body_index.html：首頁受眾與速度敘述

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

<p class="lead">
你在微積分與線性代數學過的東西，足夠看懂這三個實作背後在算什麼。這場工作坊要處理的是另一件事：
<strong>當一個 AI agent 三十秒就把這些方法實作出來，你的價值在哪裡？</strong>
</p>
<p>
答案是判斷力。agent 寫得快，但它會用錯指標、會挑錯比較方式、會給你一個看起來很有道理但其實錯的結論。
而你修過微積分與線性代數，有能力抓出來。這三小時練的就是這件事。
</p>


## tools/body_prep.html：下載量與安裝耗時

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

<p class="lead">
    全部照做大約 <strong>10 到 20 分鐘</strong>，主要時間花在等下載。
    請務必在家裡或宿舍做完。要下載的東西約 <strong>287 MB</strong>，
    全班三十人同時在教室做，網路會塞住。
  </p>
</div>

<div class="box danger">
<div class="bt">為什麼不能現場做</div>
<p>
建立 Python 環境要下載約 <strong>287 MB</strong>（Python 直譯器加上所有套件）。
本教材實測過三次，耗時從 <strong>2 秒到 6 分 38 秒</strong>都出現過，差異完全看當下的網路狀況。
</p>
<p style="margin-bottom:0">
換句話說：<strong>你沒辦法預測自己會遇到哪一種</strong>。
而三十個人同時在同一個 WiFi 上抓 287 MB，幾乎保證會遇到慢的那一種。
</p>
</div>


## tools/body_prep.html：路徑操作原敘述

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

<h4>最省事的做法：不要用打的</h4>
<p>
路徑打字很容易出錯。直接用檔案總管／Finder 走到你要的資料夾，
然後把資料夾<strong>拖進終端機視窗</strong>，路徑就會自動填好。
先打 <code>cd </code>（注意後面有空格）再拖，然後按 Enter。
</p>


## tools/body_prep.html：安裝工具大小

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

<tr><th>工具</th><th>作用</th><th>大小</th></tr>
<tr><td><strong>opencode</strong></td><td>AI agent 本體，在終端機裡跑</td><td>約 100 MB</td></tr>
<tr><td><strong>uv</strong></td><td>Python 環境管理，比 conda 快很多，而且不需要先裝 Python</td><td>約 40 MB</td></tr>


## content/first-run.md：原查證來源與限制

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

## 資料來源

本章的操作細節分成四種來源，表格裡都標註了。

**一、1.18.30 實測**

在本機 `opencode 1.18.30` 上實際操作驗證的項目：`/` 斜線指令完整清單（17 項，逐項確認）、`ctrl+p` 指令面板內容與其標示的快捷鍵、權限對話框的完整文字與選項、`Esc` 需要按兩次才中斷、`ctrl+c` 在空輸入框會直接離開、`ctrl+j` 換行、`↑` 叫回上一句、`Tab` 切換 Build/Plan、`@` 補檔名與 subagent、`!` Shell 模式、`/models` 顯示 `● Big Pickle Free`、側邊欄 Context 與 `% used`、agent 以繁體中文回答。

**二、1.18.30 預設 keybind 表**

從 `1.18.30` 執行檔內的預設 keybind 定義讀出（leader key 為 `ctrl+x`）。標註「二進位預設值（未實測）」的項目屬於此類。

`plan` agent 的權限與說明來自本機指令：

```bash
opencode debug agent plan
opencode agent list
opencode debug config
```

**三、官方文件（opencode.ai）**

- <https://opencode.ai/docs/tui/> — TUI 斜線指令與快捷鍵清單（其中 `/compact`、`/undo`、`/redo`、`/share`、`/export`、`/details`、`/thinking` 在 1.18.30 實測不存在）
- <https://opencode.ai/docs/keybinds/> — 預設 keybind 與 leader key
- <https://opencode.ai/docs/permissions/> — `allow` / `ask` / `deny`、樣式比對規則、`--auto`、對話框三個選項
- <https://opencode.ai/docs/agents/> — build / plan / general / explore / scout 的定位

**四、中文教學站（learnopencode.com）**

- <https://learnopencode.com/1-start/> — 第一階段目錄
- <https://learnopencode.com/sitemap.xml> — 全站頁面清單
- <https://learnopencode.com/2-daily/01-interface.html> — 畫面分區、`@` / `!` / `/` 三個開頭字元
- <https://learnopencode.com/2-daily/02-sessions.html> — session 定義、存放位置、自動壓縮、匯入匯出
- <https://learnopencode.com/2-daily/03-shortcuts.html> — 快捷鍵表、leader key「按了要放開」的用法
- <https://learnopencode.com/3-workflow/01-plan-build.html> — Plan / Build 能力對照與建議流程
- <https://learnopencode.com/3-workflow/03-init.html> — `/init` 掃描專案產生 `AGENTS.md` 的行為

**已知的文件與實測衝突**

learnopencode.com 與 opencode.ai/docs 都把 `/compact`、`/undo`、`/redo`、`/share`、`/export` 列為斜線指令，但 1.18.30 的 `/` 清單中不存在這些指令。本章一律**以實測為準**。

learnopencode.com 的 Plan / Build 對照表寫 Plan 可以執行 bash（✓），opencode.ai/docs 寫 Plan 把 bash 設成 `ask`；實測 `opencode debug agent plan` 顯示 `bash` 在本專案設定下為 `ask`。

**查不到、因此本章沒有寫的內容**

- `opencode.school/lessons/models/` 回 HTTP 403，未讀取
- learnopencode.com 的 `2-daily/04-sessions.html` 與 `2-daily/05-shortcuts.html` 回 404（正確路徑是 `02-sessions.html` 與 `03-shortcuts.html`）
- 官方文件提到的 `/details`、`/thinking`、`/unshare`、`/summarize` 在 1.18.30 的 `/` 清單中查不到，也找不到對應的指令面板項目，因此未列入
- `/variants`、`/workspaces`、`/org`、`/warp` 存在於 1.18.30 執行檔內，但實測在本專案的 `/` 清單中不出現（需要特定模型變體或實驗性功能開關），因此未列入
- 官方文件提到 `tui.jsonc` 可自訂 keybind，但未在 1.18.30 驗證檔案位置與格式，因此本章不教如何改鍵


## content/agents-md.md：歷史實測清單

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

本機實測（opencode 1.18.30，Linux/WSL2）：

- `opencode debug config` 於起始專案的實際輸出
- `opencode run` 的行為測試，含「無 `instructions` 鍵仍讀取 AGENTS.md」與「改名後 agent 自行讀檔」兩組對照
- `opencode agent list` 解析後的 `permission` 規則（`git push *` → `deny`）


## content/git-safety.md：歷史實測清單

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

本機實測（opencode 1.18.30，Linux/WSL2）：

- 第 5 節的 `git diff` 輸出為實際執行 git 產生，非示意
- `opencode agent list` 確認 `"git push *": "deny"` 規則正確解析
- `opencode --help` 中 `--auto` 的原文警語 "(dangerous!)"
- `starter/.venv/.gitignore` 內容確為 `*`


## content/mcp-skills.md：歷史實測清單

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

本機實測（opencode 1.18.30，Linux/WSL2）：

- `opencode mcp list` 連線 Context7 顯示 `connected` 的實際輸出（無需金鑰）
- `opencode agent list` 的內建 agent 清單（`build` / `plan` / `explore` / `general`；**文件提到的 `scout` 在 1.18.30 並未出現**）
- `opencode debug agent math-reviewer` 解析後的 `description` / `mode` / `temperature` / `prompt`，以及 `edit: deny`、`bash: deny` 兩條權限規則
- `.opencode/agent/`（單數）與 `.opencode/agents/`（複數）兩種目錄名皆可被載入
- `opencode agent --help`、`opencode mcp --help` 的子指令清單


## content/local-models.md：歷史實測清單

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

查證日期：2026-09-12。

本機實測環境：WSL2 Ubuntu 24.04 / Ollama 0.21.2 / opencode 1.18.30 /
RTX 5070 12GB / RAM 15GB / 模型 `qwen3.5:9b-q4_K_M`（9.7B、Q4_K_M、原生 context 262144）。

**文中以下內容為本機實際執行產生，非示意**：

- `ollama serve` 啟動 log 的 `vram-based default context ... total_vram="11.9 GiB" default_num_ctx=4096`
- `ollama ps` 在 num_ctx = 4096 / 16384 / 32768 / 65536 四種設定下的 SIZE 與 PROCESSOR（含 65536 溢出到 CPU）
- `/v1/chat/completions` 請求裡帶 `num_ctx` 與 `options.num_ctx` **被完全忽略**（CONTEXT 仍為 4096）
- `OLLAMA_CONTEXT_LENGTH=16384` 的 server：不帶任何參數載入後 `context_length` 為 16384
- Modelfile ＋ `ollama create` 路線：`ollama show --parameters` 出現 `num_ctx 32768`、`ollama ps` 的 CONTEXT 為 32768
- 4k vs 32k 的 BANANA7 / ALPHA1 / HOTEL8 對照實驗（含 `usage` 數字與模型回答原文）
- `/api/generate` 的 `truncating input prompt limit=4096 prompt=10020` WARN，以及
  **同樣狀況走 `/v1/chat/completions` 時 log 完全無輸出**
- `ollama show` 的 Capabilities 欄（`qwen3.5:9b-q4_K_M` 有 `tools`、`gemma3:1b` 只有 `completion`）
- `gemma3:1b` 收到帶 `tools` 的請求時回傳 `does not support tools` 的錯誤原文
- 「分層建議」表格裡的 8 個模型 tag，逐一以 `registry.ollama.ai` 的 manifest 查詢確認存在（HTTP 200）
- 支援／不支援 tool calling 的兩張表格，19 個模型逐一抓取 `ollama.com/library/<name>` 頁面，
  比對其 capability 標籤（`gemma3` 只有 vision；`gemma2`／`gemma3n`／`codegemma`／`phi3`／
  `tinyllama`／`smollm`／`falcon3`／`starcoder2` 皆無標籤；`gemma4`／`qwen3.5`／`granite4.1`／
  `llama3.2`／`qwen3`／`qwen2.5`／`qwen2.5-coder`／`phi4-mini`／`ministral-3`／`smollm2` 皆有 `tools`）
- Ollama `server/prompt.go` 的 `chatPrompt` 註解：裁切時保證保留最新訊息與 system 訊息
- `opencode models ollama` 確實列出設定檔裡的 `ollama/qwen3.5-32k`

**未實測、已在文中標註的部分**：

- 8GB / 16GB RAM 無獨顯機器、8GB VRAM 獨顯、Mac 的實際速度與可用 context（無對應硬體）
- Windows 與 macOS 的環境變數設定路徑、桌面 app 的 context length 滑桿，以及滑桿與環境變數的優先順序
- opencode 自動 compaction 的實際觸發時機（依官方文件敘述，未在本機觀察到）
- 用 opencode 對本地模型跑完一輪完整的 agent 任務（`opencode run` 在無終端機的批次環境下未送出請求）


## content/first-run.md：完整指令與快捷鍵來源表

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

## 6. 常用斜線指令速查

以下 17 個是 1.18.30 在輸入框打 `/` 之後**實際列出來**的全部內建指令（實測逐項確認）。描述欄是 opencode 自己顯示的英文說明。

| 指令 | opencode 顯示的說明 | 你會用到嗎 |
|---|---|---|
| `/agents` | Switch agent | 換 Build / Plan。按 `Tab` 更快 |
| `/connect` | Connect provider | **不用**。big-pickle 免登入，按到就按 `Esc` |
| `/debug` | View debug info | 不用 |
| `/diff` | Open diff viewer | 會。看 agent 到底改了哪幾行 |
| `/editor` | Open editor | 會。要打很長的訊息時 |
| `/exit` | Exit the app | 會。**離開 opencode 請用這個** |
| `/help` | Help | 忘記按鍵的時候 |
| `/init` | guided AGENTS.md setup | **不用**。你的專案已經有 `AGENTS.md` 了 |
| `/mcps` | Toggle MCPs | 不用 |
| `/models` | Switch model | 會。開起來會看到 `● Big Pickle　Free`，`●` 是目前選的。按 `Esc` 關掉 |
| `/move` | Move to another project dir | 不用 |
| `/new` | New session（別名 `/clear`） | 會。換題目就用 |
| `/review` | review changes [commit\|branch\|pr] | 進階。讓 agent 檢查你的改動 |
| `/sessions` | Switch session（別名 `/resume`、`/continue`） | 會。回到舊對話 |
| `/skills` | Skills | 不用 |
| `/status` | View status | 不用 |
| `/themes` | Switch theme | 想換配色再說 |

**重要差異**：opencode.ai/docs 和 learnopencode.com 都列了 `/compact`、`/undo`、`/redo`、`/share`、`/export` 這幾個斜線指令，但實測 1.18.30 的 `/` 清單裡**沒有這些**。它們變成指令面板（`ctrl+p`）裡的項目，有各自的快捷鍵：

| 想做的事 | 1.18.30 的做法 |
|---|---|
| 壓縮 context | `ctrl+x c`，或 `ctrl+p` → `Compact session` |
| 復原上一則訊息 | `ctrl+x u`，或 `ctrl+p` → `Undo previous message` |
| 匯出對話記錄 | `ctrl+x x`，或 `ctrl+p` → `Export session transcript` |
| 分享對話 | `ctrl+p` → `Share session`（沒有預設快捷鍵） |

---

## 7. 快捷鍵速查

`ctrl+x` 是 **leader key**（前置鍵）。用法是：按 `ctrl+x`，**整個放開**，再按下一個字母。不要一起按。

### 你一定會用到的

| 按鍵 | 作用 | 來源 |
|---|---|---|
| `Enter` | 送出訊息 | 實測 |
| `ctrl+j` | 輸入框內換行，不送出 | 實測 |
| `Esc` | 中斷 agent。**按一次會變成 `esc again to interrupt`，要再按一次** | 實測 |
| `ctrl+c` | 輸入框**有字** → 清空；輸入框**是空的** → 直接關掉 opencode，沒有確認 | 實測 |
| `↑` | 輸入框空的時候，叫回你上一句話 | 實測 |
| `Tab` | 切換 agent：Build ↔ Plan | 實測 |
| `ctrl+p` | 開指令面板（Commands） | 實測 |
| `ctrl+x` | leader key | 實測 |

離開 opencode 請打 `/exit`。不要習慣性連按兩下 `ctrl+c`，輸入框一空掉，第二下就把程式關了。

### leader 組合鍵

下面這些是在指令面板（`ctrl+p`）裡**實際看到 opencode 自己標示**的快捷鍵：

| 按鍵 | 作用 | 來源 |
|---|---|---|
| `ctrl+x n` | 開新 session | 實測（面板顯示） |
| `ctrl+x l` | 切換 session | 實測（面板顯示） |
| `ctrl+x c` | 壓縮目前 session | 實測（面板顯示） |
| `ctrl+x u` | 復原上一則訊息 | 實測（面板顯示） |
| `ctrl+x x` | 匯出對話記錄 | 實測（面板顯示） |
| `ctrl+x m` | 切換模型 | 實測（面板顯示） |
| `ctrl+x e` | 用外部編輯器寫訊息 | 實測（面板顯示） |
| `ctrl+x g` | 跳到某一則訊息 | 實測（面板顯示） |
| `ctrl+x s` | 看狀態 | 實測（面板顯示） |
| `ctrl+x t` | 換主題 | 實測（面板顯示） |
| `ctrl+r` | 重新命名 session | 實測（面板顯示） |

### 其他（1.18.30 預設值，本章未實測）

這幾組是從 1.18.30 的預設 keybind 表讀出來的，但現場沒有逐一按過；有些組合會被終端機或視窗管理員吃掉。

| 按鍵 | 作用 | 來源 |
|---|---|---|
| `shift+Enter` / `alt+Enter` / `ctrl+Enter` | 輸入框換行（同 `ctrl+j`） | 二進位預設值（未實測） |
| `shift+Tab` | 反向切換 agent | 二進位預設值（未實測） |
| `PageUp` / `PageDown` | 對話上下捲一頁 | 二進位預設值（未實測） |
| `ctrl+x b` | 開關側邊欄 | 二進位預設值（未實測） |
| `ctrl+x y` | 複製訊息 | 二進位預設值（未實測） |
| `ctrl+x r` | 重做（redo）訊息 | 二進位預設值（未實測） |
| `ctrl+a` / `ctrl+e` / `ctrl+k` | 輸入框內：移到行首 / 行尾 / 刪到行尾 | 二進位預設值（未實測） |
| `F2` | 換到上一個用過的模型 | 二進位預設值（未實測） |
| `ctrl+f` | 在權限對話框裡切全螢幕 | 實測（畫面提示） |

---


## content/agents-md.md：init 限制

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

（未實測：我沒有實際拿課程專案去跑 `/init`，因為風險不對稱：寫壞了要重來，跑對了也只是省幾分鐘。）


## content/git-safety.md：權限樣式歷史驗證

以下保留修改前的歷史記錄，不能視為新一輪測試結果。

其中 **`"git push *": "deny"` 這條是我實際驗證過的**：存檔後執行 `opencode agent list`，可以在解析後的權限規則裡看到 `{"permission": "bash", "pattern": "git push *", "action": "deny"}`。同一份設定裡的 `git status` / `git diff *` 樣式也一併正確解析。`rm -rf *` 那條我沒有單獨測試，它只是同樣語法的套用。


## content/mcp-skills.md：相容目錄

以下為原稿歷史記錄，保留供講師維護，未在這次文案調整時重跑。

> 實測補充：1.18.30 底下 `.opencode/agent/`（單數）和 `.opencode/agents/`（複數）**兩種目錄名都能被載入**。文件寫的是複數，**建議統一用 `agents/`**，不要混用，免得以後找不到自己的檔案放哪。


## content/mcp-skills.md：原 skills 簡介

以下為原稿歷史記錄，保留供講師維護，未在這次文案調整時重跑。

## 5. 還有一個：skills

順帶一提，opencode 也支援 skills，可以把一組重複用到的工作流程打包成檔案。

檔案位置（依序搜尋）：

```
.opencode/skills/<名字>/SKILL.md
~/.config/opencode/skills/<名字>/SKILL.md
.claude/skills/<名字>/SKILL.md
~/.claude/skills/<名字>/SKILL.md
.agents/skills/<名字>/SKILL.md
~/.agents/skills/<名字>/SKILL.md
```

`SKILL.md` 的 frontmatter 必填 `name`（小寫英數與連字號，1–64 字元）和 `description`（1–1024 字元）。

查看目前有哪些 skills：

```bash
opencode debug skill
```

**這門課不會用到 skills。** 列在這裡只是讓你知道有這個東西，之後看到別人的專案裡有 `SKILL.md` 不會一頭霧水。先把 AGENTS.md 寫好，那個的投資報酬率高得多。

---


## content/local-models.md：定位原文

以下為原稿歷史記錄，保留供講師維護，未在這次文案調整時重跑。

先把話講在前面：**對大多數人的筆電來說，本地模型的體驗會明顯比雲端差。**
慢、比較笨、比較容易亂來，而且要花時間調設定。這一章要做的，是讓你在「真的需要」的時候知道怎麼做，也知道什麼時候不該做。


## content/local-models.md：硬體分層表與推估限制

以下為原稿歷史記錄，保留供講師維護，未在這次文案調整時重跑。

### 分層建議

| 你的機器 | 建議模型（含 quantization） | 檔案大小 | 實際能開的 context | 預期體感 |
|---|---|---|---|---|
| 8GB RAM，無獨顯 | `qwen3.5:2b-q4_K_M` | 1.9GB | 8k–16k | 很慢，勉強能動（未實測） |
| 8GB RAM，無獨顯 | `llama3.2:3b-instruct-q4_K_M` | 2.0GB | 8k–16k | 很慢（未實測） |
| 8GB RAM，無獨顯 | `granite4.1:3b-q4_K_M` | 2.1GB | 8k–16k | 很慢（未實測） |
| 16GB RAM，無獨顯 | `qwen3.5:4b-q4_K_M` | 3.4GB | 16k–32k | 慢但可用（未實測） |
| 16GB RAM，無獨顯 | `granite4.1:8b-q4_K_M` | 5.3GB | 16k–32k | 慢（未實測） |
| 8GB VRAM 獨顯 | `qwen3.5:4b-q4_K_M` | 3.4GB | 32k | 順（未實測） |
| 8GB VRAM 獨顯 | `granite4.1:8b-q4_K_M` | 5.3GB | 16k–32k | 普通（未實測） |
| 12GB VRAM 獨顯 | `qwen3.5:9b-q4_K_M` | 6.6GB | 32k | 順（本機實測） |
| 16GB 以上 Mac | `qwen3.5:4b-q4_K_M` 或 `9b-q4_K_M` | 3.4 / 6.6GB | 16k–32k | 普通（未實測） |

標「未實測」的是我沒有那台機器可以驗證的，只有 12GB VRAM 那一列是下面實測數據的來源。


## content/local-models.md：context 推估表

以下為原稿歷史記錄，保留供講師維護，未在這次文案調整時重跑。

| 你的記憶體 | 建議 num_ctx | 依據 |
|---|---|---|
| 8GB RAM 無獨顯 | 8192，勉強 16384 | 推估（未實測） |
| 16GB RAM 無獨顯 | 16384 | 推估（未實測） |
| 8–12GB VRAM | 32768 | 12GB 本機實測 |
| 24GB 以上 VRAM / 32GB 以上 Mac | 65536 | 推估（未實測） |


## tools/body_prep.html：Python 環境下載記錄

原稿歷史記錄，未在本次重新測試：

第一次執行會下載 Python 直譯器與所有套件，共約 <strong>287 MB</strong>。
實測耗時在 <strong>2 秒到 6 分半</strong>之間，取決於網路。
之後在同一台機器上再跑就只要幾秒，因為東西都進快取了。


## content/first-run.md：三步任務歷史耗時

原稿歷史記錄，未在本次重新測試：

講師實測 `big-pickle` 跑一個「讀檔 → 寫檔 → 執行」的三步任務大約 **7.4 秒**。你可以試這個：


## content/first-run.md：Plan 權限範圍

原稿歷史記錄，未在本次重新測試：

`Plan` 的內建 `deny` 和本專案 `opencode.json` 裡的 `edit: "ask"` 疊在一起之後的實際結果，本章沒有實測。工作坊請用 `Build`。


## content/agents-md.md：權限樣式查證

原稿歷史記錄，未在本次重新測試：

這是實測可用的：把上面這段放進 `opencode.json` 後，用 `opencode agent list` 檢視解析後的權限規則，可以看到 `{"permission": "bash", "pattern": "git push *", "action": "deny"}` 確實生效。規則以樣式比對，**最後一條符合的規則勝出**，所以 `"*": "ask"` 要寫在前面，特例寫後面。


## content/agents-md.md：規則自動載入對照實驗

原稿歷史記錄，未在本次重新測試：

### 回答正確還不能確認什麼

我原本想做一個對照實驗：把 `AGENTS.md` 改名成 `AGENTS.md.bak`，預期 agent 就答不出 `uv run python` 了。**結果完全不是這樣。** 輸出例子：

```
→ Read AGENTS.md.bak
→ Read opencode.json

`uv run python <檔案>`。
```

看到沒有？它**自己用讀檔工具去把 `AGENTS.md.bak` 翻出來讀了**，然後照樣答對。

這件事有兩個重要的意涵：

1. **「問它規則」這個測試會有偽陽性。** 它答對，不代表規則是透過 AGENTS.md 機制自動載入的；也可能是它自己去翻檔案翻到的。agent 比你想的還會找東西。
2. 所以**要搭配層次 1 的 `opencode debug config` 一起看**。`debug config` 是靜態的設定解析結果，不會被 agent 的臨場發揮干擾。

真的想做乾淨的對照實驗，應該要把檔案**移到專案目錄外面**（例如 `mv AGENTS.md /tmp/`），不能只是改個副檔名放在原地。（我沒有再測這一步，所以不保證有效，agent 對某些外部路徑仍有讀取權限。）


## content/mcp-skills.md：章首定位

原稿歷史記錄，未在本次重新測試：

## 先講清楚：這章你可以先跳過

前兩章（`AGENTS.md`、git）是**地基**。這一章是**裝潢**。

如果你目前還在這些狀況裡，請先回去把前兩章練熟，這章留到之後再看：

- 還不太確定 `git diff` 的輸出在講什麼
- 還沒養成「叫 agent 動手前先 commit」的習慣
- AGENTS.md 寫了但沒驗證過有沒有生效
- 用 opencode 寫數學程式還不太順

理由很實際：**這章的東西都是在「你已經能順利用 agent 做事」之後，才會感覺到價值的優化。** 在地基還不穩的時候加裝潢，只會讓你要 debug 的東西變多。結果不如預期時，你會分不清是模型的問題、提示的問題，還是你多加的那個 MCP 的問題。

而且老實說：**這門課的作業，只用前兩章的內容就能完整做完。** 這章是給已經吃飽、還想多學一點的人。

準備好的話，我們開始。

---


## content/mcp-skills.md：agent create 來源差異

原稿歷史記錄，未在本次重新測試：

（注意：中文教學站 5.2a 那章沒提到這個指令，只教手寫 `.md` 檔。但**實測 1.18.30 確實有 `opencode agent create`**，以實測為準。不過它是互動式問答，還是建議直接手寫 `.md` 檔，你會更清楚每個欄位在幹嘛，也比較好改。）


## content/local-models.md：provider 設定驗證範圍

原稿歷史記錄，未在本次重新測試：

> 驗證程度說明：上面這份設定檔在撰寫環境裡實測過，`opencode models ollama`
> 確實列出 `ollama/qwen3.5-32k`（代表設定檔語法與 provider 註冊都正確），
> `/v1` 端點的工具呼叫也實測通過。但**在撰寫環境裡沒有成功跑完一輪完整的 agent 任務**
> （`opencode run` 在無終端機的批次環境下沒有送出任何請求就結束）。
> 這份設定可用來練習連接本地 provider；仍需完成後面的實際工具任務，才能確認在自己的機器上可用。


## content/git-safety.md：原 ASCII 工作流

```
  ┌─────────────────────────────────────────┐
  │  1. 動手前先存檔                          │
  │     git add -A && git commit -m "..."    │
  └─────────────────┬───────────────────────┘
                    ↓
  ┌─────────────────────────────────────────┐
  │  2. 讓 agent 改（在 opencode 裡）          │
  └─────────────────┬───────────────────────┘
                    ↓
  ┌─────────────────────────────────────────┐
  │  3. 檢查                                 │
  │     git diff                             │
  └─────────────────┬───────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   滿意 → 再 commit         不滿意 → git restore .
   git add -A &&            （回到步驟 1 的狀態）
   git commit -m "..."
```


## 本地模型：精煉前原始教學與實驗記錄完整封存

以下逐字保存本輪開始時 Git HEAD 的 `content/local-models.md`。其中硬體表、模型能力清單、API 請求、BANANA7 對照、VRAM 門檻與效能敘述都是歷史環境資料；不能外推為其他機器或新版服務的保證。新版正文只保留操作路徑與自測，這份封存供講師追溯原始證據與限制。

````markdown
# 在自己電腦上跑本地模型

> 課後延伸 · **加分項，不是必修**
> 適用版本：opencode 1.18.30 · Ollama 0.21.2

工作坊主線用的是 `opencode/big-pickle`，免登入、不用設定、速度夠快。這一章講的是另一條路：
把模型放在自己的筆電上跑。**這不是必修**，做不做都不影響你的作業。

先把話講在前面：**對大多數人的筆電來說，本地模型的體驗會明顯比雲端差。**
慢、比較笨、比較容易亂來，而且要花時間調設定。這一章要做的，是讓你在「真的需要」的時候知道怎麼做，也知道什麼時候不該做。

---

## 什麼時候才真的需要本地模型

| 本地模型的好處 | 代價 |
|---|---|
| **隱私**：程式碼與資料不離開你的電腦 | **慢**：沒有獨顯的筆電，回一段話可能要等好幾十秒 |
| **離線**：沒網路也能用（飛機上、網路爛的地方） | **笨**：2B–9B 的小模型跟雲端大模型不是同一個量級 |
| **沒有配額**：想跑多少跑多少，不會被限流 | **耗電發燙**：筆電風扇會全速轉，電池撐不久 |
| **可以隨便實驗**：換模型、改參數、看 log | **要調設定**：不設定的話，預設值幾乎一定不能用（見下面最長的那一節） |

### 誠實的建議

- **只是想把工作坊的三個 lab 做完** → 用 `opencode/big-pickle` 就好，別折騰。
- **修課報告裡要處理不能外流的資料** → 本地模型是對的選擇。
- **想搞懂 agent 到底怎麼運作** → 值得做一次。本地跑的時候你看得到 log、
  看得到 context 被截掉、看得到模型亂叫工具，這些在雲端是看不到的。
  這一章最大的價值其實在這裡。
- **筆電 8GB RAM 又沒獨顯** → 可以裝起來玩，但**不要期待它能完成 lab**。
  把它當成「觀察 agent 失敗的實驗室」，比當成生產工具實際得多。

---

## 你的機器跑得動嗎

判斷標準只有一個數字：**模型檔案 + KV cache 能不能塞進記憶體**。

- 有獨顯（NVIDIA/AMD）→ 看 **VRAM**（顯示卡自己的記憶體）。
- Mac（M 系列）→ 看**整機統一記憶體（unified memory）**，Ollama 會把它當 VRAM 用。
- 沒獨顯的 Windows/Linux 筆電 → 看 **RAM**，而且要扣掉作業系統和瀏覽器吃掉的部分
  （實務上 OS + 瀏覽器就要 3–4GB，8GB 機器真正能給模型的大概只剩 4GB）。

### 分層建議

| 你的機器 | 建議模型（含 quantization） | 檔案大小 | 實際能開的 context | 預期體感 |
|---|---|---|---|---|
| 8GB RAM，無獨顯 | `qwen3.5:2b-q4_K_M` | 1.9GB | 8k–16k | 很慢，勉強能動（未實測） |
| 8GB RAM，無獨顯 | `llama3.2:3b-instruct-q4_K_M` | 2.0GB | 8k–16k | 很慢（未實測） |
| 8GB RAM，無獨顯 | `granite4.1:3b-q4_K_M` | 2.1GB | 8k–16k | 很慢（未實測） |
| 16GB RAM，無獨顯 | `qwen3.5:4b-q4_K_M` | 3.4GB | 16k–32k | 慢但可用（未實測） |
| 16GB RAM，無獨顯 | `granite4.1:8b-q4_K_M` | 5.3GB | 16k–32k | 慢（未實測） |
| 8GB VRAM 獨顯 | `qwen3.5:4b-q4_K_M` | 3.4GB | 32k | 順（未實測） |
| 8GB VRAM 獨顯 | `granite4.1:8b-q4_K_M` | 5.3GB | 16k–32k | 普通（未實測） |
| 12GB VRAM 獨顯 | `qwen3.5:9b-q4_K_M` | 6.6GB | 32k | 順（本機實測） |
| 16GB 以上 Mac | `qwen3.5:4b-q4_K_M` 或 `9b-q4_K_M` | 3.4 / 6.6GB | 16k–32k | 普通（未實測） |

標「未實測」的是我沒有那台機器可以驗證的，只有 12GB VRAM 那一列是下面實測數據的來源。

### 記憶體怎麼估

粗略公式：

```
模型權重（GB） ≈ 參數量（B） × quantization 位元數 ÷ 8
```

`q4_K_M` 大約是 4.5 bits/參數（不是剛好 4，因為有些層保留較高精度）。所以：

- `qwen3.5:9b` 的 `ollama show` 顯示實際參數是 **9.7B**：9.7 × 4.5 ÷ 8 ≈ **5.5GB**
  → 實際檔案 6.6GB。差額主要是 embedding 層和**視覺編碼器**
  （qwen3.5 是多模態模型，即使你只用文字，那部分權重還是在檔案裡）。
- 4B 參數 × 4.5 ÷ 8 ≈ **2.3GB** → 實際檔案 3.4GB（同理）。

**但檔案大小不等於執行時吃的記憶體**，還要加上 KV cache。KV cache 會隨 context 線性長大，
這是下面那一節的重點。本機 `qwen3.5:9b-q4_K_M`（檔案 6.6GB）實測：

| context | 實際佔用（`ollama ps` 的 SIZE） | 放在哪 |
|---|---|---|
| 4096（預設） | 8.6 GB | 100% GPU |
| 16384 | 9.2 GB | 100% GPU |
| 32768 | 9.9 GB | 100% GPU |
| 65536 | 11 GB | 22% CPU / 78% GPU ← **溢出到 CPU，速度大跌** |

看最後一列：在 12GB 的卡上把 context 開到 64k，模型就塞不下，一部分被推到 CPU 跑。
**不是開越大越好。**

---

## 安裝 Ollama

Ollama 是負責「把模型載入記憶體、提供一個本機 API」的程式。opencode 只是它的客戶端。

### macOS

到 <https://ollama.com/download> 下載 .dmg，拖進 Applications。裝完會有一個選單列圖示。

### Windows

到 <https://ollama.com/download> 下載安裝檔，一路下一步。裝完會常駐在系統列。

> 如果你用 WSL2 寫作業：**建議把 Ollama 裝在 WSL 裡面**（用下面的 Linux 步驟），
> 不要裝 Windows 版再跨過去連，這樣網路位址和 GPU 都比較單純。

### Linux（含 WSL2）

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

安裝腳本會建立並啟動一個 systemd service。確認它在跑：

```bash
systemctl status ollama
curl http://localhost:11434/api/version
```

應該會看到類似 `{"version":"0.21.2"}`。

### 抓第一個模型

```bash
ollama pull qwen3.5:4b-q4_K_M     # 依你上面那張表挑一個
ollama list                        # 看有哪些模型
ollama run qwen3.5:4b-q4_K_M       # 聊天測試，打 /bye 離開
```

---

## 挑模型：tool calling 是硬門檻

**agent 的本質就是「模型呼叫工具」。** 不支援 tool calling（又叫 function calling）的模型，
在 opencode 裡**完全不能用**。這不是「效果差一點」，是連第一步都走不到。

這是初學者最容易踩的坑：看到一個模型很小、跑得動、聊天也正常，就以為可以用，
結果接到 opencode 就直接壞掉。

### 怎麼檢查

**一行指令搞定**，看 `Capabilities` 有沒有 `tools`：

```bash
ollama show qwen3.5:9b-q4_K_M
```

本機輸出（節錄）：

```
  Model
    architecture        qwen35
    parameters          9.7B
    context length      262144
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools          ← 有這行才能用
    thinking
```

對照組，`gemma3:1b`：

```
  Capabilities
    completion     ← 只有這個，沒有 tools
```

### 如果硬用不支援的模型會怎樣

實測：對 `gemma3:1b` 發一個帶 `tools` 的請求，Ollama 直接回錯誤，模型根本不會被呼叫：

```
{"error":{"message":"registry.ollama.ai/library/gemma3:1b does not support tools",
          "type":"invalid_request_error"}}
```

在 opencode 裡你會看到請求失敗、對話卡住。**這不是設定問題，是模型選錯了，換一個就好。**

### 已知不支援 tool calling 的常見小模型

以下都是 Ollama library 上該模型頁面**沒有** `tools` capability 標籤的（2026-09 查）：

| 模型 | 有的 capability | 備註 |
|---|---|---|
| `gemma3`（270m / 1b / 4b / 12b / 27b） | vision | 很多教學推薦它，但**不能拿來做 agent** |
| `gemma3n`（e2b / e4b） | 只有 text | |
| `gemma2`（2b / 9b） | 無 | |
| `codegemma`（2b / 7b） | 無 | 名字有 code，一樣不能做 agent |
| `phi3`（3.8b） | 無 | 但 `phi4-mini` 有 tools |
| `tinyllama`（1.1b） | 無 | |
| `smollm`（135m / 360m / 1.7b） | 無 | 但 `smollm2` 有 tools |
| `falcon3` | 無 | |
| `starcoder2` | 無 | 是 completion 模型，不是 chat/agent 模型 |

> 注意 Gemma 家族的分歧：`gemma2` / `gemma3` / `gemma3n` / `codegemma` **都沒有** tools，
> 但 `gemma4`（12b / 26b / 31b）**有** tools。看版本號不能判斷，一定要 `ollama show` 確認。

### 已知支援 tool calling 的小模型

| 模型 | 可選大小 | 備註 |
|---|---|---|
| `qwen3.5` | 0.8b / 2b / 4b / 9b / 27b / 35b / 122b | tools + vision + thinking，原生 context 256K |
| `granite4.1` | 3b / 8b / 30b | IBM，Apache 2.0，明講支援 tool use 與 JSON 輸出，128K context |
| `llama3.2` | 1b / 3b | 128K context |
| `qwen3` | 0.6b / 1.7b / 4b / 8b | tools + thinking |
| `qwen2.5` / `qwen2.5-coder` | 0.5b / 1.5b / 3b / 7b | 較舊但穩定 |
| `phi4-mini` | 3.8b | |
| `ministral-3` | 3b / 8b / 14b | tools + vision |
| `smollm2` | 135m / 360m / 1.7b | 有 tools 標籤，但**這個尺寸做 agent 實務上不會成功**，別浪費時間 |

**實務建議**：跑得動的前提下，**選最大的那個**。小模型省下來的記憶體，
遠遠補不回它在工具呼叫上犯的錯。

---

## 先搞清楚：token 與 context 是什麼

:::bg token 與 context 是什麼（沒概念的話先看這個）
語言模型讀文字的方式是先把它切成一塊一塊的 **token**，不是一個字一個字讀。
中文大約 **一個字 ≈ 1 到 2 個 token**，英文大約 **一個單字 ≈ 1.3 個 token**，
程式碼因為符號多，通常更耗 token。

**context**（上下文長度）就是「模型一次最多能看到幾個 token」。
它是一個硬性上限，不是建議值。超過就有東西會被丟掉。

這個上限要裝的東西比你想的多：

- 系統提示（agent 的行為規則）
- 所有工具的定義（read / write / bash… 每個都是一大段 JSON）
- 你的 `AGENTS.md`
- agent 讀進來的檔案內容
- 到目前為止的整段對話，以及每次工具執行的輸出

**一般聊天 4k 綽綽有餘，但 agent 光是「還沒開始工作」就可能用掉一大半。**
這就是下面這一節要處理的問題。
:::

## 最重要的一節：context 要設兩次

這一節是整章的重點。**只設一邊完全沒有用**，而且失敗的方式是「安靜地壞掉」：
不會報錯，只會讓模型看起來很笨。

### 為什麼是兩個地方

opencode 透過 **OpenAI 相容端點**（`http://localhost:11434/v1`）跟 Ollama 講話。
這個協定裡**沒有**「context 要多大」這個欄位。所以：

```
  opencode                                        Ollama
  --------                                        ------
  limit.context  ──── POST /v1/chat/completions ───>  num_ctx
  設定 A                                             設定 B

  「我以為模型能吃多少 token」                       「模型實際能吃多少 token」
  → 決定何時壓縮／摘要對話（compaction）             → 超過就安靜地截掉一部分

  OpenAI 相容協定裡沒有「context 要多大」這個欄位，
  所以設定 A 永遠傳不到設定 B。兩邊要各設一次。
```

- **設定 B（Ollama 的 `num_ctx`）** 決定模型真正看得到多少。超過就**安靜地截掉一部分**。
- **設定 A（opencode 的 `limit.context`）** 是 opencode 判斷「該不該壓縮／摘要對話」
  （官方文件稱為 compaction）的依據。opencode 的自動 compaction 門檻就是從 catalog 裡的
  context limit 算出來的，而 Ollama 這種自訂 provider 的 context limit 只能由你手寫。
  opencode **沒辦法**問 Ollama「你的 context 多大」，只能相信你在設定檔裡寫的數字。

**實測證明這兩者互不相通**：我在 `/v1/chat/completions` 請求裡同時塞了
`"num_ctx": 32768` 和 `"options": {"num_ctx": 32768}`，然後看 `ollama ps`：

```
NAME                 ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen3.5:9b-q4_K_M    6488c96fa5fa    8.6 GB    100% GPU     4096       4 minutes from now
                                                            ^^^^ 還是 4096，請求裡的設定被忽略
```

所以：**你在 opencode 那邊怎麼寫，都不會改變 Ollama 的 num_ctx。** 必須分開設。

### 預設值是多少（這裡有陷阱）

較新版本的 Ollama 已經不用固定的 4096，改成**開機時依可用 VRAM 自動決定**：

| 可用 VRAM | 預設 context |
|---|---|
| 小於 24 GiB | **4k** |
| 24–48 GiB | 32k |
| 48 GiB 以上 | 256k |

本機（RTX 5070 12GB）啟動時的 log，可以直接看到這個判斷：

```
level=INFO source=routes.go:1860 msg="vram-based default context"
    total_vram="11.9 GiB" default_num_ctx=4096
```

**注意這個門檻有多高**：24 GiB。RTX 4090 是 24GB、RTX 5070 是 12GB、
M2 MacBook Air 是 8 或 16GB。**幾乎所有學生的機器都落在第一層，也就是 4k。**
「我沒改過設定所以應該是預設的最佳值」這個想法在這裡是錯的。

> Ollama 的 FAQ 頁面目前還寫著「預設 4096」，跟 context-length 那一頁的分層說明不一致。
> 以 context-length 頁與你自己機器的 log 為準。

### 4k 為什麼對 agent 完全不夠

一般聊天 4k 綽綽有餘。但 agent 的 context 裡塞的是：

| 內容 | 大約 token 數（推估） |
|---|---|
| 系統提示（agent 的行為規則） | 1k–3k |
| 工具定義（read / write / bash / glob / grep… 的 JSON schema） | 2k–5k |
| `AGENTS.md` 專案規則 | 0.5k–2k |
| 讀進來的檔案內容 | 每個檔案 0.5k–5k |
| 到目前為止的對話與工具輸出 | 持續累積 |

（這些數字是推估，沒有實測。）

關鍵在於：**系統提示和工具定義是不會被丟掉的固定開銷。**
Ollama 的 `chatPrompt` 在裁切訊息時，明文保證「一定保留最新的訊息與 system 訊息」
（見原始碼註解）。也就是說，`num_ctx` 扣掉這一大塊固定開銷之後，
剩下來給「你的問題、讀進來的檔案、工具輸出」的空間才是真正可用的額度。

**光是系統提示加工具定義就可能吃掉 4k 的大半。** 在預設設定下，
你的第一個檔案還沒讀進來，額度就差不多用完了。

### 設定前 vs 設定後（本機實測）

這是整章最值得自己重跑一次的實驗。我做了一份**完全相同**的請求，
只換模型（一個 4k、一個 32k），走的就是 opencode 在用的 `/v1/chat/completions`：

請求內容：

- 一個 system message，裡面寫「系統提示驗證碼是 **BANANA7**」
- 一個 `bash` 工具定義
- 8 段筆記，每段開頭給一個代號（第 1 段是 **ALPHA1**、…、第 8 段是 **HOTEL8**），
  每段約 1000 token，共約 10000 token
- 最後問三個問題：(a) 系統提示驗證碼 (b) 第 1 段代號 (c) 第 8 段代號，
  並要求執行 `ls -la`

#### 設定前：`qwen3.5:9b-q4_K_M`（num_ctx = 4096 預設）

```
usage = {'prompt_tokens': 4049, 'completion_tokens': 961, 'total_tokens': 5010}
```

模型的回答（原文節錄）：

```
（說明）：作為語言模型，我無法在您的系統中執行命令……
(a) 系統提示驗證碼：不知道（對話中未提及）
(b) 第 1 段筆記代號：GOLF07
(c) 第 8 段筆記代號：HOTEL8
```

`tool_calls` 是 `null`。三件事同時發生：

1. **內容被吃掉了**：送進去約 10000 token，`prompt_tokens` 只有 **4049**。
2. **舊的對話輪不見了**：第 1 段代號實際是 `ALPHA1`，它很有自信地回答 `GOLF07`
   （那是第 7 段的代號）。最新的第 8 段 `HOTEL8` 它答對了，
   因為 Ollama 保留的是**最後面**的訊息。**它不會說「我不知道」，它會編一個。**
3. **連 system message 裡的驗證碼也答不出來**：它回「對話中未提及」。
   這一點要講精確：Ollama 的 `chatPrompt` **明文保證一定保留 system 訊息**，
   所以驗證碼其實還在 context 裡。它答不出來的原因不是被刪掉，
   是 4k 的空間被塞爆之後，小模型在一堆雜訊裡**用不到**那條指令。
   （同樣結構的另一次實測它答對了 `BANANA7`，這一條的表現不穩定，
   這本身就是「context 太擠」的典型徵兆。）

順帶一提，它也沒有呼叫 `bash` 工具，而是回「作為語言模型，我無法在您的系統中執行命令」。
但這一項**不能歸因於 context**，見下面 32k 的對照。

#### 設定後：`qwen3.5-32k`（num_ctx = 32768）

同一份請求，只把 model 名稱換掉：

```
usage = {'prompt_tokens': 10190, 'completion_tokens': 3262, 'total_tokens': 13452}
```

```
(a) 系統提示驗證碼：BANANA7
(b) 第 1 段筆記的代號：ALPHA1
(c) 第 8 段筆記的代號：HOTEL8
```

**三題全對**，`prompt_tokens` 是完整的 10190。**模型沒有變聰明，它只是終於看得到完整的指令。**

（**重要的對照**：即使 context 開到 32k、內容完整送達，這一輪它**還是**沒有呼叫
`bash` 工具，同樣用「我是語言模型，無法執行命令」打發。
所以「不呼叫工具」是**模型本身的能力問題，不是 context 問題**。
context 設對是必要條件，不是充分條件。剩下的問題在最後一節處理。）

#### 最陰險的一點：完全不會有警告

**在 `/v1/chat/completions` 這條路上，Ollama 的 log 一個字都不會印。**
上面那次 4k 的截斷，`journalctl -u ollama | grep truncat` 完全沒有輸出。

只有在走 `/api/generate`（直接送一整段 prompt，不是 messages）時才看得到 WARN：

```
level=WARN source=runner.go:187 msg="truncating input prompt"
    limit=4096 prompt=10020 keep=4 new=4096
```

也就是說：**opencode 走的那條路，是安靜失敗的。** 你唯一能依靠的訊號是
`usage.prompt_tokens` 和 `ollama ps` 的 CONTEXT 欄，不要指望 log 會告訴你。

（同樣的 10020 token prompt 送給 `qwen3.5-32k` 走 `/api/generate`：
`prompt_eval_count = 10020`，log 沒有 `truncating input prompt`。設定確實生效。）

#### 這解釋了所有症狀

下面把「確定是 context 造成的」跟「可能只是模型太小」分開，這樣你才知道該調設定還是該換模型。

**確定與 context 有關（本機實測可證）**

| 症狀 | 原因 |
|---|---|
| 「一直忘記我前面說什麼」 | 最舊的對話輪被丟掉，只保留最新的訊息（實測：第 1 段代號答錯、第 8 段答對） |
| 「一本正經地講錯話」 | 資訊被丟掉後模型不會說「我不知道」，它會**編一個**（實測：`GOLF07` vs 正解 `ALPHA1`） |
| 「同一件事重複做好幾次」 | 它看不到自己剛才已經做過的紀錄（同上機制） |
| 「講到一半突然變得很笨」 | 累積內容剛好越過 num_ctx 這條線（實測：`prompt_tokens` 4049 vs 10190） |

**可能與 context 有關，但也可能只是模型太小（未能單獨驗證）**

| 症狀 | 說明 |
|---|---|
| 「不遵守 `AGENTS.md` 的規則」 | 系統提示與 `AGENTS.md` 其實**不會**被丟掉（`chatPrompt` 保證保留 system 訊息）。但 context 一擠，小模型就用不到那些規則。調大 context 通常會改善，不保證解決 |
| 「亂呼叫不存在的工具，像 `execute`、`shell`」 | 工具定義同樣不會被丟掉。這多半是小模型自己的毛病，先調 context，再用最後一節的 `AGENTS.md` 約束 |
| 「該執行指令卻只印出指令」 | **實測在 4k 和 32k 都會發生**，所以主要是模型能力問題，不是 context。見最後一節 |

### 該設多大

兩個官方說法看起來矛盾，其實不衝突：

- **Ollama 官方文件**：「需要大量 context 的任務，像是 web search、agents、coding tools，
  應該至少設到 **64000**。」
- **opencode 官方文件**：「如果 tool call 表現不好，把 Ollama 的 `num_ctx` 調大，
  **從 16k–32k 開始**。」

64k 是理想值，16k–32k 是在學生筆電上的現實下限。回頭看前面那張實測表：
12GB 的卡開到 64k 就已經溢出到 CPU 了。所以：

| 你的記憶體 | 建議 num_ctx | 依據 |
|---|---|---|
| 8GB RAM 無獨顯 | 8192，勉強 16384 | 推估（未實測） |
| 16GB RAM 無獨顯 | 16384 | 推估（未實測） |
| 8–12GB VRAM | 32768 | 12GB 本機實測 |
| 24GB 以上 VRAM / 32GB 以上 Mac | 65536 | 推估（未實測） |

**從 32768 開始試**，如果 `ollama ps` 顯示 PROCESSOR 不是 100% GPU（或機器開始瘋狂 swap），
就往下調。

---

### 設定 B：Ollama 端的 num_ctx

有兩條路，**建議用第二條**。

#### 路線一：環境變數 `OLLAMA_CONTEXT_LENGTH`

影響這台機器上的**所有**模型。

**Linux / WSL2**（Ollama 由 systemd 管理）：

```bash
sudo systemctl edit ollama
```

在編輯器開啟的區塊裡加入：

```ini
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=32768"
```

存檔後重啟：

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

**macOS**（Ollama 是 app，不是 systemd service）：

```bash
launchctl setenv OLLAMA_CONTEXT_LENGTH 32768
```

然後從選單列**完全結束 Ollama 再重開**。

> `launchctl setenv` 設的變數**重開機後不會保留**（未實測；若要永久生效，
> 建議直接用下面提到的 app 設定滑桿）。

**Windows**：

「設定」→ 搜尋「環境變數」→「編輯系統環境變數」→「環境變數」→
在「使用者變數」新增 `OLLAMA_CONTEXT_LENGTH` = `32768` → 確定 →
**從系統列結束 Ollama 再重新啟動**。

**臨時測試用**（任何平台，先關掉常駐的 Ollama）：

```bash
OLLAMA_CONTEXT_LENGTH=32768 ollama serve
```

> Ollama 桌面 app（macOS / Windows）的設定畫面裡也有一個 context length 滑桿，
> 效果和這個環境變數相同，圖形介面比較好操作。
> 滑桿和環境變數同時設定時誰優先（未實測），建議只用一種。

> 有一個會讓人困惑的地方：即使設了環境變數，server 啟動的 log **還是會印**
> `vram-based default context ... default_num_ctx=4096`。那行只是在報告「VRAM 推算出來的預設值」，
> 環境變數會在**載入模型時**覆蓋它。實測 `OLLAMA_CONTEXT_LENGTH=16384` 的 server，
> 用 `/v1` 且不帶任何參數載入模型後，`context_length` 確實是 `16384`。以 `ollama ps` 為準，不要看那行 log。

#### 路線二：用 Modelfile 做一個固定 num_ctx 的模型（建議）

不用動系統服務、不用 sudo、不影響其他模型，而且**透過 `/v1` 端點也一定生效**。
（路線一和路線二在本機都實測生效過；路線二勝在不用碰系統設定，
也不會影響你電腦上其他模型。）

建立一個檔案 `Modelfile`（沒有副檔名）：

```
FROM qwen3.5:9b-q4_K_M
PARAMETER num_ctx 32768
```

建立模型：

```bash
ollama create qwen3.5-32k -f ./Modelfile
```

檢查參數有沒有寫進去：

```bash
ollama show --parameters qwen3.5-32k
```

本機實際輸出：

```
presence_penalty               1.5
temperature                    1
top_k                          20
top_p                          0.95
num_ctx                        32768     ← 有這行就對了
```

對照原本的模型（`ollama show --parameters qwen3.5:9b-q4_K_M`）**沒有 `num_ctx` 這一行**，
那就代表它在用預設值。

這個做法不會複製一份權重，`ollama list` 裡新模型的 SIZE 和原模型一樣，
磁碟不會多佔 6.6GB。

### 設定 A：opencode 端的 limit.context

見下一節的設定檔。**這個數字要和 Ollama 那邊設的一樣。**

兩邊不一致會怎樣，方向不同後果差很多：

| 情況 | 後果 |
|---|---|
| `limit.context` **大於** 真實 `num_ctx` | **危險**。opencode 以為還有空間、還沒到 compaction 門檻，Ollama 卻已經安靜地丟掉前面的內容。模型莫名其妙變笨，**log 與 API 都沒有任何錯誤訊息** |
| `limit.context` **小於** 真實 `num_ctx` | 只是浪費。opencode 太早壓縮對話，模型其實吃得下更多 |
| 兩邊相同 | 正確 |

**寧可設小，不要設大。** 但最好就是設成一樣。

---

## 接到 opencode

在你的專案根目錄建立或修改 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3.5-32k": {
          "name": "Qwen3.5 9B (local, 32k)",
          "tool_call": true,
          "limit": {
            "context": 32768,
            "output": 8192
          }
        }
      }
    }
  },
  "model": "ollama/qwen3.5-32k",
  "permission": {
    "bash": "ask",
    "edit": "ask",
    "webfetch": "ask"
  },
  "instructions": ["AGENTS.md"]
}
```

幾個容易搞錯的地方：

- `"npm": "@ai-sdk/openai-compatible"`：Ollama 走的是 OpenAI 相容協定，這行是官方寫法。
- `baseURL` 結尾**要有 `/v1`**。少了它連不上。
- `models` 底下那個 key（這裡是 `qwen3.5-32k`）**必須和 `ollama list` 裡的名字完全一致**，
  這才是真正送給 Ollama 的 model id。旁邊的 `"name"` 只是給你自己看的顯示名稱。
- 頂層 `"model"` 用 `provider/model-id` 的格式，也就是 `"ollama/qwen3.5-32k"`。
- `limit.context` 和 `limit.output` 都是必填。`output` 是單次回覆上限，8192 夠用。
- `tool_call: true` 明確告訴 opencode 這個模型會呼叫工具。

> 驗證程度說明：上面這份設定檔在撰寫環境裡實測過，`opencode models ollama`
> 確實列出 `ollama/qwen3.5-32k`（代表設定檔語法與 provider 註冊都正確），
> `/v1` 端點的工具呼叫也實測通過。但**在撰寫環境裡沒有成功跑完一輪完整的 agent 任務**
> （`opencode run` 在無終端機的批次環境下沒有送出任何請求就結束）。
> 這一段的 opencode 端行為請當成「依官方文件與 schema 寫成、部分實測」（未實測完整 agent 回合）。

### 想保留雲端模型隨時切換

把 `"model"` 留成 `"opencode/big-pickle"`，需要時在 opencode 裡用 `/models` 切換，
或在指令列直接指定：

```bash
opencode run -m ollama/qwen3.5-32k "幫我看一下 lab1_cluster.py"
```

---

## 驗證有沒有設成功

**照順序跑，任何一步不對就先別往下走。**

### 1. Ollama 活著嗎

```bash
curl http://localhost:11434/api/version
```

### 2. 模型支援 tool calling 嗎

```bash
ollama show qwen3.5-32k | grep -A6 Capabilities
```

要看到 `tools`。沒有的話，換模型，不用再往下。

### 3. Modelfile 的 num_ctx 有寫進去嗎

```bash
ollama show --parameters qwen3.5-32k | grep num_ctx
```

要看到 `num_ctx    32768`。

### 4. 實際載入後真的是這個 context 嗎（最關鍵的一步）

先發一個請求把模型載入記憶體，**注意這個請求故意不帶任何 context 參數**，
就是要驗證設定檔有沒有生效：

```bash
curl -s http://localhost:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3.5-32k","messages":[{"role":"user","content":"hi"}]}' > /dev/null
```

趁模型還在記憶體裡馬上看（Ollama 預設會保留 5 分鐘，`ollama ps` 的 UNTIL 欄會倒數）：

```bash
ollama ps
```

本機實際輸出：

```
NAME                  ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen3.5-32k:latest    d4eb55d51d55    9.9 GB    100% GPU     32768      4 minutes from now
```

三件事要同時對：

- **CONTEXT 欄 = 32768**（不是 4096）。是 4096 就代表設定沒生效。
- **PROCESSOR = 100% GPU**。出現 `xx%/xx% CPU/GPU` 表示塞不下、溢出到 CPU 了，
  會非常慢，要把 num_ctx 調小或換小一點的模型。
- **SIZE** 就是實際佔用的記憶體，拿它跟你的 VRAM／RAM 比對。

### 5. 模型真的會呼叫工具嗎

繞過 opencode 直接測，這樣出問題時才知道是誰的錯：

```bash
curl -s http://localhost:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-32k",
    "messages": [{"role":"user","content":"列出目前目錄的檔案"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "bash",
        "description": "Run a shell command",
        "parameters": {
          "type": "object",
          "properties": {"command": {"type": "string"}},
          "required": ["command"]
        }
      }
    }]
  }' | python3 -m json.tool | grep -A8 tool_calls
```

正常的話會看到類似（本機實測輸出）：

```json
"tool_calls": [{
  "id": "call_17khfbth",
  "type": "function",
  "function": {"name": "bash", "arguments": "{\"command\":\"ls -la\"}"}
}]
```

如果 `tool_calls` 是 `null`，而模型在 `content` 裡「用文字描述」它要執行 `ls -la`，
那就是這個模型的 tool calling 能力太弱，換大一點的模型。

### 6. opencode 認得這個模型嗎

在放了 `opencode.json` 的目錄下：

```bash
opencode models ollama
```

應該印出 `ollama/qwen3.5-32k`。沒印出來就是設定檔寫錯或放錯目錄。

### 7. 確認內容沒有被安靜地截掉

**這一步的重點是：不要只看 log。** 前面實測過，走 `/v1/chat/completions`
（也就是 opencode 走的路）時，Ollama 截斷內容**不會印任何警告**。

可靠的做法是比對 `usage.prompt_tokens` 跟你送進去的量。送一份**故意超過 4096**
的請求，看它有沒有被吃掉：

```bash
# 產生一份約 10000 token 的請求
python3 -c "
import json
filler = '主成分分析會先把資料中心化，再對共變異數矩陣做特徵分解。' * 400
print(json.dumps({'model':'qwen3.5-32k',
 'messages':[{'role':'user','content': filler + '\n請只回答一個字：好'}]},
 ensure_ascii=False))" > big.json

curl -s http://localhost:11434/v1/chat/completions \
  -H 'Content-Type: application/json' --data-binary @big.json \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['usage'])"
```

`prompt_tokens` 應該是**八千到一萬**（確切數字取決於 tokenizer；本機實測這一段是
`{'prompt_tokens': 8018, ...}`）。如果它剛好停在 `4049` 這種貼著 4096 的數字，
就是被截斷了，回到第 3、4 步。

log 檢查仍然有用，但只對 `/api/generate` 那條路有效（例如你用 `ollama run` 手動測試時）：

```bash
# Linux / WSL2
journalctl -u ollama --since "10 minutes ago" | grep -i truncat
# 手動啟動的 server：直接看終端機輸出
```

如果看到這行，那是鐵證：

```
level=WARN source=runner.go:187 msg="truncating input prompt" limit=4096 prompt=10020 keep=4 new=4096
```

---

## 為什麼本地小模型常常「不聽話」

就算 context 設對了，小模型還是會做出一些雲端大模型不會做的蠢事。這跟你的設定無關，是 2B–9B 模型的能力天花板。認識這些模式，你才知道什麼時候該停止 debug、直接換模型。

### 常見失敗模式

**一、亂造不存在的工具名稱。**
opencode 的內建工具有固定名字：`read`、`write`、`edit`、`bash`、`glob`、`grep`、
`apply_patch`、`todowrite`、`webfetch`、`websearch`、`question`、`lsp`、`skill`。
小模型常常無視工具定義，自己發明 `execute`、`shell`、`run`、`terminal`、`run_command`、
`python` 這種「看起來很合理」的名字。因為它訓練時看過太多別的 agent 框架，
就直接套用印象中的名字。結果是工具呼叫失敗，agent 卡住或開始重試。

**二、把該呼叫工具的動作變成「把指令印出來」，或乾脆說自己做不到。**
本機實測，在明確給了 `bash` 工具定義、並要求「請執行 `ls -la`」的情況下，
`qwen3.5:9b` 回的是（原文）：

```
（說明）：作為語言模型，我無法在您的系統中執行命令，但這可能是一個測試或模擬情境。
```

`tool_calls` 是 `null`。它**沒有真的呼叫 `bash` 工具**，只輸出了一段文字。
值得注意的是：這在 context 開到 32k、內容完整送達的情況下**仍然會發生**。
這是小模型最常見的退化行為：退回成「聊天模型」，不再是「agent」。
換句話說，context 設對是必要條件，不是充分條件。

**三、只做一步就停。**
多步驟任務（讀檔 → 改 → 執行 → 看結果 → 修）常常在第一步之後就宣告完成。

**四、幻覺自己的執行結果。**
最危險的一種：它「假裝」執行過，然後**編造**一段輸出給你看。
前面 context 那一節的實測就是同一個毛病的另一面：資訊不在 context 裡時，
它不會說「我不知道」，而是很有自信地回答 `GOLF07`（正確答案是 `ALPHA1`）。
這正是工作坊主線 `AGENTS.md` 裡那條規則要防的：

> **自己驗證**：寫完數值方法後，必須附一段驗證程式碼，並實際執行、印出比對結果。
> 不可以只說「應該正確」。

### 對策：`AGENTS.md` 要為小模型加碼

雲端模型你只要講原則，小模型**必須把工具名稱明確寫死**。
在專案的 `AGENTS.md` 裡加一段（只有用本地模型時才需要）：

```markdown
## 工具使用規則（本地模型專用）

你只能使用以下工具，名稱必須完全一致：
read, write, edit, bash, glob, grep, todowrite

不存在的工具名稱包括（絕對不要使用）：
execute, shell, run, terminal, run_command, python, execute_command

### 重要
1. 要執行指令時，**呼叫 `bash` 工具**，不要把指令當成文字印出來給我看。
   「印出指令」不算完成任務。
2. 每次只做一件事，做完看實際結果，再決定下一步。
3. 沒有真的呼叫工具就不要報告結果。你不可以編造執行輸出。
4. 完成多步驟任務前，先用一句話列出你的步驟，然後一步一步做完。
```

**這種寫法對雲端大模型是囉嗦，對本地小模型是必要的。**

還有兩個實用招數：

- **把任務切小。** 不要說「幫我完成 lab1」，要說「讀 `lab1_cluster.py` 的第 1 到 40 行，
  告訴我 `kmeans` 函式在做什麼」。小模型的成功率跟任務長度成反比。
- **關掉不需要的權限。** `opencode.json` 裡把 `webfetch` 設成 `"deny"`，
  工具清單變短，工具定義佔的 context 變少，模型選錯工具的機會也變少。

### 什麼時候該放棄

如果調完 context、寫完 `AGENTS.md` 約束，模型還是：

- 連續三次叫出不存在的工具
- 一直用文字描述而不呼叫工具
- 讀檔讀到一半就忘記在做什麼

那就是**模型太小**，不是設定問題。往上換一級（2b → 4b → 9b），
或這次就用 `opencode/big-pickle` 把作業做完。**這不是失敗，是正確的工程判斷。**

---

## 卡住了？

| 症狀 | 最可能的原因 | 怎麼處理 |
|---|---|---|
| `connection refused` / opencode 連不上 | Ollama 沒在跑 | `systemctl status ollama`（Linux）或檢查系統列圖示；`curl http://localhost:11434/api/version` |
| `404` 或找不到模型 | `baseURL` 少了 `/v1`，或 `models` 的 key 跟 `ollama list` 的名字對不上 | 兩邊逐字比對 |
| `does not support tools` | 模型不支援 tool calling | `ollama show <模型>` 看有沒有 `tools`；換模型 |
| `ollama ps` 的 CONTEXT 是 4096 | `num_ctx` 沒設成功 | 用 Modelfile 路線重做，再跑一次驗證第 3、4 步 |
| 模型一直忘記前面的事 | context 被截斷 | 比對 `usage.prompt_tokens` 跟送進去的量（走 `/v1` 時 log 不會有警告）；把 num_ctx 調到 16k–32k |
| 內容明顯被截掉，但 log 一片乾淨 | 正常，`/v1/chat/completions` 的截斷不寫 log | 以 `usage.prompt_tokens` 和 `ollama ps` 的 CONTEXT 欄為準 |
| 模型很有自信地講錯資訊 | 資訊被擠出 context，模型改用編造填補 | 同上；context 調大，並把任務切小 |
| 模型叫出 `execute` / `shell` 這種工具 | 小模型的典型錯誤 | 在 `AGENTS.md` 加工具名稱約束；還是不行就換大一點的模型 |
| 模型只印出指令、不執行 | 退化成聊天模式 | 同上；並把任務切小 |
| 超級慢，風扇狂轉 | 溢出到 CPU 了 | `ollama ps` 看 PROCESSOR 是不是 100% GPU；調小 num_ctx 或換小模型 |
| 開大 context 後反而變慢 | KV cache 塞爆 VRAM | 看前面那張實測表；12GB 卡上 9B 模型的上限大約是 32k |
| 回答前先吐一長串思考過程 | `qwen3.5` 是 thinking 模型 | 思考 token 會吃 context 也吃時間。opencode 預設是否開啟 thinking（未實測），想關掉可換非 thinking 模型如 `granite4.1` |
| Mac 上改了環境變數沒反應 | app 沒完全重啟 | 從選單列 Quit 再開；或直接用 app 設定裡的 context length 滑桿 |
| Windows 改了環境變數沒反應 | 同上 | 從系統列結束 Ollama 再重開 |
| 磁碟快滿了 | 模型檔案很大 | `ollama list` 看清單，`ollama rm <模型>` 刪掉不用的 |

---

## 資料來源

- Ollama — Context length：<https://docs.ollama.com/context-length>
- Ollama — Context length（GitHub 原始檔）：<https://github.com/ollama/ollama/blob/main/docs/context-length.mdx>
- Ollama — FAQ：<https://docs.ollama.com/faq>
- Ollama — Modelfile 參考：<https://docs.ollama.com/modelfile>
- Ollama — Quickstart：<https://docs.ollama.com/quickstart>
- Ollama — Linux 安裝：<https://docs.ollama.com/linux>
- Ollama — 下載頁：<https://ollama.com/download>
- Ollama — 「New default context lengths will break」issue #14073：<https://github.com/ollama/ollama/issues/14073>
- Ollama library — 支援 tools 的模型：<https://ollama.com/search?c=tools>
- Ollama library — 模型總覽：<https://ollama.com/library>
- Ollama library — qwen3.5：<https://ollama.com/library/qwen3.5>／<https://ollama.com/library/qwen3.5/tags>
- Ollama library — granite4.1：<https://ollama.com/library/granite4.1/tags>
- Ollama library — llama3.2：<https://ollama.com/library/llama3.2/tags>
- Ollama library — gemma3：<https://ollama.com/library/gemma3>
- Ollama library — gemma3n：<https://ollama.com/library/gemma3n>
- opencode — Providers（Ollama 章節）：<https://opencode.ai/docs/providers/>
- opencode — Config：<https://opencode.ai/docs/config/>
- opencode — 內建工具清單：<https://opencode.ai/docs/tools/>
- opencode — Compaction（自動壓縮對話的觸發條件）：<https://opencode.ai/v2/docs/compaction>
- opencode — 設定檔 JSON schema：<https://opencode.ai/config.json>
- Ollama 原始碼 `server/prompt.go`（`chatPrompt` 的裁切策略）：<https://github.com/ollama/ollama/blob/main/server/prompt.go>

查證日期：2026-09-12。

本機實測環境：WSL2 Ubuntu 24.04 / Ollama 0.21.2 / opencode 1.18.30 /
RTX 5070 12GB / RAM 15GB / 模型 `qwen3.5:9b-q4_K_M`（9.7B、Q4_K_M、原生 context 262144）。

**文中以下內容為本機實際執行產生，非示意**：

- `ollama serve` 啟動 log 的 `vram-based default context ... total_vram="11.9 GiB" default_num_ctx=4096`
- `ollama ps` 在 num_ctx = 4096 / 16384 / 32768 / 65536 四種設定下的 SIZE 與 PROCESSOR（含 65536 溢出到 CPU）
- `/v1/chat/completions` 請求裡帶 `num_ctx` 與 `options.num_ctx` **被完全忽略**（CONTEXT 仍為 4096）
- `OLLAMA_CONTEXT_LENGTH=16384` 的 server：不帶任何參數載入後 `context_length` 為 16384
- Modelfile ＋ `ollama create` 路線：`ollama show --parameters` 出現 `num_ctx 32768`、`ollama ps` 的 CONTEXT 為 32768
- 4k vs 32k 的 BANANA7 / ALPHA1 / HOTEL8 對照實驗（含 `usage` 數字與模型回答原文）
- `/api/generate` 的 `truncating input prompt limit=4096 prompt=10020` WARN，以及
  **同樣狀況走 `/v1/chat/completions` 時 log 完全無輸出**
- `ollama show` 的 Capabilities 欄（`qwen3.5:9b-q4_K_M` 有 `tools`、`gemma3:1b` 只有 `completion`）
- `gemma3:1b` 收到帶 `tools` 的請求時回傳 `does not support tools` 的錯誤原文
- 「分層建議」表格裡的 8 個模型 tag，逐一以 `registry.ollama.ai` 的 manifest 查詢確認存在（HTTP 200）
- 支援／不支援 tool calling 的兩張表格，19 個模型逐一抓取 `ollama.com/library/<name>` 頁面，
  比對其 capability 標籤（`gemma3` 只有 vision；`gemma2`／`gemma3n`／`codegemma`／`phi3`／
  `tinyllama`／`smollm`／`falcon3`／`starcoder2` 皆無標籤；`gemma4`／`qwen3.5`／`granite4.1`／
  `llama3.2`／`qwen3`／`qwen2.5`／`qwen2.5-coder`／`phi4-mini`／`ministral-3`／`smollm2` 皆有 `tools`）
- Ollama `server/prompt.go` 的 `chatPrompt` 註解：裁切時保證保留最新訊息與 system 訊息
- `opencode models ollama` 確實列出設定檔裡的 `ollama/qwen3.5-32k`

**未實測、已在文中標註的部分**：

- 8GB / 16GB RAM 無獨顯機器、8GB VRAM 獨顯、Mac 的實際速度與可用 context（無對應硬體）
- Windows 與 macOS 的環境變數設定路徑、桌面 app 的 context length 滑桿，以及滑桿與環境變數的優先順序
- opencode 自動 compaction 的實際觸發時機（依官方文件敘述，未在本機觀察到）
- 用 opencode 對本地模型跑完一輪完整的 agent 任務（`opencode run` 在無終端機的批次環境下未送出請求）

````


# 全文讀者修正：移出的作者驗證與重複安裝內容

## content/first-run.md：重複安裝段

### 1.1 安裝（如果你還沒裝）

**Linux / WSL**：`curl` 不一定裝在你的系統裡（Ubuntu 的基本安裝不含它），
所以先用一定有的 `apt` 把它補上，再裝 opencode：

```bash
sudo apt update && sudo apt install -y curl ca-certificates
curl -fsSL https://opencode.ai/install | bash
```

**macOS**：內建 `curl`，直接跑第二行就好。

**Windows（PowerShell）**：`winget` 是 Windows 11 內建的，不用先裝東西。

```powershell
winget install SST.opencode --accept-source-agreements --accept-package-agreements
```

確認裝好了：

```bash
opencode --version
```

畫面有差異時，以你正在使用的指令面板為準。


## content/agents-md.md：自動載入的作者對照紀錄

這點我實際驗證過。建一個乾淨的資料夾，`opencode.json` 裡**完全沒有 `instructions` 這個鍵**：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle"
}
```

旁邊放一份只寫了「執行 Python 一律用 `uv run python <檔案>`」的 `AGENTS.md`，然後問它：

```bash
opencode run "用一句話回答：依照專案規則，執行 Python 檔案應該用哪一個指令？"
```

回答例子：

```
> build · big-pickle

`uv run python <檔案>`
```

**規則生效了，而設定檔裡一個字都沒提到 AGENTS.md。**


## content/agents-md.md：init 與 Git 的舊操作順序

本課程已提供 `AGENTS.md`，可以直接編輯；想試 `/init` 時，請在另一個練習資料夾操作，完成後閱讀它產生的規則。

如果你真的想試：

```bash
cd ~/ai-math-lab
git add -A
git commit -m "跑 /init 之前的存檔"   # 先存檔
# 然後在 opencode 裡打 /init
# 不滿意就：
git restore AGENTS.md
```

這正是下一章要講的 git 工作流。動手前先保存目前狀態，修改後才能比較與還原。


## content/git-safety.md：auto 舊限制文案

另外先講一個有關聯的設定。opencode 有個 `--auto` 參數，`--help` 裡它自己標註為「auto-approve permissions that are not explicitly denied (**dangerous!**)」。**學習階段絕對不要用它。** 逐次確認權限，加上這章的 git 工作流，是你目前最好的組合。


## tools/body_prep.html：平台版本比較表

<p>應該各自印出一個版本號。下面是輸出格式的例子，版本數字可以不同：</p>
<div class="tw"><table>
<tr><th></th><th>WSL (Ubuntu 24.04)</th><th>Windows 11</th></tr>
<tr><td>opencode</td><td><code>1.18.30</code></td><td><code>1.18.30</code></td></tr>
<tr><td>uv</td><td><code>0.12.x</code></td><td><code>0.12.13</code></td></tr>
</table></div>
