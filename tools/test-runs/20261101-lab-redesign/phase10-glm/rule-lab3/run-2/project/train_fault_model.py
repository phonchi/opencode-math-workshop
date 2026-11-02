import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score, roc_auc_score, precision_recall_curve, confusion_matrix
)

df = pd.read_csv("data/line_faults.csv")
X = df.drop(columns=["record_id", "fault"])
y = df["fault"]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models = {
    "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, class_weight="balanced")),
    "RandomForest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42),
}

results = {}
for name, model in models.items():
    proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    results[name] = proba
    print(f"{name}: PR-AUC={average_precision_score(y, proba):.3f}  ROC-AUC={roc_auc_score(y, proba):.3f}")

# 取表現較好者畫圖，並以 recall 優先挑 threshold（故障偵測寧可誤報）
best = max(results, key=lambda k: average_precision_score(y, results[k]))
proba = results[best]
prec, rec, thr = precision_recall_curve(y, proba)
# 找 recall >= 0.9 中 precision 最高的 threshold
mask = rec[:-1] >= 0.9
t = thr[mask][np.argmax(prec[:-1][mask])] if mask.any() else 0.5
pred = (proba >= t).astype(int)
tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
print(f"\nbest={best}, threshold={t:.3f}  TP={tp} FP={fp} FN={fn} TN={tn}")
print(f"recall={tp/(tp+fn):.3f} precision={tp/(tp+fp):.3f}  誤報率={fp/(tn+fp):.3f}")

rf = models["RandomForest"].fit(X, y)
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values()
plt.figure(figsize=(7, 4))
imp.plot.barh()
plt.title("RandomForest feature importance")
plt.tight_layout()
plt.savefig("figs/feature_importance.png")

plt.figure(figsize=(7, 5))
plt.plot(rec, prec, label=best)
for name, p in results.items():
    pr, rc, _ = precision_recall_curve(y, p)
    plt.plot(rc, pr, alpha=0.6, label=name)
plt.xlabel("Recall"); plt.ylabel("Precision"); plt.legend()
plt.title("Precision-Recall (5-fold out-of-fold)")
plt.tight_layout()
plt.savefig("figs/pr_curve.png")
print("\nfigures saved to figs/")
