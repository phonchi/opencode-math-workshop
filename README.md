# OpenCode × AI-Math 工作坊教材

國立中山大學「人工智慧與數學」整合學程的 AI agent 工作坊。
對象是接觸過部分微積分、線性代數，能看懂少量 Python 的大學生。

[線上教材](https://phonchi.github.io/opencode-math-workshop/)；本機可直接開啟 `index.html`。
現場兩小時，以講師設計的生活化資料（手搖飲分店、校園外送、圖書館借閱）貫穿分群、PCA、分類與數學筆記；課後分成數學應用和 OpenCode 工作法兩條路線。

## 閱讀路線

- 課前：`prep.html`，安裝 Git、OpenCode、uv 並完成環境自測。Windows 從官方安裝檔安裝 Git，全程使用 Git Bash，opencode 與 uv 用官方腳本安裝。
- 現場：`first-run.html` → `lab1-cluster.html` → `lab2-pca.html` → `lab3-notes.html`。
- 課後工作法：`agent-workflows.html` → `agents-md.html` → `git-safety.html` → `mcp-skills.html` → `local-models.html`，選修 `herdr.html`。
- 課後數學：`math-applications.html`，低秩近似、梯度下降與最短路徑。
- 課後閱讀與筆記：`research-notes.html`，用 OpenCode 整理指定來源，回原文與自己的 Lab 核對。
- 隨時查閱：`cheatsheet.html`。

學生使用 OpenCode 內建網路模型，不需要新增付款方式。`starter/` 是起始專案；`reference/` 是完成練習後可閱讀的參考解答。

## 編輯與建置

根目錄的 HTML 都是建置產物。章節有 `content/<章名>.md` 時，以 Markdown 為唯一內容來源；其他章節改 `tools/body_<章名>.html`。

```bash
./tools/build.sh
./tools/build.sh lab2-pca
```

建置會同步 Markdown 與 body，再產生靜態側欄、段落錨點、前後章、內嵌 SVG 與互動元件。新增章節時更新 `tools/pages.json`。共用風格及行為在 `tools/site-layout.css`、`tools/site-navigation.js` 與 `_head`／`_tail` fragments。

- 程式碼圍籬有語言標記：可複製的指令、提示或檔案內容；無標記：程式輸出。
- `:::bg 標題 … :::`：課後可再閱讀的補充；必要的新概念放正文。
- `<!--DIAGRAM:名稱-->`：將 `assets/diagrams/名稱.svg` 內嵌到頁面。
- `<!--INCLUDE:tools/片段.html-->`：內嵌指定的可信 HTML 片段。

圖解來源、匯出方法及技能驗證在 `tools/diagram-sources/`；PCA 互動來源在 `tools/pca-explorer.html`。正式教學頁面只呈現概念、操作和結果判讀，歷史實測、平台差異、查核過程與讀者審查一律放 `internal/`，不從教材導覽連出。

教學資料圖由 `tools/make_figs.py` 產生，SVG、數據與 provenance 放在 `assets/figures/`。重建方式見該目錄的 README；Lab 3 圖是既有七列範例數據的重繪，不是新的梯度實驗。

### 3D 課程島 `island/`

課後地圖與收尾投影用的附加導覽層，不取代總覽，也不嵌入教材；入口在總覽 hero 與每頁側欄最後。島、海、光影與效能機制移植自 ds-cpp-selfstudy 的 `/island/`，地標依本站內容重新設計。`island/index.html` 是產物，完整建置（不帶參數的 `./tools/build.sh`）會一併重建。

| 要改什麼 | 改哪個檔 |
|---|---|
| 頁面清單、標題、分組 | 照舊只改 `tools/pages.json`，島上自動跟著變 |
| 地標名、3D 標籤短名、阿卡台詞、路線、猜題、「做完再對照」的資料 | `tools/island_meta.py`（開頭列了防劇透與比喻的約束） |
| 場景與地標動畫 | `tools/template/island-scene.js`；列表、面板、導覽在 `island.js`，對照面板在 `island-compare.js`，樣式在 `island.css` |
| 三個 Lab 的代表圖縮圖 | `node tools/build_island_figs.js`，教材的 explorer 改版後重跑並 commit |

改完：`python3 tools/build_island.py` → `python3 tools/check_island.py --net` → `node tools/check_island_browser.js`。產生器會確認每題猜題的出處片語、對照面板的每個數字都還在教材原文裡，教材改了數字而島沒跟上就會報錯。地標的動畫分兩段：沒選取時輪播的 idle 不能露出結果，答完猜題才播完整的 pose。足跡、導覽進度與「我做完這一關了」只存在該裝置的 localStorage（`aimath-island:*`），「清除足跡」會一併清掉。

## 維護檢查

```bash
node tools/shot.js
node tools/check_overflow.js
RUN_DIR=tools/test-runs/my-browser-check node tools/accept_site.js
cd starter
uv sync --locked
uv run python ../tools/verify_math.py --out ../tools/test-runs/my-math-check
```

瀏覽器工具沿用 `~/.cache/selfstudy-node` 的 Puppeteer 與本機 Chromium。驗證使用具名輸出資料夾，保留完整 log、參數與成果；跨平台執行方式及本輪驗收範圍見 `internal/validation-20260912.md`。

本機的修改不會自動更新 GitHub Pages。發布須另行確認授權。
