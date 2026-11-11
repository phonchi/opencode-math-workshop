"""Train a loan-overdue logistic model and evaluate reminder thresholds."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
TRAIN_PATH = ROOT / "data" / "loans.csv"
NEW_PATH = ROOT / "data" / "loans_new_batch.csv"
TARGET = "overdue"
ID_COLUMN = "case_no"
THRESHOLDS = (0.5, 0.3, 0.2, 0.1, 0.05)
REMINDER_RATE_LIMIT = 40 / 300


def main() -> None:
    train = pd.read_csv(TRAIN_PATH)
    new = pd.read_csv(NEW_PATH)

    if TARGET not in train or TARGET not in new:
        raise ValueError(f"Both files must contain the '{TARGET}' label.")
    if list(train.columns) != list(new.columns):
        raise ValueError("Training and new-batch columns do not match.")

    features = [column for column in train.columns if column not in {ID_COLUMN, TARGET}]
    if not features:
        raise ValueError("No predictor columns remain after excluding ID and target.")
    if not all(pd.api.types.is_numeric_dtype(train[column]) for column in features):
        raise ValueError("All predictor columns must be numeric.")
    if train[TARGET].isna().any() or new[TARGET].isna().any():
        raise ValueError("Target labels must not be missing.")
    if set(train[TARGET].unique()) != {0, 1} or set(new[TARGET].unique()) != {0, 1}:
        raise ValueError("The target must contain binary values 0 and 1 in both files.")

    X_train = train[features]
    y_train = train[TARGET].astype(int)
    X_new = new[features]
    y_new = new[TARGET].astype(int)

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "logistic",
                LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000),
            ),
        ]
    )
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_new)[:, 1]

    n = len(new)
    capacity = int(np.floor(n * REMINDER_RATE_LIMIT))
    print(f"訓練資料：{len(train)} 筆；逾期 {int(y_train.sum())} 筆")
    print(f"新批次：{n} 筆；實際逾期 {int(y_new.sum())} 筆")
    print(f"特徵：{', '.join(features)}")
    print(f"門檻提醒量上限（按 40/300 比例換算並取整）：{capacity} 封")
    print("\n門檻\t提醒數\t抓到(TP)\t漏掉(FN)\t白提醒(FP)\t符合上限")

    for threshold in THRESHOLDS:
        predicted = probabilities >= threshold
        true_positive = int((predicted & (y_new.to_numpy() == 1)).sum())
        false_negative = int((~predicted & (y_new.to_numpy() == 1)).sum())
        false_positive = int((predicted & (y_new.to_numpy() == 0)).sum())
        alerts = int(predicted.sum())
        within_limit = alerts <= capacity
        print(
            f"{threshold:.2f}\t{alerts}\t{true_positive}\t\t{false_negative}"
            f"\t\t{false_positive}\t\t{'是' if within_limit else '否'}"
        )

    print("\n欄位檢查：")
    print(f"丟棄欄位：{ID_COLUMN}（識別碼）、{TARGET}（目標標籤，不作特徵）")
    print(f"訓練特徵缺值：{int(X_train.isna().sum().sum())}；新批次特徵缺值：{int(X_new.isna().sum().sum())}")


if __name__ == "__main__":
    main()
