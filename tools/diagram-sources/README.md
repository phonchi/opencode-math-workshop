# 工作坊圖解來源與驗證

正式嵌入檔案位於 `../../assets/diagrams/`。四張圖沿用本站暖紙、靛藍、赤陶，圖片本身不包含 Viewer 控制列。

- `learning-route.html`：Diagram Design timeline，1120 × 440。使用等距的學習階段而非等距時間，圖內明示「學習順序」。SVG 依技能的 first SVG extraction 正常出口產生。
- 另外三張 `.json`：Archify workflow v2。每張 `.validate.json` 與 `.deliver.json` 保存官方 showcase 九項檢查，零錯誤、零警告，以及來源/HTML SHA-256。
- `.html` 是 deliver 保存的原始 checked artifact；`.canonical.svg` 是 `export-viewer.cjs` 以真實 Chromium 點選 Viewer Export → SVG 的結果，未做 DOM 擷取。
- `build-assets.py` 對 canonical SVG 製作教學網站衍生版本：套用專案色彩及繁體中文字型、提高節點標籤至 18px 並垂直置中、移除裝飾圖示，加入繁體中文 accessible description。節點與連線幾何不變。原稿及 canonical 出口保持不變。
- `project-tokens.md` 是使用者核准的專案覆寫，不是假稱註冊的 Diagram Design profile；未修改共享 skill 或 home registry。

## 驗證結果

三個 Archify 獨立 HTML 的官方 `visual-check` 均 pass，涵蓋 1440×900、1600×1000、1920×1080、2048×1320，沒有水平或垂直溢出，並保留兩端尺寸的明/暗畫面。結果與 SHA-256 在 `.visual-check.json`，完整 screenshots/contact sheets 同目錄。

獨立 Viewer 的大螢幕畫面下半部留白偏大，因此**不宣稱 standalone perceptual polish 通過**；正式教學交付為 inline SVG。該 limitation 不隱藏於 overflow CSS，也不把官方 automated pass 冒稱為視覺評審。

四張最終 SVG 已透過 Chromium 實際渲染並以影像工具逐張查看，文字可讀、節點與連線沒有遮蔽、教學色彩一致。`asset-check.json` 檢查文字未超出 viewBox；`*.asset.png` 為正式畫面證據。此檢查獨立於 Archify 原始 HTML 收據。

Git 圖的文字說明應與正文一起提供：restore 只還原指定的已追蹤檔案；未追蹤檔案仍保留。執行前先確認沒有自己的修改要保留。

## 重現

在專案根目錄執行 `python tools/diagram-sources/build-assets.py` 可從保留的 canonical SVG 重建四張正式圖。

修改 Archify JSON 後，先用安裝中 skill 的 `validate workflow <file> --quality showcase --json`，再 `deliver workflow <file> <html> --quality showcase --json`。使用 `export-viewer.cjs` 重新走 Viewer 匯出，再重建正式資產。Chrome 路徑與 Puppeteer 路徑須依執行機器調整。

本機 sandbox 的 Archify subprocess 曾產生空 stdout；正常許可後的官方指令全部成功。`visual-check` 需設定 `ARCHIFY_CHROME` 指向已安裝執行檔，最初缺少設定的 skipped 已由完整成功收據取代。
