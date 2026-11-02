import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

df = pd.read_csv('data/line_modes.csv')
features = [c for c in df.columns if c not in ['firmware_ver', 'sample_period_s']]
X = df[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"{'K':<3} {'Silhouette':<12} {'Calinski-H':<12} {'Davies-B':<10} {'BIC':<12}")
for k in range(2, 10):
    gmm = GaussianMixture(n_components=k, random_state=42)
    labels = gmm.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    ch = calinski_harabasz_score(X_scaled, labels)
    db = davies_bouldin_score(X_scaled, labels)
    bic = gmm.bic(X_scaled)
    print(f"{k:<3} {sil:<12.4f} {ch:<12.2f} {db:<10.4f} {bic:<12.2f}")
