import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve, f1_score

df = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase10-gemini/lab3-1/project/data/line_faults.csv')
X = df.drop(columns=['record_id', 'fault'])
y = df['fault']

# Test with class_weight='balanced'
clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

y_proba_cv = cross_val_predict(clf, X, y, cv=cv, method='predict_proba')[:, 1]

# Find best threshold maximizing F1-score
precisions, recalls, thresholds = precision_recall_curve(y, y_proba_cv)
f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
best_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
best_f1 = f1_scores[best_idx]

print(f"Best Threshold: {best_threshold:.4f}")
print(f"Best F1-score: {best_f1:.4f}")

y_pred_tuned = (y_proba_cv >= best_threshold).astype(int)
print("\nClassification Report (Balanced + Tuned Threshold):")
print(classification_report(y, y_pred_tuned))
print("ROC-AUC:", roc_auc_score(y, y_proba_cv))
