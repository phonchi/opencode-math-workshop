# sklearn digits 最佳分群數分析

日期：2026-11-02
腳本：`scripts/digits_clustering.py`、`scripts/digits_verify.py`
圖：`figs/digits_cluster_k_selection.png`

## 結論：分成 $k = 10$ 群最好

## 資料與方法

- `load_digits()`：$n = 1797$、64 維（$8\times 8$ 像素），真實標籤為數字 0–9 共 10 類。
- 預處理：`StandardScaler` 標準化；另測 PCA（保留 95% 變異 → 40 維）與 L2 正規化（cosine 距離）兩種表示法。
- 模型：KMeans（`n_init=20`），$k = 2 \sim 20$。

## 證據

### 1. 外部驗證（對照真實標籤的 ARI）

| 表示法 | ARI @ k=10 |
|---|---|
| raw（標準化 64 維） | 0.478 |
| PCA 40 維 | 0.467 |
| cosine（L2 正規化） | 0.578 |

k=10 時的 contingency 顯示：0、2、4、5、6、7 各自成群，純度 83%–99%；數字 1 拆成兩個書寫風格子群（各含大量 8 混入），3/5/9 互相糾纏。

### 2. 內部指標為何不可單獨採信

- **Silhouette / Davies-Bouldin** 峰值落在 $k = 14 \sim 15$，但曲線從 $k=8$ 到 $k=15$ 幾乎平坦（silhouette 僅 0.16→0.17），且絕對值偏低。這是資料「群與群重疊、非球狀」的典型訊號，指標傾向把同一數字的不同筆跡再切細而虛增分數。
- **Calinski-Harabasz** 峰值在 $k=2$，此指標有偏向小 $k$ 的已知偏誤，在這份資料上無參考價值。
- **Inertia elbow** 無明顯轉折。

### 3. 為什麼不是 k=15

silhouette 在 k≈15 的「峰值」來自把同一個數字（尤其 1、3）的不同寫法切成多群。指標微幅上升，但群已不再對應「一個數字一個群」的語意，屬於過度切分（over-splitting）的假象。

## k=10 的準確率

分群標籤與數字無先驗對應，先用 Hungarian algorithm 找最佳一對一映射後計算 accuracy：

| 表示法 | Hungarian accuracy | purity |
|---|---|---|
| raw（標準化 64 維） | 0.609 | 0.628 |
| PCA 40 維 | 0.589 | 0.623 |
| cosine（L2 正規化） | 0.674 | 0.716 |

腳本：`scripts/digits_accuracy.py`

## 困難對

KMeans 在這份資料的極限約 ARI 0.5–0.6，主要混淆對：1↔8、3↔9、5↔9、2↔3。若要更高純度需改用非線性方法（如 t-SNE 降維後分群），但「該分幾群」的答案仍是 10。
