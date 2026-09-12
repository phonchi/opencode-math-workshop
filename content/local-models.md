# 在自己電腦上跑本地模型

> 課後延伸 · 加分項

工作坊主線用的是 `opencode/big-pickle`，免登入、不用設定、速度夠快。這一章講的是另一條路：
把模型放在自己的筆電上跑。**這不是必修**，做不做都不影響你的作業。

先把話講在前面：**對大多數人的筆電來說，本地模型的體驗會明顯比雲端差。**
慢、比較笨、比較容易亂來，而且要花時間調設定。這一章不是要推銷本地模型，
是要讓你在「真的需要」的時候知道怎麼做，以及知道什麼時候不該做。

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

- 9B 參數 × 4.5 ÷ 8 ≈ **5.1GB** → 實際檔案 6.6GB（還有 embedding 等其他東西）
- 4B 參數 × 4.5 ÷ 8 ≈ **2.3GB** → 實際檔案 3.4GB

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
在 opencode 裡**完全不能用**——不是「效果差一點」，是連第一步都走不到。

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

## 最重要的一節：context 要設兩次

這一節是整章的重點。**只設一邊完全沒有用**，而且失敗的方式是「安靜地壞掉」——
不會報錯，只會讓模型看起來很笨。

### 為什麼是兩個地方

opencode 透過 **OpenAI 相容端點**（`http://localhost:11434/v1`）跟 Ollama 講話。
這個協定裡**沒有**「context 要多大」這個欄位。所以：

```
┌──────────────────────┐                    ┌──────────────────────┐
│  opencode            │   POST /v1/chat/   │  Ollama              │
│                      │   completions      │                      │
│  limit.context       │ ────────────────> │  num_ctx             │
│  ＝我「以為」模型     │   （請求裡帶不了    │  ＝模型「實際」      │
│    能吃多少 token     │     context 大小） │    能吃多少 token    │
└──────────────────────┘                    └──────────────────────┘
        設定 A                                      設定 B
   決定何時壓縮對話                            決定超過就截斷
```

- **設定 B（Ollama 的 `num_ctx`）** 決定模型真正看得到多少。超過就**直接把前面砍掉**。
- **設定 A（opencode 的 `limit.context`）** 決定 opencode 什麼時候該壓縮／摘要對話。
  opencode 沒辦法問 Ollama「你的 context 多大」，只能相信你在設定檔裡寫的數字。

**實測證明這兩者互不相通**：我在 `/v1/chat/completions` 請求裡同時塞了
`"num_ctx": 32768` 和 `"options": {"num_ctx": 32768}`，然後看 `ollama ps`：

```
NAME                 ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen3.5:9b-q4_K_M    6488c96fa5fa    8.6 GB    100% GPU     4096       4 minutes from now
                                                            ^^^^ 還是 4096，請求裡的設定被忽略
```

所以：**你在 opencode 那邊怎麼寫，都不會改變 Ollama 的 num_ctx。** 必須分開設。

### 預設值是多少（這裡有陷阱）

較新版本的 Ollama **不是固定 4096**，而是**開機時依可用 VRAM 自動決定**：

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
M2 MacBook Air 是 8 或 16GB——**幾乎所有學生的機器都落在第一層，也就是 4k**。
「我沒改過設定所以應該是預設的最佳值」這個想法在這裡是錯的。

> Ollama 的 FAQ 頁面目前還寫著「預設 4096」，跟 context-length 那一頁的分層說明不一致。
> 以 context-length 頁與你自己機器的 log 為準。

### 4k 為什麼對 agent 完全不夠

一般聊天 4k 綽綽有餘。但 agent 的 context 裡塞的是：

| 內容 | 大約 token 數 |
|---|---|
| 系統提示（agent 的行為規則） | 1k–3k |
| 工具定義（read / write / bash / glob / grep… 的 JSON schema） | 2k–5k |
| `AGENTS.md` 專案規則 | 0.5k–2k |
| 讀進來的檔案內容 | 每個檔案 0.5k–5k |
| 到目前為止的對話與工具輸出 | 持續累積 |

**光是系統提示加工具定義就可能超過 4k。** 也就是說，在預設設定下，
模型有可能在「還沒看到你第一句話」之前，context 就已經滿了。

### 設定前 vs 設定後

我實測了一次「送超過 4k 的內容給預設設定的模型」，這是 Ollama server 的 log：

```
level=WARN source=runner.go:187 msg="truncating input prompt"
    limit=4096 prompt=10020 keep=4 new=4096
```

10020 個 token 進去，**只有 4096 個留下來**。API 回傳的 `prompt_eval_count` 也確實是 `4096`。
而且——**呼叫端完全不會收到任何錯誤或警告**。opencode 那邊看起來一切正常。

被砍掉的是**最前面**的部分，也就是系統提示和工具定義所在的位置。這直接解釋了所有症狀：

| 你看到的症狀 | 真正的原因 |
|---|---|
| 「一直忘記我前面說什麼」 | 對話前半被截斷了 |
| 「亂呼叫不存在的工具，像 `execute`、`shell`」 | 工具定義被截掉，模型只能用猜的 |
| 「同一件事重複做好幾次」 | 它看不到自己剛才已經做過的紀錄 |
| 「不遵守 `AGENTS.md` 的規則」 | `AGENTS.md` 在 context 最前面，最先被砍 |
| 「講到一半突然變得很笨」 | 累積內容剛好越過 4096 這條線 |

對照設定成 32k 之後：同樣的 prompt 完整進去，log 沒有 `truncating input prompt`，
工具呼叫正常。**這不是「模型變聰明了」，是它終於看得到完整的指令。**

### 該設多大

兩個官方說法看起來矛盾，其實不衝突：

- **Ollama 官方文件**：「需要大量 context 的任務，像是 web search、agents、coding tools，
  應該至少設到 **64000**。」
- **opencode 官方文件**：「如果 tool call 表現不好，把 Ollama 的 `num_ctx` 調大，
  **從 16k–32k 開始**。」

64k 是理想值，16k–32k 是在學生筆電上的現實下限。回頭看前面那張實測表：
12GB 的卡開到 64k 就已經溢出到 CPU 了。所以：

| 你的記憶體 | 建議 num_ctx |
|---|---|
| 8GB RAM 無獨顯 | 8192，勉強 16384 |
| 16GB RAM 無獨顯 | 16384 |
| 8–12GB VRAM | 32768 |
| 24GB 以上 VRAM / 32GB 以上 Mac | 65536 |

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
> 滑桿和環境變數同時設定時誰優先（未實測）——建議只用一種。

> 有一個會讓人困惑的地方：即使設了環境變數，server 啟動的 log **還是會印**
> `vram-based default context ... default_num_ctx=4096`。那行只是在報告「VRAM 推算出來的預設值」，
> 環境變數會在**載入模型時**覆蓋它。實測 `OLLAMA_CONTEXT_LENGTH=16384` 的 server，
> 用 `/v1` 且不帶任何參數載入模型後，`context_length` 確實是 `16384`。以 `ollama ps` 為準，不要看那行 log。

#### 路線二：用 Modelfile 做一個固定 num_ctx 的模型（建議）

不用動系統服務、不用 sudo、不影響其他模型，而且**透過 `/v1` 端點也一定生效**——
這是本機唯一完整驗證過、從頭到尾都對的路線。

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
| `limit.context` **大於** 真實 `num_ctx` | **危險**。opencode 以為還有空間、不壓縮對話，Ollama 安靜地截斷。模型莫名其妙變笨，**完全沒有錯誤訊息** |
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

- `"npm": "@ai-sdk/openai-compatible"` —— Ollama 走的是 OpenAI 相容協定，這行是官方寫法。
- `baseURL` 結尾**要有 `/v1`**。少了它連不上。
- `models` 底下那個 key（這裡是 `qwen3.5-32k`）**必須和 `ollama list` 裡的名字完全一致**，
  這才是真正送給 Ollama 的 model id。旁邊的 `"name"` 只是給你自己看的顯示名稱。
- 頂層 `"model"` 用 `provider/model-id` 的格式，也就是 `"ollama/qwen3.5-32k"`。
- `limit.context` 和 `limit.output` 都是必填。`output` 是單次回覆上限，8192 夠用。
- `tool_call: true` 明確告訴 opencode 這個模型會呼叫工具。

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

趁模型還在記憶體裡（預設約 4 分鐘）馬上看：

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
那就是這個模型的 tool calling 能力太弱——換大一點的模型。

### 6. opencode 認得這個模型嗎

在放了 `opencode.json` 的目錄下：

```bash
opencode models ollama
```

應該印出 `ollama/qwen3.5-32k`。沒印出來就是設定檔寫錯或放錯目錄。

### 7. 看 Ollama 的 log 有沒有在截斷

跑完一輪真實的 agent 任務後：

```bash
# Linux / WSL2
journalctl -u ollama --since "10 minutes ago" | grep -i truncat

# 手動啟動的 server：直接看終端機輸出
```

**沒有任何輸出才是對的。** 如果看到：

```
level=WARN source=runner.go:187 msg="truncating input prompt" limit=4096 prompt=10020 keep=4 new=4096
```

代表 `num_ctx` 根本沒設成功，回到第 3、4 步。這個 log 是最誠實的證據。

---

## 為什麼本地小模型常常「不聽話」

就算 context 設對了，小模型還是會做出一些雲端大模型不會做的蠢事。這不是你設定錯，
是 2B–9B 模型的能力天花板。認識這些模式，你才知道什麼時候該停止 debug、直接換模型。

### 常見失敗模式

**一、亂造不存在的工具名稱。**
opencode 的內建工具有固定名字：`read`、`write`、`edit`、`bash`、`glob`、`grep`、
`apply_patch`、`todowrite`、`webfetch`、`websearch`、`question`、`lsp`、`skill`。
小模型常常無視工具定義，自己發明 `execute`、`shell`、`run`、`terminal`、`run_command`、
`python` 這種「看起來很合理」的名字。因為它訓練時看過太多別的 agent 框架，
就直接套用印象中的名字。結果是工具呼叫失敗，agent 卡住或開始重試。

**二、把該呼叫工具的動作變成「把指令印出來」。**
你要它跑測試，它回你：

> 你可以執行以下指令來跑測試：
> ```bash
> uv run python lab1_cluster.py
> ```

它**沒有真的呼叫 `bash` 工具**，只是輸出了一段文字。這是小模型最常見的退化行為——
退回成「聊天模型」而不是「agent」。

**三、只做一步就停。**
多步驟任務（讀檔 → 改 → 執行 → 看結果 → 修）常常在第一步之後就宣告完成。

**四、幻覺自己的執行結果。**
最危險的一種：它「假裝」執行過，然後**編造**一段輸出給你看。
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
| 模型一直忘記前面的事 | context 被截斷 | `journalctl -u ollama \| grep truncat` 確認；把 num_ctx 調到 16k–32k |
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
- opencode — 設定檔 JSON schema：<https://opencode.ai/config.json>

本機實測環境：WSL2 Ubuntu 24.04 / Ollama 0.21.2 / opencode 1.18.30 /
RTX 5070 12GB / RAM 15GB / 模型 `qwen3.5:9b-q4_K_M`。
文中所有 `ollama ps`、`ollama show`、server log 與 curl 的輸出，都是在這台機器上實際跑出來的。
標註「（未實測）」的部分是我沒有對應硬體可以驗證的推估。查證日期：2026-09-12。
