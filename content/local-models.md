# 在自己電腦上跑本地模型

> 課後選修 · 先完成工作坊主線，再選擇是否嘗試

本地模型把推論工作放在自己的電腦上，由 Ollama 載入模型，OpenCode 負責接收你的任務與操作工具。這一章練習如何連接兩者，以及怎麼確認 agent 真的完成了工作。

如果目的是完成工作坊，沿用 `opencode/big-pickle` 即可。本地路線適合想研究模型設定，或需要讓推論資料留在自己電腦上的同學；使用外部工具時，仍要留意它會把哪些內容送上網。

## 先看自己的需求與電腦

本地模型需要下載權重，執行時也會占用記憶體。**模型檔案放得下，不代表執行時的記憶體一定夠。** 對話變長、可用的工具變多，都可能增加負擔。

- 有獨立顯示卡時，留意顯示卡記憶體；沒有時，留意一般記憶體與其他程式的用量。
- 先從短對話與小任務開始。載入很慢、系統明顯卡住，就縮小任務、換較小模型，或回到網路模型。
- 挑模型時，同時檢查大小與 **tool calling** 能力。tool calling 是模型依照工具定義提出操作請求，例如讀檔或執行指令。

模型名稱或大小本身不能保證能做好 agent 任務。可以先看 [Ollama 的 tools 模型清單](https://ollama.com/search?c=tools)，再依後面的檢查流程確認自己的選擇。

## 安裝 Ollama

請在和工作坊相同的環境中操作。原生 Windows 練習就用 Windows 版；WSL 練習就把 Ollama 裝在 WSL，先避免跨兩個系統連接。

### Windows 與 macOS

從 [Ollama 官方下載頁](https://ollama.com/download) 安裝對應版本，開啟 Ollama。Windows 安裝後請重開 PowerShell，讓終端機能找到新指令。

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

Context 是模型一次能讀到的內容，包括你的需求、對話、檔案內容與工具說明。**Token** 是模型切分文字的單位，不能直接把 token 數當成中文字數。

這裡有兩個需要配合的設定：

| 設定 | 管哪一件事 |
|---|---|
| Ollama 的 `num_ctx` | 模型實際載入多少 context 空間 |
| OpenCode 的 `limit.context` | 告訴 OpenCode 模型能接收多少內容，以便管理對話 |

只改 OpenCode，不會替 Ollama 配好記憶體。兩邊不一致時，OpenCode 可能仍繼續送出模型放不下的內容。不要只看「沒有錯誤訊息」就判定設定成功，請看模型載入後的狀態。

:::bg 完整範例：用 Modelfile 固定 context，再接到 OpenCode

這份範例沿用 `qwen3.5:9b-q4_K_M` 與 `32768` 的 context 設定，方便逐項對照。它是設定範例，不是每台學生筆電都適合的建議；記憶體不足時請停止載入，改選較小模型。換模型時，以下名稱都要一起調整。

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

先另存一份原本的 `opencode.json`，例如 `opencode-cloud.json.bak`，方便比較與還原。在原檔加入下面的 `provider` 區塊，其他既有的規則與權限保留。若你還沒加其他設定，下面是可對照的完整範例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle",
  "provider": {
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
  },
  "permission": { "bash": "ask", "edit": "ask", "webfetch": "ask" },
  "instructions": ["AGENTS.md"]
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

檢查 `CONTEXT` 是否與 `32768` 相符，同時留意 `PROCESSOR` 與系統是否卡頓。如果數字不符，先查看原本是否另設了 `OLLAMA_CONTEXT_LENGTH`；請選一種設定方式管理，避免互相覆蓋。

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

## 卡住時先查這幾項

| 看到的情況 | 下一步 |
|---|---|
| 找不到 `ollama` 指令 | 安裝後重開終端機，再試 `ollama --version` |
| `connection refused` | 確認 Ollama 已開啟，且和 OpenCode 在同一個環境 |
| 找不到模型或 `404` | 對照 `ollama list`、設定中的模型名稱與 `/v1` 網址 |
| `does not support tools` | 用 `ollama show` 檢查能力，改選支援工具的模型 |
| `CONTEXT` 和設定不符 | 檢查 Modelfile、環境變數與實際載入的模型名稱 |
| 系統變得很慢 | 停下任務，縮小 context 或換較小模型；不要只增加等待時間 |
| 只印出指令或宣稱完成 | 查實際檔案與工具紀錄，把任務縮成一步再試 |
| 忘記先前的要求 | 將重點寫進 `notes/progress.md`，換新對話重讀；參考 [需求與續作](agent-workflows.html) |

## 接著怎麼用

成功後，把自己的模型名稱、設定方式和成功指令記在 `notes/`。不要把自己的速度或記憶體用量當成同學電腦也能達到的結果。

## 參考資料

- [Ollama 官方下載](https://ollama.com/download)
- [Ollama 快速開始](https://docs.ollama.com/quickstart)
- [Ollama context length](https://docs.ollama.com/context-length)
- [Ollama Modelfile](https://docs.ollama.com/modelfile)
- [OpenCode providers](https://opencode.ai/docs/providers/)
