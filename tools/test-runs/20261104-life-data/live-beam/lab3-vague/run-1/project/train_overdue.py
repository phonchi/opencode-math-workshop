import csv, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score,
    precision_score, recall_score, confusion_matrix, RocCurveDisplay, PrecisionRecallDisplay)

rows = list(csv.DictReader(open("data/loans.csv")))
feat_names = ["pages", "past_ontime_pct", "past_avg_days", "commute_min", "account_age_days", "book_age_years"]
X = np.array([[float(r[k]) for k in feat_names] for r in rows])
y = np.array([int(r["overdue"]) for r in rows])
X[:, 1] = np.clip(X[:, 1], 0, 100)

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
pred = (proba >= 0.5).astype(int)
tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
metrics = {
    "n": len(y), "positives": int(y.sum()), "base_rate": float(y.mean()),
    "auc": float(roc_auc_score(y, proba)),
    "avg_precision": float(average_precision_score(y, proba)),
    "precision": float(precision_score(y, pred, zero_division=0)),
    "recall": float(recall_score(y, pred, zero_division=0)),
    "f1": float(f1_score(y, pred, zero_division=0)),
    "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
}
print(metrics)

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
model.fit(Xtr, ytr)
pte = model.predict_proba(Xte)[:, 1]
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
RocCurveDisplay.from_predictions(yte, pte, ax=ax[0])
PrecisionRecallDisplay.from_predictions(yte, pte, ax=ax[1])
fig.tight_layout()
fig.savefig("figs/overdue_eval.png", dpi=150)
plt.close(fig)
