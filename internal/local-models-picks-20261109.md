# 本地模型章：「依記憶體挑起點」推薦表的查證與實測

日期：2026-11-09。延續 `internal/local-models-video-20261108.md`。使用者要求依影片 [AI懶人報 EP460](https://www.youtube.com/watch?v=1nomxygMILI) 推薦模型，並對放得進 12 GB 顯示卡的候選實際跑本章最後一關。

## 模型對應與來源

候選取自影片提到的模型（16 GB 級 Gemma 4 E4B、Qwen3.5 9B、gpt-oss-20b；32 GB 級 Qwen3.8 27B、Gemma 4 26B、Qwen3.6 35B；128 GB 級 gpt-oss-120b）。8 GB 列用同系列較小的 `qwen3.5:4b`，影片沒有提到這一顆。名稱、大小與能力於 2026-11-09 從 Ollama 模型庫頁面（`https://ollama.com/library/<名稱>` 與 `/tags`）取得：

| Ollama 名稱 | 下載大小 | 能力標籤 | 備註 |
|---|---|---|---|
| `qwen3.5:4b` | 3.3 GB | tools、thinking、vision | |
| `qwen3.5:9b` | 6.6 GB | tools、thinking、vision | 影片說 HF 檔約 5.7 GB，Ollama 版含視覺元件 |
| `gemma4:e4b` | 6.6 GB | tools、thinking、vision、audio | 影片說約 5 GB |
| `gpt-oss:20b` | 14 GB | tools、thinking | 影片說檔案約 12 GB |
| `gemma4:26b` | 16 GB | 同 gemma4 | 模型頁寫明「Mixture of Experts model with 4B active parameters」 |
| `qwen3.8:27b` | 18 GB | tools、thinking、vision | |
| `qwen3.6:35b` | 23 GB | tools、thinking、vision | 35B-A3B MoE |
| `gpt-oss:120b` | 65 GB | tools、thinking | 影片說約 63 GB |

`tags` 頁上的大小區間（例如 `6.6GB - 9.5GB`）包含 MLX 等變體，表中取預設標籤的大小。影片中的 Qwen3.8 Flash Next 在 Ollama 模型庫找不到對應名稱，未列入。

## 實測

實驗目錄：`tools/test-runs/20261109-model-picks/`（`run_final_task.py`、`run.log`、`summary.json`、`runs/<模型>-run<n>/{transcript.txt,result.json}`、`models/`、`modelfiles/`）。

- 環境：WSL2 Ubuntu、RTX 5070 12 GB、Ollama 0.40.15（本輪由使用者從 0.21.2 升級；舊版下載 `gemma4:e4b`、`qwen3.5:4b` 回傳 412，要求新版）、OpenCode 1.18.30。
- 方法：每個模型以 Modelfile 加 `PARAMETER num_ctx 32768` 建立 `<名稱>-32k`；複製 `starter/`，登錄 Ollama provider；以乾淨 HOME（只有 OpenCode 自己的快取）執行 `opencode run "<本章最後一關的任務文字>"`；結束後由腳本自行檢查 `local_hello.py` 是否存在、`uv run python local_hello.py` 的輸出是否為 1 到 100 的十個平方數（每行取最後一個數字，或整段數字依序）。每個模型兩次。
- 與教材不同之處：`opencode run` 是非互動模式，無人回答 `ask`，所以測試副本改用最小權限：`bash` 只允許 `uv run python local_hello.py`，其餘指令、上網與專案外的資料夾一律拒絕。第一次以 `allow` 全開的設定被自動模式的安全檢查擋下，才改成這樣。
- `ollama ps` 確認三個模型都以 CONTEXT 32768、100% GPU 執行。

| 模型 | 第 1 次 | 第 2 次 |
|---|---|---|
| `qwen3.5:9b` | 完成，27.3 秒 | 完成，41.4 秒 |
| `gemma4:e4b` | 完成，43.5 秒 | 完成，15.2 秒 |
| `qwen3.5:4b` | 未完成：只呼叫 todowrite 列出待辦（「讀取 AGENTS.md」標為進行中，沒有實際 Read），未寫檔 | 未完成：只 Read AGENTS.md 後結束，沒有列待辦 |

完成的四次都寫檔並執行出正確結果。有文字回報的三次與實際結果相符；`qwen3.5:9b` 第 1 次在執行後直接結束，transcript 沒有最後回報（審查時 Fable、Astra、agy 指出，已核對）。`qwen3.5:4b` 沒有謊稱完成，只是停在第一步；transcript 中沒有權限拒絕紀錄。耗時只代表這台機器、這次執行，正文不寫。

## 失敗嘗試（保留供追溯）

- `runs-failed-freshhome-20261109T0806/`、`runs-failed-pwd-20261109T0810/`：全部在約 1.5 秒內以 `UnknownError` 結束。`--print-logs` 顯示 `ProviderModelNotFoundError: Model not found: ollama/<名稱>`。原因是 OpenCode 1.18.30 依環境變數 `PWD` 判斷專案位置；Python `subprocess` 以 `cwd=` 切換目錄時 `PWD` 仍是上層目錄，所以沒讀到專案的 `opencode.json`。在子行程環境設定 `PWD` 後即正常（同一專案、同一 HOME 對照：未設 rc=1，設定後 rc=0）。日後寫 OpenCode 的自動化測試要注意這點。

## 未實測

`gpt-oss:20b`（14 GB，超過 12 GB 顯示卡）及 24 GB 以上各列都未實測；正文以「未實測」標示。速度一律不寫入正文。

## 審查（2026-11-09）

Fable、Astra（有網路）、agy 於同三個 Herdr 分頁審查。採納：`qwen3.5:4b` 不是影片介紹的模型要標明；`gpt-oss:20b` 也是 MoE（約 21B 總參數、3.6B 啟用；`120b` 亦為 MoE，約 117B 總參數）要標示；9B 第 1 次沒有最後回報、4B 兩次的行為各不相同，正文改為逐次描述；補充測試權限與課堂 `ask` 流程不同；表頭改「候選模型」以免把失敗的 4B 讀成推薦；記憶體一律指「能給模型的記憶體」；沒有獨立顯示卡不等於一定用 CPU，改為用 `ollama ps` 的 `PROCESSOR` 欄確認；下載大小限定為測試時的預設版本；8 GB 結論改為「這次沒有找到能通過的模型」；`gpt-oss:20b` 註明 16 GB Mac 放不下、16 GB 顯示卡 context 空間有限需實測；128 GB 改為「影片以 128 GB 機器示範」。
複核（同三個 job，第二輪）：agy 無新問題；Fable、Astra 指出影片的 64 GB 指整台機器記憶體、表格中 9B 的「兩次都完成」與正文缺回報不一致、下載大小只有三顆是實測版本、無獨顯多半用不到內建 GPU、本檔 gpt-oss 參數量只適用 20b；均已修正。

## 正文調整（2026-11-09，使用者決定）

使用者要求推薦表只列表格、不提實測：正文移除「講師實測：最後一關」欄、測試環境與結果兩段，以及依實測得出的 8 GB 結論，改引影片對 16 GB 以下小模型的說法（影片 03:16–03:48）。本檔的實測紀錄與 `tools/test-runs/20261109-model-picks/` 保留，供講師追溯。
