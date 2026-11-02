import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

# Load digits dataset
digits = load_digits()
X = digits.data  # shape (1797, 64)
n_samples, n_features = X.shape

# Center the data
X_mean = np.mean(X, axis=0)
X_centered = X - X_mean

# Compute covariance matrix
cov_matrix = np.cov(X_centered, rowvar=False)

# Eigendecomposition
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

# Sort eigenvalues and eigenvectors in descending order
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# Take first 10 principal components
n_components = 10
components_manual = eigenvectors[:, :n_components].T  # shape (n_components, n_features)
X_transformed_manual = X_centered @ components_manual.T

# Compare with sklearn PCA
pca_sklearn = PCA(n_components=n_components)
X_transformed_sklearn = pca_sklearn.fit_transform(X)

print("Manual PCA shape:", X_transformed_manual.shape)
print("Sklearn PCA shape:", X_transformed_sklearn.shape)
print("\nExplained variance ratio (manual):")
print(eigenvalues[:n_components] / np.sum(eigenvalues))
print("\nExplained variance ratio (sklearn):")
print(pca_sklearn.explained_variance_ratio_)
print("\nMax absolute difference in transformed data:")
# Sign may differ, so check absolute difference
diff = np.abs(np.abs(X_transformed_manual) - np.abs(X_transformed_sklearn))
print(np.max(diff))
print("\nMean absolute difference:")
print(np.mean(diff))
