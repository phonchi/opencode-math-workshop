import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score

digits = load_digits()
X = digits.data
y = digits.target

# Scale + PCA
X_scaled = StandardScaler().fit_transform(X)
X_pca = PCA(n_components=16, random_state=42).fit_transform(X_scaled)

print("With StandardScaler + PCA (16 dims):")
for k in range(8, 14):
    kmeans = KMeans(n_init=10, n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_pca)
    sil = silhouette_score(X_pca, labels)
    ari = adjusted_rand_score(y, labels)
    nmi = normalized_mutual_info_score(y, labels)
    print(f"k={k}: Silhouette={sil:.4f}, ARI={ari:.4f}, NMI={nmi:.4f}")
