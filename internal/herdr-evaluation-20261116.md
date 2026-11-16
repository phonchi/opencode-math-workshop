# Herdr 評估與選修章撰寫紀錄（2026-11-16）

## 起因

講師認為 herdr.dev 對 Windows、macOS 初學者都好用，問要換掉現有終端機，還是當延伸教學。參考影片：

- [摸摸說門道：Herdr 好用嗎？](https://www.youtube.com/watch?v=C2zXbxPzqu4&t=662s)，桌面版
- [AI懶人報 EP459](https://www.youtube.com/watch?v=OVl3fFSHxqY)，TUI 版

兩支都有人工字幕，用 youtube-read 讀過，逐字稿不放進 repo。

## 第一輪諮詢：換掉還是延伸

三方都在 Herdr 分頁中以唯讀方式執行，用同一份中性提示詞。

| 分頁 | job ID | 建議 |
|---|---|---|
| Astra（GPT-6 Astra，Codex） | `6638bde0-64e4-4c76-bf01-89a94079e791` | B：現場不變，課後選修 |
| Fable 5.1（Claude） | `c14a83c8-a9d4-46a1-beae-292421ab97be` | B |
| Gemini 3.8 Flash high（agy） | `bb579b18-8fe2-4f2a-8f71-eefcc4e5a547` | B，人力不足時選 C；反對 A |

共同理由：

- 現場每人只跑一個 OpenCode，多 agent 管理派不上用場。
- Herdr 不解決共用 IP 的額度問題。
- 桌面 app 才推出不久，改版很快。
- Windows 預設 shell 是 PowerShell，與課程的 Git Bash 流程不合。

## 主持人核對的事實

核對來源：herdr-app 與 herdr-core 的 README、CHANGELOG、`defaults/AGENTS.md`，以及 herdr.dev 的 privacy、tui/docs 頁面。

- **平台**：桌面 app 的 macOS 安裝檔只支援 Apple Silicon，Intel Mac 要自己編譯；Windows 只有 x64；Linux 需要桌面環境與 Vulkan。TUI 支援 Intel Mac，Windows 版已是正式版（GA）。
- **Windows shell**：herdr-core 預設用 PowerShell 7，沒有就用 Windows PowerShell。在 `%APPDATA%\herdr-core\config.toml` 用頂層鍵 `shell` 可以改成 Git Bash。改用 Git Bash 後，issue #5958（仍開著）指出 cwd 不會跟著 `cd` 更新。
- **狀態燈**：桌面 app 只認 OSC 7501 的回報，不讀畫面。OpenCode 在 v2.2.6、v2.3.0 的 `packages/tui/src/context/program-status.ts` 會回報 working、blocked、idle，不送 done。
- **遙測**：預設開啟，到 Settings → Privacy 關閉。Gemini 說的 `telemetry: false` 和 `DO_NOT_TRACK` 在官方文件找不到。
- **OpenCode 安裝**：課前頁在 Git Bash 裡安裝，PATH 只寫進 `.bash_profile`（`tools/test-runs/20261111-v2-windows/`）。

## 講師的決定與第二、三輪

- 三方在第二輪的大綱都以 TUI 為前提。講師決定改用**桌面 app**，放在課後選修，並要求直接撰寫，三方可以協助潤稿與審查。
- 放置位置：Fable 與 Gemini 建議在 agent-workflows 加補充框，Astra 建議新開一章。app 版要說明安裝、shell 設定與遙測，補充框裝不下，所以新開 `herdr` 頁，排在 local-models 之後；agent-workflows 的 Session 一節末尾加一句連結。
- 第三輪由三方審查草稿，修正以下各點：
  - `cat >>` 改成 `cat >`，重複執行也不會產生重複的鍵。
  - 做完後的狀態改成 Done 或 Idle。
  - 開 OpenCode 一律先開一般終端機，再自己輸入 `opencode`。
  - Linux 的貼上鍵改成 `Shift+Insert`。
  - cwd 問題不再寫「不影響使用」，改成提醒每個新窗格先 `cd`。
  - 縮短 Mods 段落。
  - 補上打開 Settings 的方法。
- Gemini 說下載頁是 404，實測是 HTTP 200，不採用。

## Windows 實測

在講師的 Windows 上，用 `hc` 從背景開終端機實測，沒有操作 GUI。結果與未測項目見 `tools/test-runs/20261116-herdr-app-windows/README.md`。

## 尚待 GUI 確認

- 預設按鍵（`Ctrl+Shift+O`／`Cmd+D` 往右切開、`Ctrl+,`／`Cmd+,` 設定）是從 `defaults/keys*.json` 查到的，還沒有在 GUI 按過。
- 側欄顯示 Done 或 Idle。
- 關掉視窗再打開後，窗格與對話是否都還在。
- 從 Git Bash 呼叫 PowerShell 安裝。`install.ps1` 只讀過內容，沒有重跑。
- 用全新 Windows 帳號從頭安裝。T1b 已確認 Herdr 的 bash 會讀 `.bash_profile`，所以只登記在 profile 的 opencode 也找得到。
