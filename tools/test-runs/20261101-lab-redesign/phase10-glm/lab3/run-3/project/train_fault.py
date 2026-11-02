import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix,
                             precision_recall_curve, average_precision_score)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/line_faults.csv")
X = df.drop(columns=["record_id", "fault"])
y = df["fault"]

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

models = {
    "logreg": Pipeline([("sc", StandardScaler()),
                        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))]),
    "rf": Pipeline([("clf", RandomForestClassifier(
        n_estimators=400, class_weight="balanced", random_state=42))]),
}

cv = StratifiedKFold(5, shuffle=True, random_state=42)
for name, m in models.items():
    scores = cross_validate(m, X_tr, y_tr, cv=cv,
                            scoring=["average_precision", "roc_auc", "recall", "precision"])
    print(f"{name}: AP={scores['test_average_precision'].mean():.3f}"
          f" ±{scores['test_average_precision'].std():.3f}"
          f" AUC={scores['test_roc_auc'].mean():.3f}"
          f" rec={scores['test_recall'].mean():.3f}"
          f" prec={scores['test_precision'].mean():.3f}")

m = models["rf"].fit(X_tr, y_tr)
proba = m.predict_proba(X_te)[:, 1]
ap = average_precision_score(y_te, proba)
print("\nTEST AP =", round(ap, 3))
for t in [0.3, 0.5, 0.7]:
    pred = (proba >= t).astype(int)
    print(f"\nthreshold {t}: confusion\n{confusion_matrix(y_te, pred)}")
    print(classification_report(y_te, pred, digits=3, zero_division=0))

imp = pd.Series(m.named_steps["clf"].feature_importances_, index=X.columns)
print("\nfeature importances:\n", imp.sort_values(ascending=False))

# PR 曲線圖
plt.figure(figsize=(6, 5))
for name, mod in models.items():
    p = mod.fit(X_tr, y_tr).predict_proba(X_te)[:, 1]
    prec, rec, _ = precision_recall_curve(y_te, p)
    plt.plot(rec, prec, label=f"{name} (AP={average_precision_score(y_te, p):.3f})")
base = y_te.mean()
plt.axhline(base, ls="--", c="gray", label=f"baseline {base:.3f}")
plt.xlabel("Recall"); plt.ylabel("Precision"); plt.legend()
plt.title("Fault detection PR curve (test set)")
plt.savefig("figs/fault_pr_curve.png", dpi=150, bbox_inches="tight")

# feature importance 圖
plt.figure(figsize=(6, 4))
imp.sort_values().plot(kind="barh")
plt.title("Random Forest feature importance")
plt.tight_layout()
plt.savefig("figs/fault_importance.png", dpi=150)

# 檢查 modes 資料的分布偏移
modes = pd.read_csv("data/line_modes.csv").drop(columns=["firmware_ver", "sample_period_s"])
print("\nmodes vs faults 特徵均值比較：")
print(pd.DataFrame({"faults": X.mean(), "modes": modes.mean()}))
