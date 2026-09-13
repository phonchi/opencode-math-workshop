# Lab 1：k-means 的 k 值選擇（digits 資料集）

## 研究問題

對 sklearn digits 資料集（$n=1797$ 筆、$d=64$ 維）跑 k-means 時，

用「內距和（inertia）」與「輪廓分數（silhouette score）」當指標，該選多少個叢集 $k$？

## 符號與定義

- $X \in \mathbb{R}^{n \times d}$：digits 影像資料（原始資料流，未標準化）。
- $k$：叢集個數（本實驗掃 $k = 2, 3, \dots, 12$）。
- $C_j$：第 $j$ 個叢集，$\mu_j$ 為其中心。
- 慣量（inertia）：
  $$
  J(k) = \sum_{j=1}^{k} \sum_{x_i \in C_j} \lVert x_i - \mu_j \rVert^2
  $$
  衡量點到所屬中心的平均平方距離總和，$k$ 越大慣量越小。
- 輪廓分數：對第 $i$ 個樣本定義
  $a_i$ = 同叢集內其他點的平均距離，$b_i$ = 到最近其他叢集的平均距離，
  $$
  s_i = \frac{b_i - a_i}{\max(a_i, b_i)} \in [-1, 1],
  $$
  全資料集輪廓分數即 $\frac{1}{n}\sum_i s_i$，越高代表叢集內聚、分離好。

## 程式做了什麼

來源：`lab1_cluster.py`。

- 對 $k = 2 \ldots 12$ 依序執行 `KMeans(n_clusters=k, random_state=0, n_init=10)`，
  一次 fit + predict，並用 `silhouette_score` 計算全體輪廓分數。
- 印出每個 $k$ 的 inertia 與 silhouette，取其最大者為最佳 $k$。
- 畫「inertia vs k」與「silhouette vs k」兩張子圖，存 `figs/lab1_k_selection.png`。

## 觀察到的結果（來源：`notes/lab1-output.log`）

| $k$ | inertia | silhouette |
|---|---|---|
| 2 | 1914619.62 | 0.118328 |
| 3 | 1730182.26 | 0.126495 |
| 4 | 1612274.92 | 0.122893 |
| 5 | 1497722.51 | 0.138188 |
| 6 | 1404975.29 | 0.151523 |
| 7 | 1336539.98 | 0.162264 |
| 8 | 1265053.09 | 0.178431 |
| 9 | 1202300.13 | **0.189253** |
| 10 | 1165188.89 | 0.182536 |
| 11 | 1131794.98 | 0.182963 |
| 12 | 1112363.39 | 0.184758 |

- 最佳 $k$（silhouette 最高）＝ **9**（silhouette $=0.189253$）。
- Inertia 隨 $k$ 嚴格遞減，符合 $J(k)$ 的定義性質。

## 推論與未確認事項

- 推論：k-means 的慣量恆隨 $k$ 增加而下降，因此不適合單獨拿來選 $k$（無明顯「手肘」點時尤然）；
  本實驗以 silhouette 為選 $k$ 依據，最佳 $k=9$，與 digits 的 $10$ 類數字十分接近但未重合。
- 未確認：圖檔 `figs/lab1_k_selection.png`。程式第 42 行有存檔指令，但目前 `figs/` 目錄為空，
  **圖檔不在專案內**，無法確認是否成功產生或已遺失。
- 執行證據：`notes/lab1-output.log` 存在且格式與程式的 `print` 一致，可視為已成功執行的紀錄。
  實際執行指令未另行紀錄，本專案執行慣例為 `uv run python lab1_cluster.py`
  （stdout 重導向以產生 log）。

## 檢查問題

如果只看慣量曲線，你會選哪個 $k$？為什麼不建議用慣量選 $k$？

<details>
<summary>答案</summary>

慣量曲線沒有陡峭的「手肘」點、且慣量隨 $k$ 單調下降，任何更大的 $k$ 都會配更低慣量，
因此無法據此判斷。慣量只保證「叢集越細碎、平方距離越小」，不代表分群品質好，
所以要用 silhouette（能反映內聚與分離）這類指標來選 $k$。本實驗以 silhouette 為準，
最佳為 $k=9$。

</details>