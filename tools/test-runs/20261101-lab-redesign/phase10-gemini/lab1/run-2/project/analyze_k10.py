import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

df = pd.read_csv('data/line_modes.csv')
features = [c for c in df.columns if c not in ['firmware_ver', 'sample_period_s']]
X = df[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

for k in range(9, 13):
    gmm = GaussianMixture(n_components=k, random_state=42)
    labels = gmm.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    ch = calinski_harabasz_score(X_scaled, labels)
    db = davies_bouldin_score(X_scaled, labels)
    bic = gmm.bic(X_scaled)
    print(f"K={k}: Sil={sil:.4f}, CH={ch:.2f}, DB={db:.4f}, BIC={bic:.2f}")
