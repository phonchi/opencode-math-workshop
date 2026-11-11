"""Compare k-means clusterings without using shop identities."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "shops_daily.csv"
FIGURE_PATH = ROOT / "figs" / "lab1_k_selection.png"


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    if data.empty or not all(pd.api.types.is_numeric_dtype(t) for t in data.dtypes):
        raise ValueError("Input must contain rows and only numeric columns.")
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError("Input contains missing or non-finite values; no imputation is applied.")
    if len(data) <= 12:
        raise ValueError("At least 13 rows are required to evaluate k=2 through 12.")

    # Population standard deviation, matching StandardScaler's convention.
    std = data.std(ddof=0)
    dropped = std.index[std == 0].tolist()
    features = data.drop(columns=dropped)
    if features.empty:
        raise ValueError("All columns have zero standard deviation.")
    scaled = StandardScaler().fit_transform(features)

    print(f"Rows: {len(data)}")
    print(f"Dropped zero-standard-deviation columns: {', '.join(dropped) or '(none)'}")
    print(f"Features used: {', '.join(features.columns)}")
    print("\nk  silhouette  Calinski-Harabasz  Davies-Bouldin  cluster sizes (label:count)")

    results = []
    for k in range(2, 13):
        labels = KMeans(n_clusters=k, random_state=0, n_init=10).fit_predict(scaled)
        if np.unique(labels).size != k:
            raise ValueError(f"k={k} produced fewer than {k} distinct clusters.")
        silhouette = silhouette_score(scaled, labels)
        calinski = calinski_harabasz_score(scaled, labels)
        davies = davies_bouldin_score(scaled, labels)
        counts = np.bincount(labels, minlength=k)
        results.append((k, silhouette, calinski, davies))
        sizes = ", ".join(f"{i}:{count}" for i, count in enumerate(counts))
        print(f"{k:2d}  {silhouette:10.4f}  {calinski:17.2f}  {davies:14.4f}  {sizes}")

    scores = pd.DataFrame(
        results, columns=["k", "silhouette", "calinski_harabasz", "davies_bouldin"]
    )
    print("\nBest k by metric (ties resolved toward smaller k):")
    print(f"  Silhouette (higher): {scores.loc[scores.silhouette.idxmax(), 'k']}")
    print(f"  Calinski-Harabasz (higher): {scores.loc[scores.calinski_harabasz.idxmax(), 'k']}")
    print(f"  Davies-Bouldin (lower): {scores.loc[scores.davies_bouldin.idxmin(), 'k']}")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, column, title in zip(
        axes,
        ("silhouette", "calinski_harabasz", "davies_bouldin"),
        ("Silhouette (higher is better)", "Calinski-Harabasz (higher is better)",
         "Davies-Bouldin (lower is better)"),
    ):
        ax.plot(scores["k"], scores[column], marker="o")
        ax.set_title(title)
        ax.set_xlabel("Number of clusters (k)")
        ax.set_ylabel(column.replace("_", " ").title())
        ax.set_xticks(scores["k"])
        ax.grid(alpha=0.3)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PATH, dpi=160)
    plt.close(fig)
    print(f"\nFigure saved: {FIGURE_PATH}")


if __name__ == "__main__":
    main()
