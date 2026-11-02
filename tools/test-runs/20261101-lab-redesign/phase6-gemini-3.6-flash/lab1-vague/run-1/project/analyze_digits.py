import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score, adjusted_mutual_info_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Ensure directories exist
os.makedirs("figs", exist_ok=True)
os.makedirs("notes", exist_ok=True)

# Load dataset
digits = load_digits()
X, y = digits.data, digits.target

# Standardize data / PCA preprocessing
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=0.95, random_state=42)
X_pca = pca.fit_transform(X_scaled)

k_range = range(2, 21)

# Metrics evaluation for Raw and PCA data
metrics_raw = {'k': [], 'inertia': [], 'silhouette': [], 'ch': [], 'db': [], 'ari': [], 'ami': []}
metrics_pca = {'k': [], 'inertia': [], 'silhouette': [], 'ch': [], 'db': [], 'ari': [], 'ami': []}

for k in k_range:
    # Raw K-Means
    kmeans_raw = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_raw = kmeans_raw.fit_predict(X)
    metrics_raw['k'].append(k)
    metrics_raw['inertia'].append(kmeans_raw.inertia_)
    metrics_raw['silhouette'].append(silhouette_score(X, labels_raw))
    metrics_raw['ch'].append(calinski_harabasz_score(X, labels_raw))
    metrics_raw['db'].append(davies_bouldin_score(X, labels_raw))
    metrics_raw['ari'].append(adjusted_rand_score(y, labels_raw))
    metrics_raw['ami'].append(adjusted_mutual_info_score(y, labels_raw))

    # PCA K-Means
    kmeans_pca = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_pca = kmeans_pca.fit_predict(X_pca)
    metrics_pca['k'].append(k)
    metrics_pca['inertia'].append(kmeans_pca.inertia_)
    metrics_pca['silhouette'].append(silhouette_score(X_pca, labels_pca))
    metrics_pca['ch'].append(calinski_harabasz_score(X_pca, labels_pca))
    metrics_pca['db'].append(davies_bouldin_score(X_pca, labels_pca))
    metrics_pca['ari'].append(adjusted_rand_score(y, labels_pca))
    metrics_pca['ami'].append(adjusted_mutual_info_score(y, labels_pca))

# Plotting
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# 1. Inertia (Elbow Method)
axes[0, 0].plot(k_range, metrics_raw['inertia'], 'o-', label='Raw Data')
axes[0, 0].set_title('Elbow Method (Inertia)')
axes[0, 0].set_xlabel('Number of Clusters (k)')
axes[0, 0].set_ylabel('Inertia')
axes[0, 0].axvline(x=10, color='r', linestyle='--', label='k=10')
axes[0, 0].legend()
axes[0, 0].grid(True)

# 2. Silhouette Score
axes[0, 1].plot(k_range, metrics_raw['silhouette'], 'o-', label='Raw Data')
axes[0, 1].plot(k_range, metrics_pca['silhouette'], 's--', label='PCA Data')
axes[0, 1].set_title('Silhouette Score (Higher is better)')
axes[0, 1].set_xlabel('Number of Clusters (k)')
axes[0, 1].set_ylabel('Silhouette Score')
axes[0, 1].axvline(x=9, color='g', linestyle=':', label='Peak (k=9/10)')
axes[0, 1].axvline(x=10, color='r', linestyle='--', label='k=10')
axes[0, 1].legend()
axes[0, 1].grid(True)

# 3. Calinski-Harabasz Index
axes[0, 2].plot(k_range, metrics_raw['ch'], 'o-', label='Raw Data')
axes[0, 2].set_title('Calinski-Harabasz Index (Higher is better)')
axes[0, 2].set_xlabel('Number of Clusters (k)')
axes[0, 2].set_ylabel('CH Index')
axes[0, 2].axvline(x=9, color='g', linestyle=':', label='k=9')
axes[0, 2].axvline(x=10, color='r', linestyle='--', label='k=10')
axes[0, 2].legend()
axes[0, 2].grid(True)

# 4. Davies-Bouldin Index
axes[1, 0].plot(k_range, metrics_raw['db'], 'o-', label='Raw Data')
axes[1, 0].set_title('Davies-Bouldin Index (Lower is better)')
axes[1, 0].set_xlabel('Number of Clusters (k)')
axes[1, 0].set_ylabel('DB Index')
axes[1, 0].axvline(x=9, color='g', linestyle=':', label='k=9')
axes[1, 0].axvline(x=10, color='r', linestyle='--', label='k=10')
axes[1, 0].legend()
axes[1, 0].grid(True)

# 5. Adjusted Rand Index (Ground Truth Evaluation)
axes[1, 1].plot(k_range, metrics_raw['ari'], 'o-', label='Raw ARI')
axes[1, 1].plot(k_range, metrics_pca['ari'], 's--', label='PCA ARI')
axes[1, 1].set_title('Adjusted Rand Index (ARI vs Ground Truth)')
axes[1, 1].set_xlabel('Number of Clusters (k)')
axes[1, 1].set_ylabel('ARI')
axes[1, 1].axvline(x=10, color='r', linestyle='--', label='k=10')
axes[1, 1].legend()
axes[1, 1].grid(True)

# 6. Adjusted Mutual Info (AMI vs Ground Truth)
axes[1, 2].plot(k_range, metrics_raw['ami'], 'o-', label='Raw AMI')
axes[1, 2].plot(k_range, metrics_pca['ami'], 's--', label='PCA AMI')
axes[1, 2].set_title('Adjusted Mutual Info (AMI vs Ground Truth)')
axes[1, 2].set_xlabel('Number of Clusters (k)')
axes[1, 2].set_ylabel('AMI')
axes[1, 2].axvline(x=10, color='r', linestyle='--', label='k=10')
axes[1, 2].legend()
axes[1, 2].grid(True)

plt.tight_layout()
plt.savefig("figs/digits_clustering.png", dpi=300)
print("Plot saved to figs/digits_clustering.png")

print("\n--- Raw Data Evaluation Table ---")
print("k\tSilhouette\tCH Index\tDB Index\tARI\tAMI")
for i in range(len(k_range)):
    print(f"{metrics_raw['k'][i]}\t{metrics_raw['silhouette'][i]:.4f}\t\t{metrics_raw['ch'][i]:.1f}\t\t{metrics_raw['db'][i]:.4f}\t\t{metrics_raw['ari'][i]:.4f}\t{metrics_raw['ami'][i]:.4f}")

