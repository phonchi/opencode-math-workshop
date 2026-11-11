"""Compare a covariance-eigendecomposition PCA with scikit-learn PCA."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


DATA_PATH = Path(__file__).resolve().parent / "data" / "orders.csv"
N_COMPONENTS = 4
TOL = 1e-10
SCORE_TOL = 1e-9
BUGS = ("none", "ratio_topk", "denom_n", "no_center", "rows")


def manual_pca(X: np.ndarray, n_components: int, bug: str = "none") -> dict[str, np.ndarray]:
    """Center X, then compute PCA from the sample covariance matrix."""
    mean = X.mean(axis=0)
    centered = X - mean
    covariance_input = X if bug == "no_center" else centered
    denominator = len(X) if bug == "denom_n" else len(X) - 1
    covariance = covariance_input.T @ covariance_input / denominator
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    sorted_eigenvectors = eigenvectors[:, order]
    components = (sorted_eigenvectors[:n_components, :] if bug == "rows"
                  else sorted_eigenvectors[:, :n_components].T)
    ratio_denominator = (eigenvalues[:n_components].sum() if bug == "ratio_topk"
                         else np.trace(covariance))
    return {
        "mean": mean,
        "components": components,
        "scores": centered @ components.T,
        "explained_variance": eigenvalues[:n_components],
        "explained_variance_ratio": eigenvalues[:n_components] / ratio_denominator,
    }


def original_checks(manual: dict[str, np.ndarray], reference: PCA,
                    reference_scores: np.ndarray) -> list[tuple[str, float, float]]:
    # Eigenvectors may have opposite signs; align each component before comparison.
    signs = np.sign(np.sum(manual["components"] * reference.components_, axis=1))
    signs[signs == 0] = 1
    aligned_components = manual["components"] * signs[:, None]
    aligned_scores = manual["scores"] * signs[None, :]
    manual_projection = manual["components"].T @ manual["components"]
    reference_projection = reference.components_.T @ reference.components_

    return [
        ("中心點最大絕對誤差", np.max(np.abs(manual["mean"] - reference.mean_)), TOL),
        ("主成分正交性最大絕對誤差", np.max(np.abs(manual["components"] @ manual["components"].T - np.eye(N_COMPONENTS))), TOL),
        ("解釋變異量最大絕對誤差", np.max(np.abs(manual["explained_variance"] - reference.explained_variance_)), TOL),
        ("解釋變異比例最大絕對誤差", np.max(np.abs(manual["explained_variance_ratio"] - reference.explained_variance_ratio_)), TOL),
        ("主成分子空間投影矩陣最大絕對誤差", np.max(np.abs(manual_projection - reference_projection)), TOL),
        ("符號對齊後主成分最大絕對誤差", np.max(np.abs(aligned_components - reference.components_)), TOL),
        ("符號對齊後投影分數最大絕對誤差", np.max(np.abs(aligned_scores - reference_scores)), SCORE_TOL),
    ]

def main() -> None:
    parser = argparse.ArgumentParser(description="比較 PCA 錯誤模式與原本的檢查。")
    parser.add_argument("--bug", choices=BUGS, nargs="+", default=list(BUGS),
                        help="選擇一種或多種模式；預設執行全部。")
    args = parser.parse_args()

    data = pd.read_csv(DATA_PATH)
    if len(data) < N_COMPONENTS:
        raise ValueError(f"At least {N_COMPONENTS} rows are required.")
    if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in data.dtypes):
        raise ValueError("All columns must be numeric; no columns are dropped by type.")
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError("Input contains missing or non-finite values; no imputation is applied.")

    # Divide by population standard deviation only; centering happens inside PCA.
    std = data.std(ddof=0)
    dropped = std.index[std == 0].tolist()
    features = data.drop(columns=dropped)
    if features.shape[1] < N_COMPONENTS:
        raise ValueError(f"At least {N_COMPONENTS} nonconstant columns are required.")
    X = features.to_numpy(dtype=float) / std[features.columns].to_numpy()
    if not np.isfinite(X).all():
        raise ValueError("Scaling produced non-finite values.")

    reference = PCA(n_components=N_COMPONENTS, svd_solver="full")
    reference_scores = reference.fit_transform(X)
    results = [original_checks(manual_pca(X, N_COMPONENTS, bug), reference, reference_scores)
               for bug in args.bug]

    print(f"資料筆數：{len(data)}；使用欄位數：{features.shape[1]}；"
          f"丟掉的零標準差欄位：{', '.join(dropped) if dropped else '無'}")
    print("各欄除以母體標準差（ddof=0），不先減平均；對照組為 sklearn PCA(full)。")
    print("檢查 × 錯誤模式（各格為實際誤差與 PASS/FAIL；誤差須 <= 門檻）")
    print("檢查 | 門檻 | " + " | ".join(args.bug))
    print("--- | --- | " + " | ".join("---" for _ in args.bug))
    for row in zip(*results):
        name, _, threshold = row[0]
        cells = []
        for _, value, _ in row:
            passed = bool(np.isfinite(value) and value <= threshold)
            cells.append(f"{value:.3e} {'PASS' if passed else 'FAIL'}")
        print(f"{name} | {threshold:.3e} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
