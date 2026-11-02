import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_recall_curve, average_precision_score,
)
import matplotlib.pyplot as plt

df = pd.read_csv("data/line_faults.csv")
X = df.drop(columns=["record_id", "fault"])
y = df["fault"]

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

model = RandomForestClassifier(
    n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1
)

cv = StratifiedKFold(5, shuffle=True, random_state=42)
scoring = ["roc_auc", "average_precision", "recall", "precision"]
cv_res = cross_validate(model, X_tr, y_tr, cv=cv, scoring=scoring)
for s in scoring:
    vals = cv_res[f"test_{s}"]
    print(f"CV {s}: {vals.mean():.3f} ± {vals.std():.3f}")

model.fit(X_tr, y_tr)
proba = model.predict_proba(X_te)[:, 1]

# threshold:抓 recall 為主（漏掉故障代價高），precision 至少 0.5
prec, rec, thr = precision_recall_curve(y_te, proba)
mask = prec[:-1] >= 0.5
best_i = int(mask.argmax())
thr_used = thr[best_i]
pred = (proba >= thr_used).astype(int)

print(f"\nthreshold = {thr_used:.3f}")
print(confusion_matrix(y_te, pred))
print(classification_report(y_te, pred, digits=3))
print(f"holdout AP = {average_precision_score(y_te, proba):.3f}")

print("\nfeature importance:")
for name, imp in sorted(zip(X.columns, model.feature_importances_), key=lambda t: -t[1]):
    print(f"  {name:16s} {imp:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
axes[0].plot(rec, prec)
axes[0].set(xlabel="Recall", ylabel="Precision", title="PR curve (holdout)")
axes[1].barh(list(X.columns), model.feature_importances_)
axes[1].set(title="Feature importance")
plt.tight_layout()
plt.savefig("figs/fault_model_eval.png", dpi=150)
print("saved figs/fault_model_eval.png")
