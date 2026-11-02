import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def pca_hand(X, n_components):
    """回傳 (mean, components, explained_variance, explained_variance_ratio)。"""
    mean = X.mean(axis=0)
    Xc = X - mean

    # 對中心化資料做 SVD：Xc = U S Vt，Vt 的每一列就是主成分方向
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)

    n_samples = X.shape[0]
    explained_variance = (S ** 2) / (n_samples - 1)
    explained_variance_ratio = explained_variance / explained_variance.sum()

    components = Vt[:n_components]
    return (
        mean,
        components,
        explained_variance[:n_components],
        explained_variance_ratio[:n_components],
    )


def main():
    digits = load_digits()
    X, y = digits.data, digits.target
    n_components = 10

    mean, components, ev, evr = pca_hand(X, n_components)

    # sklearn 對照組
    sk = PCA(n_components=n_components, svd_solver="full")
    X_sk = sk.fit_transform(X)

    # 手刻投影
    X_hand = (X - mean) @ components.T

    print("=== 解釋變異量比例（前 10 個主成分）===")
    print("手刻 :", np.round(evr, 6))
    print("sklearn:", np.round(sk.explained_variance_ratio_, 6))
    print("最大差異:", np.abs(evr - sk.explained_variance_ratio_).max())

    # 主成分方向只差正負號，逐個對齊後比較
    sign = np.sign(np.sum(components * sk.components_, axis=1))
    sign[sign == 0] = 1
    aligned = components * sign[:, None]
    print("\n=== 主成分方向 ===")
    print("對齊後最大差異:", np.abs(aligned - sk.components_).max())

    print("\n=== 投影座標 ===")
    # sklearn 的投影也依同樣的正負號對齊
    print("投影最大差異:", np.abs(X_hand - X_sk * sign).max())

    # 重建誤差（用前 10 維重建回 64 維）
    X_rec_hand = X_hand @ components + mean
    X_rec_sk = sk.inverse_transform(X_sk)
    print("\n=== 重建 ===")
    print("手刻重建 MSE:", np.mean((X - X_rec_hand) ** 2))
    print("sklearn 重建 MSE:", np.mean((X - X_rec_sk) ** 2))

    # 累積解釋變異量
    print("\n累積解釋變異量（前 10）:", evr.sum())

    # 圖：scree plot + 重建範例
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].bar(np.arange(1, n_components + 1), evr, alpha=0.8, label="individual")
    axes[0].plot(
        np.arange(1, n_components + 1), np.cumsum(evr),
        "o-", color="crimson", label="cumulative",
    )
    axes[0].set_xlabel("principal component")
    axes[0].set_ylabel("explained variance ratio")
    axes[0].set_title("PCA on digits (top 10)")
    axes[0].legend()

    axes[1].imshow(
        X_rec_hand[0].reshape(8, 8), cmap="gray",
        vmin=0, vmax=16,
    )
    axes[1].set_title(f"reconstruction with 10 PCs (label={y[0]})")
    axes[1].axis("off")

    fig.tight_layout()
    fig.savefig("figs/pca_digits.png", dpi=150)
    print("\n圖已存到 figs/pca_digits.png")


if __name__ == "__main__":
    main()
