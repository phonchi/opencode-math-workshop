import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    average_precision_score, roc_curve, precision_recall_curve
)
import os

os.makedirs('figs', exist_ok=True)
os.makedirs('notes', exist_ok=True)

# 1. Load data
df = pd.read_csv('data/line_faults.csv')
X = df.drop(columns=['record_id', 'fault'])
y = df['fault']

print(f"Data shape: {X.shape}, Positive ratio: {y.mean():.4f}")

# 2. Train-test split (Stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Models to evaluate
models = {
    'Logistic Regression': LogisticRegression(class_weight='balanced', random_state=42),
    'Random Forest': RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42),
    'Hist Gradient Boosting': HistGradientBoostingClassifier(random_state=42)
}

results = {}

plt.figure(figsize=(12, 5))

# Plot ROC curves
plt.subplot(1, 2, 1)
for name, model in models.items():
    if 'Logistic' in name:
        model.fit(X_train_scaled, y_train)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    auc = roc_auc_score(y_test, y_pred_proba)
    ap = average_precision_score(y_test, y_pred_proba)
    results[name] = {'auc': auc, 'ap': ap, 'model': model}
    
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.plot(fpr, tpr, label=f'{name} (AUC = {auc:.3f})')

plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves')
plt.legend()

# Plot PR curves
plt.subplot(1, 2, 2)
for name, model in models.items():
    if 'Logistic' in name:
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    plt.plot(recall, precision, label=f'{name} (AP = {results[name]["ap"]:.3f})')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curves')
plt.legend()

plt.tight_layout()
plt.savefig('figs/roc_pr_curves.png', dpi=300)
plt.close()

print("\nModel Evaluation Results:")
for name, res in results.items():
    print(f"--- {name} ---")
    print(f"ROC-AUC: {res['auc']:.4f}")
    print(f"PR-AUC (AP): {res['ap']:.4f}")
    
    if 'Logistic' in name:
        y_pred = res['model'].predict(X_test_scaled)
    else:
        y_pred = res['model'].predict(X_test)
    print(classification_report(y_test, y_pred))

# Detailed Confusion Matrix for Random Forest (best tree model)
best_model_name = max(results, key=lambda k: results[k]['auc'])
best_model = results[best_model_name]['model']
print(f"\nBest Model by ROC-AUC: {best_model_name}")

if 'Logistic' in best_model_name:
    y_pred_best = best_model.predict(X_test_scaled)
else:
    y_pred_best = best_model.predict(X_test)

cm = confusion_matrix(y_test, y_pred_best)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Normal (0)', 'Fault (1)'],
            yticklabels=['Normal (0)', 'Fault (1)'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title(f'Confusion Matrix ({best_model_name})')
plt.savefig('figs/confusion_matrix.png', dpi=300)
plt.close()

# Feature Importance (Random Forest)
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    features = X.columns
    fi_df = pd.DataFrame({'feature': features, 'importance': importances}).sort_values('importance', ascending=False)
    
    plt.figure(figsize=(8, 5))
    sns.barplot(x='importance', y='feature', data=fi_df, palette='viridis')
    plt.title(f'Feature Importance ({best_model_name})')
    plt.tight_layout()
    plt.savefig('figs/feature_importance.png', dpi=300)
    plt.close()
    print("\nFeature Importances:")
    print(fi_df)
elif hasattr(best_model, 'coef_'):
    importances = np.abs(best_model.coef_[0])
    features = X.columns
    fi_df = pd.DataFrame({'feature': features, 'importance': importances}).sort_values('importance', ascending=False)
    
    plt.figure(figsize=(8, 5))
    sns.barplot(x='importance', y='feature', data=fi_df, palette='viridis')
    plt.title(f'Feature Coefficients (Abs) ({best_model_name})')
    plt.tight_layout()
    plt.savefig('figs/feature_importance.png', dpi=300)
    plt.close()
    print("\nFeature Importances (Coefficients):")
    print(fi_df)
