import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

df = pd.read_csv('data/line_modes.csv')
X = df.drop(columns=['firmware_ver', 'sample_period_s'], errors='ignore')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("K | Silhouette | Calinski-Harabasz | Davies-Bouldin")
print("-" * 50)
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    ch = calinski_harabasz_score(X_scaled, labels)
    db = davies_bouldin_score(X_scaled, labels)
    print(f"{k} | {sil:.4f}     | {ch:.2f}          | {db:.4f}")
