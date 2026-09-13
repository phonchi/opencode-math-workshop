# 全文讀者再讀後的修正追蹤

更新日期：2026-09-13。此文件記錄作者再讀報告 `internal/reader-student-review.md` 之後，教學來源已實際完成的修正；原報告是先前快照，行號可能改變。本批不改各 Lab、首頁、速查表或新數學應用，這些由主代理處理。

| 原報告項目 | 已完成修正 | 來源 |
|---|---|---|
| R5 專案路徑 | 移除後續章節固定 `cd ~/ai-math-lab`，改成先開啟課前同一份資料夾，用 pwd／ls 確認；不猜學生是否放在 Documents | first-run、agents-md、git-safety、mcp-skills |
| R5 init／Git 依賴 | 移除回原專案直接跑 init 的矛盾範例，改為先完成 Git 章，再於其他專案試 init | agents-md |
| R9 Git 比較基準 | 明確說明工作目錄、暫存區 index、HEAD；區分 diff、diff --cached、diff HEAD；restore 預設從 index 還原未暫存變更，另說明 --staged 保留檔案內容而取消暫存 | git-safety |
| R9 核心流程 | 先 status／diff／閱讀新檔，再 add、cached 檢查、commit；保留與還原拆成兩條路線，還原限制為尚未 add 的修改 | git-safety |
| R9 commit 後檢查 | 不再說 commit 後完全失去檢查機會，改成普通 diff 不再顯示、需另看歷史比較 | git-safety、agents-md |
| 首次 add 排除環境 | 首次 add 前明確建立 .gitignore，排除 .venv、__pycache__ 與 pyc，第6節只補充其餘項目 | git-safety |
| R1 筆記銜接 | 沿用主代理已改的互動 prompt；將筆記例子改為 Lab3 已有 notes/logistic.md，差異示例也改為梯度檢查的局部證據界線 | git-safety |
| R10 查證敘事 | 移出「我實際驗證過」乾淨環境對照，刪除 diff 真實／示意的作者辯白與文件差異敘事；學生頁沒有 internal 入口 | agents-md、git-safety、first-run |
| R11 reviewer 目錄 | 新增跨平台 Python mkdir 指令，先建立 .opencode/agents，再建立 .md，補 .txt 提醒；保留主代理已修的 JSON 與 task deny | mcp-skills |
| R12 本地自測 | 正文自測前明確要求目前模型是 ollama/...；仍為 Big Pickle 時先完成連接，避免測到雲端而誤認本地成功 | local-models |
| 重複安裝 | 第一次對話改連至課前準備；本章只保留資料夾、必要檔案與 Python import 檢查 | first-run |
| prep 報告感 | 移除 WSL／Windows 精確版本比較表、無依據的「九成是PATH」；保留查看版本的指令與下一步 | body_prep.html |
| auto 前後一致 | Git 章不再說學習階段絕對不能用，改成互動練習逐次確認，課前小型非互動自測例外連回prep | git-safety |

移出的歷史敘述附加保存在 `internal/teaching-maintenance-notes.md`，未放在學生網站上。

來源檢查：本批 Markdown 圍籬／補充區塊配對，prep HTML 結構，以及限本批來源的 git diff --check。未建置根目錄 HTML、未推送；平台互動與全站渲染由主代理整合驗收。

## 最後定點回查（2026-09-13）

本次只回查原作者讀者報告 R1–R12 與四個短句的對應位置，未再全文掃描，也未重跑數學實驗。根目錄生成頁與來源同時核對了首頁、prep、Lab3及速查表的重點。

| 原項目 | 回查結論 | 現況依據 |
|---|---|---|
| R1 非互動寫檔 | **確認無誤** | AGENTS.md 的實際任務已改互動 prompt；Git 使用已存在的 notes/logistic.md，先啟動 OpenCode、完成後離開再查看 diff |
| R2 PowerShell 語法 | **確認無誤（來源修正）** | prep 是 mkdir notes／mkdir figs 兩行；Git .gitignore 是文字編輯器與純檔案內容，沒有 Bash heredoc；本次不冒充新的 Windows 實跑 |
| R3 群數與錯誤合併解釋 | **確認無誤** | 首頁現為「指標偏好 k=9，資料有10種數字標籤」，沒有選錯 k／真實答案10；Lab1明說最大化silhouette選9有依據，並移除合併必然降低群內距離的錯誤因果 |
| R4 L2尺度與截距 | **確認無誤** | Lab3上下兩處一致：一般 λ||β||²/2，sklearn λ=1/(nC)，β不含截距；顯示的||w||仍含截距另有說明；唯一性限定本例兩類均存在 |
| R5 路徑與init依賴 | **確認無誤** | 本批後續章節不再固定cd ~/ai-math-lab；init改在完成Git章後於其他專案試，不再範例跳回原專案 |
| R6 現場與課後推導 | **確認無誤** | 現場prompt與清單已改概念／公式對照，完整推導另有課後prompt；最後兩句舊銜接也已修，來源與生成頁一致 |
| R7 表格與曲線驗收 | **確認無誤** | 梯度任務指定誤差容差；清單要求比較不同步長誤差，沒有要求必定看到U形圖；畫圖仍是課後練習 |
| R8 統計關係用語 | **確認無誤** | Lab1明示初始化敏感性不等於母體顯著性；Lab2共變異數接近零已限定為線性共同變動，保留非線性關係可能 |
| R9 Git基準 | **確認無誤** | 主章區分index／HEAD、diff／cached／diff HEAD，restore限制未暫存；速查表也明說從暫存區還原、不刪未追蹤檔案 |
| R10 查證敘事 | **確認無誤** | 指定作者驗證段落已移出，Git只說明diff內容，速查表不再比較官方／坊間與特定版本的缺漏 |
| R11 reviewer目錄 | **確認無誤** | 先用Path(...).mkdir(parents=True, exist_ok=True)，再建math-reviewer.md，並提醒勿多出.txt |
| R12 本地模型自測 | **確認無誤** | 正文先要求畫面為ollama/...；若仍為Big Pickle，先完成連接與切換，避免測錯模型 |
| 短句：連乘下溢 | **確認無誤** | 改為許多介於0與1的數連乘「可能」無法表示，不再宣稱357項必然下溢 |
| 短句：單調即停止 | **確認無誤** | 改由分群不變、容差或最大迭代次數停止，不以單調性單獨證明有限停止 |
| 短句：版本表／九成PATH | **確認無誤** | 平台精確版本對照表與九成敘述已移除；保留查看版本與重開終端機 |
| 短句：重複安裝 | **確認無誤** | first-run只連回prep，並保留位置、設定檔與import確認 |

### R6 最後收尾確認

主代理完成兩句修正與 Lab3 單頁重建後，本代理定點重讀來源及生成頁：

- `tools/body_lab3-notes.html:236`、`lab3-notes.html:938` 已改「因此仍要對照目標公式，不能只看數值 PASS」。
- `tools/body_lab3-notes.html:367`、`lab3-notes.html:1069` 已改「把今天已完成的程式、檢查與發現整理成筆記」。

確認無誤。原作者讀者報告 R1–R12 與四個短句均已修正並回查，至此封版；沒有尚待處理的原報告項目。此結論限於所列教學內容修正，不替代主代理另行執行的平台與瀏覽器驗收。
