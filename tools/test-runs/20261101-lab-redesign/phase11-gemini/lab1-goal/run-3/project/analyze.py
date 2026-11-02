import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
import matplotlib.pyplot as plt
import os

# 1. 讀取資料
data_path = "data/line_modes.csv"
batch_path = "data/line_modes_batches.csv"

df = pd.read_csv(data_path)
df_batches = pd.read_csv(batch_path)
y_true = df_batches['batch'].values

print(f"資料筆數: {df.shape[0]}, 特徵數: {df.shape[1]}")
print(f"真實批次數量: {len(np.unique(y_true))}, 批次列表: {np.unique(y_true)}")

# 2. 特徵標準化 (Standardization)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

results = {}

for k in [9, 10]:
    # 3. K-Means 分群設定 (固定 random_state 以確保重現性)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    y_pred = kmeans.fit_predict(X_scaled)
    
    # 4. 計算指標
    sil = silhouette_score(X_scaled, y_pred)
    ari = adjusted_rand_score(y_true, y_pred)
    
    results[k] = {
        'silhouette': sil,
        'ari': ari,
        'labels': y_pred
    }
    print(f"k = {k}: Silhouette Score = {sil:.4f}, ARI = {ari:.4f}")

# 5. 繪製並儲存圖表到 figs/
os.makedirs("figs", exist_ok=True)
fig, ax = plt.subplots(figsize=(8, 5))
ks = [9, 10]
sils = [results[k]['silhouette'] for k in ks]
aris = [results[k]['ari'] for k in ks]

x = np.arange(len(ks))
width = 0.35

rects1 = ax.bar(x - width/2, sils, width, label='Silhouette Score', color='skyblue')
rects2 = ax.bar(x + width/2, aris, width, label='ARI', color='salmon')

ax.set_ylabel('Score')
ax.set_title('Comparison of k=9 and k=10 Clustering Performance')
ax.set_xticks(x)
ax.set_xticklabels([f'k={k}' for k in ks])
ax.legend()

fig.tight_layout()
plt.savefig("figs/clustering_comparison.png", dpi=300)
plt.close()

# 6. 寫入筆記到 notes/
os.makedirs("notes", exist_ok=True)
note_content = f"""# 產線感測讀數分群分析 (k=9 vs k=10)

## 實驗設定與決策
1. **資料前處理**：使用 `StandardScaler` 將 8 個感測器特徵進行標準化（均值為 0，變異數為 1），消除不同量綱的影響。
2. **分群演算法**：採用 `KMeans` 演算法，設定 `random_state=42` 與 `n_init=10` 以確保結果可重現。
3. **評估指標**：
   - **Silhouette Score**：評估群集內聚力與分離度。
   - **Adjusted Rand Index (ARI)**：與真實批次標籤（10 批）對比分群一致性。

## 結果摘要
- **k = 9**：
  - Silhouette Score = {results[9]['silhouette']:.4f}
  - ARI = {results[9]['ari']:.4f}
- **k = 10**：
  - Silhouette Score = {results[10]['silhouette']:.4f}
  - ARI = {results[10]['ari']:.4f}

## 業務用途建議
由於實際批次數為 10 批，且用途為「追蹤每筆讀數來自哪個批次，不同批次不能合併」，若 $k=9$ 會強制將其中兩批合併，違反「不同批次不能合併」的核心需求。即使 $k=10$ 的評估指標（或 ARI）可能需要考量，實務上批次追蹤應對應真實批次數 $k=10$。
"""

with open("notes/clustering_analysis.md", "w", encoding="utf-8") as f:
    f.write(note_content)

print("分析完成，圖表已存至 figs/clustering_comparison.png，筆記已存至 notes/clustering_analysis.md")
