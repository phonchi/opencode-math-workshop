import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# 讀取資料
df = pd.read_csv('data/line_modes.csv')
print(f"資料筆數: {len(df)}")
print(df.head())
print(df.describe())

# 檢視各特徵的獨立值或分佈
print("firmware_ver 獨特值:", df['firmware_ver'].unique())
print("sample_period_s 獨特值:", df['sample_period_s'].unique())

X = df.drop(columns=['firmware_ver', 'sample_period_s'], errors='ignore')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 測試不同分群數 k (1 到 10)
bic = []
aic = []
sil = []
K_range = range(1, 10)

for k in K_range:
    gmm = GaussianMixture(n_components=k, random_state=42)
    gmm.fit(X_scaled)
    bic.append(gmm.bic(X_scaled))
    aic.append(gmm.aic(X_scaled))
    if k > 1:
        labels = gmm.predict(X_scaled)
        sil.append(silhouette_score(X_scaled, labels))
    else:
        sil.append(np.nan)

print("K range:", list(K_range))
print("BIC:", bic)
print("AIC:", aic)
print("Silhouette scores:", sil)

# 決定最佳 k (依據最低 BIC 或 AIC 或最高 Silhouette)
best_k_bic = list(K_range)[np.argmin(bic)]
print(f"依據 BIC 推薦的運作模式數量: {best_k_bic}")

# 使用最佳 k 進行 GMM 分群
best_gmm = GaussianMixture(n_components=best_k_bic, random_state=42)
labels = best_gmm.fit_predict(X_scaled)
df['mode'] = labels

print("各模式樣本數:")
print(df['mode'].value_counts().sort_index())

print("各模式特徵平均值:")
print(df.groupby('mode').mean())

# 繪製圖表並存到 figs/
plt.figure(figsize=(10, 6))
plt.plot(list(K_range), bic, marker='o', label='BIC')
plt.plot(list(K_range), aic, marker='s', label='AIC')
plt.xlabel('Number of Components (k)')
plt.ylabel('Information Criterion')
plt.title('GMM BIC / AIC for Line Modes')
plt.legend()
plt.grid(True)
plt.savefig('figs/line_modes_bic_aic.png', dpi=300, bbox_inches='tight')
plt.close()

# 繪製分群結果散佈圖 (temp_c vs speed_rpm)
plt.figure(figsize=(10, 6))
scatter = plt.scatter(df['temp_c'], df['speed_rpm'], c=df['mode'], cmap='viridis', alpha=0.7)
plt.colorbar(scatter, label='Mode')
plt.xlabel('Temperature (°C)')
plt.ylabel('Speed (RPM)')
plt.title(f'Production Line Modes (Detected {best_k_bic} modes)')
plt.grid(True)
plt.savefig('figs/line_modes_scatter.png', dpi=300, bbox_inches='tight')
plt.close()
