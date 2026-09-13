# 教材精修與驗收

本輪開始於 2026-09-12，跨日至 2026-09-13。正式教學頁只放概念、操作與判讀；本文件供講師維護。

## 交付範圍

暖色雙欄與章節導覽、手機收合目錄、四張圖解、PCA 二維投影互動、數學應用與 OpenCode 工作法兩條課後路線。保留三小時、digits 三個 Lab 與免登入 big-pickle。根目錄 HTML 為產物，build 自動同步原稿與內嵌資產。

全文讀者審查已涵蓋全部 13 頁，包括收合補充與任務範例。學生視角是參與過文案的作者再讀；另一位未參與教材文案撰寫的讀者做獨立技術與章間通讀。原始發現與修正後回查分別保存，不把初稿問題視為最終未修事項：

- `reader-student-review.md`：全文閱讀紀錄及原始 R1–R12。
- `reader-technical-review.md`：獨立 F1–F7、數學反例與來源、逐項修正回查。
- `reader-fixes.md`：R1–R12 及短句全部修正後的確認。
- `math-review.md`：新數學練習及 PCA 的獨立推導。

## 可核對的驗證入口

所有本輪正式證據位於 `tools/test-runs/20260912-workshop-refresh/`。

| 項目 | 證據 |
|---|---|
| 全站 Chromium：1440／1280／1024／390，13 頁與受測 SHA | `browser/acceptance-summary.json`、`browser/acceptance-scope.md` |
| 所有最新網頁截圖 | `browser/accepted-final-all-items-contact-sheet.html` |
| 建置可重現、13 頁與瀏覽器受測版本一致 | `build-verification.json` |
| WSL 隔離 uv 環境及完整參考解答 | `wsl/math/result.json`，每個 Lab 的完整 log 同目錄 |
| 原生 Windows uv 環境及完整參考解答 | `windows/evidence/reference/result.json` |
| 跨平台低秩／梯度下降／最短路徑／PCA 固定資料比對 | `comparison/cross-platform.json` |
| 數學圖形與參數 | `comparison/all-math-figures.html`、`windows/montage.html` |
| Git 暫存區、diff、restore 實際行為 | `git-semantics/result.json`、`git-semantics/run.log` |
| 原生 Windows Edge 首頁／PCA 兩種寬度與互動 smoke | `windows/browser-smoke/browser-result.json` |
| 原生 Windows 正式課前 1–10 平方數自測 | `windows/hello10-check.json`（完整 prompt／工具結果同平台目錄） |
| 原生 PowerShell 逐行建立 notes／figs | `windows/browser-smoke/mkdir-result.json` |
| 原生 Windows 真實 agent 與子任務 | `windows/README.md`、`windows/acceptance.json`、`windows/run.log` |
| WSL 真實 agent 原始任務／修正與工作法 | `wsl/lessons/`、`wsl/workflows/`；最終狀態以 `wsl/acceptance.json` 為準 |

瀏覽器檢查涵蓋公式與字型載入、內部連結／錨點、整頁溢出與真正裁切、桌機及手機導覽、no-JS 導覽、剪貼簿及 file:// 備援、勾選重載、收合內容、PCA 按鈕／滑桿／鍵盤及獨立數值比對。允許寬表格／輸出在自己的容器捲動，不以縮小至不可讀字級掩蓋問題。原生 Windows Edge 另完成首頁與 PCA 在 1440／390 的 smoke：沒有頁面橫向溢出，PCA 調整／主方向／重設與複製回饋通過。Windows file:// 的剪貼簿差異已確認為 CRLF：原指令 239 字元、剪貼簿 247 字元，增加的 8 字元正好對應 8 處 CRLF；將 CRLF 正規化為 LF 後完全一致，沒有漏字。完整診斷在 `windows/browser-smoke/clipboard-newline-diagnostic.json`，保留原始不相等的歷史結果。WSL Chromium 的 localhost HTTP 內容比對也通過。

## 測試的實際邊界

- 本輪從獨立練習資料夾重建 uv 環境，使用已安裝的 OpenCode／uv。沒有刪除全域設定、重灌工具，或把「版本指令成功」說成重新安裝成功。既有安裝紀錄仍在原本的 `tools/test-runs/`。
- WSL 與 Windows 的完整數學參考檢查，包含 Lab3 的梯度下降、可分性、L2 與新課後題。真實 agent 的輸出是另一路證據，不與參考答案混稱。
- 真實 agent 已測分群、PCA 與 logistic 的 loss／gradient／筆記。Lab3 原始較寬泛的要求曾讓模型擴張任務；正式教材已加入明確檔名、資料尺度、固定檢查點與分段停止要求。完整固定訓練與 L2 流程以參考程式驗證，不宣稱模型逐字跑完所有課後分支。
- WSL 原始 PCA 生成程式將前十個成分重新正規化；只看兩份輸出相等不能認定比例正確。保留原始錯誤、reviewer 發現及一次精確修正。修正後總體樣本變異為 1202.147712160703，前十個累計比例為 0.7382267688459535，與 sklearn 比例最大差 1.67e-16；獨立核算不依賴模型自報 PASS。
- Skill 驗收分成被發現、實際 skill 工具載入；subagent 驗收比對實際工具與程式前後 hash；續作驗收使用不同 session ID，要求辨識存在與缺少的成果。
- 初版 WSL reviewer 曾唯讀查詢其他環境的 sklearn 原碼，其版本不能作為本次 uv 環境的證據。正式 Markdown／JSON 範本都已補 `external_directory: deny` 與專案內讀取限制；新設定的解析檢查與舊執行紀錄分開保存。
- 模型生成檔案保存為測試證據，不直接當教材。已知的生成敘述錯誤（例如 logistic docstring 的推導符號）保留於平台限制；正式教材及參考公式另經獨立核對。
- 沒有重新測試 macOS 安裝、Windows Ollama、大型本地模型或所有第三方 MCP；這些不是本輪主線完成的依據。遇認證／配額的選修服務，教材提供停止與官方文件閱讀路線。

## 維護原則

實測使用 `opencode/big-pickle`、空的隔離憑證儲存與限定 provider，未啟用 billing、信用卡、付費升級或其他計費方式。模型可用性及免費政策會變，工作坊前需要重新做課前自測；失敗時先處理問題，不自行改接付費模型。

本輪不發布、不推送；本機產物由 `index.html` 開始閱讀。Git HEAD 基準為 `1c1a4a2`，新修改留在工作目錄，未用全域設定或其他專案做驗收實驗。

## 完成狀態

2026-09-13：本輪模型工作均已明確結束，原生 Edge 測試程序已清理。最終受測 HTML 與可重現建置結果一致；沒有尚待回收的背景工作。完整完成摘要見 `tools/test-runs/20260912-workshop-refresh/final-summary.json`。
