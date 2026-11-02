import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Load data
df = pd.read_csv('data/line_modes.csv')
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print(df.describe())

# Check unique values for each column
for col in df.columns:
    print(f"{col}: unique count = {df[col].nunique()}")

# Let's run GaussianMixture and KMeans for k from 1 to 10 and check BIC/AIC and Silhouette
features = [c for c in df.columns if c not in ['firmware_ver', 'sample_period_s']]
print("Using features for clustering:", features)

X = df[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

bics = []
aics = []
inertias = []
K_range = range(1, 10)

for k in K_range:
    gmm = GaussianMixture(n_components=k, random_state=42)
    gmm.fit(X_scaled)
    bics.append(gmm.bic(X_scaled))
    aics.append(gmm.aic(X_scaled))
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

print("BIC values:", bics)
print("AIC values:", aics)

# Best K by GMM BIC
best_k_bic = K_range[np.argmin(bics)]
print("Best K by BIC:", best_k_bic)

# Fit final GMM with best_k_bic (or let's inspect if best_k_bic is 3, 4, etc.)
gmm_best = GaussianMixture(n_components=best_k_bic, random_state=42)
labels = gmm_best.fit_predict(X_scaled)
df['mode'] = labels

print("Cluster counts:")
print(df['mode'].value_counts())

# Cluster centers in original scale
centers_scaled = gmm_best.means_
centers_original = scaler.inverse_transform(centers_scaled)
centers_df = pd.DataFrame(centers_original, columns=features)
print("\nCluster centers (original scale):")
print(centers_df)

# Plot PCA visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis', alpha=0.7, edgecolors='k')
plt.title(f'Line Modes Clustering (K={best_k_bic})')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.colorbar(scatter, label='Mode')
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('figs/line_modes_cluster.png', dpi=300, bbox_inches='tight')
plt.close()
