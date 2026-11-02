import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

# Load data
df_channels = pd.read_csv('data/line_channels.csv')
df_fault = pd.read_csv('data/line_channels_fault.csv')

print("Channels shape:", df_channels.shape)
print("Fault shape:", df_fault.shape)
print("Fault distribution:\n", df_fault['fault'].value_counts(normalize=True))

X = df_channels.values
y = df_fault['fault'].values

# Evaluate 3, 4, 5 components using cross-validation
# We can evaluate:
# 1. PCA reconstruction error (Q-statistic) AUC
# 2. Logistic Regression on PCA features AUC
# 3. Random Forest on PCA features AUC

def evaluate_pca_cv(n_components_list=[3, 4, 5], n_splits=5):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    results_recon = {k: [] for k in n_components_list}
    results_lr = {k: [] for k in n_components_list}
    results_rf = {k: [] for k in n_components_list}
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Preprocessing (StandardScaler) fitted ONLY on train fold
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        for k in n_components_list:
            # PCA fitted ONLY on train fold
            pca = PCA(n_components=k, random_state=42)
            X_train_pca = pca.fit_transform(X_train_scaled)
            X_test_pca = pca.transform(X_test_scaled)
            
            # 1. Reconstruction error (Q-statistic / SPE)
            # Inverse transform X_test_pca back to scaled space
            X_test_recon = pca.inverse_transform(X_test_pca)
            recon_error = np.sum((X_test_scaled - X_test_recon) ** 2, axis=1)
            try:
                auc_recon = roc_auc_score(y_test, recon_error)
            except:
                auc_recon = np.nan
            results_recon[k].append(auc_recon)
            
            # 2. Logistic Regression on PCA features
            lr = LogisticRegression(random_state=42)
            lr.fit(X_train_pca, y_train)
            y_pred_lr = lr.predict_proba(X_test_pca)[:, 1]
            try:
                auc_lr = roc_auc_score(y_test, y_pred_lr)
            except:
                auc_lr = np.nan
            results_lr[k].append(auc_lr)
            
            # 3. Random Forest on PCA features
            rf = RandomForestClassifier(random_state=42)
            rf.fit(X_train_pca, y_train)
            y_pred_rf = rf.predict_proba(X_test_pca)[:, 1]
            try:
                auc_rf = roc_auc_score(y_test, y_pred_rf)
            except:
                auc_rf = np.nan
            results_rf[k].append(auc_rf)
            
    print("--- Reconstruction Error (Q-statistic) AUC ---")
    for k in n_components_list:
        print(f"k={k}: mean AUC = {np.mean(results_recon[k]):.4f} +/- {np.std(results_recon[k]):.4f}")
        
    print("\n--- Logistic Regression on PCA features AUC ---")
    for k in n_components_list:
        print(f"k={k}: mean AUC = {np.mean(results_lr[k]):.4f} +/- {np.std(results_lr[k]):.4f}")

    print("\n--- Random Forest on PCA features AUC ---")
    for k in n_components_list:
        print(f"k={k}: mean AUC = {np.mean(results_rf[k]):.4f} +/- {np.std(results_rf[k]):.4f}")

if __name__ == '__main__':
    evaluate_pca_cv()
