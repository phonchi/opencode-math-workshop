import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

N_COMPONENTS = 10


def hand_crafted_pca(X, n_components):
    n_samples = X.shape[0]

    mean = X.mean(axis=0)
    X_centered = X - mean

    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

    eigenvalues = (S**2) / (n_samples - 1)
    explained_variance_ratio = eigenvalues / np.sum(eigenvalues)

    components = Vt[:n_components, :].copy()
    for i in range(components.shape[0]):
        j = int(np.argmax(np.abs(components[i])))
        if components[i, j] < 0:
            components[i] = -components[i]

    projected = X_centered @ components.T

    return components, eigenvalues, explained_variance_ratio, projected


def main():
    data = load_digits()
    X = data.data.astype(np.float64)

    components, eigenvalues, explained_variance_ratio, projected = hand_crafted_pca(X, N_COMPONENTS)

    sk_pca = PCA(n_components=N_COMPONENTS)
    projected_sk = sk_pca.fit_transform(X)

    components_sk = sk_pca.components_
    eigenvalues_sk = sk_pca.explained_variance_
    explained_variance_sk = sk_pca.explained_variance_ratio_

    components_match = np.allclose(components, components_sk, rtol=1e-5, atol=1e-8)
    eigenvalues_match = np.allclose(eigenvalues[:N_COMPONENTS], eigenvalues_sk, rtol=1e-6)
    evr_match = np.allclose(explained_variance_ratio[:N_COMPONENTS], explained_variance_sk, rtol=1e-6)
    projection_match = np.allclose(projected, projected_sk, rtol=1e-5, atol=1e-8)

    cumulative_variance = np.sum(explained_variance_ratio[:N_COMPONENTS])
    print(f"hand-crafted PCA on digits: X shape = {X.shape}, n_components = {N_COMPONENTS}")
    print(f"eigenvalues (top {N_COMPONENTS}): {eigenvalues[:N_COMPONENTS]}")
    print(f"explained variance ratio (top {N_COMPONENTS}): {explained_variance_ratio[:N_COMPONENTS]}")
    print(f"cumulative explained variance: {cumulative_variance:.6f}")
    print(f"components match sklearn PCA: {components_match}")
    print(f"eigenvalues match sklearn PCA: {eigenvalues_match}")
    print(f"explained variance ratio match sklearn PCA: {evr_match}")
    print(f"projections match sklearn PCA: {projection_match}")

    plt.figure(figsize=(8, 5))
    plt.plot(np.arange(1, N_COMPONENTS + 1), eigenvalues[:N_COMPONENTS], "o-", label="hand-crafted SVD")
    plt.plot(np.arange(1, N_COMPONENTS + 1), eigenvalues_sk, "o--", label="sklearn PCA")
    plt.xlabel("Principal component")
    plt.ylabel("Eigenvalue")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figs/pca_digits_svd.png")
    plt.close()


if __name__ == "__main__":
    main()
