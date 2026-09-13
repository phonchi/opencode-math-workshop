# 第二位讀者：全文技術與章間流程審查

日期：2026-09-12。審查者：`layout_diagrams`，不是教學文案作者。本輪逐頁讀完 13 頁的正文、提示範本、程式碼／輸出範例、展開補充與練習；沒有把瀏覽器檢查或掃標題當成全文審查。原有 body 以文字抽取閱讀，Markdown 頁讀完整來源；工具回傳有截斷的段落另行補讀。

本文是內部審查紀錄，不是學生教材，也不應從正式網站連入。審查期間主代理同步修正來源，下列分開記錄初次發現與來源回查；產物是否已重建另看主代理最終驗收。

## 逐頁閱讀覆蓋

| 頁面 | 實際閱讀與判斷 |
|---|---|
| `index` | 讀過課程定位、示範對話、時間表、所有課程卡片、課前提醒。三小時與兩條課後入口可成立；「k=10 是真實答案」的卡片應與 Lab 1 的語義／幾何區分一致。 |
| `prep` | 讀過終端機入門、三平台安裝、完整三份設定檔、自測、錯誤表。發現 PowerShell 多資料夾命令問題；`run --auto` 自測例外說明本身合理。 |
| `first-run` | 讀過安裝銜接、TUI 圖例、所有操作與權限表、兩種模式、session、context、排錯。`ask` 在非互動下自動拒絕的說明已與 prep 一致。 |
| `lab1-cluster` | 讀過所有資料／numpy／k-means／silhouette／ARI 補充、任務、結果、追問與練習。指標與類別數區分是正確主題；合併群會降低群內平均距離的解釋不成立，見 F5。 |
| `lab2-pca` | 讀過正文、五道驗證、numpy 寫法、中心化、譜隙與兩項但書；另完整檢查 PCA 互動。共同尺度為何能逃過前四關的代數正確；共變異數與重根邊界說明見 F6／F7。 |
| `lab3-notes` | 讀過概似、sigmoid、梯度、中央差分、可分性證明、sklearn 比對、正則化與兩層筆記需求。無正則化可分資料沒有有限 MLE 的論證正確；原 L2 與 sklearn 的尺度／截距慣例不一致，見 F3。 |
| `agent-workflows` | 讀過完整任務模板、群中心示例、逐步實作、完整錯誤模板、模型不可用、context 與續作練習。任務要求與既有 Lab 可接續，明確保留原檔並要求核對成果。 |
| `agents-md` | 讀過規則機制、instructions、全域／專案、init、六種寫法、完整範例、反例、三層驗證、練習。區分設定讀取／行為證據已改善；寫檔行為測試原使用非互動 ask 路徑，見 F2。 |
| `git-safety` | 讀過安裝、七個命令、完整工作流、diff 例子、gitignore、圖檔政策、筆記、權限與急救表。PowerShell heredoc、非互動改檔與 index／HEAD 語義問題見 F1／F2／F4。 |
| `mcp-skills` | 讀過 MCP remote／local 設定、排錯、兩種 reviewer 完整範例、subagent、完整 SKILL.md 與練習。MCP optional 且額度／認證停止條件清楚；reviewer 已同時拒絕 edit/bash/task，且沒有執行證據時不宣稱測試通過。 |
| `local-models` | 讀過精簡後完整 231 行，包括 Ollama 安裝、tools、Modelfile、provider、context、寫檔檢查及排錯。主線與本地選修已明確分開；配置名稱彼此對應，並要求核對實際工具執行。未在本輪重新載入本地模型。 |
| `math-applications` | 讀過低秩近似、梯度下降、最短路徑的所有任務、公式與判讀。獨立推導三個可驗證結果，見下節；三題均沿用既有環境與輸出目錄。 |
| `cheatsheet` | 讀過全部 CLI、TUI、快捷鍵、uv、git、錯誤表、提示習慣與三 Lab 數值表。快捷鍵／ask 說明與 first-run 一致；git 簡化定義需和 F4 同步。 |

## 確認無誤的推導與檢查

- **PCA 共同尺度盲點：確認無誤。** 若 `C'=cC` 且 `c>0`，特徵向量可保持相同，特徵值全乘 `c`，解釋變異比例約去 `c`，投影重建不依賴特徵值尺度；直接比較特徵值才會識別此處的分母差異。這是「對照本章 n−1 定義」的錯誤，不能擴大成所有採用 n 分母的 PCA 皆無效。
- **Logistic 梯度與可分性：確認無誤。** 對 `log(1+exp(z))-yz` 微分得到 `sigmoid(z)-y`；鏈鎖律給 `Xb.T@(p-y)/n`。嚴格分隔方向上 `L(cv)` 趨近 0，而有限參數的每項 loss 正，故無有限最小值點；這個證明只涉及本批樣本。
- **低秩示例：確認無誤。** `exp(-5(x²+y²))` 可分成一個外積；`cos(6x+3y)=cos(6x)cos(3y)-sin(6x)sin(3y)` 再提供兩個外積，因此示例矩陣秩最多 3。保留四項可在浮點誤差內重建，不能外推到一般影像。
- **梯度下降示例：確認無誤。** 代入更新式得到 `x[t+1]-3=(1-2η)(x[t]-3)`；三個倍率分別為 `0.8`、`-0.6`、`-1.2`，依序為不交替收斂、交替收斂、交替發散。
- **最短路徑示例：確認無誤。** A-B-C-D-E 距離為 5；A 的最短前綴至 B/C/D 依序為 2/3/4，至 E 為 5，符合非負權重下的逐步最短距離。新增無邊的 F 應回報無路徑，不能當成 0。
- **瀏覽器互動：確認無誤。** 13 頁四種寬度的版面、字型、MathJax 與本機鏈結已完成；PCA 的 0/45/90/180/主成分角度與獨立參考數值比對，容差 `1e-10`。完整證據在 `tools/test-runs/20260912-workshop-refresh/browser/acceptance-summary.json`，其 hash 對應的是本輪文案修正前、當時已建置的受測 HTML；之後來源再修改，仍須重新建置及必要的定點檢查。

## 發現、證據與修正方向

### F1 · P1 · Windows 無法照貼的命令

初次閱讀 `tools/body_prep.html:159` 的共用建立資料夾範本為 `mkdir notes figs`。在本機 Windows PowerShell 執行唯讀預演 `mkdir notes figs -WhatIf`，exit code 1，`FullyQualifiedErrorId: PositionalParameterNotFound,mkdir`。`Get-Command mkdir` 同時顯示 Path 的 `Position=0`、`ValueFromRemainingArguments=False`。

另初讀 `content/git-safety.md` 的 gitignore 範例使用 `cat > .gitignore <<'EOF'`，是 Bash heredoc，PowerShell 無法照貼。

**來源回查：確認已修。** prep 現為逐行 `mkdir notes`／`mkdir figs`（`tools/body_prep.html:159–162`）；gitignore 改成文字編輯器建檔並貼純檔案內容（`content/git-safety.md` 第 6 節）。本 reviewer 沒有自行更改這些教學來源。

### F2 · P1 · 非互動寫檔範例和 ask 權限衝突

初讀 AGENTS.md 第 9 節的層次 3 使用 `opencode run "在 notes/ 寫一個 test.md…"`；Git 第 7 節使用 `opencode run "幫我潤飾 notes/pca.md…"`。同一課程配置把 `edit` 設為 `ask`，prep／first-run 已明寫 `run` 沒有人回答權限要求而會 auto-reject，兩個範例因而不能保證產生所教的寫檔結果。

**來源回查：確認已修。** `content/agents-md.md:426–434` 與 `content/git-safety.md:356–373` 已改成先開互動模式，再貼任務並確認寫檔要求。避免為了一個教學範例把全域權限改成 allow。

### F3 · P2 · 平均 logistic loss 與 sklearn C 的正則化尺度不一致

初讀 `tools/body_lab3-notes.html:124`、同檔 `359` 以平均 loss 加上 `||w||²/(2C)` 說明 sklearn `C=1`。然而 sklearn 在無 sample/class weights 的本題中對應平均 loss 加上 `||β||²/(2nC)`，而預設 lbfgs 不懲罰截距。此題 n=357；照原公式手刻會將懲罰強度放大 357 倍，且把截距一起懲罰時又是不同目標。

核對來源：[scikit-learn Logistic regression 數學式](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)。也讀過目前安裝的 `starter/.venv/lib/python3.13/site-packages/sklearn/linear_model/_logistic.py:463–474,580`：實作以 `sw_sum=n_samples` 並設 `l2_reg_strength=1/(C*sw_sum)`。

**來源回查：上半已修，下半待同步確認。** `tools/body_lab3-notes.html:124–131` 已改為 `λ||β||²/2`，說明 `λ=1/(nC)`、截距不受懲罰與兩類都存在；回查時第 359–360 行尚有原 `1/(2C)||w||²` 段，已即時回報主代理。幾何間隔文字也應說分母只取特徵權重：`reference/lab3_logistic.py:93` 實際用 `norm(v[:d])`，正文 `margin/||v||` 若 v 包含截距容易誤讀。

### F4 · P2 · Git 的 index 與 HEAD 被混為同一個基準

`content/git-safety.md:108–123,189` 與 `tools/body_cheatsheet.html:122–124` 把預設 `git diff`、`git restore` 說成相對上次 commit。實際上預設 diff 比工作樹與 index；restore 預設從 index 還原工作樹。反例：修改後先 `git add`，尚未 commit 時，`git diff` 可以沒有輸出，`git restore .` 也不會把已暫存內容退回 HEAD。

來源：[git diff](https://git-scm.com/docs/git-diff)、[git restore](https://git-scm.com/docs/git-restore)。這會讓初學者把「diff 空白」誤判成沒有改動，也會困惑為何還原無效。

最小修正：明說本章先檢查、再 add 的前提；用「尚未暫存」取代「所有未 commit」。補充 `git diff --cached` 看已暫存內容、`git diff HEAD` 看相對提交的整體差異，並保留 untracked 不會被 restore 刪掉的既有說明。不必因此教更多破壞性還原命令。

### F5 · P2 · 群合併為何提高 silhouette 的敘述過度推論

`tools/body_lab1-cluster.html:209–216` 宣稱特定數字對重疊，合併後「群內距離會變小、群間距離會變大，silhouette 自然就上去了」。群合併不保證降低同群平均距離。例如把 `{0,0.1}` 併入 `{0.2,0.3}`，點 0 的同群平均距離由 0.1 變為 `(0.1+0.2+0.3)/3=0.2`，反而增加。這份 k=9 的具體原因也不能只由一組分數或列出相似數字對就判定。

最小修正：保留幾何目標不等於數字標籤的核心，將具體成因當作要查看群中心與群別×標籤交叉表的問題。並同步首頁 `tools/body_index.html:93`「真實答案是 10」的用語，避免摘要又把標籤數誤當成幾何最優 k。若目標本來就是最大化 silhouette，選其最高值本身不是程式錯誤；需先說明何種研究目標不能只依此判斷。

### F6 · P2 · 共變異數接近零不代表沒有關係

`tools/body_lab2-pca.html:58–59` 寫「接近 0 代表兩者沒什麼關係」。反例：X 等機率取 -1/0/1，Y=X²；`E[X]=E[XY]=0`，故 covariance 為 0，但 Y 完全由 X 決定。

最小修正：改成「線性共同變动弱；仍可能有非線性關係」，不要把不相關說成獨立。

### F7 · P2 · 重根跨過 K 的截斷邊界時，投影矩陣也不必相同

`tools/body_lab2-pca.html:285–287` 建議重根時比較 `W.T@W`，還需限定比較完整重根區塊，或保留與捨棄方向間有譜隙。例：`C=diag(2,1,1), K=2`，保留 `{e1,e2}` 與 `{e1,e3}` 都是最佳二維 PCA，但投影矩陣分別是 `diag(1,1,0)` 與 `diag(1,0,1)`，不相等。

digits 主線已列第 10/11 特徵值間隔，**該主線的逐向量比較確認無誤**。只需補全「換資料遇到重根」的課後泛化說明，不必重寫整個 Lab。

## 章間流程與冗餘

1. 主線有清楚遞進：環境→工具行為→分群指標→PCA 驗證盲點→梯度與推導筆記。新的 PCA 互動能在特徵分解之前先建立投影直覺；Lab 3 已把更深的理論移入可展開區塊，對現場節奏有幫助。
2. 課後兩條線可以並行。`agent-workflows` 以既有 Lab 為輸入，`math-applications` 以新數學問題為輸入，兩者不需要彼此先修。操作線的 pager 為 workflow→AGENTS→git→MCP→local，與側欄一致。首頁仍保留舊數字標號／較早的卡片順序，沒有功能阻斷，但不要把卡片順序說成唯一必修順序。
3. `first-run` 已將大型快捷鍵清單集中到 cheatsheet；剩餘安裝段可作忘記準備者的補救入口。prep 的完整設定與 AGENTS 章的深入拆解目的不同，不應為了縮字數整段刪除。真正需要同步的是重複出现的**行為定義**（ask、git 基準、L2 尺度），不是所有重複句子。
4. `cd ~/ai-math-lab` 在多個課後範例中仍是假定位置，而 prep 允許在 Documents 等任意位置建立專案。建議每章第一次使用時提醒「換成自己建立的路徑」，讓同學不會從已正確的資料夾被帶去不存在的家目錄路徑。

## 限制

這是全文內容與有限技術核對，不宣稱每個即時模型都會生成與範例逐字相同的回應，也沒有在本輪重新測試所有第三方 MCP 或下載本地模型。瀏覽器的通過不抵銷 F4–F7；主代理完成來源修正與重建後，應只針對受影響頁做必要回查。

## 2026-09-13 修正後定點回查

按主代理要求，只重新讀取已列出的問題段落，未重新展開全站掃描，也未建置或啟動新一輪瀏覽器。

- **F3 確認無誤，來源已修。** `tools/body_lab3-notes.html:124–131` 使用不含截距的 `β`、獨立截距 `b`、`λ=1/(nC)`；同檔 `359` 的第二個說明也已改成 `||β||²/(2nC)`，並說明輸出的 `||w||` 仍包含截距。兩處現在描述同一個目標，而非只修上方公式。有限唯一解的結論已限制於本例兩類均存在且懲罰為正的情境。
- **F4 確認無誤，來源已修。** `content/git-safety.md` 第 3 節現已區分工作目錄、index 與 HEAD；表格列出 `git diff`、`git diff --cached`、`git diff HEAD` 三種基準。restore 段清楚限制為未暫存修改，已暫存情況另說明，完整工作流也先檢查再 add。`tools/body_cheatsheet.html:120–126` 已同步，沒有讓速查表保留舊的還原承諾。
- **F5 的因果敘述確認已修。** `tools/body_lab1-cluster.html:209–215` 將 k=9 明確限制為本資料／初始化／搜尋範圍中的觀察；說明合併不保證降低群內距離或提高 silhouette，改為用群中心及群別×標籤組成尋找原因。`292–293` 不再把模糊群中心當作合併證據，也不把改 random_state 當成母體顯著性檢定。
- **F6 確認無誤，來源已修。** `tools/body_lab2-pca.html:59` 改為線性共同變動較弱，仍可能有非線性關係。
- **F7 確認無誤，來源已修。** `tools/body_lab2-pca.html:287` 明確要求完整重根區塊，並補上第 K／K+1 特徵值間隔；從重根中間截斷時，不要求兩個最佳 K 維子空間的投影矩陣相同。

### PCA 手機學習可用性

以實際 390 px 手機版的完整元素截圖 `tools/test-runs/20260912-workshop-refresh/browser/final-check/review-pca-explorer-mobile.png` 判斷，這個互動**可以用來學習**，不只是不溢出：題目與操作說明在圖前，滑桿跨滿可用寬度，兩個按鈕各自可讀，投影變異／平均重建平方距離並排且字體足夠大；黑圓點、空心方框、藍線及虛線有不同形狀／線型，圖下文字也解釋其意義。操作區最小高度 44 px；數學推導可展開，不會擋住初次操作。

證據限制：手機版可視判斷與程式化滑桿／按鈕／鍵盤檢查已完成，沒有用真實手指在實體手機上操作。點／方框在小圖上較小，但這個練習不要求觸碰個別資料點，使用者只須調整滑桿和比較整體形狀，因此不構成目前的操作阻礙。前一版元素截圖頂端被 sticky header 覆蓋是截圖自動捲動造成，乾淨的 document-clip 原圖已修正，網站並無該裁切。

## 最終建置後驗收

2026-09-13：主代理完成全部讀者修正並建置後，比對先前驗收 hash；只重測 11 個變動頁（44 個頁面／viewport 情境）與 11 個相關互動情境，0 項失敗。兩個未變頁沿用相同 hash 的既有證據。最終 13 頁的 HTML SHA-256 與所選報告皆吻合，完整範圍表在 `tools/test-runs/20260912-workshop-refresh/browser/acceptance-scope.md`，最新全部截圖入口為 `accepted-final-all-items-contact-sheet.html`。本次沒有再修改教學正文或重新全文審查。

### Lab 3 最後兩句文字補測

主代理再調整 Lab 3 兩句課前／課後銜接文案後，只對該頁補測四種寬度、MathJax、字型與內鏈，4／4 通過、0 失敗，沒有重測無變互動。其餘 12 頁 HTML hash 未變；13 頁完整 hash 範圍表與截圖總覽均已更新。原始證據：`tools/test-runs/20260912-workshop-refresh/browser/lab3-copy-final/report.json`。

### Reviewer 專案範圍限制補查

2026-09-13：核對 `content/mcp-skills.md` 的 Markdown reviewer 與 JSON reviewer，兩者都限定本專案與已有輸出、避免讀取其他 Python 環境；`edit`／`bash`／`task`／`external_directory` 四項皆為 `deny`，來源一致性確認無誤。僅 MCP 頁補測四種寬度、MathJax、字型與內鏈，4／4 通過、0 失敗；沒有新增模型回合，也不以這項瀏覽器檢查聲稱所有外部讀取路徑皆完成行為測試。正式範圍表的 13 頁 HTML hash 與全部截圖入口已更新。證據：`tools/test-runs/20260912-workshop-refresh/browser/mcp-scope-final/report.json`。
