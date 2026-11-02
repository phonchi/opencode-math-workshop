import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score

df_channels = pd.read_csv('data/line_channels.csv')
df_fault = pd.read_csv('data/line_channels_fault.csv')

X = df_channels.values
y = df_fault['fault'].values

# Check explained variance ratio on full data (or per fold)
scaler_full = StandardScaler()
X_scaled_full = scaler_full.fit_transform(X)
for k in [3, 4, 5]:
    pca_full = PCA(n_components=k, random_state=42)
    pca_full.fit(X_scaled_full)
    print(f"k={k}: Explained variance ratio sum = {np.sum(pca_full.explained_variance_ratio_):.4f}, individual = {pca_full.explained_variance_ratio_}")

# CV evaluation of classifiers on PCA features
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
models = {
    'LogisticRegression': LogisticRegression(random_state=42),
    'RandomForest': RandomForestClassifier(random_state=42),
    'GradientBoosting': GradientBoostingClassifier(random_state=42),
    'SVM': SVC(probability=True, random_state=42)
}

results = {name: {k: [] for k in [3, 4, 5]} for name in models}

for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    for k in [3, 4, 5]:
        pca = PCA(n_components=k, random_state=42)
        X_train_pca = pca.fit_transform(X_train_scaled)
        X_test_pca = pca.transform(X_test_scaled)
        
        for name, clf in models.items():
            clf.fit(X_train_pca, y_train)
            y_pred = clf.predict_proba(X_test_pca)[:, 1]
            try:
                auc = roc_auc_score(y_test, y_pred)
            except:
                auc = np.nan
            results[name][k].append(auc)

print("\n=== Supervised Classifier AUC on PCA Features (CV) ===")
for name in models:
    print(f"\n--- Model: {name} ---")
    for k in [3, 4, 5]:
        mean_auc = np.mean(results[name][k])
        std_auc = np.std(results[name][k])
        print(f"k={k}: AUC = {mean_auc:.4f} +/- {std_auc:.4f}")
