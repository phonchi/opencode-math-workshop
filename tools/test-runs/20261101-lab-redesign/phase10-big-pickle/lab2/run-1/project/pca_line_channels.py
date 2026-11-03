import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK TC", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DATA = "data/line_channels.csv"
FIG = "figs"


def load_data():
    raw = np.genfromtxt(DATA, delimiter=",", names=True)
    cols = list(raw.dtype.names)
    X = np.column_stack([raw[c] for c in cols])
    return cols, X


def main():
    cols, X = load_data()
    Z = StandardScaler().fit_transform(X)
    n, p = Z.shape

    pca = PCA().fit(Z)
    ev = pca.explained_variance_ratio_
    cum = np.cumsum(ev)
    eig = np.linalg.eigvalsh(np.corrcoef(X.T))[::-1]

    print(f"shape={Z.shape}")
    print("explained variance:", np.round(ev, 4))
    print("cumulative:", np.round(cum, 4))
    print("eigenvalues:", np.round(eig, 4))
    print("Kaiser (eigenvalue>1):", int((eig > 1).sum()))

    k80 = int(np.searchsorted(cum, 0.80) + 1)
    k90 = int(np.searchsorted(cum, 0.90) + 1)
    k95 = int(np.searchsorted(cum, 0.95) + 1)
    print(f"PCs for 80/90/95%: {k80}/{k90}/{k95}")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].bar(np.arange(1, p + 1), ev * 100, color="#4C72B0")
    ax[0].plot(np.arange(1, p + 1), ev * 100, "o-", color="#C44E52", ms=3)
    ax[0].set(xlabel="Principal component", ylabel="Explained variance (%)",
              title="Scree plot")
    ax[0].set_xticks(np.arange(1, p + 1))

    ax[1].plot(np.arange(1, p + 1), cum * 100, "o-", color="#4C72B0")
    for level, ls in [(80, ":"), (90, "--"), (95, "-.")]:
        ax[1].axhline(level, color="gray", ls=ls, lw=1)
        ax[1].text(p + 0.1, level + 0.5, f"{level}%", fontsize=8, color="gray")
    ax[1].axvline(4, color="#C44E52", ls="--", lw=1)
    ax[1].text(4.1, 40, "Kaiser: 4 PCs", color="#C44E52", fontsize=9)
    ax[1].set(xlabel="Number of PCs", ylabel="Cumulative explained variance (%)",
              title="Cumulative variance", ylim=(0, 103))
    ax[1].set_xticks(np.arange(1, p + 1))
    fig.tight_layout()
    fig.savefig(f"{FIG}/pca_scree.png", dpi=160)
    plt.close(fig)

    k_show = 6
    load = pca.components_[:k_show]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    vmax = np.abs(load).max()
    im = ax.imshow(load, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(p), cols)
    ax.set_yticks(range(k_show), [f"PC{i+1}" for i in range(k_show)])
    for i in range(k_show):
        for j in range(p):
            ax.text(j, i, f"{load[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title("PCA loadings (standardized channels)")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(f"{FIG}/pca_loadings.png", dpi=160)
    plt.close(fig)

    ks = np.arange(1, p)
    r2 = np.zeros((len(ks), p))
    for i, k in enumerate(ks):
        m = PCA(n_components=k).fit(Z)
        rec = m.inverse_transform(m.transform(Z))
        r2[i] = 1 - ((Z - rec) ** 2).mean(axis=0)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    im = ax.imshow(r2, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(p), cols)
    ax.set_yticks(range(len(ks)), ks)
    for i in range(len(ks)):
        for j in range(p):
            ax.text(j, i, f"{r2[i, j]:.2f}", ha="center", va="center",
                    fontsize=7, color="white" if r2[i, j] < 0.6 else "black")
    ax.set(xlabel="Channel", ylabel="Number of PCs",
           title="Per-channel reconstruction $R^2$")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(f"{FIG}/pca_reconstruction.png", dpi=160)
    plt.close(fig)

    scores = pca.transform(Z)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].scatter(scores[:, 0], scores[:, 1], s=8, alpha=0.5, color="#4C72B0")
    ax[0].set(xlabel=f"PC1 ({ev[0]*100:.1f}%)", ylabel=f"PC2 ({ev[1]*100:.1f}%)",
              title="Scores: PC1 vs PC2")
    ax[1].scatter(scores[:, 2], scores[:, 3], s=8, alpha=0.5, color="#55A868")
    ax[1].set(xlabel=f"PC3 ({ev[2]*100:.1f}%)", ylabel=f"PC4 ({ev[3]*100:.1f}%)",
              title="Scores: PC3 vs PC4")
    fig.tight_layout()
    fig.savefig(f"{FIG}/pca_scores.png", dpi=160)
    plt.close(fig)

    groups = {"ch01-ch08": cols[:8], "ch09-ch10": cols[8:10], "ch11": cols[10:]}
    for name, g in groups.items():
        idx = [cols.index(c) for c in g]
        Zg = StandardScaler().fit_transform(X[:, idx])
        pg = PCA().fit(Zg)
        cg = np.cumsum(pg.explained_variance_ratio_)
        print(f"{name}: cum={np.round(cg, 4)}")


if __name__ == "__main__":
    main()
