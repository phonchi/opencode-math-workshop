# MCP、skills 與 subagent

> 課後延伸．**加分項，不是必修**

## 這章怎麼選著讀

已經完成一個 Lab，就可以從第 5 節做自己的數學筆記 skill。想找另一個角色檢查程式，讀第 3、4 節；需要查外部套件文件，再讀第 2 節的 MCP。

所有練習都沿用課前建立的同一份專案；先在該資料夾開啟終端機，用 `pwd`、`ls` 確認位置與檔案。先查看要建立的檔案與權限，逐項增加需要的能力；不必一次完成全部設定。

## 1. 這些工具各解決什麼問題

先從你想解決的問題來選：

| | 一句話 | 解決的問題 |
|---|---|---|
| **skill** | 保存某一類任務的流程 | 整理筆記時，每次都要重講同一套要求 |
| **MCP** | 給 agent **新的工具**（外部能力） | 它**做不到**某件事 |
| **自訂 agent** | 給 agent **新的人格**（專屬指令與權限） | 它**做得到，但做事方式**不對 |
| **subagent** | 把工作**拆給另一個對話**去做 | 它**能做，但一次做太多**會亂 |

用一個具體場景串起來：

> 你在寫 PCA 的作業。
>
> - agent 不知道 scikit-learn 新版的 API 怎麼用，它的知識停在舊版 → **MCP**（接一個能查即時套件文件的工具）
> - 你想要一個「只檢查數學對不對、絕對不准改你程式」的審查員 → **自訂 agent**（定義一個唯讀的 reviewer）
> - 主線在寫 PCA，但你想順便查一下你完成的 Lab 程式裡哪裡用到隨機性 → **subagent**（丟給子任務去翻，不要用這些細節污染主對話）

再換個比喻：MCP 是**多給它一隻手**，自訂 agent 是**換一個專家來**，subagent 是**找人分頭辦事**。

---

## 2. MCP：給 agent 新的工具

### 這是什麼

MCP（Model Context Protocol）是一套標準協定，讓 agent 能連上外部服務取得能力。opencode 本身只有讀檔、寫檔、執行指令、抓網頁這些內建工具。接上 MCP server 之後，agent 就多了那個 server 提供的工具。

### 對數學/研究最有用的例子：查套件文件

下面是一個選修的外部工具例子。先完成本機的 skill 與 reviewer 練習也可以，不必先設定 MCP。

**問題**：`opencode/big-pickle` 和所有模型一樣，知識有時間截止點。你問它 scikit-learn 某個參數怎麼用，它可能給你一個兩年前的 API，跑起來噴 `TypeError`。你也可以叫它用 `webfetch` 去抓文件，但那是抓整頁 HTML，又慢又雜。

Context7 可以替 agent 提供套件文件查詢；查到後仍要確認文件版本與本專案相符。官方安裝與使用條件見 [Context7 官方說明](https://github.com/upstash/context7)。

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
opencode mcp list
```

連線成功時的輸出例子：

```
┌  MCP Servers
│
●  ✓ context7 connected
│      https://mcp.context7.com/mcp
│
└  1 server(s)
```

看到 `connected` 表示連線成功，還要實際查一次文件才知道服務能否使用。Context7 官方目前建議使用金鑰取得較高額度；本教材只示範不帶金鑰的連線，服務可用性與配額會變動。遇到認證、額度或付費要求就停止，改用下方的官方文件路線，不必申請帳號或啟用付費設定。

接上之後可以這樣問：

```text
scikit-learn 最新版的 PCA，取得解釋變異比例的屬性叫什麼？查文件確認再回答。
```

### 不接 MCP 也能查官方文件

把這段貼進 OpenCode，允許它讀取指定的公開文件：

```text
請讀 https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html，
說明 n_init 的用途，並和 lab1_cluster.py 的設定比較。
請附上來源連結；如果讀不到網頁，直接說明，不要靠猜測補上 API 行為。
```

網頁讀不到時，你也可以自己在瀏覽器開啟官方文件，把需要的短段落貼進對話。

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

可以先查看有哪些管理指令：

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

用 `opencode agent list` 可查看目前的角色，常用的是：

```
build (primary)
plan (primary)
explore (subagent)
general (subagent)
```

（另外還有 `compaction`、`summary`、`title` 等內部用的，不用管。）

- **primary agent** 是你直接對話的對象，在介面裡按 **Tab** 切換。本課程用 `build` 執行任務，改檔與執行依專案的 `ask` 設定詢問；`plan` 適合先分析步驟。實際限制會受版本與專案設定影響，請查看權限要求。
- **subagent** 是被主 agent 呼叫去做特定工作的。`explore` 唯讀探索程式碼，`general` 通用。

**自訂 agent 就是自己定義一個**，給它專屬的系統提示、溫度和權限。

### 檔案放哪裡

```
專案層：<專案根目錄>/.opencode/agents/<名字>.md
全域：  ~/.config/opencode/agents/<名字>.md
```

**檔名就是 agent 的名字。** `math-reviewer.md` 會產生一個叫 `math-reviewer` 的 agent。專案層優先於全域。

本課程統一用專案內的 `.opencode/agents/`，讓設定跟著練習檔案一起保存。

### 什麼情況值得做

老實說，**大部分情況不值得**。你在 AGENTS.md 裡多寫一條規則，通常就解決了。

值得做的是這種情形：**你需要一個權限跟主 agent 不同的角色。** 這是 AGENTS.md 做不到的。AGENTS.md 是全專案共用的提示，而 agent 可以有自己的權限設定。

最典型的例子就是「**只做數學驗證的 reviewer**」：你想要一個看得到你的程式、並關閉本練習會用到的編輯、執行指令與再委派入口的審查員。

### 完整範例：數學驗證 reviewer

先在專案終端機建立資料夾：

```bash
uv run python -c "from pathlib import Path; Path('.opencode/agents').mkdir(parents=True, exist_ok=True)"
```

再用文字編輯器建立 `.opencode/agents/math-reviewer.md`，貼上以下內容。檔名結尾是 `.md`，不要多出 `.txt`：

```markdown
---
description: 檢查數學程式的正確性與可重現性，只讀不改
mode: subagent
temperature: 0.1
permission:
  edit: deny
  bash: deny
  task: deny
  external_directory: deny
---

你是數學驗證審查員。只讀取本專案內的程式與已有輸出，不讀其他資料夾或其他 Python 環境的套件。若本專案沒有對應證據，明確說明缺少。你的工作是**檢查**，不是修改。

檢查以下項目，逐項回報「通過」或「有問題」，有問題要指出行號：

1. **數學正確性**：公式與演算法步驟是否正確？矩陣維度是否對得起來？
2. **可重現性**：所有用到隨機性的地方是否都有固定種子（`random_state=0`
   或 `np.random.seed(0)`）？
3. **有沒有偷懶**：如果程式宣稱是「手刻」實作，檢查是否偷偷呼叫了
   sklearn 的對應函式來充數。
4. **數值穩定性**：有沒有除以可能為零的量？有沒有對可能為負的數開根號？
   大數相減造成的抵消誤差？
5. **驗證段落**：有沒有附上驗證程式碼？若提供了執行輸出，核對輸出與結論是否相符。
   本角色不能執行指令；沒有現成紀錄時必須寫「尚無執行證據」，不能宣稱已通過測試。

回報格式：用台灣繁體中文，條列，每一項先寫結論再寫理由。
不要修改任何檔案。不要執行任何指令。
```

**確認設定被載入**：

```bash
opencode agent list                    # 看 math-reviewer 有沒有出現
opencode debug agent math-reviewer     # 看解析後的完整設定
```

檢查 `opencode debug agent math-reviewer` 中的模式、提示與權限。輸出中應有對應欄位：

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
{ "permission": "task", "action": "deny", "pattern": "*" }
{ "permission": "external_directory", "action": "deny", "pattern": "*" }
```

**這就是自訂 agent 相對於 AGENTS.md 的關鍵優勢**：`edit: deny` 是機制上的封鎖，不是口頭請求。這份設定拒絕本練習的編輯、執行指令與再委派入口；若日後加入其他工具，也要檢查那些工具的權限。

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

> **關於 `model` 欄位的提醒**：官方文件和中文教學站的範例幾乎都寫 `model: anthropic/claude-sonnet-4-...`。**照抄會壞掉**，因為這門課只用 `opencode/big-pickle`（本工作坊選用的免費模型）。**直接把 `model` 那行刪掉**，agent 就會沿用你在 `opencode.json` 設的模型。上面的範例就是這樣寫的。

### 也可以寫在 opencode.json 裡

不想開新檔案的話，也可以定義在 `opencode.json` 的 `agent` 區塊：

```json
{
  "agent": {
    "math-reviewer": {
      "description": "檢查數學程式的正確性與可重現性，只讀不改",
      "mode": "subagent",
      "prompt": "只讀本專案內的程式與已有輸出，不讀其他資料夾或Python環境。唯讀檢查數學公式、矩陣維度、隨機種子與驗證段落。指出實際檔案與行號。不修改、不執行、不再委派；沒有現成輸出時寫尚無執行證據，不可宣稱測試通過。",
      "permission": { "edit": "deny", "bash": "deny", "task": "deny", "external_directory": "deny" }
    }
  }
}
```

**但建議用 `.md` 檔**，因為系統提示會很長，寫在 JSON 裡要處理跳脫字元，很痛苦。

### `opencode agent create`

也可以用互動方式建立：

```bash
opencode agent create
```

它會用互動問答引導你設定位置、描述、系統提示和權限。

本章採直接建立 `.md` 檔的做法，方便閱讀每個欄位並修改。

---

<!--DIAGRAM:agent-delegation-->

## 4. subagent / task：什麼時候該拆子任務

### 這是什麼

主 agent 可以把一件工作丟給 subagent，subagent 在**自己獨立的對話脈絡**裡完成，只把結果回報給主 agent。

關鍵在於**脈絡隔離**：subagent 翻了二十個檔案，那二十個檔案的內容**不會**塞進你的主對話。回到主對話的只有結論。

### 為什麼這件事重要

模型的 context（一次能看的內容量）是有限的。當對話塞滿雜訊（你為了找一個函式而讓它印出的一堆檔案內容），真正重要的東西就會被擠掉或稀釋：你的 AGENTS.md 規則、你的需求、你正在寫的程式。

你會觀察到的症狀：**對話進行到後面，agent 開始忘記規則、開始用 `python` 而不是 `uv run python`、開始用英文回你。** 這通常不是模型變笨，是 context 被雜訊淹沒了。

### 什麼時候該拆

**該拆的情況：**

1. **大範圍搜尋**：「我完成的 Lab 程式裡，哪些地方用到隨機性？」需要翻很多檔案，但你只要一個清單。
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
@explore 請唯讀檢查 lab1_cluster.py、lab2_pca.py、lab3_logistic.py 裡用到隨機性的地方。只看實際存在的檔案，回報檔名、行號與用途，不要修改或執行。
```

`explore` 是內建的唯讀探索 subagent，很適合這種「翻檔案找東西」的工作，而且它唯讀，不可能改壞你的東西。

或者直接描述工作，讓主 agent 自己決定要不要拆：

```text
先用子任務調查我已完成的 Lab 程式的隨機性用法，整理成清單，
然後我們再討論要怎麼統一設定種子。
```

### 相關設定

- 保留目前的子任務深度設定；練習先由主 agent 分派一層子任務即可。
- `permission` 裡的 `task` 鍵可以控制能不能啟動 subagent。

---

## 5. 自己做一個數學筆記 skill

`AGENTS.md` 放整個專案一直適用的規則；**skill** 放某一類任務才需要的流程。下面把「根據實際結果整理數學筆記」做成一個 skill，之後換一個 Lab 也能沿用。

### 建立資料夾與 SKILL.md

回到專案資料夾的終端機。下列指令在 PowerShell 與 WSL 都能使用：

```bash
uv run python -c "from pathlib import Path; Path('.opencode/skills/math-notes').mkdir(parents=True, exist_ok=True)"
```

用文字編輯器建立 `.opencode/skills/math-notes/SKILL.md`，貼上以下完整內容。Windows 請確認副檔名是 `.md`，沒有多出 `.txt`。

```markdown
---
name: math-notes
description: 根據本專案已完成的數學實驗與輸出整理學習筆記；當使用者要求把 Lab 結果寫成可複習的筆記時使用。
---

# 數學實驗筆記

先讀使用者指定的程式、結果與既有筆記，再整理這次任務。

- 筆記寫清楚研究問題、符號與必要假設，再說明做了什麼、看到什麼。
- 公式使用 Markdown 的 $...$ 與 $$...$$。沒有解釋過的符號要先定義。
- 結果註明來源檔案與實際執行指令；沒有執行輸出時，標明只有程式可讀。
- 保留原始數字與結論的適用範圍。分開寫已觀察結果、推論與尚未確認的事。
- 以學生可以自己回答的一個檢查問題收尾，答案另列。
- 依使用者指定路徑存檔；若檔案已存在，先讀內容再更新。不要為了寫筆記另做實驗。
```

資料夾名稱與 frontmatter 的 `name` 都是 `math-notes`。`description` 說明何時使用；下面的正文才是實際流程。這份練習只需一個檔案，沒有額外安裝或網路服務。[OpenCode 官方 skills 說明](https://opencode.ai/docs/skills/) 列出了命名、載入與權限規則。

### 先確認發現，再確認真的載入

在同一個專案資料夾執行：

```bash
opencode debug skill
```

清單應出現 `math-notes` 和你剛建立的路徑。這只確認 **skill 被發現**，還不代表某次任務已經使用它。

重新啟動 OpenCode，貼上：

```text
請用 skill 工具載入 math-notes。
讀取 lab1_cluster.py 與 figs/lab1_k_selection.png；若目前模型不能讀圖，
請明說，改以程式與這段對話裡實際提供的執行輸出為依據，不要猜圖上數值。
將這次分群實驗整理成 notes/lab1-review.md。
沒有的輸出請標示缺少，不要重新執行實驗。
```

觀察工具紀錄有沒有載入 `math-notes`，再打開產出的筆記。它應說明資料、參數與結論的範圍；只看到模型說「我用了 skill」還不夠。若沒載入，先檢查檔名、frontmatter 與 `opencode debug skill` 的清單，再要求它使用 skill 工具。

### 換一個任務，看看流程能否沿用

用自己已完成的 PCA 或 logistic 程式再做一次，指定不同筆記檔名。比較兩份筆記：流程可以一致，內容、數字和結論必須來自各自的實驗。最後刪掉或縮短你發現沒有幫助的規則，讓 skill 保持容易閱讀。

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

先把需求、輸出與完成判準講清楚。 先改你的提示，再改你的 AGENTS.md，都沒用了才考慮這章的東西。

---

## 7. 本章重點

1. **這章是加分項，不是必修。** 前兩章沒練熟就先回去練。
2. MCP 給**新工具**，自訂 agent 給**新人格**，subagent 做**工作拆分**。
3. MCP 寫在 `opencode.json` 的 `mcp` 區塊，分 `remote`（只要 `url`）和 `local`（`command` 要是**陣列**）。
4. 外部 MCP 是選修；遇到認證或配額限制就改讀官方文件，不開啟付費設定。
5. `opencode mcp list` 確認連線後，還要實際查一次文件。
6. 自訂 agent 放 `.opencode/agents/<名字>.md`，用 `opencode debug agent <名字>` 驗證。
7. 自訂 agent 的關鍵價值是**權限隔離**（`edit: deny` 是機制封鎖，不是口頭請求），這是 AGENTS.md 做不到的。
8. **範例裡的 `model` 欄位要刪掉**，這門課只用 `opencode/big-pickle`。
9. skill 保存重複流程；subagent 用在「翻很多東西、結論很短」的工作，保持主對話乾淨。
10. 加東西之前先問：**是不是我的提示沒講清楚？** 通常是。

---

## 練習

（做不完很正常，這章本來就是額外的。）

1. 先建立本章的 `math-notes` skill，用 `opencode debug skill` 確認能找到它。
2. 要求 agent 載入 skill，整理你已完成的一個 Lab；開啟筆記核對來源與結論。
3. 建立 `.opencode/agents/math-reviewer.md`，用 `opencode debug agent math-reviewer` 確認 `edit` 是 `deny`。
4. 用 `@math-reviewer` 檢查你寫過的一支程式，看它抓不抓得到問題。
5. 用 `@explore` 檢查自己已完成的 Lab 檔案，找出用到隨機性的地方。
6. 想一想：第 3 題那個 reviewer，哪些規則其實寫在 AGENTS.md 就夠了？哪些**非得**是獨立 agent 不可？

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
