import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve
)

# Create figs directory if not exists
os.makedirs("figs", exist_ok=True)
os.makedirs("notes", exist_ok=True)

# 1. Load data
df = pd.read_csv("data/line_faults.csv")
print("Dataset shape:", df.shape)

# Drop record_id
X = df.drop(columns=['record_id', 'fault'])
y = df['fault']

print("Feature columns:", X.columns.tolist())
print(f"Class distribution: Normal (0) = {(y==0).sum()}, Fault (1) = {(y==1).sum()}, Ratio = {y.mean():.4f}")

# Train/Test split for final evaluation
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_full)
X_test_scaled = scaler.transform(X_test)

# 2. Define models
pos_weight = (y_train_full == 0).sum() / (y_train_full == 1).sum()

models = {
    "Logistic Regression": LogisticRegression(class_weight='balanced', random_state=42),
    "Random Forest": RandomForestClassifier(class_weight='balanced', n_estimators=200, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "XGBoost": XGBClassifier(scale_pos_weight=pos_weight, random_state=42, eval_metric='logloss')
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_results = {}
for name, model in models.items():
    aucs = []
    f1s = []
    recalls = []
    precisions = []
    
    for train_idx, val_idx in cv.split(X_train_full, y_train_full):
        X_tr, X_val = X_train_scaled[train_idx], X_train_scaled[val_idx]
        y_tr, y_val = y_train_full.iloc[train_idx], y_train_full.iloc[val_idx]
        
        # For tree models, unscaled is often fine, but using scaled for consistency or model-specific
        if name in ["Random Forest", "Gradient Boosting", "XGBoost"]:
            # tree models don't strictly need scaling, but let's use unscaled for trees if preferred, or scaled.
            # Let's use unscaled original for trees
            X_tr_t = X_train_full.iloc[train_idx]
            X_val_t = X_train_full.iloc[val_idx]
            model.fit(X_tr_t, y_tr)
            preds = model.predict(X_val_t)
            probs = model.predict_proba(X_val_t)[:, 1]
        else:
            model.fit(X_tr, y_tr)
            preds = model.predict(X_val)
            probs = model.predict_proba(X_val)[:, 1]
            
        aucs.append(roc_auc_score(y_val, probs))
        f1s.append(f1_score(y_val, preds, zero_division=0))
        recalls.append(recall_score(y_val, preds, zero_division=0))
        precisions.append(precision_score(y_val, preds, zero_division=0))
        
    cv_results[name] = {
        "ROC-AUC": np.mean(aucs),
        "F1": np.mean(f1s),
        "Recall": np.mean(recalls),
        "Precision": np.mean(precisions)
    }

print("\n--- Cross-Validation Results ---")
for name, res in cv_results.items():
    print(f"{name}: ROC-AUC={res['ROC-AUC']:.4f}, F1={res['F1']:.4f}, Recall={res['Recall']:.4f}, Precision={res['Precision']:.4f}")

# Select best model based on ROC-AUC or F1
best_model_name = max(cv_results, key=lambda k: cv_results[k]['ROC-AUC'])
print(f"\nBest Model by ROC-AUC: {best_model_name}")

# Train best model on full train set and evaluate on test set
best_model = models[best_model_name]
if best_model_name in ["Random Forest", "Gradient Boosting", "XGBoost"]:
    best_model.fit(X_train_full, y_train_full)
    test_preds = best_model.predict(X_test)
    test_probs = best_model.predict_proba(X_test)[:, 1]
else:
    best_model.fit(X_train_scaled, y_train_full)
    test_preds = best_model.predict(X_test_scaled)
    test_probs = best_model.predict_proba(X_test_scaled)[:, 1]

print(f"\n--- Test Set Evaluation ({best_model_name}) ---")
print("Accuracy:", accuracy_score(y_test, test_preds))
print("Precision:", precision_score(y_test, test_preds, zero_division=0))
print("Recall:", recall_score(y_test, test_preds, zero_division=0))
print("F1-score:", f1_score(y_test, test_preds, zero_division=0))
print("ROC-AUC:", roc_auc_score(y_test, test_probs))
print("PR-AUC:", average_precision_score(y_test, test_probs))

# Confusion Matrix
cm = confusion_matrix(y_test, test_preds)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Normal (0)', 'Fault (1)'],
            yticklabels=['Normal (0)', 'Fault (1)'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title(f'Confusion Matrix - {best_model_name}')
plt.tight_layout()
plt.savefig('figs/confusion_matrix.png', dpi=300)
plt.close()

# ROC Curve
plt.figure(figsize=(6, 5))
for name, model in models.items():
    if name in ["Random Forest", "Gradient Boosting", "XGBoost"]:
        probs = model.predict_proba(X_test)[:, 1]
    else:
        probs = model.predict_proba(X_test_scaled)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, probs)
    auc_val = roc_auc_score(y_test, probs)
    plt.plot(fpr, tpr, label=f'{name} (AUC = {auc_val:.3f})')

plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('figs/roc_curves.png', dpi=300)
plt.close()

# Precision-Recall Curve
plt.figure(figsize=(6, 5))
for name, model in models.items():
    if name in ["Random Forest", "Gradient Boosting", "XGBoost"]:
        probs = model.predict_proba(X_test)[:, 1]
    else:
        probs = model.predict_proba(X_test_scaled)[:, 1]
    precision_vals, recall_vals, _ = precision_recall_curve(y_test, probs)
    ap_val = average_precision_score(y_test, probs)
    plt.plot(recall_vals, precision_vals, label=f'{name} (AP = {ap_val:.3f})')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curves')
plt.legend(loc='lower left')
plt.tight_layout()
plt.savefig('figs/pr_curves.png', dpi=300)
plt.close()

# Feature Importance (if tree-based)
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feat_imp = pd.Series(importances, index=X.columns).sort_values(ascending=True)
    plt.figure(figsize=(8, 5))
    feat_imp.plot(kind='barh', color='skyblue')
    plt.title(f'Feature Importance - {best_model_name}')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig('figs/feature_importance.png', dpi=300)
    plt.close()
