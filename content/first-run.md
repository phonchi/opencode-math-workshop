# 第一次對話

> 現場 30 分鐘

## 這一章你會學到

- 用一行指令啟動 opencode，看懂畫面上每一塊在說什麼
- 送出你的第一個指令，並且看懂 agent 是「先想、再動手、再回報」
- 在 agent 要改檔或跑指令時，看得懂權限對話框並做出選擇
- 知道 session 是什麼、什麼時候該開新的、context 快滿了怎麼辦

---

## 1. 啟動

### 1.1 先完成課前準備

這一章從已準備好的專案開始。尚未安裝 OpenCode、uv 或建立設定檔時，先完成 [課前準備](prep.html) 的自測，再回到這裡。

### 1.2 確認是同一個專案

開啟課前建立的 `ai-math-lab` 資料夾，在該處開啟終端機。它可能位於 Documents，也可能在你選的其他位置；請以自己的實際路徑為準。

```bash
pwd
ls
```

清單裡應有 `pyproject.toml`、`opencode.json` 與 `AGENTS.md`。

檢查環境：

```bash
uv run python -c "import numpy, sklearn, matplotlib, networkx; print('環境 OK')"
```

這個專案一律用 `uv run python 檔名.py` 執行程式，不要用 `python`、`python3`，也不要用 `pip install`。要加套件用 `uv add 套件名`。這條規則已經寫在專案的 `AGENTS.md` 裡；執行時仍請看一下它用的指令。

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

`opencode run` 丟一句話進去、印出結果就結束。本專案將改檔與執行設為 `ask`，非互動模式遇到這些動作會自動拒絕。練習請用 `opencode`，逐次查看與回答權限要求。

### 1.4 模型不用設定

這個專案的 `opencode.json` 已經把模型指定成 `opencode/big-pickle`：

```json
{
  "model": "opencode/big-pickle"
}
```

`big-pickle` 不用登入、不用 API key、不用信用卡。啟動後畫面上會有一行提示 `Run /connect to add an AI provider and start coding`，**忽略它**。那是給要接自己帳號的人看的，你不需要。

---

## 2. 認識畫面

啟動後還沒開始對話時，畫面大概長這樣（位置會隨終端機寬度調整）：

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

`8% used` 表示目前使用了多少 context 空間。底部狀態列也會同步顯示成 `16.0K (8%)`。第 5 節會用到它。

`$0.00 spent` 表示這次對話目前沒有列出費用。課堂只選指定的免費模型；若服務要求付費或連接帳號，先停下來請講師確認。

終端機太窄時，部分資訊會收起來。把視窗拉寬，或在 `ctrl+p` 指令面板尋找側邊欄選項。

### 輸入框的三個特殊開頭字元

| 打什麼 | 會發生什麼 | 例子 |
|---|---|---|
| `/` | 跳出斜線指令清單 | `/models` |
| `@` | 補檔名，也可以叫 subagent | 打 `@AGENT` 會補成 `@AGENTS.md`；`@explore`、`@general` 是 subagent |
| `!` | 進入 Shell 模式，直接在這裡跑 shell 指令，底部會顯示 `esc exit shell mode`，按 `Esc` 退出 | `!ls -la` |

---

<!--DIAGRAM:agent-task-->

## 3. 你的第一個指令

### 3.1 先問一個不用動手的問題

在輸入框打下面這句，按 `Enter`：

```text
請讀 AGENTS.md，用三句話說明這個專案的規矩
```

你會看到三件事：

1. **agent 先「想」**。畫面上會出現一段淺色的思考過程（Thought），說它打算怎麼做。
2. **它用了工具**。你會看到 `read` 之類的工具呼叫列出來。
3. **它用繁體中文回答**。這不是巧合：`AGENTS.md` 裡寫了「一律使用台灣繁體中文回答」，agent 啟動時就把這個檔讀進去了。請核對它是否照著規則回應。

這一句只是讀檔，不會跳出權限對話框。

### 3.2 再下一個要動手的指令

```
請用 uv run python 印出 numpy 的版本
```

這次不一樣：agent 要跑 shell 指令，所以會停下來問你。往下看第 4 節。

### 3.3 一個完整的三步任務

接著試一個同時需要讀檔、寫檔與執行的任務：

```text
讀 pyproject.toml，在 notes/ 寫一個 環境說明.md，列出這個專案用到的套件。
然後執行 uv run python -c "import numpy; print(numpy.__version__)"
確認環境真的跑得起來。
```

跑的過程中如果你想停下來：按 `Esc`。**注意按一次不夠**。底部會從 `esc interrupt` 變成 `esc again to interrupt`，要再按一次才真的中斷（如果它正在執行工具，請等畫面確認中斷）。

### 3.4 打多行字

輸入框裡按 `Enter` 就送出了。要換行不送出，按 **`ctrl+j`**。`shift+Enter`、`alt+Enter`、`ctrl+Enter` 也綁著同樣的功能，但有些終端機吃不到這幾組，`ctrl+j` 最保險。

要打很長的一段（例如整段數學推導），用 `/editor` 或 `ctrl+x e` 開你平常用的編輯器來寫。

### 3.5 想重打上一句

輸入框空的時候按 `↑`，會把你上一句話叫回來。

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

權限要求的畫面例子：

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

- **`opencode run` 沒有互動權限對話框**。本專案設為 `ask` 的動作會自動拒絕；設成 `allow` 或使用 `--auto` 時才可能直接執行。練習階段用 `opencode`。
- **`--auto` 這個參數不要加**。`opencode --auto` 會自動同意所有沒被明確 `deny` 的請求，官方文件自己標註 `dangerous!`。

### 4.5 順便說 agent 模式

按 `Tab` 可以在兩個 agent 之間切換，畫面左下角的 `Build · Big Pickle` 會跟著變成 `Plan · Big Pickle`。

| agent | 用來做什麼 |
|---|---|
| `Build` | 預設。可以讀、可以改、可以跑指令。工作坊全程用這個 |
| `Plan` | 官方說明是 `Plan mode. Disallows all edit tools.`，內建權限把 `edit` 設成 `deny`（只允許寫 `.opencode/plans/*.md`），適合先讓它分析、不要動你的檔案 |

模式與專案設定會共同影響權限。現場需要實際產生檔案時用 `Build`；先規劃時可用 `Plan`，仍要閱讀工具與權限提示。

---

## 5. session：對話的記憶邊界

### 5.1 session 是什麼

一個 session 就是一串獨立的對話，有自己的記憶。opencode 把它存在本機（`~/.local/share/opencode/opencode.db`，來源：learnopencode.com），所以你關掉終端機之後還找得回來。

agent 的「記憶」只有這個 session 裡的訊息，加上它自己去讀的檔案。換了 session，前面講的話它就不知道了。

### 5.2 什麼時候該開新 session

**換題目就開新的。** 做完 Lab 1 的分群要開始做 Lab 2 的 PCA，就開新 session。理由有兩個：

- 舊對話會一直佔 context，愈用愈慢、愈容易被壓縮掉細節
- 不相干的舊內容會干擾判斷（例如它以為你還要繼續做分群）

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

壓縮對話可以用其中一種操作：

- 按 `ctrl+x c`
- 或按 `ctrl+p` 開指令面板，搜尋 `compact`，選 `Compact session`

注意：指令面板裡的 session 相關指令**要先有對話才會出現**。在剛啟動的首頁按 `ctrl+p` 搜 `compact` 會顯示 `No results found`。

也可能由程式自動壓縮對話；不必等它觸發，重要結論先寫成檔案。要練習完整的續作流程，接著看 [把需求說清楚，讓工作接得下去](agent-workflows.html)。

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

## 6. 先記住這些操作

| 操作 | 用途 |
|---|---|
| `ctrl+p` | 打開指令面板，找不到功能時從這裡搜尋 |
| `ctrl+j` | 在同一段任務裡換行 |
| `Tab` | 切換目前的主要 agent 模式，切換後查看畫面標示 |
| `Esc`，再按一次 | 中斷正在進行的回應；看到中斷提示後確認工作已停下 |
| `/new` | 開新的對話 |
| `/sessions` | 找回既有對話 |
| `/exit` | 離開 OpenCode |

其他指令放在 [速查表](cheatsheet.html)，用到再查即可。按 `ctrl+x c` 壓縮對話時，先按 `ctrl+x`、放開，再按 `c`。

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
| agent 改檔或執行前沒有問我 | 權限可能是 `allow`，或啟動時加了 `--auto` | 確認專案設定為 `ask`，重新用 `opencode` 啟動，不加 `--auto` |
| 跑 `python xxx.py` 說找不到套件 | 沒走 uv 的環境 | 一律用 `uv run python xxx.py` |
| 側邊欄的 Context / tokens 看不到 | 終端機視窗太窄，側邊欄自動收起來了 | 把視窗拉寬，或在 `ctrl+p` 搜尋側邊欄 |
| `% used` 已經很高，agent 開始忘記前面講過的事 | context 快滿了 | 換題目就 `/new`；同一題就按 `ctrl+x c` 壓縮，壓縮前先把結論寫進 `notes/` |
| 找不到某個斜線指令 | 功能名稱或位置會隨介面調整 | 用 `ctrl+p` 開啟指令面板搜尋；壓縮對話也可按 `ctrl+x c` |

---

## 參考資料

- [OpenCode 操作介面](https://opencode.ai/docs/tui/)
- [OpenCode 權限](https://opencode.ai/docs/permissions/)
- [OpenCode 快捷鍵](https://opencode.ai/docs/keybinds/)
- [中文入門教學](https://learnopencode.com/1-start/)

找不到指令時，按 `ctrl+p` 開啟指令面板搜尋。
