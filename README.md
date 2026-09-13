# OpenCode × AI-Math 工作坊教材

國立中山大學「人工智慧與數學」整合學程的 AI agent 工作坊。
對象是接觸過部分微積分、線性代數，能看懂少量 Python 的大學生。

[線上教材](https://phonchi.github.io/opencode-math-workshop/)；本機可直接開啟 `index.html`。
現場三小時，以 sklearn digits 貫穿分群、PCA、分類與數學筆記；課後分成數學應用和 OpenCode 工作法兩條路線。

## 閱讀路線

- 課前：`prep.html`，安裝 OpenCode、uv 並完成環境自測。
- 現場：`first-run.html` → `lab1-cluster.html` → `lab2-pca.html` → `lab3-notes.html`。
- 課後工作法：`agent-workflows.html` → `agents-md.html` → `git-safety.html` → `mcp-skills.html` → `local-models.html`。
- 課後數學：`math-applications.html`，低秩近似、梯度下降與最短路徑。
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
