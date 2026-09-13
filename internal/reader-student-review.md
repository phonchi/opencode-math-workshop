# 目標學生全文再讀：作者自查

2026-09-12。這是**作者再讀**：本代理先前參與了多數教學文案修改，不能把這份結果稱為未參與作者的獨立讀者審查。另一路獨立讀者由主代理安排。

受眾：只接觸部分微積分、線性代數，能看懂少量 Python，尚未熟悉 numpy、sklearn、終端機與 Git。

已依指定順序全文讀過全部 13 頁來源，含程式／prompt 範本、收合補充與頁尾；HTML body 以去除標籤但保留全部文字的方式閱讀，避免 inline CSS 影響閱讀。MCP 首段曾因工具輸出長度被省略，已另讀 1–95 行補齊。沒有修改任何教學來源，僅新增本報告。未重跑大型實驗、模型或瀏覽器驗收。

以下是讀取中的來源快照。主代理同時修正 Lab 3，已另列「發現後已修」，不把已修項目當成仍未處理。後續修正可能改變行號。

## 應先修正：直接影響照做或數學結論

### R1．兩個課後練習仍用非互動模式寫檔，會被本課程的 ask 擋下

位置：`content/agents-md.md:431`、`content/git-safety.md:358`。

AGENTS.md 第三層實際任務用 `opencode run "在 notes/ 寫一個 test.md..."`；Git 筆記潤飾也用 `opencode run`。兩者均未加 `--auto`，但課前設定是 `edit: ask`。依已核實的主線行為，這些寫檔請求會自動拒絕；學生可能反而以為規則沒生效。

最小建議：改成先輸入 `opencode`，再提供獨立的對話 prompt，沿用現場逐次確認流程。Git 例子的 `notes/pca.md` 也不是前面必定建立的檔案；可改用 Lab 3 已產生的 `notes/logistic.md`，或先明確要求建立示例筆記。

### R2．Windows 的可照抄指令仍夾有 Bash 專用語法

位置：`content/git-safety.md:288`–307；另有 `tools/body_prep.html:161`。

Git 教學直接提供 `cat > .gitignore <<'EOF'`，這是 Bash heredoc，不能在 Windows PowerShell 原樣執行。課前同一份跨平台指令中的 `mkdir notes figs` 也沒有採 PowerShell 明確的多路徑形式。

最小建議：`.gitignore` 改成「用文字編輯器建立檔案」加純檔案內容；課前改成兩行 `mkdir notes`、`mkdir figs`。這不必增加新的 shell 概念。

驗證限制：Bash heredoc 與 PowerShell 語法不相容可由語法確認；本次嘗試唯讀呼叫 Windows PowerShell 取得 `mkdir` 定義時，WSL interop 回 `UtilBindVsockAnyPort: socket failed 1`。因此本報告**沒有宣稱親自重現 mkdir 的 Windows 執行錯誤**，請交平台驗收確認或直接採無歧義的兩行寫法。

### R3．Lab 1 的「合併群會讓群內距離變小」錯誤，首頁仍把標籤數當分群答案

位置：`tools/body_lab1-cluster.html:182`–188、`:208`–223；首頁 `tools/body_index.html:58`、`:93`。

正文說合併相似數字後「群內距離會變小、群間距離會變大，silhouette 自然就上去了」。合併不保證降低群內距離，更不保證 silhouette 上升；還具體歸因於哪些數字混在一起，卻沒有相應的群組／標籤交叉表。首頁也說「選錯 k」「真實答案是 10」，與正文稍後澄清的「10 是標註類別數，不一定是最佳幾何分群」衝突。

最小建議：首頁改成「指標選 9，標籤有 10 類，兩者回答的是不同問題」；正文保留已算出的指標差異，把原因改成待檢查的假說，或只解釋 silhouette 的幾何目標。不要宣稱合併必然縮小群內距離。agent 知道 digits 有標籤並不難，因此「它不知道你手上有真實標籤」也宜改成「沒有先確認你要優化哪個目標」。

### R4．Lab 3 的 L2 公式與使用的 sklearn C 尺度不一致

位置：`tools/body_lab3-notes.html:124`、`:349`–360；`reference/lab3_logistic.py:148`。

正文 L 是平均對數損失，卻用 `L+||w||²/(2C)` 解釋 sklearn `C=1`，且 w 在前文包含截距。sklearn 此例實際懲罰是平均損失加 `||β||²/(2Cn)`，β 不含截距。

獨立來源核對：本機 `starter/.venv/lib/python3.13/site-packages/sklearn/linear_model/_logistic.py:464`–473 說明其目標為 `C*sum(pointwise_loss)+penalty`，`:580` 使用 `l2_reg_strength=1/(C*sw_sum)`；`_linear_loss.py:168` 將 `coef[:-1]` 當作權重，`:226` 起的 L2 penalty 只作用於該權重。

最小建議：一般介紹寫 `L(β,b)+λ||β||²/2`，解釋 β 不含截距；接本例時說明 λ=1/(Cn)，n=357。不要把 sklearn 的結果說成「對含截距的全部 w 加平方懲罰」所得。唯一解結論限定本例兩類樣本均存在，或把完整存在性論證移入補充。

### R5．後續章節重新假定專案在家目錄，和課前任選 Documents 的路線斷裂

位置：`tools/body_prep.html:158`、`content/agents-md.md:40`／`:162`／`:368`／`:403`、`content/git-safety.md:73`／`:158`／`:289`、`content/mcp-skills.md:69`／`:261`。

課前讓讀者自選位置（例 Documents），後續可複製範例卻固定 `cd ~/ai-math-lab`。照課前建立 `~/Documents/ai-math-lab` 的學生會得到路徑不存在，或進到另一份同名專案。

最小建議：各章開始用一句話要求開啟「課前建立的同一個資料夾」，以 `pwd`、`ls` 確認；後续命令不再硬寫猜測的 `cd` 位置。`AGENTS.md` 的 `/init` 段另說要去另一個練習資料夾，但例子又回原專案且先用尚未教的 Git，建議移成 Git 章之後的選修實驗或簡化成單一一致路線。

## 學生判讀與概念銜接

### R6．Lab 3 說推導可課後讀，但第一個必做 prompt 仍要求完整概似推導

位置：`tools/body_lab3-notes.html:15` 對照 `:170`–172、`:409`。

頁首說概似推導放深入補充，現場可先操作；第一個任務卻立即要求推導負對數概似和梯度，完成清單也要求已看過推導。對只修部分微積分的讀者，兩條路線仍沒有真正分開。

最小建議：現場 prompt 先要求以兩三句話解釋損失與梯度、依本頁提供的公式實作；完整推導放獨立的課後 prompt。相應把完成清單改成能說明損失與梯度各在做什麼。

### R7．Lab 3 完成清單要求看到曲線，但實際任務只要求表格

位置：`tools/body_lab3-notes.html:192`–198、`:410`、`:421`。

主線梯度檢查只要求製作表格；「畫成 log-log 圖」仍是最後的選修。然而必做檢查清單要求「我看到兩頭都會 FAIL 的 U 型曲線」。學生照做後沒有圖，無法誠實勾選。

最小建議：清單改成「我比較過各步長的誤差，知道過大或過小可能不準確」；或把畫圖正式加入主線。另須指定 PASS 的誤差容差，避免把教材中特定一組 FAIL/PASS 當成所有檢查點的必然結果。

### R8．兩處統計關係用語會教成錯誤判準

位置：`tools/body_lab1-cluster.html:294`、`tools/body_lab2-pca.html:59`。

Lab 1 用不同 random_state 重跑並看分布重疊，接著問「有無統計意義」。這測的是初始化敏感性，不能直接當成樣本母體上的顯著性檢定，分布是否重疊也不是一般的顯著性判準。Lab 2 把共變異數接近零說成「兩者沒什麼關係」，會把缺少線性關係誤解成沒有任何關係。

最小建議：前者直接改成「結果對初始化是否穩定」，保留種子重跑的實用練習；後者改成「沒有明顯線性共同變動，仍可能有非線性關係」。

### R9．Git 預設 diff／restore 的比較基準寫錯

位置：`content/git-safety.md:111`–130、`:189`，`tools/body_cheatsheet.html:122`／`:124`。

預設 `git diff` 比工作目錄與暫存區，預設 `git restore` 從暫存區還原；不是任何時候都直接相對上一個 commit。學生若先 `git add`、再後悔，照「所有未 commit 修改都可 git restore」的說法操作，檔案不會回到預期版本。

最小建議：明說本章這組簡化流程的前提是「修改後尚未 git add」；補一小句 `git diff --cached` 可看已暫存變更。無需引入整套進階 reset 教學。已 commit 的修改仍可從歷史比較，因此「commit 後失去檢查機會」宜限定成「一般 git diff 不再顯示」。

### R10．仍有應移往 internal 的作者查證敘事

位置：`content/agents-md.md:67`–89、`content/git-safety.md:203`、`tools/body_cheatsheet.html:69`–73。

AGENTS.md 保留「這點我實際驗證過」與乾淨環境對照報告；Git 強調「實際跑出來，不是示意」；速查表仍討論「官方與坊間列了，某版本卻沒有」。這些內容不是學生下一個操作，且使用者最新指示明確要求文件差異／未寫項目移 internal。

最小建議：AGENTS.md 直接解釋自動發現與 instructions 的作用，證據過程移 internal；Git 改「下面是一段 diff」；速查表只留「找不到斜線指令時用 ctrl+p 搜尋」，保留能操作的替代按鍵。對話／安裝示例本身有教學作用，不需一起刪。

### R11．自訂 reviewer 少了建立資料夾的入門步驟

位置：`content/mcp-skills.md:227`。

skill 練習明確先建立巢狀資料夾，reviewer 卻直接要求建立 `.opencode/agents/math-reviewer.md`。對使用記事本而不熟檔案路徑的學生，資料夾不存在時無法直接另存成這個檔案。

最小建議：加一行 `uv run python -c "from pathlib import Path; Path('.opencode/agents').mkdir(parents=True, exist_ok=True)"`，再教建立檔案。現有 reviewer Markdown／JSON 的 task deny 與證據措辭修正已確認無誤，不重報舊問題。

### R12．本地模型自測前需要在正文再次核對當前模型

位置：`content/local-models.md:150`–173。

完整設定範例為收合區塊，且刻意保留網路模型為預設。下一個正文標題直接進入檔案自測；略過收合範例的學生可能仍用 big-pickle 完成，誤以為本地設定成功。

最小建議：自測 prompt 前加「先確認畫面目前選的是 `ollama/...`，如果仍是 Big Pickle，先回上一節完成連接」。不需要增加硬體測試表或歷史限制標籤。

## 可一併修正的短句

- `tools/body_lab3-notes.html:77`：「357 個介於 0 和 1 的數連乘，會小到 float64 直接變成 0」過強。例如 `0.5**357≈3.406e-108`，仍遠大於最小正常數。改「可能小到下溢，取 log 可避免直接連乘」。
- `tools/body_lab1-cluster.html:100`：「每一步 J 不會變大，所以一定會停」只靠單調性推不出有限停止。改「每步不增加目標值；實作另以分群不再改變、容差或最大迭代次數停止」。
- `tools/body_prep.html:138`–147：以 WSL／Windows 為欄的精確版本比較表，以及「九成是 PATH」沒有幫助讀者做下一步。留 `opencode --version`／`uv --version` 和「先重開終端機」即可。
- `content/first-run.md:16`–40 重複課前安裝，再次進入模型／uv說明；可縮成「尚未準備請先完成課前準備」，保留啟動前最短檢查，讓30分鐘章節更聚焦。

## 逐頁全文閱讀紀錄

| 頁面 | 全文閱讀結果 |
|---|---|
| index | 已完整讀；R3 的 k／標籤數框架需修，其餘學習路徑可跟隨 |
| prep | 已完整讀；R2 跨平台指令、版本／PATH報告式短句需修 |
| first-run | 已完整讀；run／ask／auto 主說明確認無誤；可縮減重複安裝 |
| Lab 1 | 已完整讀；R3、R8 及停止條件短句需修 |
| Lab 2 | 已完整讀；新增投影互動和五關驗證連接確認無誤；R8 共變異數用語需修 |
| Lab 3 | 已完整讀；R4、R6、R7及連乘短句需修；本輪中途已補實作參數並修MLE逆向推論 |
| agent-workflows | 已完整讀；確認無誤：需求→小步驟→錯誤求助→保存進度→新對話重讀順序可跟隨 |
| agents-md | 已完整讀；R1、R5、R10需修；規則與權限的基本區分已建立 |
| git-safety | 已完整讀；R1、R2、R5、R9、R10需修；Git安裝／身分設定已具備 |
| mcp-skills | 已完整讀；R5、R11需修；skill發現／實際載入區分、免費路線、reviewer證據界線確認無誤 |
| local-models | 已完整讀；精煉後不再像量測報告，R12需補；設定和自測順序其餘確認無誤 |
| math-applications | 已完整讀；確認無誤：先給直覺、再給任務與獨立檢查；簡單路徑定義已補 |
| cheatsheet | 已完整讀；R9、R10需修；常用指令與主章權限規則大致一致 |

## 發現後已修正並重讀確認

主代理在本輪加入 Lab 3 的檔名、像素除以16、0/1標籤、截距欄與固定w0，並把步驟限制為先loss/grad、再梯度檢查；讀者不再必須猜參考輸出的前處理。此為文字要求完整度確認，模型能否確實照做交平台實跑驗收。

原「linprog找不到嚴格分隔⇒MLE有限且唯一」已改為不足以保證，並提醒準完全分離與特徵相依。獨立反例為 x=[-1,0,0,1]、y=[0,0,1,1]：x=0的兩筆標籤相反，所以不能嚴格分隔；但斜率w→∞時平均損失 `0.5*log(1+exp(-w))+0.5*log(2)` 單調趨近下界，無有限w取得下界。因此修正方向確認無誤。

新數學固定示例的獨立核算另見 `internal/math-review.md`；此處不重跑大實驗、不拿作者再讀替代獨立讀者與跨平台驗收。
