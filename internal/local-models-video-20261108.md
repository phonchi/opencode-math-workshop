# 本地模型章：依 AI懶人報 EP460 補充的查證紀錄

日期：2026-11-08。來源影片：[AI懶人報 EP460：你的電腦能跑什麼 AI？](https://www.youtube.com/watch?v=1nomxygMILI)（2026-11-04，16:00，人工繁中字幕 355 段，以 `youtube-read` skill 抓取，逐字稿在講師機器 `~/.local/share/youtube-read/1nomxygMILI/`）。

## 採用與不採用

| 影片內容 | 處理 | 理由 |
|---|---|---|
| 4 位元模型約參數量 × 0.6 GB | 採用，另補 8 位元約 1.1 GB | 對照 Hugging Face 實際檔案（下表） |
| Mac 預設只讓 GPU 用約 3/4 記憶體 | 改寫為依機型的經驗值：32 GB 以下約 2/3（16 GB 約 10–11 GB），更大的約 3/4，註明以載入結果為準 | MLX-LM README 只說可用 `sysctl iogpu.wired_limit_mb` 調高上限。審查時 Fable 引用 llama.cpp discussion #2182：32 GB 以下預設約 2/3。網路二手資料多說約 3/4，未找到 Apple 一手文件。16 GB 用 3/4 會高估，故正文改寫 |
| Ollama 預設 context：<24 GiB 4k、24–48 GiB 32k、≥48 GiB 256k | 採用 | [Ollama context length](https://docs.ollama.com/context-length) 原文；同頁建議 agent、coding 工具至少 64000 |
| agent 打一聲「嗨」約 5,000 token | 改用本機實測：OpenCode 約 7,555 | 見下方實驗 |
| MoE：記憶體看總參數、速度看啟用參數 | 採用（`:::bg`） | 概念正確；35B-A3B 的 4 位元檔 22.13 GB |
| chat template、低於 4 位元、KV cache 壓縮會弄壞工具呼叫 | 採用（`:::bg`），KV cache 部分改寫 | 見下方差異 |
| Ollama 只監聽本機、17.5 萬台對外開放 | 採用 | [Ollama FAQ](https://docs.ollama.com/faq)：預設綁 `127.0.0.1:11434`。[SentinelOne 原始報告](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/)：“175,108 unique Ollama hosts”、“Over 293 days of scanning”、“Over 48% of observed hosts advertise tool-calling capabilities via their API endpoints.”（講師機器抓取被 429 擋下，由 Astra 審查時開啟並逐字摘錄；SecurityWeek、The Hacker News、TechRadar 報導數字一致）。48% 是 API 宣告的能力，不是實際執行工具的比例 |
| 雲端規劃、本地執行 | 採用一段定位 | 概念性建議，不引用影片的公司案例 |
| 16–128 GB 各級可跑模型與 tok/s | 不採用 | 影片自承為社群數據、未自行量測；與先前把分層表移出正文的決定一致 |
| LM Studio、llama.cpp 比較 | 不採用 | 本章只教 Ollama 路線 |

## 檔案大小核對（Hugging Face API，2026-11-08）

| 檔案 | 大小 | GB／十億參數 |
|---|---|---|
| unsloth/Qwen3.5-9B-GGUF `Qwen3.5-9B-Q4_K_M.gguf` | 5.68 GB | 0.63（名目 9B；Ollama 顯示 9.7B 時為 0.59） |
| unsloth/Qwen3.5-9B-GGUF `Qwen3.5-9B-Q8_0.gguf` | 9.53 GB | 1.06 |
| unsloth/Qwen3.8-27B-GGUF `Qwen3.8-27B-UD-Q4_K_M.gguf` | 16.46 GB | 0.61 |
| unsloth/Qwen3.8-27B-GGUF `Qwen3.8-27B-Q8_0.gguf` | 29.05 GB | 1.08 |
| unsloth/Qwen3.6-35B-A3B-GGUF `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` | 22.13 GB | 0.63 |

Ollama 的 `qwen3.5:9b-q4_K_M` 為 6.6 GB；`ollama show` 顯示 9.7B 參數且 Capabilities 含 `vision`，差額來自看圖元件。

## KV cache 說法與原始來源的差異

影片說「把 KV cache 壓成八位元，六個工具呼叫裡五個格式壞掉」。影片引用的 [Level1Techs 文章](https://forum.level1techs.com/t/why-your-local-llm-feels-dumber-than-it-is/253917)首文寫的是：只量化 KV cache 時出現可重現的工具呼叫錯誤，BF16 正常，int8 最後恢復，int4 沒有恢復。第 23 則回覆比較多種 8 位元格式，int8 最好、兩種 fp8 差異大，作者結論是不要量化 KV cache，非要的話 int8 傷害最小。38 則貼文中沒找到「六個壞五個」的文字（可能在圖片內，未驗證）。Ollama FAQ 則說 `q8_0` 約省一半記憶體、通常沒有明顯影響。正文因此寫成：Level1Techs 評測中壓到 4 位元後工具呼叫出錯且沒有恢復，做 agent 任務時維持預設 `f16`。

## 本機實測：OpenCode 開場送出多少 token

實驗目錄：`tools/test-runs/20261108-local-models-video/`（`run.log`、`proxy.py`、`measure.py`、`requests-clean/`、`measure*.json`、`shots/`）。第一次量測的原始請求 `requests/` 與乾淨 HOME 的快取 `clean-home/` 只留在講師機器（前者含講師私人全域指示），以 `.gitignore` 排除。

- 環境：WSL2 Ubuntu、opencode 1.18.30、Ollama 0.21.2、RTX 5070 12 GB、模型 `qwen3.5-32k`（`qwen3.5:9b-q4_K_M` + `num_ctx 32768`）。
- 方法：複製 `starter/` 到 `project/`，provider 指向本機記錄代理 `127.0.0.1:11435`，代理把請求原樣轉給 Ollama 並存檔；執行 `opencode run "嗨" -m ollama/qwen3.5-32k`。再把存下的請求以非串流、`max_tokens=1` 重送 Ollama，讀 `usage.prompt_tokens`；另送一份去掉 `tools` 的版本，分離工具定義的成本。
- 第一次在講師帳號下執行：主請求 19,623 token。拆解發現 OpenCode 讀入了講師的 `~/.claude/CLAUDE.md` 與全域 skills 清單，學生機器不會有，不採用。
- 以乾淨 HOME（`clean-home/`，XDG 目錄全部指向其中）重跑：主請求 **7,555** token，去掉 10 個工具定義後 2,385，工具定義約 **5,170**；另有一個 550 token 的標題產生請求。乾淨環境仍含 OpenCode 內建的 `<available_skills>` 區塊。正文寫「約 7,500，其中約 5,200 是工具定義」。
- 限制：單次量測；token 數依模型的 tokenizer 而異（此為 Qwen3.5），OpenCode 改版也會變動。

## 審查

潤稿依 `speak-human-tw`（使用者授權直接套用）。改動交由三個 Herdr 分頁獨立檢查：Fable 5.1（job `47481a5c-d4ae-4b1b-9eae-905103b2f847`）、GPT-6 Astra（job `04937ae4-0361-41ea-8181-a32332b8b213`，有網路）、agy（job `5611b8f6-85ca-421c-86d6-94ea571ff07a`）。採納的主要更正：Mac 估算改寫；MoE 拿掉倍數並說明筆電放不下；4k 的影響改為第一輪說明與工具定義就放不下；context 滿時 OpenCode 會先 compaction；預設 context 表改 GiB 並標明區間；量化表標出例子型號；三個工具呼叫設定改成「可能」並補檢查方法與 KV cache 的測試條件；資安段改用原始報告的精確說法、拿掉 Tailscale、補權限設定位置與「工作資料夾不是隔離環境」。未處理：OpenCode providers 官方文件目前的寫法與本章 `npm`／`options` 寫法不同（本章寫法在 1.18.30 實測可用，屬既有內容）。`ollama show --template` 對 `qwen3.5` 只顯示 `{{ .Prompt }}`，因此不拿來當檢查方法。

複核（同三個 job，第二輪）：Fable 與 Astra 指出 Mac 規則仍把 24/32 GB 歸入 3/4，Astra 另指出 MoE、CPU 分擔、超限行為與「無獨顯即第一列」寫得過於確定，agy 指出「測量化」易誤讀；均已修正。三方對其餘修正均回報 fixed／none found。
