# 原生 Windows 工作坊驗證

本次使用獨立 `C:\Users\User\Documents\ai-math-refresh-20260912`，不覆寫既有學生專案、不重新安裝 OpenCode/uv、不修改全域設定。PowerShell process PATH 加入已安裝工具目錄；OpenCode config/data/cache 隔離於 `isolated/`，並移除 process API 憑證環境變數，使用免登入 `opencode/big-pickle`。

## 已完成

- 原生 `uv sync`、套件 import：成功。Windows 11、Python 3.14.7、OpenCode 1.18.30、uv 0.12.13。版本細節在 `evidence/reference/result.json` 與 setup transcript。
- `verify_math.py`：Lab1/2/3、低秩近似、梯度下降、最短路徑及 PCA 互動獨立數學參考全部 PASS。這是參考程式驗證，與 agent 產生結果分開記錄。
- 非互動 `ask`：write hello.py 被 auto-rejecting 拒絕，沒有產檔。工具 exit status 0 不代表權限操作成功；實際 tool state 是 error。
- `--auto`：write hello.py 成功，`uv run python hello.py` exit 0，印出 `[1, 4, 9, 16, 25]`。
- 真實 Lab1 prompt：生成並執行 `lab1_cluster.py`、`figs/lab1_k_selection.png`，固定 seed/n_init，silhouette 最佳 k=9。
- 真實 PCA prompt：生成並執行 `lab2_pca.py`，以 numpy 手刻 n−1 covariance/eigh。五項對照全部 PASS，符號對齊後最大投影差 3.464e−13。
- `opencode debug skill` 發現專案 `math-notes`；`debug agent math-reviewer` 最後有效的 edit/bash/task 均為 deny。

- Lab3 初次模型擅自擴張成 IRLS 訓練並反覆診斷，已精確取消自己啟動的 PID 39736；native exit −1 / host exit 255，記錄在 `lab3-cancellation.json`。沒有把取消寫成完成。
- 沿同一 session 做唯一有界修正，保留舊 `logistic.py`，另建新版指定 `lab3_logistic.py`，完成全部 357 筆資料、65 維、seed 0 的有限差分及 `notes/logistic.md`，正常 exit 0。h=1e−4 最大絕對誤差 7.171e−12。
- 對最終生成程式做獨立數學檢查：PCA 投影矩陣對 NumPy SVD 最大誤差 9.992e−16；logistic 在新隨機輸入對 SciPy expit 梯度與 65 維差分通過。收據 `evidence/generated-independent.json`。

- 合併 workflow 正常完成：實際 `skill` 工具載入 math-notes，寫 `notes/lab1-review.md`；兩個 `task` 子任務完成；主 agent 寫 `notes/progress.md`，沒有重新執行實驗。
- 從隔離 OpenCode DB 唯讀匯出兩個子 session 的完整 parts：math-reviewer 只有 read/read；explore 只有 read/read/read/grep/glob，沒有 write/edit/bash。`subagent-tool-check.json` 與各 session parts 為證據，三份程式 hash 前後一致。
- Workflow 專案刻意只有 Lab1/2 stdout、沒有圖檔與Lab3 stdout；agent 有如實標示缺少，沒有冒稱存在。

- 全新 session `ses_f69a8bb86ffeUProqRItDzMomZ` 與原 workflow session 不同，正常完成並正確指出缺圖、缺Lab3 stdout；全部工具只有read，沒有改檔或執行。`fresh-session-check.json` 為證據。所有本代理啟動的驗收工作已達明確終態，沒有留在執行中的模型。

## 證據與重現

`setup.ps1`、`agent-run.ps1`、`debug.ps1` 保存命令；`prompts/` 保存實際送出文字；`snapshot/` 保存測試時參考來源與 lock；`agent-projects/` 保存各獨立 agent 專案，省略可重建的 `.venv` / `node_modules`。`run.log` 是完整 log 合併，原始 log 與 UTF-8 便讀副本在 `evidence/`；`agent-summary.json` 列出確切 session 與工具執行，`sha256.json` 提供檔案辨識。

初次 hello 的 PowerShell 非 ASCII 轉碼在最終敘述出現替代字元，但 write path、權限錯誤與數值 stdout 可查。後續設定 process OutputEncoding=UTF-8；Windows PowerShell `Tee-Object` 檔案本身為 UTF-16，採 BOM 解碼後保留原始檔與 UTF-8 副本。個別 Get-ChildItem 日期字串仍受子 shell 本地編碼影響。

`montage.html` / `montage.png` 涵蓋目前所有實驗圖，保留各圖相對路徑。未啟用付款、訂閱升級或 API 計費設定。

Lab3 的完整固定梯度下降/可分離性/L2 教學鏈，由 reference suite 驗證；真實 agent 測試針對初始實作、梯度與筆記，不能把這兩種範圍混為一談。

生成筆記保留為實際模型輸出，不視為正式參考答案。例：lab1-review 的 inertia 公式正確，但其文字「平均平方距離總和」不精確，inertia 實為總平方距離；這也展示輸出仍需學生查核。
