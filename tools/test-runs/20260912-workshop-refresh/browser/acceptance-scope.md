# 最終 HTML 驗收範圍

下表每個 SHA-256 均與相應瀏覽器報告的載入前及結束後值相符。每頁皆涵蓋 1440／1280／1024／390 px；輸出與表格允許自身捲動，沒有整頁橫向溢出或真正裁切。

| 頁面 | HTML SHA-256 | 證據報告 | 結果 |
|---|---|---|---|
| index.html | `6ef3197ca4a5acf1a8c73baf3e9402000c0b3a69fcda6610ba80b934093fe9de` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| prep.html | `0b92ede68e97b74f717c9d4af446667a7865ebcfd02a18bb7f4cbbc4baa20244` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| first-run.html | `0a6987e39c2e2f10b54767ee802e400251d4a12bc292d0137d37632bc74627bb` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| lab1-cluster.html | `ebb5fb15ec9c743e31e55cb2d269775ab4f6e4e0b15262e8e27a296ccc7ec2fe` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| lab2-pca.html | `27db3cf45d1f0c238fd44f239858d15667908b20e0fcb7f1c95bd085ef57e4b7` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| lab3-notes.html | `e8635e4d76d3964b71b513bb811b2a71dafbfe2122ffbdcdc1c22e46277daba9` | [lab3-copy-final/report.json](lab3-copy-final/report.json) | 確認無誤 |
| agent-workflows.html | `ed9c9e8eea284c0958c2ef4073961ef49c7c150e3c176065b8965d4eeb52c7da` | [report.json](report.json) | 確認無誤 |
| agents-md.html | `8b7abe7ae5de4a3917df2433f60bfd12e12929a4787e7645005b18622538b362` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| git-safety.html | `ff3872b676cfe4766ab59d947031132ed75672e02d6a2c5b3bc5dc8cea7ca969` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| mcp-skills.html | `cb94346a97b2df42b1a8a98eaf5618f36eb858841134843b55be22051c25b793` | [mcp-scope-final/report.json](mcp-scope-final/report.json) | 確認無誤 |
| local-models.html | `9dead98f5d4e5b25cc09c7a571828de64b665ca2998182fcb4cc57e3ef52716f` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |
| math-applications.html | `d8d124d7e72216b2637e098ed4de0b73f2d0063f26d5aeae699801f1df83f4d0` | [final-check/report.json](final-check/report.json) | 確認無誤 |
| cheatsheet.html | `6adf913b9eb800579e3df9a15bc0f88df79da71e4cd673082eb9eefb6a82e7f2` | [reader-fixes-final/report.json](reader-fixes-final/report.json) | 確認無誤 |

最終回合只重測 11 個 hash 改變的頁面，共 44 個頁面／viewport 情境，11 個互動情境，0 項失敗。`agent-workflows` 與 `math-applications` 的 hash 未變，沿用先前受測證據。

全部 62 張最新情境截圖入口：[完整總覽](accepted-final-all-items-contact-sheet.html)。本輪長圖總覽只產生 HTML；歷史 PNG 保留在原位置，不代表最新總覽。

此表不宣稱已做實體手機觸控、所有瀏覽器品牌，或每個第三方模型／MCP 的即時操作。

最後文字補測：Lab 3 兩句教學文案修改後，只補測該頁四種寬度、MathJax、字型、版面與內鏈，4／4 通過；沒有重跑未變的 PCA 等互動。其餘 12 頁 hash 未變，沿用表中既有受測證據。最新 Lab 3 四張截圖已替換完整總覽的對應入口。

Reviewer 範圍修正補測：Markdown 與 JSON 模板都限制只讀本專案／已有輸出，且 edit、bash、task、external_directory 四項均為 deny；來源一致性確認無誤。僅 MCP 頁 HTML hash 改變，補測四種寬度、MathJax、字型與內鏈，4／4 通過、0 失敗；未新增模型呼叫或重跑互動。其餘 12 頁 hash 沿用，總覽更新對應四張截圖。
