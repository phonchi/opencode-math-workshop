# 專案進度（progress）

記錄日期：2026-09-12（僅依目前專案真實檔案與既有輸出整理，未重跑任何實驗）

## 目標與限制

- 目標：以 sklearn digits 資料集練習三種數學方法並自我驗證——
  Lab1 k-means 的 $k$ 值選擇、Lab2 手刻 PCA、Lab3 logisitic 迴歸梯度檢查。
- 限制：執行 Python 一律 `uv run python`；[隨機處一律固定種子](../../AGENTS.md)；
  圖存 `figs/`；筆記存 `notes/`。

## 完成成果（相對路徑）

| 項目 | 檔案 | 狀態 |
|---|---|---|
| Lab1 程式 | `lab1_cluster.py` | 存在 |
| Lab1 執行輸出 | `notes/lab1-output.log` | 存在（13 行） |
| Lab1 圖 | `figs/lab1_k_selection.png` | **不存在**（`figs/` 目前為空） |
| Lab2 程式 | `lab2_pca.py` | 存在 |
| Lab2 執行輸出 | `notes/lab2-output.log` | 存在（56 行，全部 PASS） |
| Lab3 程式 | `lab3_logistic.py` | 存在 |
| Lab3 執行輸出 | `notes/lab3-output.log` | **不存在** |
| Lab1 複習筆記 | `notes/lab1-review.md` | 已建立 |
| 數學審查 agent | `.opencode/agents/math-reviewer.md` | 已存在（唯讀） |

## 實際成功指令

- **無留存指令紀錄**：專案內沒有 shell 歷史或 makefile/manifest 記錄每支程式的實際執行指令。
- 執行證據：兩個 log 檔的內容與對應程式的 `print` 語句完全一致
  （lab1 的 `k`, `inertia`, `silhouette` 逐行對應；lab2 的 5 組驗證格式逐字對應）。
- 依專案慣例可推測為 `uv run python lab1_cluster.py`、`uv run python lab2_pca.py`
  （stdout 重導向到 `notes/`），**但此為推測，非已紀錄之指令**。

## 關鍵結果

- **Lab1（`notes/lab1-output.log`）**：silhouette 最高落在 $k=9$（$0.189253$）；
  inertia 隨 $k$ 單調遞減（$1914619.62 \rightarrow 1112363.39$）；
  $k=10,11,12$ 的 silhouette（$0.182536, 0.182963, 0.184758$）與 $k=9$ 差距很小。
- **Lab2（`notes/lab2-output.log` + math-reviewer 審查）**：手刻 PCA 通過 5 組驗證，
  全部 `max|diff| \le 4.263\times10^{-13} \ll$ TOL $=10^{-9}$`；審查結論「通過，可宣稱一致」。
- **Lab3**：無執行輸出，無法確認有限差分 vs 解析梯度的誤差數值。

## 隨機性盤點（explore 委派結果，未修改程式）

| 檔案 | 行號 | 型態與用途 |
|---|---|---|
| `lab1_cluster.py` | 7 | 常數 `random_state = 0` |
| `lab1_cluster.py` | 16 | `KMeans(random_state=0, n_init=10)`（唯一實際隨機來源，影響 labels/inertia/silhouette） |
| `lab2_pca.py` | 43 | `np.random.seed(0)`（已設，但其後無 `np.random.*` 被呼叫，不影響結果） |
| `lab2_pca.py` | 47 | `PCA(random_state=0)`（`svd_solver="full"` 為確定性，種子不被使用） |
| `lab3_logistic.py` | 49 | `np.random.RandomState(0).normal(...)`（唯一實際隨機來源，生成驗證起點 $w_0$） |
| `lab3_logistic.py` | 54 | 僅輸出說明字串 |

結論：三檔的隨機來源全部固定種子 0，符合可重現規範；未發現無種子的隱性隨機。

## 未完成或不能確定的部分

- `figs/lab1_k_selection.png` 不存在 ⇒ 圖是否成功產生無法確認（或已遺失）。
- Lab3 無執行輸出 ⇒ **不能宣稱已跑過**。
- 各 Lab 的實際執行指令無紀錄 ⇒ 只能以 log 作為執行證據，無法重述指令。
- Lab2、Lab3 尚無對應的複習筆記（本次僅要求 `lab1-review.md`）。

## 下一步

- 若要補齊圖與 Lab3 輸出：重跑 `uv run python lab1_cluster.py` 與
  `uv run python lab3_logistic.py`，將 stdout 重導向到 `notes/`，確認 `figs/` 產生圖檔。
- 視需要為 Lab2、Lab3 建立複習筆記，並讓 math-reviewer 覆核 Lab3 數值結果。