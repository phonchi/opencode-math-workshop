# OpenCode × AI-Math 工作坊教材

國立中山大學「人工智慧與數學」整合學程　三小時 AI agent 工作坊的教學網站。

**線上閱讀：<https://phonchi.github.io/opencode-math-workshop/>**

也可以直接用瀏覽器開本機的 `index.html`，功能完全相同。

## 內容

| 檔案 | 章節 | 定位 |
|---|---|---|
| `index.html` | 總覽與三小時流程 | |
| `prep.html` | 00 課前準備 | 學生須在工作坊前完成 |
| `first-run.html` | 01 第一次對話 | 現場 30 分 |
| `lab1-cluster.html` | 02 Lab 1 分群 | 現場 40 分 |
| `lab2-pca.html` | 03 Lab 2 降維 | 現場 40 分 |
| `lab3-notes.html` | 04 Lab 3 分類與筆記 | 現場 40 分 |
| `local-models.html` | 05 本地模型 | 課後 |
| `agents-md.html` | 06 AGENTS.md | 課後 |
| `git-safety.html` | 07 git 安全網 | 課後 |
| `mcp-skills.html` | 08 MCP 與 subagent | 課後 |
| `cheatsheet.html` | 09 速查表 | 隨時 |

## 目錄結構

```
content/          章節內容（Markdown 原稿，部分章節）
tools/            建置與驗收工具
  _head.fragment  共用的 <head> 與導覽列（設計系統在這裡）
  _tail.fragment  共用的頁尾、JS、MathJax 設定
  body_*.html     各頁內容（.html 是產物，改這裡不是改根目錄）
  build.sh        組成根目錄的 .html
  md2body.py      content/*.md → tools/body_*.html
  shot.js         瀏覽器渲染驗收（截圖、溢出、console 錯誤）
  check_overflow.js  逐頁量每個 pre/table 有沒有被裁切（桌機與筆電寬度）
  test-runs/      實測紀錄與 log
starter/          發給學生的起始專案
reference/        講師用的參考解答（學生不需要）
handoffs/         交接文件
```

## 維護

`.html` **全部是產物**，不要直接改。改 `tools/body_*.html` 或 `content/*.md`，然後：

```bash
./tools/build.sh              # 全部重建
./tools/build.sh lab2-pca     # 只重建一頁
node tools/shot.js            # 瀏覽器驗收（需要 ~/.cache/selfstudy-node 的 puppeteer-core）
node tools/check_overflow.js  # 檢查有沒有內容被右邊裁掉
```

參考解答要重跑：

```bash
cd starter && uv sync
uv run python ../reference/lab1_cluster.py
uv run python ../reference/lab2_pca.py
uv run python ../reference/lab3_logistic.py
```

## 實測基準

本教材的所有指令與數值都在以下環境實測過：

- WSL2 / Ubuntu 24.04：opencode 1.18.30、uv 0.12.x、Ollama 0.21.2、RTX 5070 12GB
- Windows 11：opencode 1.18.30、uv 0.12.13（winget 安裝）
- 日期：2026-09-12

**未實測**：macOS（步驟依官方文件撰寫並已標註）、Windows 版 Ollama。

## 寫作慣例

- 程式碼圍籬**有語言標記** = 學生要照抄的指令，會產生複製鈕；
  **無語言標記** = 程式的輸出，不給複製鈕，過寬時自動縮字級
- `:::bg 標題 … :::` 產生可收合的「背景補充」。假設讀者只修過微積分與線性代數，
  會寫基本 Python 但沒碰過 numpy/sklearn，缺的背景都放這裡，懂的人可以直接跳過
- 外部網址直接寫 `<https://…>` 或裸 URL 即可，轉換器會自動變成可點的連結

詳細測試紀錄見 `tools/test-runs/`。
