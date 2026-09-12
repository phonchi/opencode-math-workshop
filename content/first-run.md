# 第一次對話

> 現場 30 分鐘

## 這一章你會學到

- 用一行指令啟動 opencode，看懂畫面上每一塊在說什麼
- 送出你的第一個指令，並且看懂 agent 是「先想、再動手、再回報」
- 在 agent 要改檔或跑指令時，看得懂權限對話框並做出選擇
- 知道 session 是什麼、什麼時候該開新的、context 快滿了怎麼辦

---

## 1. 啟動

### 1.1 安裝（如果你還沒裝）

Linux / macOS / WSL：

```bash
curl -fsSL https://opencode.ai/install | bash
```

Windows（PowerShell）：

```powershell
winget install SST.opencode --accept-source-agreements --accept-package-agreements
```

確認裝好了：

```bash
opencode --version
```

本章所有內容都在 `1.18.30` 上實測。如果你的版本號不一樣，畫面可能會有差別。

### 1.2 建好 Python 環境

進到工作坊的專案資料夾（講師發的那個，例如 `ai-math-lab`），先把 Python 環境裝起來（第一次會跑幾分鐘）：

```bash
uv sync
```

檢查環境：

```bash
uv run python -c "import numpy, sklearn, matplotlib, networkx; print('環境 OK')"
```

這個專案一律用 `uv run python 檔名.py` 執行程式，不要用 `python`、`python3`，也不要用 `pip install`。要加套件用 `uv add 套件名`。這條規則已經寫在專案的 `AGENTS.md` 裡，agent 自己會遵守。

### 1.3 兩種啟動方式

**互動模式（本章都用這個）**：

```bash
opencode
```

直接進入 TUI（終端機介面），可以一句一句對話，agent 要動手之前會停下來問你。

**非互動模式（先知道有這個就好，這一章不要用）**：

```bash
opencode run "讀 pyproject.toml，用一句話說明這個專案裝了哪些套件"
```

`opencode run` 丟一句話進去、印出結果就結束。實測它**不會問權限**，會直接寫檔、直接執行指令。所以在你還不熟的階段，一律用 `opencode`（互動模式）。

### 1.4 模型不用設定

這個專案的 `opencode.json` 已經把模型指定成 `opencode/big-pickle`：

```json
{
  "model": "opencode/big-pickle"
}
```

`big-pickle` 不用登入、不用 API key、不用信用卡。啟動後畫面上會有一行提示 `Run /connect to add an AI provider and start coding` ——**忽略它**。那是給要接自己帳號的人看的，你不需要。

---

## 2. 認識畫面

啟動後還沒開始對話時，畫面大概長這樣（實測擷取，位置會隨終端機寬度調整）：

```
                              █▀▀█ █▀▀█ █▀▀█ █▀▀▄ █▀▀▀ █▀▀█ █▀▀█ █▀▀█
                              █  █ █  █ █▀▀▀ █  █ █    █  █ █  █ █▀▀▀
                              ▀▀▀▀ █▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀

      ┃
      ┃  Ask anything… "What is the tech stack of this project?"
      ┃
      ┃  Build · Big Pickle OpenCode Zen
      ╹▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                                       tab agents  ctrl+p commands

              ● Tip Run /connect to add an AI provider and start coding

  /home/you/ai-math-lab                                          1.18.30
```

由上往下看：

| 畫面上的東西 | 意思 |
|---|---|
| `Ask anything…` | 輸入框。游標在這裡，直接打字就行 |
| `Build · Big Pickle OpenCode Zen` | 現在用的 **agent**（Build）· **模型**（Big Pickle）· **供應商**（OpenCode Zen） |
| `tab agents` | 按 `Tab` 可以換 agent |
| `ctrl+p commands` | 按 `ctrl+p` 開指令面板 |
| 最底左邊 | 你現在在哪個資料夾。**開始之前先確認這行是對的** |
| 最底右邊 | opencode 版本 |

開始對話之後，右邊會多出一欄側邊欄：

```
                                     列出資料夾內所有檔案     <- session 名稱（自動命名）

                                     Context
                                     16,007 tokens
                                     8% used
                                     $0.00 spent

                                     LSP
                                     LSPs are disabled
```

`8% used` 是**這一章最重要的一個數字**：它是目前對話佔掉模型記憶上限的百分比。底部狀態列也會同步顯示成 `16.0K (8%)`。第 5 節會用到它。

`$0.00 spent` 因為 `big-pickle` 是免費的，所以永遠是 0。

側邊欄在終端機太窄的時候會自動收起來，可以用 `ctrl+x b` 開關（未實測）。

### 輸入框的三個特殊開頭字元

| 打什麼 | 會發生什麼 | 例子 |
|---|---|---|
| `/` | 跳出斜線指令清單 | `/models` |
| `@` | 補檔名，也可以叫 subagent | 打 `@AGENT` 會補成 `@AGENTS.md`；`@explore`、`@general` 是 subagent |
| `!` | 進入 Shell 模式，直接在這裡跑 shell 指令，底部會顯示 `esc exit shell mode`，按 `Esc` 退出 | `!ls -la` |

---

## 3. 你的第一個指令

### 3.1 先問一個不用動手的問題

在輸入框打下面這句，按 `Enter`：

```
請讀 AGENTS.md，用三句話說明這個專案的規矩
```

你會看到三件事：

1. **agent 先「想」**。畫面上會出現一段淺色的思考過程（Thought），說它打算怎麼做。
2. **它用了工具**。你會看到 `read` 之類的工具呼叫列出來。
3. **它用繁體中文回答**。這不是巧合——`AGENTS.md` 裡寫了「一律使用台灣繁體中文回答」，agent 啟動時就把這個檔讀進去了。實測確認有效。

這一句只是讀檔，不會跳出權限對話框。

### 3.2 再下一個要動手的指令

```
請用 uv run python 印出 numpy 的版本
```

這次不一樣：agent 要跑 shell 指令，所以會停下來問你。往下看第 4 節。

### 3.3 一個完整的三步任務

講師實測 `big-pickle` 跑一個「讀檔 → 寫檔 → 執行」的三步任務大約 **7.4 秒**。你可以試這個：

```
讀 pyproject.toml，在 notes/ 寫一個 環境說明.md 列出這個專案用到的套件，然後用 uv run python -c "import numpy; print(numpy.__version__)" 確認環境能跑
```

跑的過程中如果你想停下來：按 `Esc`。**注意按一次不夠**——底部會從 `esc interrupt` 變成 `esc again to interrupt`，要再按一次才真的中斷（實測；如果它正在執行工具，可能要多按幾次）。

### 3.4 打多行字

輸入框裡按 `Enter` 就送出了。要換行不送出，按 **`ctrl+j`**（實測可用）。`shift+Enter`、`alt+Enter`、`ctrl+Enter` 也綁著同樣的功能，但有些終端機吃不到這幾組，`ctrl+j` 最保險。

要打很長的一段（例如整段數學推導），用 `/editor` 或 `ctrl+x e` 開你平常用的編輯器來寫。

### 3.5 想重打上一句

輸入框空的時候按 `↑`，會把你上一句話叫回來（實測）。

---

## 4. 權限：agent 要動手之前會先問你

### 4.1 你會看到什麼

你的 `opencode.json` 裡有這段：

```json
{
  "permission": {
    "bash": "ask",
    "edit": "ask",
    "webfetch": "ask"
  }
}
```

意思是：agent 要**跑指令**（bash）、**改檔案**（edit）、**上網抓資料**（webfetch）之前，都要先問你。

實測畫面（1.18.30）：

```
  ┃  △ Permission required
  ┃    # Shell command
  ┃
  ┃  $ ls -la
  ┃
  ┃   Allow once   Allow always   Reject      ctrl+f fullscreen  ⇆ select  enter confirm
```

### 4.2 怎麼回答

| 選項 | 意思 | 工作坊建議 |
|---|---|---|
| `Allow once` | 只允許這一次 | **每次都選這個**。你才會看到 agent 到底做了哪些事 |
| `Allow always` | 這個 session 之後同類的請求都不再問 | 熟了之後再用 |
| `Reject` | 拒絕。agent 會換別的做法或停下來 | 看到不該跑的指令就選這個 |

操作方式：用方向鍵或 `Tab`（畫面提示的 `⇆ select`）移動，按 `Enter` 確認。預設游標在 `Allow once`，所以看完指令沒問題就直接按 `Enter`。

指令太長被截掉的時候，按 `ctrl+f` 全螢幕看完整內容。

### 4.3 三個值的意思

`opencode.json` 裡每個權限可以設成三個值之一：

| 值 | 行為 |
|---|---|
| `"allow"` | 不問，直接做 |
| `"ask"` | 跳對話框問你 |
| `"deny"` | 直接擋掉，agent 不能做 |

也可以針對指令樣式分開設定，例如允許 `git status` 但禁止 `rm`：

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "rm *": "deny"
    }
  }
}
```

比對樣式時**最後一條符合的規則生效**。（來源：opencode.ai/docs/permissions）

### 4.4 兩個要記住的例外

- **`opencode run` 完全不會問**。它是非互動模式，直接寫檔、直接執行。所以練習階段用 `opencode`。
- **`--auto` 這個參數不要加**。`opencode --auto` 會自動同意所有沒被明確 `deny` 的請求，官方文件自己標註 `dangerous!`。

### 4.5 順便說 agent 模式

按 `Tab` 可以在兩個 agent 之間切換，畫面左下角的 `Build · Big Pickle` 會跟著變成 `Plan · Big Pickle`（實測）。

| agent | 用來做什麼 |
|---|---|
| `Build` | 預設。可以讀、可以改、可以跑指令。工作坊全程用這個 |
| `Plan` | 官方說明是 `Plan mode. Disallows all edit tools.`，內建權限把 `edit` 設成 `deny`（只允許寫 `.opencode/plans/*.md`），適合先讓它分析、不要動你的檔案 |

`Plan` 的內建 `deny` 和本專案 `opencode.json` 裡的 `edit: "ask"` 疊在一起之後的實際結果，本章沒有實測。工作坊請用 `Build`。

---

## 5. session：對話的記憶邊界

### 5.1 session 是什麼

一個 session 就是一串獨立的對話，有自己的記憶。opencode 把它存在本機（`~/.local/share/opencode/opencode.db`，來源：learnopencode.com），所以你關掉終端機之後還找得回來。

agent 的「記憶」只有這個 session 裡的訊息，加上它自己去讀的檔案。換了 session，前面講的話它就不知道了。

### 5.2 什麼時候該開新 session

**換題目就開新的。** 做完 Lab 1 的分群要開始做 Lab 2 的 PCA，就開新 session。理由有兩個：

- 舊對話會一直佔 context，愈用愈慢、愈容易被壓縮掉細節
- 不相干的舊內容會干擾判斷（例如它以為你還在用 Lab 1 的資料）

開新 session：

```
/new
```

或按 `ctrl+x n`。

### 5.3 context 滿了怎麼辦

看側邊欄的 `% used`（或底部的 `16.0K (8%)`）。判斷方式：

- **換題目了** → `/new`（`ctrl+x n`）
- **同一個題目還沒做完，但 `% used` 已經很高** → 壓縮（compact）

壓縮會讓 agent 把前面的對話摘要成一小段，然後把舊訊息清掉，留下摘要繼續做。細節會流失，所以重要的結論要先寫進 `notes/` 裡的 `.md` 檔，不要只留在對話裡。

在 1.18.30，壓縮**沒有斜線指令**，要用其中一種：

- 按 `ctrl+x c`
- 或按 `ctrl+p` 開指令面板，搜尋 `compact`，選 `Compact session`

注意：指令面板裡的 session 相關指令**要先有對話才會出現**。在剛啟動的首頁按 `ctrl+p` 搜 `compact` 會顯示 `No results found`（實測）。

learnopencode.com 提到對話太長時 opencode 也會自動觸發壓縮（未實測）。

### 5.4 回到舊 session

```
/sessions
```

或按 `ctrl+x l`。別名 `/resume`、`/continue` 也是同一個指令。session 名稱是 opencode 依你第一句話自動取的，會顯示在右上角。

如果你已經離開 opencode 了，在終端機下：

```bash
opencode        # 進來後用 /sessions 挑
opencode -c     # 直接接續上一個 session
```

---

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

離開 opencode 請打 `/exit`。不要習慣性連按兩下 `ctrl+c`——輸入框一空掉，第二下就把程式關了。

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

## 卡住了？

| 你看到的 | 為什麼 | 怎麼解 |
|---|---|---|
| `Error: Internal server error` | 這是預設的錯誤訊息，什麼資訊都沒有 | 加上 log 參數重跑：`opencode run "訊息" --print-logs --log-level ERROR`，才看得到真正的原因 |
| `Unrecognized request argument supplied: prompt_cache_key` | 上游的 bug，偶發 | **重試一次就好**。不用改任何設定 |
| 畫面底部一直顯示 `esc again to interrupt` | 你只按了一次 `Esc`，還沒真的中斷 | 再按一次 `Esc`。如果它正在跑工具，多按幾次 |
| opencode 突然關掉了 | 輸入框是空的時候按了 `ctrl+c`，那就是「離開」 | 重新 `opencode`，再用 `/sessions`（`ctrl+x l`）找回剛剛的對話，或直接 `opencode -c` |
| `● Tip Run /connect to add an AI provider` | 這是給要接自己帳號的人看的提示 | 忽略。`big-pickle` 不用連任何 provider |
| agent 用簡體中文或英文回答 | 它沒讀到 `AGENTS.md` | 確認你是在專案資料夾裡啟動的（看畫面最底左邊那行路徑），不是在家目錄 |
| agent 直接改了檔案、沒問我 | 你用的是 `opencode run` | 改用 `opencode`（互動模式）。也確認沒有加 `--auto` |
| 跑 `python xxx.py` 說找不到套件 | 沒走 uv 的環境 | 一律用 `uv run python xxx.py` |
| 側邊欄的 Context / tokens 看不到 | 終端機視窗太窄，側邊欄自動收起來了 | 把視窗拉寬，或按 `ctrl+x b`（未實測） |
| `% used` 已經很高，agent 開始忘記前面講過的事 | context 快滿了 | 換題目就 `/new`；同一題就按 `ctrl+x c` 壓縮，壓縮前先把結論寫進 `notes/` |
| `/compact`、`/undo`、`/share` 打了沒反應 | 1.18.30 沒有這幾個斜線指令 | 用 `ctrl+x c`、`ctrl+x u`，或 `ctrl+p` 開指令面板搜尋 |

---

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
