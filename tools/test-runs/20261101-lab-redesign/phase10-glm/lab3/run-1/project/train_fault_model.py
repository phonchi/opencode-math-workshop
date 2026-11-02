import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_recall_curve, RocCurveDisplay,
)

df = pd.read_csv("data/line_faults.csv")
X = df.drop(columns=["record_id", "fault"])
y = df["fault"]

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

clf = RandomForestClassifier(
    n_estimators=500, class_weight="balanced", random_state=42, n_jobs=-1
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_res = cross_validate(
    clf, X_tr, y_tr, cv=cv,
    scoring=["roc_auc", "average_precision", "recall", "precision"],
)
print("=== 5-fold CV (train) ===")
for m in ["test_roc_auc", "test_average_precision", "test_recall", "test_precision"]:
    print(f"{m}: {cv_res[m].mean():.3f} +/- {cv_res[m].std():.3f}")

clf.fit(X_tr, y_tr)
y_pred = clf.predict(X_te)
y_prob = clf.predict_proba(X_te)[:, 1]

print("\n=== Holdout test ===")
print(classification_report(y_te, y_pred, digits=3))
print("Confusion matrix:")
print(confusion_matrix(y_te, y_pred))

fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
RocCurveDisplay.from_predictions(y_te, y_prob, ax=axes[0])
axes[0].set_title("ROC curve (holdout)")

prec, rec, thr = precision_recall_curve(y_te, y_prob)
axes[1].plot(rec, prec)
axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
axes[1].set_title("Precision-Recall curve (holdout)")
axes[1].grid(alpha=0.3)

imp = pd.Series(clf.feature_importances_, index=X.columns).sort_values()
axes[2].barh(imp.index, imp.values)
axes[2].set_title("Feature importance")
plt.tight_layout()
plt.savefig("figs/fault_model_eval.png", dpi=150)
print("\nSaved figs/fault_model_eval.png")

# 在低誤報成本下掃 threshold，提供上線建議
print("\n=== Threshold sweep (holdout) ===")
print(f"{'thr':>5} {'precision':>10} {'recall':>8} {'#alerts':>8}")
for t in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
    pred = (y_prob >= t).astype(int)
    tp = int(((pred == 1) & (y_te == 1)).sum())
    fp = int(((pred == 1) & (y_te == 0)).sum())
    fn = int(((pred == 0) & (y_te == 1)).sum())
    p = tp / (tp + fp) if tp + fp else 0
    r = tp / (tp + fn) if tp + fn else 0
    print(f"{t:>5} {p:>10.3f} {r:>8.3f} {tp + fp:>8}")
