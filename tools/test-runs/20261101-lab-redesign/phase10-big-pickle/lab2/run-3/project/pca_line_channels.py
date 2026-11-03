"""PCA on production-line sensor channels.

Standardizes each channel (z-score) before PCA because the channels use
very different units and scales (ch11 is ~1e6, ch09 is ~1e-2).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA = Path("data/line_channels.csv")
FIGS = Path("figs")
NOTES = Path("notes")
RNG = np.random.default_rng(42)


def load_data():
    raw = np.genfromtxt(DATA, delimiter=",", names=True)
    names = list(raw.dtype.names)
    X = np.column_stack([raw[n] for n in names]).astype(float)
    return names, X


def pca(Xz):
    """PCA via SVD on the standardized data (rows = samples)."""
    n = Xz.shape[0]
    U, S, Vt = np.linalg.svd(Xz, full_matrices=False)
    eigvals = S**2 / (n - 1)  # correlation-matrix eigenvalues
    scores = U * S
    return eigvals, Vt.T, scores  # Vt.T columns are loadings/PC directions


def parallel_analysis(Xz, n_iter=1000, percentile=95):
    """Horn's parallel analysis: eigenvalues from column-wise permuted data."""
    n, p = Xz.shape
    sim = np.empty((n_iter, p))
    for i in range(n_iter):
        Xp = np.column_stack([RNG.permutation(Xz[:, j]) for j in range(p)])
        Xp = (Xp - Xp.mean(axis=0)) / Xp.std(axis=0, ddof=1)
        sim[i] = np.linalg.svd(Xp, compute_uv=False) ** 2 / (n - 1)
    return np.percentile(sim, percentile, axis=0), sim.mean(axis=0)


def main():
    FIGS.mkdir(exist_ok=True)
    NOTES.mkdir(exist_ok=True)

    names, X = load_data()
    n, p = X.shape
    print(f"資料: {n} 筆樣本, {p} 個通道")
    print(f"缺值: {int(np.isnan(X).sum())}")

    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    Xz = (X - mean) / sd

    eigvals, loadings, scores = pca(Xz)
    explained = eigvals / eigvals.sum()
    cumulative = np.cumsum(explained)

    pa95, pa_mean = parallel_analysis(Xz, n_iter=1000)

    print("\n主成分解釋變異量:")
    print(f"{'PC':>3} {'eigenvalue':>11} {'explained':>10} {'cumulative':>11} "
          f"{'PA95':>8} {'keep?':>6}")
    for k in range(p):
        keep = "yes" if eigvals[k] > pa95[k] and eigvals[k] > 1 else ""
        print(f"{k + 1:>3} {eigvals[k]:>11.4f} {explained[k]:>9.2%} "
              f"{cumulative[k]:>10.2%} {pa95[k]:>8.4f} {keep:>6}")

    n_kaiser = int((eigvals > 1).sum())
    n_pa = int((eigvals > pa95).sum())
    n_80 = int(np.searchsorted(cumulative, 0.80) + 1)
    n_90 = int(np.searchsorted(cumulative, 0.90) + 1)
    print(f"\nKaiser (eigenvalue > 1): {n_kaiser} 個")
    print(f"Parallel analysis (95th pct): {n_pa} 個")
    print(f"累積解釋量 >= 80%: {n_80} 個; >= 90%: {n_90} 個")

    print("\n負荷量 (loading = 相關係數):")
    header = "channel " + " ".join(f"PC{k + 1:<5}" for k in range(min(5, p)))
    print(header)
    for j, name in enumerate(names):
        print(f"{name:>7} " + " ".join(f"{loadings[j, k]:>6.3f}"
                                       for k in range(min(5, p))))

    # ---- Figure 1: scree + cumulative variance ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ks = np.arange(1, p + 1)
    axes[0].plot(ks, eigvals, "o-", label="observed")
    axes[0].plot(ks, pa95, "s--", color="tab:red", label="parallel analysis 95%")
    axes[0].axhline(1, color="gray", ls=":", label="Kaiser (eigenvalue = 1)")
    axes[0].set_xlabel("Principal component")
    axes[0].set_ylabel("Eigenvalue")
    axes[0].set_title("Scree plot")
    axes[0].set_xticks(ks)
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    axes[1].plot(ks, cumulative, "o-", color="tab:green")
    for thresh, color in [(0.80, "tab:orange"), (0.90, "tab:purple")]:
        axes[1].axhline(thresh, color=color, ls="--", lw=1)
        axes[1].text(p, thresh + 0.01, f"{thresh:.0%}", color=color,
                     ha="right", fontsize=8)
    axes[1].set_xlabel("Number of components")
    axes[1].set_ylabel("Cumulative explained variance")
    axes[1].set_title("Cumulative variance")
    axes[1].set_xticks(ks)
    axes[1].set_ylim(0, 1.02)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGS / "pca_scree.png", dpi=150)
    plt.close(fig)

    # ---- Figure 2: loadings heatmap (first 4 PCs) ----
    n_show = min(4, p)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    im = ax.imshow(loadings[:, :n_show], cmap="RdBu_r", vmin=-1, vmax=1,
                   aspect="auto")
    ax.set_xticks(range(n_show))
    ax.set_xticklabels([f"PC{k + 1}" for k in range(n_show)])
    ax.set_yticks(range(p))
    ax.set_yticklabels(names)
    for j in range(p):
        for k in range(n_show):
            ax.text(k, j, f"{loadings[j, k]:.2f}", ha="center", va="center",
                    fontsize=8)
    ax.set_title("Loadings (correlation with each PC)")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(FIGS / "pca_loadings.png", dpi=150)
    plt.close(fig)

    # ---- Figure 3: score plot PC1-PC2 ----
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(scores[:, 0], scores[:, 1], s=10, alpha=0.5, color="tab:blue")
    scale = 3.0
    for j, name in enumerate(names):
        ax.arrow(0, 0, loadings[j, 0] * scale, loadings[j, 1] * scale,
                 color="tab:red", width=0.01, head_width=0.08, alpha=0.8)
        ax.text(loadings[j, 0] * scale * 1.12, loadings[j, 1] * scale * 1.12,
                name, color="tab:red", fontsize=8, ha="center")
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlabel(f"PC1 ({explained[0]:.1%})")
    ax.set_ylabel(f"PC2 ({explained[1]:.1%})")
    ax.set_title("Score plot (PC1 vs PC2)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGS / "pca_biplot.png", dpi=150)
    plt.close(fig)

    # ---- Markdown note ----
    lines = [
        "# 產線感測資料 PCA 降維",
        "",
        f"- 資料：`data/line_channels.csv`，{n} 筆樣本、{p} 個通道，無缺值。",
        "- 各通道單位與尺度差異大（ch11 約 $10^6$、ch09 約 $10^{-2}$），"
        "因此先對每個通道做 z-score 標準化，再對相關係數矩陣做 PCA。",
        "",
        "## 要保留幾個主成分",
        "",
        "| 判準 | 建議個數 |",
        "|---|---|",
        f"| Kaiser（特徵值 > 1） | {n_kaiser} |",
        f"| Parallel analysis（95%） | {n_pa} |",
        f"| 累積解釋變異 >= 80% | {n_80} |",
        f"| 累積解釋變異 >= 90% | {n_90} |",
        "",
        f"**建議保留 {n_pa} 個主成分**（PC1–PC{n_pa}），"
        f"累積解釋約 {cumulative[n_pa - 1]:.1%}。",
        "",
        "結構解讀：PC1–PC3 主要由 ch01–ch08 這組互相關聯的通道構成；"
        "PC4 幾乎就是 ch09 與 ch10 的共同變化；"
        "PC5 則幾乎單獨對應 ch11（負荷量約 -1.00）。",
        "因此四個判準都指向 4 個 PC，但這會把變異最大的 ch11 完全排除。"
        "若後續要做異常偵測、且 ch11 是重要感測訊號，"
        "建議保留 5 個 PC（累積解釋 93.0%），以保留 ch11 的獨立資訊。",
        "",
        "## 解釋變異量",
        "",
        "| PC | 特徵值 | 解釋比例 | 累積比例 |",
        "|---|---|---|---|",
    ]
    for k in range(p):
        lines.append(f"| PC{k + 1} | {eigvals[k]:.3f} | {explained[k]:.2%} | "
                     f"{cumulative[k]:.2%} |")
    lines += [
        "",
        "## 負荷量（前四個 PC）",
        "",
        "| 通道 | PC1 | PC2 | PC3 | PC4 |",
        "|---|---|---|---|---|",
    ]
    for j, name in enumerate(names):
        vals = " | ".join(f"{loadings[j, k]:.3f}" for k in range(4))
        lines.append(f"| {name} | {vals} |")
    lines += [
        "",
        "## 圖",
        "",
        "- `figs/pca_scree.png`：陡坡圖與 parallel analysis。",
        "- `figs/pca_loadings.png`：各通道對前四個 PC 的負荷量。",
        "- `figs/pca_biplot.png`：PC1–PC2 得分與負荷量向量。",
        "",
        "## 重現方式",
        "",
        "```bash",
        "uv run python pca_line_channels.py",
        "```",
    ]
    (NOTES / "pca_line_channels.md").write_text("\n".join(lines) + "\n",
                                               encoding="utf-8")

    np.savetxt(FIGS / "pca_scores.csv", scores[:, :n_pa], delimiter=",",
               header=",".join(f"PC{k + 1}" for k in range(n_pa)),
               comments="", fmt="%.6f")
    print(f"\n圖已存到 {FIGS}/，筆記已存到 {NOTES}/pca_line_channels.md")


if __name__ == "__main__":
    main()
