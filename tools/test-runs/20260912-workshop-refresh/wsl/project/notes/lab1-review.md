# K-Means 聚類的 k 選擇筆記（lab1_cluster.py）

日期：2026-09-13 · 執行檔：`lab1_cluster.py` · 執行指令：

```bash
uv run python lab1_cluster.py
```

以下的數字與圖均出自既有輸出 `notes/lab1_cluster-output.log` 與
`figs/lab1_k_selection.png`，本輪**不重跑實驗**，只依既有檔案整理。

---

## 1. 研究問題與資料

問題：對手寫數字資料集 *digits*，用兩種準則——**慣性（inertia）**與
**輪廓係數（silhouette score）**——決定叢集個數 $k$。

- 資料：`sklearn.datasets.load_digits()`，共 $n=1797$ 個樣本、$d=64$ 個特徵
  （8×8 灰階像素）。
- 演算法：`sklearn.cluster.KMeans`（非手刻，本 Lab 目的在選 $k$，不是實作演算法），
  掃 $k=2,3,\ldots,12$，全部固定 `random_state=0`、`n_init=10`。
- 準則：
  - inertia：$\displaystyle\sum_{i=1}^{n}\lVert x_i-\mu_{c_i}\rVert^{2}$，
    其中 $c_i$ 是點 $i$ 被分到的簇中心索引、$\mu_{c_i}$ 是該簇中心。愈小代表簇內愈緊密，通常隨 $k$ 遞減。
  - silhouette：$\displaystyle s(i)=\frac{b(i)-a(i)}{\max\{a(i),b(i)\}}$，
    其中 $a(i)$ 是點 $i$ 到同簇其他點的平均距離（簇內凝聚度），$b(i)$ 是到最近其他簇的平均距離（簇間分離度）。$s\in[-1,1]$，愈接近 $1$ 愈好。

---

## 2. 執行結果（log 原文數值）

```
k= 2  inertia=  1914619.62  silhouette=0.1183
k= 3  inertia=  1730182.26  silhouette=0.1265
k= 4  inertia=  1612274.92  silhouette=0.1229
k= 5  inertia=  1497722.51  silhouette=0.1382
k= 6  inertia=  1404975.29  silhouette=0.1515
k= 7  inertia=  1336539.98  silhouette=0.1623
k= 8  inertia=  1265053.09  silhouette=0.1784
k= 9  inertia=  1202300.13  silhouette=0.1893
k=10  inertia=  1165188.89  silhouette=0.1825
k=11  inertia=  1131794.98  silhouette=0.1830
k=12  inertia=  1112363.39  silhouette=0.1848

最高的 silhouette 出現在 k = 9
```

圖檔：`figs/lab1_k_selection.png`（左 inertia vs k、右 silhouette vs k，含 $k=9$ 的基準線）。

程式選 $k$ 的方式：依序掃描 $k=2,\ldots,12$，遇到比目前最高更高的 silhouette
就更新 `best_k`（等價於取第一個最大值），輸出 $k=9$。

---

## 3. 觀察與推論

1. **慣性單調遞減**：從 $1.91\times10^{6}$（$k=2$）降到 $1.11\times10^{6}$（$k=12$），
   符合「$k$ 愈大簇圍愈小」的必然趨勢；曲線沒有明顯「手肘」，單靠肘部法不能決定 $k$。
2. **silhouette 在 $k=9$ 最高**：$0.1893$，$k=8\to9$ 上升，$k=10$ 掉到 $0.1825$，
   之後回升但未超過 $0.185$。最佳 $k=9$。
3. **$k=9$ 的解釋**：digits 有 10 個真實類別，$k=9$ 接近但不等於 10。顯示以像素
   歐氏距離分群時，「與標籤數相同」不一定是最佳切分；整體 silhouette（0.12~0.19）
   偏低，代表簇間分離並不好、有重疊。
4. 兩種準則並用：inertia 無手肘、silhouette 給出單峰，因此本 Lab 以 silhouette
   為主要依據，結論 $k=9$。

---

## 4. 尚未確認的部分

- **只有單一種子、單次執行**：`random_state=0` 固定，但沒有多次重跑
  （不同種子）統計「$k=9$ 是否穩定勝出」，也沒有 cross-validation。
- **silhouette 的適用範圍**：演算法是 `k-means++` 起始 + `n_init=10` 取最佳結果；
  silhouette 基於同一標籤計算，沒驗證不同初始化策略下的差異。
- **log 只回應程式輸出**：`figs/lab1_k_selection.png` 檔名與程式
  （`lab1_cluster.py:39`）一致，且檔案存在，但 log 沒有印出存檔成功的訊息，
  圖檔內容是否與本 log 完全對應無法由文字輸出獨立確認。

---

## 5. 檢查問題

> 若有一位同學只用 inertia 選 $k$，他會得到什麼結論？為什麼本 Lab 反而用
> silhouette 判斷？

答案：inertia 在 $k=2\sim12$ 全程單調遞減且無明顯手肘，無法挑出一個「轉折點」，
說「$k$ 愈大愈好」沒有意義；而 silhouette 在 $k=9$ 有清楚的多峰（$0.1893$，
高過兩旁的 $0.1784$、$0.1825$），可以直接選出最佳 $k$，所以用 silhouette。