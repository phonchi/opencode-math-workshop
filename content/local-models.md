# 在自己電腦上跑本地模型

> 課後選修 · 先完成工作坊主線，再選擇是否嘗試

本地模型把推論工作放在自己的電腦上，由 Ollama 載入模型，OpenCode 負責接收你的任務與操作工具。這一章練習如何連接兩者，以及怎麼確認 agent 真的完成了工作。

如果目的是完成工作坊，沿用 `opencode/big-pickle` 即可。本地路線適合想研究模型設定，或需要讓推論資料留在自己電腦上的同學；使用外部工具時，仍要留意它會把哪些內容送上網。

本地模型和網路模型可以分工。需要規劃、推理較難的任務交給網路模型；資料不想送出去、份量大而重複的工作，例如逐份整理私人筆記、把一批檔案轉成表格，再考慮留在本地。

## 先看自己的需求與電腦

本地模型需要下載權重，執行時也會占用記憶體。**模型檔案放得下，不代表執行時的記憶體一定夠。** 對話變長、可用的工具變多，都可能增加負擔。

- 有獨立顯示卡時，留意顯示卡記憶體；沒有時，留意一般記憶體與其他程式的用量。
- 先從短對話與小任務開始。載入很慢、系統明顯卡住，就縮小任務、換較小模型，或回到網路模型。
- 挑模型時，同時檢查大小與 **tool calling**（工具呼叫）能力。tool calling 是模型依照工具定義提出操作請求，例如讀檔或執行指令。

模型名稱或大小本身不能保證能做好 agent 任務。可以先看 [Ollama 的 tools 模型清單](https://ollama.com/search?c=tools)，再依後面的檢查流程確認自己的選擇。

### 估算放不放得下

模型名稱裡的 `9b`、`27b` 是參數量，單位是十億（billion）。原始權重很大，下載的版本通常經過 **量化**：用較少位元儲存每個參數，檔案變小，品質也會損失一些，壓得越多損失越大。量化程度寫在名稱尾端，例如 `q4_K_M` 是以 4 位元為主的混合量化、`q8_0` 是 8 位元。名稱沒寫的話，`ollama show` 輸出的 `quantization` 欄位會列出來。

| 量化 | 每十億參數約需 | 例：Qwen3.5 9B | 例：Qwen3.8 27B |
|---|---|---|---|
| 4 位元（`q4_K_M` 一類） | 0.6 GB | 約 5.7 GB | 約 16.5 GB |
| 8 位元（`q8_0`） | 1.1 GB | 約 9.5 GB | 約 29 GB |

例子是 Hugging Face 上的實際檔案；同參數量的其他模型會略有出入。本章範例 `qwen3.5:9b-q4_K_M` 多帶了處理圖片的視覺元件，`ollama list` 顯示 6.6 GB。表中只算模型檔本身，context 也要占記憶體，對話越長占得越多，所以還要再多留一段空間。

以 12 GB 顯示卡為例，6.6 GB 的範例模型放得進去，剩下約 5 GB 給 context 與其他用途，載入後再用 `ollama ps` 確認實際狀況。27B 的 4 位元模型無法完整放進顯示卡，Ollama 會把一部分改放一般記憶體、交給 CPU 計算；一般記憶體也夠的話還能跑，但會慢很多。

Apple silicon 的 Mac 由 CPU 與 GPU 共用同一塊記憶體，macOS 預設會保留一部分給系統，能給模型的上限依機型而異。常見的經驗值是 32 GB 以下約三分之二（16 GB 的機器約 10–11 GB），更大的約四分之三。這只是估算，實際上限以載入結果為準。

### 依記憶體挑起點

下表整理影片 [AI懶人報 EP460](https://www.youtube.com/watch?v=1nomxygMILI) 介紹的模型，換成 Ollama 模型庫裡可以直接下載的名稱；8 GB 那一列的 `qwen3.5:4b` 是同系列較小的版本。這些模型在模型庫都標有 `tools`。

表中的記憶體一律指「能給模型的記憶體」：有獨立顯示卡時看顯示卡記憶體，Mac 用上一段的估算。沒有獨立顯示卡時，Ollama 多半用不到內建的 GPU，會改用 CPU；載入後用 `ollama ps` 的 `PROCESSOR` 欄確認。下載大小是 2026 年 11 月模型庫預設版本的大小，同名的其他版本會不同；執行時還要再加上 context。

| 能給模型的記憶體 | 候選模型 | 下載大小 |
|---|---|---|
| 約 8 GB | `qwen3.5:4b` | 3.3 GB |
| 12–16 GB | `qwen3.5:9b` | 6.6 GB |
| 12–16 GB | `gemma4:e4b` | 6.6 GB |
| 16 GB | `gpt-oss:20b`（MoE） | 14 GB |
| 24–32 GB | `gemma4:26b`（MoE） | 16 GB |
| 24–32 GB | `qwen3.8:27b` | 18 GB |
| 32 GB | `qwen3.6:35b`（MoE） | 23 GB |

影片提到，16 GB 以下能跑的小模型適合改寫、翻譯、摘要；要它當 agent 自己規劃多個步驟、呼叫工具，就容易出錯。`gpt-oss:20b` 放進 16 GB 的顯示卡後，留給 context 的空間不多，開 32k 之前先實際確認；照前面的估算，16 GB 的 Mac 放不下它。整台機器的記憶體到 64 GB 時，影片的建議是繼續用 27B 這一級，改用 8 位元版本或開更長的 context；影片再以 128 GB 的機器示範更大的模型，例如 65 GB 的 `gpt-oss:120b`。

:::bg 為什麼有些較大的模型反而比較快：MoE

模型每產生一個 token，都要把參與計算的參數從記憶體讀一遍。一般的 **稠密模型**（dense model）每次動用全部參數，所以其他條件相同時，模型越大、每個 token 越慢。

**MoE**（mixture of experts）把模型分成許多組「專家」，每個 token 只啟用其中幾組。名稱常會標出每次啟用的量，例如 `35B-A3B` 代表總共約 350 億個參數，每次只動用約 30 億。每個 token 要搬的資料少很多，通常明顯較快，實際速度仍要在自己的電腦上測。

但所有專家都要放在記憶體裡待命，**記憶體看總參數，速度主要看每次啟用的參數**；硬體、量化與軟體實作也會影響速度。`35B-A3B` 的 4 位元版本仍要約 22 GB，8–16 GB 的筆電放不下這一類。記憶體夠大、想要較快的回應時，可以留意名稱帶 `A3B` 這類標示的 MoE 模型；做較長的 agent 任務時，再實際比較它和同大小的稠密模型哪一個比較穩。

:::

## 安裝 Ollama

請在和工作坊相同的環境中操作。原生 Windows 練習就用 Windows 版；WSL 練習就把 Ollama 裝在 WSL，先避免跨兩個系統連接。

### Windows 與 macOS

從 [Ollama 官方下載頁](https://ollama.com/download) 安裝對應版本，開啟 Ollama。Windows 安裝後請重開 Git Bash，讓終端機能找到新指令。

### Linux／WSL

在 Ubuntu 終端機執行官方安裝指令：

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

如果系統由 systemd 管理服務，可以查看狀態：

```bash
systemctl status ollama
```

按 `q` 離開狀態畫面。其他啟動方式請依 [Ollama Linux 說明](https://docs.ollama.com/linux) 操作。

### 確認指令可用

```bash
ollama --version
ollama list
```

`ollama list` 是已下載的模型清單。尚未下載時，沒有模型列出是正常的；不是要另外申請帳號。

## 先讓模型能聊天，再檢查工具能力

在模型頁選好一個完整名稱後，用 `ollama pull` 下載，再用 `ollama run` 開始短對話。兩個指令後面都要接你選的模型名稱。下面的完整設定範例提供可照抄的寫法。

聊天時問一個簡單問題，確認有回應後輸入 `/bye` 離開。接著用 `ollama show` 加上同一個模型名稱，查看 `Capabilities` 是否包含 `tools`。

你要找的是這類資訊：

```
Capabilities
  completion
  tools
```

有 `tools` 代表提供工具呼叫介面，**還要再用實際任務檢查模型是否會正確使用它**。如果出現 `does not support tools`，先重新確認模型能力；不要靠改 OpenCode 的顯示名稱來繞過。

## Context 是什麼，為什麼兩邊都要設定

Context 是模型一次能讀到的內容，包括你的需求、對話、檔案內容與工具說明。**Token** 是模型切分文字的單位，不能直接把 token 數當成中文字數。context 快滿時，OpenCode 會先把較早的對話摘要壓縮；真的超過上限時，依後端與設定，可能截掉較早的內容，也可能直接報錯。不論哪一種，細節都可能遺失，模型就忘了你先前交代的事。

你還沒開口，agent 就已經先放進一大段說明。講師在工作坊的 starter 專案裡用 OpenCode 1.18.30 接 Qwen3.5 本地模型，只輸入「嗨」，送出的內容就約有 7,500 個 token，其中約 5,200 個是讀檔、寫檔、執行指令等工具的定義。版本或模型不同，數字會跟著變。

Ollama 的預設 context 卻依顯示卡記憶體決定：

| 顯示卡記憶體 | Ollama 預設 context |
|---|---|
| 未滿 24 GiB | 4k（4,096） |
| 24 GiB 以上、未滿 48 GiB | 32k |
| 48 GiB 以上 | 256k |

多數學生筆電落在第一列；實際是哪一列，以 Ollama 偵測到的 GPU 記憶體為準，Mac 則依能給模型的記憶體判斷。照上面的量測，**預設的 4k 連第一輪附帶的說明和工具定義都放不下**，工具呼叫可能一開始就出錯。Ollama 官方建議 agent 與寫程式的工具至少設到 64,000；記憶體不夠時，可以像後面的範例先設 32,768（32k）練習小任務，對話越長越早被壓縮或截掉。

這裡有兩個需要配合的設定：

| 設定 | 管哪一件事 |
|---|---|
| Ollama 的 `num_ctx` | 模型實際載入多少 context 空間 |
| OpenCode 的 `limit.context` | 告訴 OpenCode 模型能接收多少內容，以便管理對話 |

只改 OpenCode，不會替 Ollama 配好記憶體。兩邊不一致時，OpenCode 可能仍繼續送出模型放不下的內容。不要只看「沒有錯誤訊息」就判定設定成功，請看模型載入後的狀態。

:::bg 完整範例：用 Modelfile 固定 context，再接到 OpenCode

這份範例用 `qwen3.5:9b-q4_K_M` 與 `32768` 的 context 設定作示範，方便逐項對照。它是設定範例，不是每台學生筆電都適合的建議；記憶體不足時請停止載入，改選較小模型。換模型時，以下名稱都要一起調整。

### 下載並試一段短對話

```bash
ollama pull qwen3.5:9b-q4_K_M
ollama run qwen3.5:9b-q4_K_M
```

對話裡輸入 `/bye` 離開，再檢查能力：

```bash
ollama show qwen3.5:9b-q4_K_M
```

### 建立固定設定的模型名稱

在工作坊專案裡建立 `Modelfile`，沒有副檔名，內容如下：

```text
FROM qwen3.5:9b-q4_K_M
PARAMETER num_ctx 32768
```

回到終端機，逐行執行：

```bash
ollama create qwen3.5-32k -f ./Modelfile
ollama show --parameters qwen3.5-32k
```

參數輸出應有 `num_ctx 32768`。這個新名稱讓你可以保留原模型，分開使用不同 context 設定。

### 在專案設定中登錄 provider

先另存一份原本的 `opencode.json`，例如 `opencode-cloud.json.bak`，方便比較與還原。在原檔的 `provider` 裡，和 `nvidia` 並列加入 `ollama`，其他既有的規則與權限都保留。加完後 `provider` 這段長這樣：

```json
{
  "provider": {
    "nvidia": {
      "models": {
        "z-ai/glm-5.3-flash": {
          "options": { "reasoningEffort": "low" }
        }
      }
    },
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": {
        "qwen3.5-32k": {
          "name": "Qwen3.5 local",
          "tool_call": true,
          "limit": { "context": 32768, "output": 8192 }
        }
      }
    }
  }
}
```

`baseURL` 是 Ollama 的本機服務位址；這個相容介面的網址要包含 `/v1`。`models` 下的名稱必須與 `ollama list` 相同；`name` 只是顯示文字。

這裡先保留網路模型為預設。確認設定能被讀取：

```bash
opencode models ollama
```

清單應出現 `ollama/qwen3.5-32k`。接著啟動 `opencode`，用 `/models` 選擇它，並確認畫面標示為本地模型。

### 看實際載入的 context

送出一個簡短問題，讓模型載入。它還在執行或留在記憶體裡時，另開同一環境的終端機：

```bash
ollama ps
```

檢查 `CONTEXT` 是否與 `32768` 相符，同時留意 `PROCESSOR` 與系統是否卡頓。如果數字不符，先查看原本是否另設了 `OLLAMA_CONTEXT_LENGTH`，或在 Ollama App 的設定裡調過 context length；請選一種設定方式管理，避免互相覆蓋。

降低 context 時，修改 `Modelfile` 後重新執行 `ollama create`，並同步調整 OpenCode 的 `limit.context`。若仍無法穩定執行，就先回到網路模型。

:::

## 最後一關：它真的有建立檔案嗎

模型能回話、清單能列出名字，都還不代表 agent 任務完成。**先確認畫面目前選的是 `ollama/...` 本地模型。** 如果仍顯示 Big Pickle，先展開上一節完成連接與模型切換；否則測到的是網路模型。確認後，在 OpenCode 的互動模式中貼上：

```text
請讀 AGENTS.md，再建立 local_hello.py，內容是印出 1 到 10 的平方。
用 uv run python local_hello.py 實際執行。
完成後回報你寫入的檔案與執行指令；沒有成功的部分請明說。
```

逐次閱讀並回答權限要求。看工具紀錄是否真的有讀檔、寫檔與執行，接著在終端機自己核對：

```bash
uv run python -c "from pathlib import Path; p=Path('local_hello.py'); print('檔案存在：', p.is_file()); print(p.read_text(encoding='utf-8') if p.is_file() else '尚未建立')"
uv run python local_hello.py
```

檔案內容應計算並印出平方數。輸出可以分行，也可以排成一列；順序應是：

```
1 4 9 16 25 36 49 64 81 100
```

請看清楚兩件事：程式是不是自己執行後真的得到這個結果，以及 agent 有沒有把失敗的步驟說成完成。這個小任務跑通後，再試讀取一個已完成的 Lab，先不要一次要求重寫整個專案。

## 只有文字回覆，卻沒有動手

模型可能只印出一段指令，或說檔案已寫好卻沒有實際呼叫工具。先把任務縮小成「讀這個檔案並說明內容」，再逐步增加寫檔與執行。

可以在 `AGENTS.md` 補上簡短要求：

```markdown
## 執行與回報

- 需要讀檔、寫檔或執行時，使用目前提供的對應工具。
- 印出指令不代表已經執行；只回報工具實際產生的結果。
- 任務沒有完成時，說明停在哪一步，不要補造輸出。
```

規則可以提醒模型，但不能補足所有能力差距。確認設定、縮小任務後仍做不到，就換模型或回到工作坊的網路模型，不必一直修改同一份設定。

:::bg 可能讓工具呼叫失效的三個設定

聊天看起來正常，一到讀檔、寫檔就出錯時，可以檢查下面三個設定。工具呼叫要求模型輸出格式完全正確的請求，比一般聊天更容易受影響。

- **對話範本（chat template）不對。** 每個模型都有自己的對話格式。網路上重新打包的模型檔若沒帶上這份格式，軟體會改用通用格式，模型可能讀錯對話、產生不出正確的工具請求。直接從 Ollama 模型庫下載的話，這項可以先略過；自己匯入模型檔時，優先選原作者發布的版本，懷疑時換一個版本比較。
- **量化壓得太多。** 為了塞進較小的電腦，有些版本壓到 3 位元或 2 位元，壓得越多越容易出錯。做 agent 任務時選 `q4_K_M` 或更高。
- **KV cache 被壓縮。** KV cache（鍵值快取）是模型記住前文用的資料，context 越長占得越多。Ollama 可以用 `OLLAMA_KV_CACHE_TYPE` 壓縮它來省記憶體，預設是不壓縮的 `f16`，官方說 `q8_0` 通常沒有明顯影響。Level1Techs 用另一套推論軟體測長 context 的工具任務時，KV cache 壓到 4 位元後工具呼叫出錯，之後也沒能自行修正。沒有設定過這個變數就維持預設，不用處理。

:::

## 本地不等於安全

資料不送出去，確實比較私密，但 agent 能碰到什麼，比模型在哪裡跑更重要。SentinelOne 與 Censys 在 2026 年初公布的調查，前後掃描 293 天，找到約 17.5 萬台不需要密碼就能從網路連上的 Ollama 主機，其中超過 48% 透過 API 宣告支援工具呼叫。Ollama 預設只接受本機連線，這些主機多半是被設定成對外開放，例如改了 `OLLAMA_HOST`，或用 Docker 直接公開連接埠。

照下面幾點設定：

- **讓 Ollama 只監聽本機。** 預設位址是 `127.0.0.1:11434`。不要為了方便把 `OLLAMA_HOST` 改成 `0.0.0.0`；從外面連回自己的電腦屬於進階設定，這門課用不到。
- **保持軟體更新。** Ollama 修過多次安全漏洞，定期更新到最新版。
- **模型檔從可信來源下載。** 優先使用 Ollama 模型庫或原作者發布的版本。
- **agent 的工作資料夾不放密碼與金鑰。** 模型檔本身不會執行程式，但 OpenCode 給了它讀檔與執行指令的工具，而且工作資料夾不是隔離環境，工具仍可能讀到其他位置的檔案。專案的 `opencode.json` 已把 `edit`、`bash` 設為 `ask`，保持這個設定，逐次確認它要做什麼；設定方式見[用 AGENTS.md 馴服 agent](agents-md.html)。

## 卡住時先查這幾項

| 看到的情況 | 下一步 |
|---|---|
| 找不到 `ollama` 指令 | 安裝後重開終端機，再試 `ollama --version` |
| `connection refused` | 確認 Ollama 已開啟，且和 OpenCode 在同一個環境 |
| 找不到模型或 `404` | 對照 `ollama list`、設定中的模型名稱與 `/v1` 網址 |
| `does not support tools` | 用 `ollama show` 檢查能力，改選支援工具的模型 |
| `CONTEXT` 和設定不符 | 檢查 Modelfile、環境變數與實際載入的模型名稱 |
| 系統變得很慢 | 停下任務，縮小 context 或換較小模型；不要只增加等待時間 |
| 聊天正常，工具呼叫卻出錯 | 檢查量化程度與 KV cache 設定，再換 Ollama 模型庫的版本試試 |
| 送出後很久才開始回答 | 模型要先讀完整段 context；一次少讀幾個檔案，或換較小、較快的模型 |
| 只印出指令或宣稱完成 | 查實際檔案與工具紀錄，把任務縮成一步再試 |
| 忘記先前的要求 | 將重點寫進 `notes/progress.md`，換新對話重讀；參考 [讓 agent 把工作做完整](agent-workflows.html) |

## 接著怎麼用

成功後，把自己的模型名稱、設定方式和成功指令記在 `notes/`。不要把自己的速度或記憶體用量當成同學電腦也能達到的結果。

## 參考資料

- [Ollama 官方下載](https://ollama.com/download)
- [Ollama 快速開始](https://docs.ollama.com/quickstart)
- [Ollama context length](https://docs.ollama.com/context-length)
- [Ollama Modelfile](https://docs.ollama.com/modelfile)
- [OpenCode providers](https://opencode.ai/docs/providers/)
- [Ollama FAQ](https://docs.ollama.com/faq)：對外開放、KV cache 量化等設定
- [Hugging Face：Unsloth Qwen3.8-27B GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF)：各種量化的實際檔案大小
- [SentinelOne：對外開放的 Ollama 主機調查](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/)
- [Level1Techs：Why your local LLM feels dumber than it is](https://forum.level1techs.com/t/why-your-local-llm-feels-dumber-than-it-is/253917)：以 vLLM 與 Qwen3.6 測試量化與 KV cache 對長 context 工具任務的影響
- 延伸觀看：[AI懶人報 EP460：你的電腦能跑什麼 AI？](https://www.youtube.com/watch?v=1nomxygMILI)，依記憶體大小介紹模型與常見設定陷阱；片中速度為社群數據，僅供參考
