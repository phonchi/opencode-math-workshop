import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

df = pd.read_csv('data/line_modes.csv')
features = ['temp_c', 'vibration_mm_s', 'pressure_kpa', 'flow_lpm', 'current_a', 'speed_rpm']
X = df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 測試 k = 4, 5, 6
for k in [4, 5, 6]:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df[f'cluster_{k}'] = kmeans.fit_predict(X_scaled)
    print(f"\n--- K = {k} 聚類中心 (原始特徵尺度) ---")
    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    centers_df = pd.DataFrame(centers, columns=features)
    print(centers_df)

# 繪製溫度對轉速的分群散佈圖 (以 k=5 為例)
plt.figure(figsize=(10, 6))
kmeans_5 = KMeans(n_clusters=5, random_state=42, n_init=10)
labels_5 = kmeans_5.fit_predict(X_scaled)
scatter = plt.scatter(df['temp_c'], df['speed_rpm'], c=labels_5, cmap='tab10', alpha=0.8, edgecolor='k', s=40)
plt.colorbar(scatter, label='Cluster / Mode')
plt.xlabel('Temperature (°C)')
plt.ylabel('Speed (RPM)')
plt.title('Production Line Sensor Readings - Operating Modes ($k=5$)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('figs/line_modes_k5.png', dpi=300, bbox_inches='tight')
plt.close()

# 繪製 k=4 的散佈圖
plt.figure(figsize=(10, 6))
kmeans_4 = KMeans(n_clusters=4, random_state=42, n_init=10)
labels_4 = kmeans_4.fit_predict(X_scaled)
scatter = plt.scatter(df['temp_c'], df['speed_rpm'], c=labels_4, cmap='tab10', alpha=0.8, edgecolor='k', s=40)
plt.colorbar(scatter, label='Cluster / Mode')
plt.xlabel('Temperature (°C)')
plt.ylabel('Speed (RPM)')
plt.title('Production Line Sensor Readings - Operating Modes ($k=4$)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('figs/line_modes_k4.png', dpi=300, bbox_inches='tight')
plt.close()
