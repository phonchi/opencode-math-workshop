import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score, normalized_mutual_info_score

# Load digits dataset
digits = load_digits()
X = digits.data
y = digits.target

print(f"Dataset shape: {X.shape}")
print(f"Number of true classes: {len(np.unique(y))}")

k_range = range(2, 16)
inertias = []
silhouette_scores = []
ch_scores = []
db_scores = []
ari_scores = []
nmi_scores = []

for k in k_range:
    kmeans = KMeans(n_init=10, n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X)
    
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X, labels))
    ch_scores.append(calinski_harabasz_score(X, labels))
    db_scores.append(davies_bouldin_score(X, labels))
    ari_scores.append(adjusted_rand_score(y, labels))
    nmi_scores.append(normalized_mutual_info_score(y, labels))
    
    print(f"k={k:2d}: Silhouette={silhouette_scores[-1]:.4f}, CH={ch_scores[-1]:.2f}, DB={db_scores[-1]:.4f}, ARI={ari_scores[-1]:.4f}, NMI={nmi_scores[-1]:.4f}")

# Find best k according to various metrics
best_k_sil = k_range[np.argmax(silhouette_scores)]
best_k_ch = k_range[np.argmax(ch_scores)]
best_k_db = k_range[np.argmin(db_scores)]
best_k_ari = k_range[np.argmax(ari_scores)]

print("\n--- Summary of Best K ---")
print(f"Best k by Silhouette Score: {best_k_sil}")
print(f"Best k by Calinski-Harabasz Index: {best_k_ch}")
print(f"Best k by Davies-Bouldin Index: {best_k_db}")
print(f"Best k by Adjusted Rand Index (vs true labels): {best_k_ari}")

# Plotting
fig, axes = plt.subplots(3, 2, figsize=(12, 15))

axes[0, 0].plot(k_range, inertias, marker='o')
axes[0, 0].set_title('Elbow Method (Inertia)')
axes[0, 0].set_xlabel('k')
axes[0, 0].set_ylabel('Inertia')

axes[0, 1].plot(k_range, silhouette_scores, marker='o', color='green')
axes[0, 1].set_title('Silhouette Score (higher is better)')
axes[0, 1].set_xlabel('k')
axes[0, 1].set_ylabel('Silhouette Score')
axes[0, 1].axvline(x=10, color='r', linestyle='--', alpha=0.7, label='k=10 (True classes)')
axes[0, 1].legend()

axes[1, 0].plot(k_range, ch_scores, marker='o', color='purple')
axes[1, 0].set_title('Calinski-Harabasz Index (higher is better)')
axes[1, 0].set_xlabel('k')
axes[1, 0].set_ylabel('CH Score')
axes[1, 0].axvline(x=10, color='r', linestyle='--', alpha=0.7, label='k=10')

axes[1, 1].plot(k_range, db_scores, marker='o', color='orange')
axes[1, 1].set_title('Davies-Bouldin Index (lower is better)')
axes[1, 1].set_xlabel('k')
axes[1, 1].set_ylabel('DB Score')
axes[1, 1].axvline(x=10, color='r', linestyle='--', alpha=0.7, label='k=10')

axes[2, 0].plot(k_range, ari_scores, marker='o', color='blue')
axes[2, 0].set_title('Adjusted Rand Index (vs True Labels)')
axes[2, 0].set_xlabel('k')
axes[2, 0].set_ylabel('ARI')
axes[2, 0].axvline(x=10, color='r', linestyle='--', alpha=0.7, label='k=10')

axes[2, 1].plot(k_range, nmi_scores, marker='o', color='brown')
axes[2, 1].set_title('Normalized Mutual Information (vs True Labels)')
axes[2, 1].set_xlabel('k')
axes[2, 1].set_ylabel('NMI')
axes[2, 1].axvline(x=10, color='r', linestyle='--', alpha=0.7, label='k=10')

plt.tight_layout()
plt.savefig('figs/digits_clustering_analysis.png', dpi=300)
print("\nPlot saved to figs/digits_clustering_analysis.png")
