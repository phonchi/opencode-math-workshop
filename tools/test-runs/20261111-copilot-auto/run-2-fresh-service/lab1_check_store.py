"""Evaluate the previously selected k=9 clustering against store labels."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent


def main() -> None:
    data = pd.read_csv(ROOT / "data" / "shops_daily.csv")
    stores = pd.read_csv(ROOT / "data" / "shops_daily_store.csv")
    if len(data) != len(stores):
        raise ValueError("The two files have different row counts and cannot be aligned by position.")
    if "store" not in stores or stores["store"].isna().any():
        raise ValueError("The store column is missing or contains missing values.")
    if not all(pd.api.types.is_numeric_dtype(t) for t in data.dtypes):
        raise ValueError("Input features must be numeric.")
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError("Input features must not contain missing or non-finite values.")

    features = data.loc[:, data.std(ddof=0) != 0]
    scaled = StandardScaler().fit_transform(features)
    labels = KMeans(n_clusters=9, random_state=0, n_init=10).fit_predict(scaled)

    # Store labels are used only after clustering, aligned by CSV row order.
    ari = adjusted_rand_score(stores["store"], labels)
    counts = pd.crosstab(labels, stores["store"]).rename_axis(index="cluster")
    counts["total"] = counts.sum(axis=1)
    print(f"Rows: {len(data)}; distinct stores: {stores['store'].nunique()}")
    print(f"Adjusted Rand index: {ari:.6f}")
    print("\nDays by cluster and store (aligned by row order):")
    print(counts.to_string())


if __name__ == "__main__":
    main()
