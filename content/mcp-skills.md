# 再往前一步：MCP、自訂 agent、subagent

> 課後延伸．**加分項，不是必修**
> 適用版本：opencode 1.18.30

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

## 1. 三個東西各解決什麼問題

初學者最容易混淆這三個名詞。一句話講清楚差別：

| | 一句話 | 解決的問題 |
|---|---|---|
| **MCP** | 給 agent **新的工具**（外部能力） | 它**做不到**某件事 |
| **自訂 agent** | 給 agent **新的人格**（專屬指令與權限） | 它**做得到，但做事方式**不對 |
| **subagent** | 把工作**拆給另一個對話**去做 | 它**能做，但一次做太多**會亂 |

用一個具體場景串起來：

> 你在寫 PCA 的作業。
>
> - agent 不知道 scikit-learn 新版的 API 怎麼用，它的知識停在舊版 → **MCP**（接一個能查即時套件文件的工具）
> - 你想要一個「只檢查數學對不對、絕對不准改你程式」的審查員 → **自訂 agent**（定義一個唯讀的 reviewer）
> - 主線在寫 PCA，但你想順便查一下三份參考程式裡哪裡用到隨機性 → **subagent**（丟給子任務去翻，不要用這些細節污染主對話）

再換個比喻：MCP 是**多給它一隻手**，自訂 agent 是**換一個專家來**，subagent 是**找人分頭辦事**。

---

## 2. MCP：給 agent 新的工具

### 這是什麼

MCP（Model Context Protocol）是一套標準協定，讓 agent 能連上外部服務取得能力。opencode 本身只有讀檔、寫檔、執行指令、抓網頁這些內建工具。接上 MCP server 之後，agent 就多了那個 server 提供的工具。

### 對數學/研究最有用的例子：查套件文件

這是我實際測試過、確認能用的例子。

**問題**：`opencode/big-pickle` 和所有模型一樣，知識有時間截止點。你問它 scikit-learn 某個參數怎麼用，它可能給你一個兩年前的 API，跑起來噴 `TypeError`。你也可以叫它用 `webfetch` 去抓文件，但那是抓整頁 HTML，又慢又雜。

**解法**：接上 Context7，它專門提供**套件的即時文件查詢**，agent 可以直接查 numpy、scipy、scikit-learn、matplotlib 的當前 API。

在專案根目錄的 `opencode.json` 加上 `mcp` 區塊：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle",
  "permission": { "bash": "ask", "edit": "ask", "webfetch": "ask" },
  "instructions": ["AGENTS.md"],
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```

存檔後驗證：

```bash
cd ~/ai-math-lab
opencode mcp list
```

實測輸出：

```
┌  MCP Servers
│
●  ✓ context7 connected
│      https://mcp.context7.com/mcp
│
└  1 server(s)
```

看到 `connected` 就成功了。**這個 server 不需要註冊、不需要 API key、不需要付費**，和 `opencode/big-pickle` 一樣可以直接用。

接上之後可以這樣問：

```text
scikit-learn 最新版的 PCA，取得解釋變異比例的屬性叫什麼？查文件確認再回答。
```

### 兩種 MCP：remote 與 local

**remote**：連到別人架好的網路服務。你不用安裝任何東西。

```json
{
  "mcp": {
    "my-remote-mcp": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

- `url`（必填）：server 網址
- `headers`（選填）：需要金鑰時用。**注意 `{env:MY_API_KEY}` 這種寫法**：它會去讀環境變數，**不要把金鑰直接寫進 `opencode.json`**，因為那個檔案會進 git。
- `enabled`（選填）：設 `false` 可暫時關掉而不用刪設定
- `timeout`（選填）：取得工具清單的逾時毫秒數
- `oauth`（選填）：需要 OAuth 授權時用，設 `false` 可停用自動偵測

**local**：在你電腦上跑一個程式當 server。

```json
{
  "mcp": {
    "my-local-mcp": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
      "enabled": true,
      "environment": {
        "MY_ENV_VAR": "value"
      }
    }
  }
}
```

- `command`（必填）：**陣列**，不是字串。`["npx", "-y", "套件名"]`
- `environment`（選填）：環境變數
- `cwd`（選填）：工作目錄

上面那個 `server-everything` 是官方的測試用 server，拿來確認 MCP 機制有沒有通就好，本身沒有實用功能。

**這門課建議只用 remote**，因為 local 需要 Node.js 環境、要下載套件，多一層可能出錯的地方。

### `opencode mcp` 這個 CLI

實測 1.18.30 有這些子指令：

```bash
opencode mcp add [name]      # 新增 MCP server
opencode mcp list            # 列出所有 server 與連線狀態（別名 ls）
opencode mcp auth [name]     # 對支援 OAuth 的 server 進行認證
opencode mcp logout [name]   # 移除已儲存的 OAuth 憑證
opencode mcp debug <name>    # 偵錯 OAuth 連線問題
```

**最常用的是 `opencode mcp list`**，改完設定就跑一次確認狀態。可能的狀態有 `connected`、`disabled`、`failed`、`needs_auth`、`needs_client_registration`。

### 排錯

| 症狀 | 原因 | 解法 |
|---|---|---|
| `failed` | 網址錯或服務掛了 | 檢查 `url` 拼字，用瀏覽器試連 |
| 連線逾時 | 網路慢 | 加大 `timeout` 值 |
| `needs_auth` | 需要認證 | `opencode mcp debug <name>` |
| local server 起不來 | `command` 寫錯或找不到執行檔 | 確認是**陣列**格式，確認 `npx` 在 PATH 裡 |
| 設定改了沒反應 | 檔案格式錯誤 | `opencode debug config` 看有沒有讀進去 |

### 什麼時候不該加 MCP

**每個 MCP 都會把它的工具清單塞進 context**，工具一多，模型挑錯工具的機率就上升，也會排擠掉你真正的問題內容。

**原則：只加你這禮拜真的會用到的。** 不要因為看起來很酷就接五個。這門課接一個 Context7 就夠了，甚至不接也完全能完成作業。

---

## 3. 自訂 agent：換一個專家來

### 這是什麼

opencode 內建了幾個 agent。實測 1.18.30 用 `opencode agent list` 可以看到：

```
build (primary)
plan (primary)
explore (subagent)
general (subagent)
```

（另外還有 `compaction`、`summary`、`title` 等內部用的，不用管。）

- **primary agent** 是你直接對話的對象，在介面裡按 **Tab** 切換。`build` 是預設，權限全開；`plan` 只規劃不動手（檔案編輯與 bash 預設是 `ask`）。
- **subagent** 是被主 agent 呼叫去做特定工作的。`explore` 唯讀探索程式碼，`general` 通用。

**自訂 agent 就是自己定義一個**，給它專屬的系統提示、溫度和權限。

### 檔案放哪裡

```
專案層：<專案根目錄>/.opencode/agents/<名字>.md
全域：  ~/.config/opencode/agents/<名字>.md
```

**檔名就是 agent 的名字。** `math-reviewer.md` 會產生一個叫 `math-reviewer` 的 agent。專案層優先於全域。

> 實測補充：1.18.30 底下 `.opencode/agent/`（單數）和 `.opencode/agents/`（複數）**兩種目錄名都能被載入**。文件寫的是複數，**建議統一用 `agents/`**，不要混用，免得以後找不到自己的檔案放哪。

### 什麼情況值得做

老實說，**大部分情況不值得**。你在 AGENTS.md 裡多寫一條規則，通常就解決了。

值得做的是這種情形：**你需要一個權限跟主 agent 不同的角色。** 這是 AGENTS.md 做不到的。AGENTS.md 是全專案共用的提示，而 agent 可以有自己的權限設定。

最典型的例子就是「**只做數學驗證的 reviewer**」：你想要一個看得到你的程式、但**在機制上不可能改你的程式**的審查員。

### 完整範例：數學驗證 reviewer

建立 `.opencode/agents/math-reviewer.md`：

```markdown
---
description: 檢查數學程式的正確性與可重現性，只讀不改
mode: subagent
temperature: 0.1
permission:
  edit: deny
  bash: deny
---

你是數學驗證審查員。你的工作是**檢查**，不是修改。

檢查以下項目，逐項回報「通過」或「有問題」，有問題要指出行號：

1. **數學正確性**：公式與演算法步驟是否正確？矩陣維度是否對得起來？
2. **可重現性**：所有用到隨機性的地方是否都有固定種子（`random_state=0`
   或 `np.random.seed(0)`）？
3. **有沒有偷懶**：如果程式宣稱是「手刻」實作，檢查是否偷偷呼叫了
   sklearn 的對應函式來充數。
4. **數值穩定性**：有沒有除以可能為零的量？有沒有對可能為負的數開根號？
   大數相減造成的抵消誤差？
5. **驗證段落**：有沒有附上驗證程式碼，並且是真的執行過、印出比對結果，
   而不只是宣稱「應該正確」？

回報格式：用台灣繁體中文，條列，每一項先寫結論再寫理由。
不要修改任何檔案。不要執行任何指令。
```

**驗證它有沒有被正確載入**（實測可用）：

```bash
cd ~/ai-math-lab
opencode agent list                    # 看 math-reviewer 有沒有出現
opencode debug agent math-reviewer     # 看解析後的完整設定
```

`opencode debug agent math-reviewer` 的實測輸出裡可以確認這些欄位都正確生效：

```json
{
  "name": "math-reviewer",
  "mode": "subagent",
  "description": "檢查數學程式的正確性與可重現性，只讀不改",
  "temperature": 0.1,
  "prompt": "你是數學驗證審查員。..."
}
```

而且權限規則裡確實出現了：

```json
{ "permission": "edit", "action": "deny", "pattern": "*" }
{ "permission": "bash", "action": "deny", "pattern": "*" }
```

**這就是自訂 agent 相對於 AGENTS.md 的關鍵優勢**：`edit: deny` 是機制上的封鎖，不是口頭請求。這個 reviewer 在技術上就是不可能改到你的程式。

### 怎麼用它

在 opencode 對話裡用 `@` 呼叫：

```
@math-reviewer 檢查 lab2_pca.py 的手刻 PCA 有沒有問題
```

主 agent 也可能根據 `description` 自動判斷要不要叫它，所以 `description` 要寫清楚這個 agent 適合做什麼。

### frontmatter 可用的欄位

| 欄位 | 說明 |
|---|---|
| `description` | 這個 agent 做什麼。**主 agent 靠它判斷要不要呼叫**，要寫清楚 |
| `mode` | `subagent`（被呼叫）或 `primary`（Tab 切換） |
| `model` | 指定模型。**這門課請省略**，省略就沿用 `opencode/big-pickle` |
| `temperature` | 0 到 1。驗證、審查類的工作用低值（0.1），創意類用高值 |
| `prompt` | 用 `{file:./prompts/xxx.txt}` 從外部檔案讀系統提示 |
| `permission` | 權限覆寫，會蓋過全域設定 |
| `disable` | 設 `true` 暫時停用 |

> **關於 `model` 欄位的提醒**：官方文件和中文教學站的範例幾乎都寫 `model: anthropic/claude-sonnet-4-...`。**照抄會壞掉**，因為這門課只用 `opencode/big-pickle`（唯一免登入免付費的）。**直接把 `model` 那行刪掉**，agent 就會沿用你在 `opencode.json` 設的模型。上面的範例就是這樣寫的。

### 也可以寫在 opencode.json 裡

不想開新檔案的話，也可以定義在 `opencode.json` 的 `agent` 區塊：

```json
{
  "agent": {
    "math-reviewer": {
      "description": "檢查數學程式的正確性與可重現性，只讀不改",
      "mode": "subagent",
      "permission": { "edit": "deny", "bash": "deny" }
    }
  }
}
```

**但建議用 `.md` 檔**，因為系統提示會很長，寫在 JSON 裡要處理跳脫字元，很痛苦。

### `opencode agent create`

實測 1.18.30 確實有這個指令：

```bash
opencode agent create
```

它會用互動問答引導你設定位置、描述、系統提示和權限。

（注意：中文教學站 5.2a 那章沒提到這個指令，只教手寫 `.md` 檔。但**實測 1.18.30 確實有 `opencode agent create`**，以實測為準。不過它是互動式問答，還是建議直接手寫 `.md` 檔，你會更清楚每個欄位在幹嘛，也比較好改。）

---

## 4. subagent / task：什麼時候該拆子任務

### 這是什麼

主 agent 可以把一件工作丟給 subagent，subagent 在**自己獨立的對話脈絡**裡完成，只把結果回報給主 agent。

關鍵在於**脈絡隔離**：subagent 翻了二十個檔案，那二十個檔案的內容**不會**塞進你的主對話。回到主對話的只有結論。

### 為什麼這件事重要

模型的 context（一次能看的內容量）是有限的。當對話塞滿雜訊（你為了找一個函式而讓它印出的一堆檔案內容），真正重要的東西就會被擠掉或稀釋：你的 AGENTS.md 規則、你的需求、你正在寫的程式。

你會觀察到的症狀：**對話進行到後面，agent 開始忘記規則、開始用 `python` 而不是 `uv run python`、開始用英文回你。** 這通常不是模型變笨，是 context 被雜訊淹沒了。

### 什麼時候該拆

**該拆的情況：**

1. **大範圍搜尋**：「三份 reference 程式裡，哪些地方用到隨機性？」需要翻很多檔案，但你只要一個清單。
2. **獨立的檢查工作**：「檢查我的 PCA 實作對不對」，用上面那個 `math-reviewer`，不要讓審查的往返污染你寫程式的主線。
3. **主線做到一半的岔題**：正在寫程式，突然想查個東西。拆出去，主線保持乾淨。
4. **需要不同權限的工作**：主線需要能改檔案，審查工作**不該**能改檔案。

**不該拆的情況：**

1. **單一檔案的小修改**：直接做，拆出去的溝通成本比省下的多。
2. **需要完整前後文才能判斷的工作**：subagent 看不到你主對話裡講過的東西，你得把背景重講一遍，常常反而更慢。
3. **你自己還不清楚要什麼的時候**：先在主對話裡把需求想清楚。

**判斷原則：這件事需要翻很多東西，但結論只有幾句話？→ 拆。**

### 怎麼用

最簡單的方式就是直接 `@` 呼叫：

```text
@explore 找出 reference/ 底下三支程式裡所有用到隨機性的地方
```

`explore` 是內建的唯讀探索 subagent，很適合這種「翻檔案找東西」的工作，而且它唯讀，不可能改壞你的東西。

或者直接描述工作，讓主 agent 自己決定要不要拆：

```text
先用子任務調查 reference/ 裡三支程式的隨機性用法，整理成清單，
然後我們再討論要怎麼統一設定種子。
```

### 相關設定

- `subagent_depth`：控制 subagent 能不能再呼叫 subagent，預設值 `1`。（未實測：我沒有實際測試改這個值的效果。預設值對這門課完全夠用，不用動它。）
- `permission` 裡的 `task` 鍵可以控制能不能啟動 subagent。

---

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

## 6. 一張表做決定

遇到問題時，先問自己這個問題：

```
   agent 做不到這件事？
        ↓ 是
      → MCP（給它新工具）

   做得到，但做事的「方式」不對？
        ↓ 是
      → 先試 AGENTS.md 多寫一條規則
        還是不行，或需要不同權限 → 自訂 agent

   做得到，但一次做太多、對話變亂？
        ↓ 是
      → subagent（拆出去做）

   以上都不是？
        ↓
      → 那就是提示要寫清楚一點。這是最常見的答案。
```

**最後這一條請認真看待。** 初學者最常見的狀況是：結果不如預期 → 以為要加工具 → 裝了一堆 MCP 和自訂 agent → 結果更亂。

**實際上八成的問題，是把需求講清楚就解決了。** 先改你的提示，再改你的 AGENTS.md，都沒用了才考慮這章的東西。

---

## 7. 本章重點

1. **這章是加分項，不是必修。** 前兩章沒練熟就先回去練。
2. MCP 給**新工具**，自訂 agent 給**新人格**，subagent 做**工作拆分**。
3. MCP 寫在 `opencode.json` 的 `mcp` 區塊，分 `remote`（只要 `url`）和 `local`（`command` 要是**陣列**）。
4. Context7（`https://mcp.context7.com/mcp`）是實測可用、免金鑰的套件文件查詢 server。
5. 用 `opencode mcp list` 確認連線，看到 `connected` 才算成功。
6. 自訂 agent 放 `.opencode/agents/<名字>.md`，用 `opencode debug agent <名字>` 驗證。
7. 自訂 agent 的關鍵價值是**權限隔離**（`edit: deny` 是機制封鎖，不是口頭請求），這是 AGENTS.md 做不到的。
8. **範例裡的 `model` 欄位要刪掉**，這門課只用 `opencode/big-pickle`。
9. subagent 用在「翻很多東西、結論很短」的工作，保持主對話乾淨。
10. 加東西之前先問：**是不是我的提示沒講清楚？** 通常是。

---

## 練習

（做不完很正常，這章本來就是額外的。）

1. 把 Context7 加進 `opencode.json`，用 `opencode mcp list` 確認 `connected`。
2. 問它一個 scikit-learn 的 API 問題，要求它查文件確認再回答。
3. 建立 `.opencode/agents/math-reviewer.md`，用 `opencode debug agent math-reviewer` 確認 `edit` 是 `deny`。
4. 用 `@math-reviewer` 檢查你寫過的一支程式，看它抓不抓得到問題。
5. 用 `@explore` 找出 `reference/` 裡所有用到隨機性的地方。
6. 想一想：第 3 題那個 reviewer，哪些規則其實寫在 AGENTS.md 就夠了？哪些**非得**是獨立 agent 不可？

---

## 查得到但這裡略過的東西

這章只寫我實際驗證過、而且對這門課有用的部分。以下這些 opencode 有，但初學階段用不到，所以略過：plugins（`plugin` 設定與 `@opencode-ai/plugin`）、custom tools、LSP 設定、formatters、`command` 自訂指令、themes 與 keybinds、session 分享、GitHub/GitLab 整合、SDK 與 remote server、context compaction、git worktree。有興趣的話，資料來源第二項的中文教學站第 5 階段都有中文說明。

---

## 資料來源

- https://opencode.ai/docs/mcp-servers/ — `mcp` 設定區塊、local 與 remote 的鍵、`opencode mcp` 子指令
- https://opencode.ai/docs/agents/ — primary 與 subagent、agent 檔案位置、frontmatter 欄位、`agent` JSON 區塊
- https://opencode.ai/docs/permissions/ — `permission` 的鍵與值、agent 層級覆寫
- https://opencode.ai/docs/config/ — `subagent_depth`、`agent`、`mcp` 等頂層設定鍵
- https://opencode.ai/docs/skills/ — SKILL.md 位置與 frontmatter 必填欄位
- https://learnopencode.com/5-advanced/07a-mcp-basics.html — MCP 設定範例與排錯表（中文教學站，簡體）
- https://learnopencode.com/5-advanced/02a-agent-quickstart.html — 自訂 agent 快速上手（中文教學站，簡體）
- https://learnopencode.com/4-scenarios/coder-agents.html — reviewer 類 agent 的 frontmatter 範例（中文教學站，簡體；其範例用 `~/.config/opencode/agent/` 單數路徑）

本機實測（opencode 1.18.30，Linux/WSL2）：

- `opencode mcp list` 連線 Context7 顯示 `connected` 的實際輸出（無需金鑰）
- `opencode agent list` 的內建 agent 清單（`build` / `plan` / `explore` / `general`；**文件提到的 `scout` 在 1.18.30 並未出現**）
- `opencode debug agent math-reviewer` 解析後的 `description` / `mode` / `temperature` / `prompt`，以及 `edit: deny`、`bash: deny` 兩條權限規則
- `.opencode/agent/`（單數）與 `.opencode/agents/`（複數）兩種目錄名皆可被載入
- `opencode agent --help`、`opencode mcp --help` 的子指令清單
