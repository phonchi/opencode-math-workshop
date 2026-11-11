"""Evaluate complaint AUC using 3, 4, or 5 training-fold PCA components."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
ORDERS_PATH = ROOT / "data" / "orders.csv"
COMPLAINT_PATH = ROOT / "data" / "orders_complaint.csv"
COMPONENTS = (3, 4, 5)
N_SPLITS = 5
RANDOM_STATE = 42
AUC_GAP_THRESHOLD = 0.02


def main() -> None:
    data = pd.read_csv(ORDERS_PATH)
    complaint_data = pd.read_csv(COMPLAINT_PATH)

    if data.empty:
        raise ValueError("orders.csv must contain rows.")
    if len(data) != len(complaint_data):
        raise ValueError(
            "orders.csv and orders_complaint.csv have different row counts; "
            "they cannot be aligned by row order."
        )
    if list(complaint_data.columns) != ["complaint"]:
        raise ValueError("orders_complaint.csv must contain only the 'complaint' column.")
    if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in data.dtypes):
        raise ValueError("All order features must be numeric.")
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError("Order features contain missing or non-finite values.")

    y = complaint_data["complaint"]
    if y.isna().any() or set(y.unique()) != {0, 1}:
        raise ValueError("The complaint label must contain both binary values 0 and 1.")

    # Labels are kept separate from X and used only to stratify folds and score predictions.
    X = data.copy()
    dropped = X.columns[X.std(ddof=0) == 0].tolist()
    if dropped:
        X = X.drop(columns=dropped)
    if X.shape[1] < max(COMPONENTS):
        raise ValueError(f"At least {max(COMPONENTS)} feature columns are required for PCA.")
    if y.value_counts().min() < N_SPLITS:
        raise ValueError("Each complaint class needs at least 5 rows for stratified 5-fold CV.")

    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    fold_results = {n: {"auc": [], "cumulative_variance": []} for n in COMPONENTS}

    for train_index, test_index in cv.split(X, y):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        for n_components in COMPONENTS:
            model = Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    ("pca", PCA(n_components=n_components)),
                    (
                        "logistic",
                        LogisticRegression(
                            solver="lbfgs", C=1.0, max_iter=1000, random_state=RANDOM_STATE
                        ),
                    ),
                ]
            )
            model.fit(X_train, y_train)
            probabilities = model.predict_proba(X_test)[:, 1]
            fold_results[n_components]["auc"].append(roc_auc_score(y_test, probabilities))
            fold_results[n_components]["cumulative_variance"].append(
                model.named_steps["pca"].explained_variance_ratio_.sum()
            )

    print(f"資料筆數：{len(X)}；特徵數：{X.shape[1]}；客訴正例：{int(y.sum())}")
    print(f"丟掉的特徵欄位：{', '.join(dropped) if dropped else '無'}")
    print(f"交叉驗證：分層 {N_SPLITS} 折；AUC 回報各折平均 ± 標準差")
    print("\n主成分數  累積解釋變異（平均 ± 標準差）  AUC（平均 ± 標準差）")

    summary = {}
    for n_components in COMPONENTS:
        variance = np.asarray(fold_results[n_components]["cumulative_variance"])
        auc = np.asarray(fold_results[n_components]["auc"])
        summary[n_components] = {
            "variance": float(variance.mean()),
            "auc": float(auc.mean()),
        }
        print(
            f"{n_components:>5}      "
            f"{variance.mean():.4f} ± {variance.std(ddof=1):.4f}"
            f"                 {auc.mean():.4f} ± {auc.std(ddof=1):.4f}"
        )

    gap = summary[5]["auc"] - summary[4]["auc"]
    print(f"\n5 個減 4 個主成分的 AUC 差：{gap:.4f}")
    if gap > AUC_GAP_THRESHOLD:
        print(
            f"依原主張的門檻（差距嚴格大於 {AUC_GAP_THRESHOLD:.2f}），"
            "4 個主成分的 AUC 低超過 0.02；依你的條件，應撤回主張。"
        )
    else:
        print(
            f"依原主張的門檻（差距未嚴格大於 {AUC_GAP_THRESHOLD:.2f}），"
            "4 個主成分的 AUC 沒有低超過 0.02；依你的條件，不需撤回主張。"
        )


if __name__ == "__main__":
    main()
