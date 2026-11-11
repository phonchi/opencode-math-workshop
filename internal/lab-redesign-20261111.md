# 第三輪改寫：V2、依用途選答案、減少手刻（2026-11-11）

講師試教後提出 12 點修改。本文件記錄決定與實測，正文不放這些內容。

## 決定
- 學員改裝 OpenCode V2（`curl -fsSL https://opencode.ai/v2/install | bash`），並在 `~/.config/opencode/cli.json` 開啟第三方外掛 `@rashidrazak/opencode-status-line`。
- Lab 1、Lab 2 沒有唯一答案：兩關都同時給兩個用途（Lab 1 店型手冊／客訴回查；Lab 2 訂單概況／客訴預警），讓學生看到答案依用途而不同。判斷步驟的「AI 常見的反應」收合全部移除；參考數字改放「參考結果」收合。
- Lab 1 需求卡不再寫「10 家分店」「第 1、10 家同一捷運站」。改由三個不看店別的指標分歧（silhouette、DB 選 9，CH 選 10）帶出依用途選；店別紀錄延到選好 k 之後才下載。
- 「列出你替我做的每個決定（前處理、準則、門檻、丟掉的欄位），先不要下結論。」三關同一句，收尾寫成 AGENTS.md 規則。課前 AGENTS.md 不放這條，以免第一步就沒有對照。
- 短 prompt＋Plan：課前 AGENTS.md 加「Plan 模式先一次問一題、附建議答案、最多 3 題」。只在 Lab 1 第 4 步使用，其餘直接給 prompt 或收合的參考 prompt。
- 同儕配對與要學生動筆寫卡的步驟刪除，卡片改成已填好的示範。
- Lab 3 的手刻 logistic 與梯度檢查移到課後收合；`notes/decision.md` 與第一次記 context 用量移到門檻決策之後。
- PCA 動畫：點、刻度、方向、投影、比例都由同一份座標計算，兩軸同比例尺；第 5 步改為標準化／原始公里分鐘／原始公尺分鐘三種。
- 參考程式改為先讀學生專案的 `data/`，找不到再讀 repo 的 `assets/data/`；各關課後補充有「下載參考程式」。
- starter 加 pandas（`pandas>=2.2`；Python 3.11 以上鎖到 3.1.1）。

## 已驗證的數字
- Lab 1（標準化、random_state=0、n_init=10）：silhouette 最高 k=9（0.7942）、DB 最低 k=9（0.2740）、CH 最高 k=10（4956.0，k=9 為 4726.1）。k=9→10 只把 159 筆那群拆成 85、74 筆。ARI：k=9 0.8811、k=10 0.9902，k=10 有 3 筆與店別不一致（資料列 73、81、575），跨 100 個 random_state 不變（Astra 實算）。
- Lab 2：AUC 0.588／1.000／1.000 是 5 折折外分數合併後算一次；逐折平均為 0.574／1.000／1.000。正文只寫「5 折交叉驗證」。
- PCA 動畫 60 點：標準化 PC1 45.0°、96.26%；原始公里／分鐘 74.48°、98.92%；原始公尺／分鐘 0.18°、99.9998%（瀏覽器 dataset 與 Astra 的 numpy 計算一致）。
- 參考程式在 repo 與 Windows 學生專案各跑一次，PASS/FAIL 與三位小數一致：`tools/test-runs/20261111-reference/`。

## V2 與 V1 的差異（Windows Git Bash 實測）
詳見 `tools/test-runs/20261111-v2-windows/README.md`。教材有改的：
- 切換 Build／Plan 改為 `Shift+Tab`（`Tab` 無作用）。
- 權限選項 `Always allow`（V1 為 `Allow always`）。
- `opencode run` 自動拒絕的錯誤訊息改為 `This non-interactive run cannot ask the user for permission…`。
- `/new` 在頂端開新的 session 分頁；啟動畫面沒有 Tip 列。
- V1 寫法的 `opencode.json` 仍可用（V2 自動轉換），starter 不必改。

## 顧問意見
三個 Herdr 分頁的唯讀建議（Astra：數學與資料；Fable：教學結構；Gemini 3.8：V2 事實）。Gemini 報告中的設定覆蓋順序、`OPENCODE_CONFIG`、auth 改 SQLite 等說法與官方頁或實測不符，沒有採用。設定檔收合區只寫實測與官方文件一致的部分。

## 潤稿與審閱
- speak-human-tw 潤稿 6 處（Lab 3 重複句與避險語、Lab 3 步驟拆段、Lab 1 三指標改列表、課前狀態列範例字串移除、PCA 動畫第 5 步說明、Lab 3 規則句）。
- 潤稿後請三個分頁審閱：
  - Astra：Lab 2 標籤「只能用來檢查」與訓練分類器衝突、參考 prompt 的 W 形狀未定義會讓 WWᵀ 檢查誤判、Lab 3 梯度方向說反。三處都已修。Astra 另外重跑 5 支參考程式並核對 PCA 動畫，確認無誤。
  - Fable：Lab 3 課後梯度收合的公式框與 danger 框被切空（搬移時的切段錯誤）、Lab 1 切回 Build 要收小範圍、Plan 問答要有明確換軌條件、`notes/decision.md` 與 AGENTS.md 規則要給可貼的句子、圖說與驗收卡名稱不一致。都已修。「Plan 模式執行 ls」那則保留，因為實測時它直接列出檔案、沒有先發問。
  - Gemini 3.8：first-run 環境檢查漏 pandas、Lab 2／3 下載後沒提醒按 Esc 離開 Shell、mcp-skills 一處 Tab、故障排除的路徑位置。都已修。

## 追加：provider 討論與 GitHub Copilot（同日稍晚）
- 與 Astra、Fable、Gemini 3.8 討論其他 provider。結論：沒有同時符合免費、按帳號計、免綁卡、OpenCode 可接、一堂課夠用的新選項。Groq（token 日上限太小）、OpenRouter 免費（未儲值 50 請求／日）、Cerebras、Ollama Cloud、Mistral 免費都不建議。尚未決定：Zen 預設改用零保留的 `glm-5.3-flash-free`／`deepseek-v4.1-flash-free`、NVIDIA 改用 flash 模型、是否改 Gemini 優先。
- NVIDIA 免費額度：個人帳號 40 RPM（NVIDIA 論壇工作人員 2026-05-30 回覆）；每日 10,000 請求只見於第三方追蹤頁。課前頁補了「註冊要手機簡訊驗證碼」。
- Copilot：v2.2.7 起支援 Auto（PR #62997）。credits 數字經 Astra、Fable 查證並抽查原文：1 credit＝0.01 美元、按 token 依模型價目扣；Pro 1,500、Pro+ 7,000、Max 20,000；Student 200（官方 community 公告）；Free 未公布。Free／Student 只能用 Auto。Student 不在 2026-04-24 訓練政策內（官方 FAQ #188488）。Auto 九折只寫到付費方案的 Chat／cloud agent，OpenCode 是否適用不確定，正文不寫。
- Copilot Auto 實跑見 `tools/test-runs/20261111-copilot-auto/`：照教材 prompt 三關約 8.2 credits。舊背景服務上 `patch` 工具卡住，重啟服務後未重現。
- 處置：starter 與課前頁的 `opencode.json` 加 `"plugins": ["-opencode.tool.patch"]`（GPT 系列模型改用 write/edit，其他模型不受影響；原始碼依據 `packages/core/src/tool/plugin/patch.ts:288`，Astra 讀碼、實測可用）；「卡住了？」表加一列（`/exit` → `opencode service restart` → 重開）；課前頁新增「選配：已經有 GitHub Copilot 的人」收合。
