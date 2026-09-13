# 工作進度摘要（2026-09-13 唯讀整理階段）

本次只做**唯讀審查與筆記整理**，不重跑任何實驗、不修改任何 .py 檔。
以下依「目標限制 → 成果路徑 → 實際指令/結果 → 缺少/未確認 → 下一步」記錄。

---

## 1. 目標與限制

| 項目 | 說明 |
|------|------|
| 範圍 | 三個 Lab（lab1_cluster、lab2_pca、lab3_logistic）＋ 對應的 notes / figs |
| 不做的事 | 不跑任何 `uv run python`（除非 log 已存在）、不改 .py、不做實驗 |
| 依據 | `lab*_cluster.py`、`lab2_pca.py`、`lab3_logistic.py`、`notes/*-output.log`、`figs/*` |
| 平行審查 | `@math-reviewer` 檢查 lab2 手刻 PCA、`@explore` 檢查三個檔的隨機性 |

---

## 2. 成果與相對路徑

| 成果 | 路徑 |
|------|------|
| lab1 cluster 程式 | `lab1_cluster.py` |
| lab1 cluster 執行輸出 | `notes/lab1_cluster-output.log` |
| lab1 cluster 圖檔 | `figs/lab1_k_selection.png` |
| **lab1 review 筆記（本次新增）** | `notes/lab1-review.md` |
| lab2 pca 程式 | `lab2_pca.py` |
| lab2 pca 執行輸出 | `notes/lab2_pca-output.log` |
| lab3 logistic 程式 | `lab3_logistic.py` |
| lab3 logistic 筆記（既有） | `notes/logistic.md` |
| lab3 logistic-regression 額外檔 | `lab3_logreg.py`（無對應 output.log） |
| 本進度摘要（本次新增） | `notes/progress.md` |

---

## 3. 實際指令與結果

### 3.1 lab1_cluster.py

執行指令（記錄於 log 第 1 行）：

```bash
uv run python lab1_cluster.py
```

結果重點（`notes/lab1_cluster-output.log`）：
- 掃描 $k=2\sim12$，inertia 從 $1\,914\,619$ 單調遞減至 $1\,112\,363$（無明顯手肘）。
- silhouette 在 **$k=9$ 最高**：$0.1893$；$k=10$ 掉至 $0.1825$。
- 程式輸出「最高的 silhouette 出現在 k = 9」。
- 圖檔已存 `figs/lab1_k_selection.png`。
- 詳見 `notes/lab1-review.md`。

### 3.2 lab2_pca.py

執行指令（記錄於 log 第 1 行）：

```bash
uv run python lab2_pca.py
```

結果重點（`notes/lab2_pca-output.log`）：
- 手刻 PCA（中心化 → 共變異數矩陣 → `eigh` → 降冪排序 → 符號對齊）
  與 sklearn `PCA(svd_solver="full")` 的特徵值最大差 $\approx 2.8\times10^{-13}$，吻合。
- 解釋變異比例「累計(前10) = 1.000000」——**這是分母 Bug**（見 §4）。
- 正交性檢查：Gram 非對角最大 $\approx 8.9\times10^{-16}$，正確。
- 重建誤差：手刻與 sklearn 皆 $751.79$，差 $\approx 2.8\times10^{-12}$。
- 圖檔（若程式有 `savefig`）未包含在 log 內，但程式結尾無 `savefig`，
  因此本檔**不產生圖檔**（與 lab1 不同）。

### 3.3 lab3_logistic.py

執行指令（記錄於 `notes/logistic.md`）：

```bash
uv run python lab3_logistic.py
```

結果重點（`notes/logistic.md`，無獨立 -output.log）：
- 資料：digits 中標籤 3 與 8（$n=357$，$d=65$ 含截距欄）。
- 實作了 `loss(w)` 與 `grad(w)`，均為手刻。
- 有限差分梯度檢查：$h=10^{-3}\sim10^{-7}$ 時 PASS（最大絕對誤差 $<10^{-8}$）；
  $h$ 太大或太小進入「U 型誤差曲線」。
- 無訓練、無資料切分——本輪範圍只到梯度檢查。

---

## 4. 缺少 / 未確認部分

### 缺少的檔案或輸出

| 項目 | 說明 |
|------|------|
| `notes/lab3_logistic-output.log` | lab3 沒有獨立的 output log，結果只記在 `notes/logistic.md` 內 |
| `notes/lab3_logreg-output.log` | `lab3_logreg.py` 存在但無對應 log |
| `figs/lab2_*.png` | `lab2_pca.py` 程式結尾未呼叫 `savefig`，無圖檔 |

### 數學上的已知問題（由 `@math-reviewer` 審查）

| 檔案位置 | 問題 |
|---------|------|
| `lab2_pca.py:50-51` | `ratio_hand = var_hand / var_hand.sum()` 的分母是「前 10 個特徵值的和」，不是全部 64 個特徵值的和。導致累計比例恆為 1.0，未真正對照 sklearn 的 `explained_variance_ratio_` |
| 同上 | `var_sk = var_sk / var_sk.sum()` 用同樣的錯誤分母，即使手刻與 sklearn 兩者結果「一致」，也不是正確的解釋變異比例 |
| `notes/lab2_pca-output.log` | log 如實反映了上述 bug 的輸出（累計 = 1.000000），但未標示任何異常 |

### 隨機性審查結果（由 `@explore` 檢查）

| 檔案 | 行號 | 用途 | 種子 |
|------|------|------|------|
| `lab1_cluster.py` | 14 | `KMeans(n_clusters=k, random_state=0, n_init=10)` — k-means++ 起始點 | ✓ `random_state=0` |
| `lab2_pca.py` | 34 | `PCA(n_components=10, svd_solver="full", random_state=0)` — 但 `full` 為確定性，`random_state` 不生效 | 本質無隨機 |
| `lab3_logistic.py` | 62 | `np.random.RandomState(0).normal(size=d) * 0.01` — 梯度檢查點 | ✓ 局部 `RandomState(0)` |

結論：三個檔案中**真正具隨機性**的呼叫（lab1 的 KMeans、lab3 的檢查點）都已設種子，
現況可重現。無未設種子的隨機來源。

### 其他

- lab3 的 `sigmoid`、`loss`、`grad` 實作正確（經梯度檢查確認），但未包含訓練迴圈。
- lab1 僅單一隨機種子（`random_state=0`）一次執行；未跑多次統計
  「$k=9$ 是否穩定勝出」。

---

## 5. 下一步建議

| 優先級 | 項目 | 說明 |
|--------|------|------|
| 高 | 修正 `lab2_pca.py:50-51` | 分母改為全部 64 個特徵值和（或 `np.var(X, axis=0).sum()`），
  並直接讀 `ref.explained_variance_ratio_` 做對照；修正後**重跑**並更新 `notes/lab2_pca-output.log` |
| 中 | 為 lab3 產生 `-output.log` | 跑一次 `uv run python lab3_logistic.py` 並導出，
  方便未來用相同格式審查 |
| 中 | lab1 多種子穩定性 | 用不同 `random_state` 重跑 $k=2\sim12$，
  統計「$k=9$ 幾次勝出」或計算 silhouette 的標準差 |
| 低 | 為 lab2 加圖檔 | `savefig` 輸出 PCA 前幾主成分的變異比例長條圖或累積曲線圖 |
| 低 | 整理 `lab3_logreg.py` | 該檔尚未納入本次審查，可視需求補做筆記 |