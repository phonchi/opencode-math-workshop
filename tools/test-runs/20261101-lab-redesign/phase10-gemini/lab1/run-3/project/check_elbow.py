import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

df = pd.read_csv('data/line_modes.csv')
X = df.drop(columns=['firmware_ver', 'sample_period_s'], errors='ignore')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

inertias = []
sil_scores = []
K_range = range(1, 10)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    if k > 1:
        sil_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    else:
        sil_scores.append(np.nan)

print("KMeans Inertias:", inertias)
print("KMeans Silhouette Scores:", sil_scores)

# 計算 Inertia 差分（肘部法則）
diffs = np.diff(inertias)
diffs2 = np.diff(diffs)
print("Inertia diffs:", diffs)
print("Inertia diffs2:", diffs2)
