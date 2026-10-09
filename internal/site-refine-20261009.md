# 2026-10-09 工作坊網站精修

基準 HEAD：`6a916d5`。本輪實作與驗收已完成；使用者其後以「推送吧」授權提交並推送至 `origin/main`。GitHub Pages 的發布來源為 `main` 根目錄，實際發布版本以 Git 與 Pages 部署紀錄為準。

## 活動與取捨

定位依中山大學人工智慧與數學整合學程的活動頁，正式活動名稱為「AI Agent × 數學｜OpenCode 體驗工作坊」。維持兩小時的 OpenCode 操作與三個 Lab，沿用暖紙色、靛藍、赤陶色與既有字體。成大資源改編為獨立課後章節，主線只留入口。

- 首頁改為正式名稱、課前與第一次對話兩個入口、真實 digits 樣本與三個實作問題。課後清單與側欄同序。
- 文案按使用者確認的六處修改與其後「直接潤稿」授權，使用 speak-human-tw；公式、指令、展示數值與承諾邊界保留。
- 每個 Lab 增加現場閱讀路徑；PCA 只改善操作提示，沒有改計算或新增互動。
- 三組圖均有桌機／手機版與可重現產圖來源。Lab 1 重算全部 11 組指標；Lab 3 只重繪既有七列，沒有補點或重跑訓練。
- `research-notes.html` 教學生用現有 OpenCode 整理指定的公開短摘錄、自己的程式與已有結果。來源、AI 解釋、自己的推導分開記錄；預設從 PCA 的中心化問題開始。

Claude Opus 5.5 已完成三輪唯讀諮詢，沿用既有訂閱，工具關閉，只提供從公開網站取得的教材。主代理採納正式名稱、首屏入口、分組路線與少量資料圖；沒有採用跳過第一次對話、增加 PCA 反轉開關或更多圖表等建議。去除帳號資訊後的完整三輪結果保存在 `tools/test-runs/20261009-site-refine/claude-consultation.json`。

## 驗收與限制

證據根目錄：`tools/test-runs/20261009-site-refine/`；最終彙整為 `summary.json`。

- 14 頁 × 4 種尺寸，共 56 組版面檢查通過。尺寸為 1440×1000、1280×900、1024×900、390×844；瀏覽器為 Chromium 151。
- 15 項互動檢查通過：首屏入口、桌機與手機錨點／收合、file:// 複製備援、無 JavaScript 導覽、勾選重載、PCA 獨立數值與按鈕／鍵盤、Lab 3 課後入口、新筆記模板複製，以及 localhost HTTP 載入與複製。
- 原有 13 頁的公式、指令、展示數字、段落錨點、checkbox ID 均與基準相符，導覽行為及參考程式沒有修改。新中心化小例子已獨立核算。
- 完整建置重現 28 個 HTML／body 檔；兩次獨立產圖的 19 個圖檔與數據檔逐位元一致。此結果限相同資料、參數與已記錄套件版本，不保證跨版本一致。
- 圖表與新區塊的桌機／手機視覺截圖另見 `visual-details/`。字型、公式、圖片與頁面內連結檢查通過；寬輸出和表格允許在自身容器捲動。
- 第一輪整站瀏覽器檢查中途斷線，原失敗紀錄保留於 `browser/`；最終分組驗收全部通過，見 `browser-final/`。初版區塊截圖有固定導覽列遮蓋，保留在 `visual-details-initial/`，正式截圖改以文件座標取得。
- 沒有重新測試免費模型供應、所有安裝平台、外部 MCP、本地模型或真實 agent 的全部 Lab。這次驗證不應被解讀成這些項目的重新認證。

## 維護入口

根目錄 HTML 仍由來源建置，勿直接修改。新章內容在 `content/research-notes.md`；三組圖由 `tools/make_figs.py` 產生，完整資料與 provenance 在 `assets/figures/`。PNG 與截圖沿用專案既有 Git ignore 規則，本機保留；網站引用可追蹤的 SVG。

活動頁：<https://sites.google.com/view/ai-math/home>，<https://sites.google.com/view/ai-math/活動資訊>。
課後參考：<https://ncku-ai-literacy-research.em65780.chatgpt.site/>。
PCA 閱讀：<https://scikit-learn.org/stable/modules/decomposition.html#pca>。
