import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA

df = pd.read_csv('data/line_modes.csv')
features = [c for c in df.columns if c not in ['firmware_ver', 'sample_period_s']]
X = df[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

gmm = GaussianMixture(n_components=9, random_state=42)
labels = gmm.fit_predict(X_scaled)
df['mode'] = labels

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab10', alpha=0.8, edgecolors='k', s=50)
plt.title('Production Line Operating Modes (K=9 GMM Clustering)', fontsize=14, fontweight='bold')
plt.xlabel('Principal Component 1 (PC1)', fontsize=12)
plt.ylabel('Principal Component 2 (PC2)', fontsize=12)
plt.colorbar(scatter, label='Operating Mode')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('figs/line_modes_cluster.png', dpi=300, bbox_inches='tight')
plt.close()
