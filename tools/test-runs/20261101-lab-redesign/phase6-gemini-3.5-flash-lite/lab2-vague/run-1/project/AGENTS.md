# AI-Math 工作坊　專案規則

## 語言
一律使用台灣繁體中文回答。程式碼、變數名稱、套件名稱保留英文。

## 執行環境
本專案用 uv 管理環境。執行 Python 一律用：`uv run python <檔案>`
不要用 `python`、`python3`、`pip install`。要加套件用 `uv add <套件>`。

## 圖檔
所有圖存到 `figs/`，用 `savefig()`，不要用 `plt.show()`（無視窗環境無效）。

## 筆記
筆記寫在 `notes/` 底下的 .md 檔，數學式用 $...$ 與 $$...$$。

## 不要做的事
- 不要 git commit 或 git push，除非我明講。
- 不要刪除 `figs/` 或 `notes/` 裡既有的檔案。
