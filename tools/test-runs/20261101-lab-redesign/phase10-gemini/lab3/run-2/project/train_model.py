import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, auc, f1_score, precision_score, recall_score
)

# Ensure output directories exist
os.makedirs('figs', exist_ok=True)
os.makedirs('notes', exist_ok=True)

# Load data
df = pd.read_csv('data/line_faults.csv')
print(f"Dataset shape: {df.shape}")
print(f"Fault distribution:\n{df['fault'].value_counts(normalize=True)}")

X = df.drop(columns=['record_id', 'fault'])
y = df['fault']
feature_names = X.columns.tolist()

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Models
models = {
    'Logistic Regression': LogisticRegression(class_weight='balanced', random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(random_state=42)
}

results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\n--- Cross-Validation Evaluation ---")
for name, model in models.items():
    auc_scores = []
    f1_scores = []
    precision_scores = []
    recall_scores = []
    
    for train_idx, val_idx in cv.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
        
        # Use scaled for LR, unscaled for tree models
        if name == 'Logistic Regression':
            s = StandardScaler()
            X_tr_s = s.fit_transform(X_tr)
            X_val_s = s.transform(X_val)
            model.fit(X_tr_s, y_tr)
            y_pred = model.predict(X_val_s)
            y_prob = model.predict_proba(X_val_s)[:, 1]
        else:
            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_val)
            y_prob = model.predict_proba(X_val)[:, 1]
            
        auc_scores.append(roc_auc_score(y_val, y_prob))
        f1_scores.append(f1_score(y_val, y_pred, zero_division=0))
        precision_scores.append(precision_score(y_val, y_pred, zero_division=0))
        recall_scores.append(recall_score(y_val, y_pred, zero_division=0))
        
    results[name] = {
        'ROC-AUC': np.mean(auc_scores),
        'F1': np.mean(f1_scores),
        'Precision': np.mean(precision_scores),
        'Recall': np.mean(recall_scores)
    }
    print(f"{name}: ROC-AUC={np.mean(auc_scores):.4f}, F1={np.mean(f1_scores):.4f}, Precision={np.mean(precision_scores):.4f}, Recall={np.mean(recall_scores):.4f}")

# Holdout evaluation & plotting ROC / PR curves
plt.figure(figsize=(10, 8))
plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')

holdout_metrics = {}
for name, model in models.items():
    if name == 'Logistic Regression':
        model.fit(X_train_scaled, y_train)
        y_prob = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = model.predict(X_test)
        
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    test_auc = roc_auc_score(y_test, y_prob)
    plt.plot(fpr, tpr, label=f'{name} (AUC = {test_auc:.4f})')
    
    holdout_metrics[name] = {
        'ROC-AUC': test_auc,
        'F1': f1_score(y_test, y_pred, zero_division=0),
        'Precision': precision_score(y_test, y_pred, zero_division=0),
        'Recall': recall_score(y_test, y_pred, zero_division=0)
    }

plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curves (Test Set)', fontsize=14)
plt.legend(loc='lower right', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('figs/roc_curves.png', dpi=300)
plt.close()

# Feature Importance Plot (using Random Forest)
rf_model = models['Random Forest']
rf_model.fit(X_train, y_train)
importances = rf_model.feature_importances_
indices = np.argsort(importances)

plt.figure(figsize=(8, 6))
plt.title('Random Forest Feature Importances', fontsize=14)
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
plt.xlabel('Relative Importance', fontsize=12)
plt.tight_layout()
plt.savefig('figs/feature_importance.png', dpi=300)
plt.close()

print("\n--- Holdout Test Set Evaluation ---")
for name, m in holdout_metrics.items():
    print(f"{name}: ROC-AUC={m['ROC-AUC']:.4f}, F1={m['F1']:.4f}, Precision={m['Precision']:.4f}, Recall={m['Recall']:.4f}")
