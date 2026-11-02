import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve

# Load data
df = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase10-gemini/lab3-1/project/data/line_faults.csv')
print("Dataset shape:", df.shape)
print("Class distribution:\n", df['fault'].value_counts(normalize=True))

X = df.drop(columns=['record_id', 'fault'])
y = df['fault']

# Model training & CV
clf = RandomForestClassifier(n_estimators=100, random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

y_pred_cv = cross_val_predict(clf, X, y, cv=cv)
y_proba_cv = cross_val_predict(clf, X, y, cv=cv, method='predict_proba')[:, 1]

print("\nClassification Report (Cross-Validation):")
print(classification_report(y, y_pred_cv))

auc = roc_auc_score(y, y_proba_cv)
print(f"ROC-AUC: {auc:.4f}")

# Train on full data for feature importance
clf.fit(X, y)
importances = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nFeature Importances:")
print(importances)

# Plotting
os.makedirs('figs', exist_ok=True)
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
fpr, tpr, _ = roc_curve(y, y_proba_cv)
plt.plot(fpr, tpr, label=f'ROC AUC = {auc:.3f}', color='blue')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()

plt.subplot(1, 2, 2)
importances.plot(kind='barh', color='skyblue')
plt.xlabel('Importance')
plt.title('Feature Importance')
plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig('/home/phonchi/.cache/oc-lab-redesign/runs/phase10-gemini/lab3-1/project/figs/fault_model_eval.png', dpi=300)
print("\nPlot saved to figs/fault_model_eval.png")
