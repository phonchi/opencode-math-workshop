import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score

df_channels = pd.read_csv('data/line_channels.csv')
df_fault = pd.read_csv('data/line_channels_fault.csv')

X = df_channels.values
y = df_fault['fault'].values

def compute_pca_monitoring_stats(X_train_scaled, X_test_scaled, pca, k):
    # Train stats for T^2
    # PCA components and singular values / explained variance
    # Explained variance of each PC: pca.explained_variance_ (which are lambda_i)
    # T^2 = sum_{i=1}^k (t_i^2 / lambda_i)
    
    # Transform test set
    X_test_pca = pca.transform(X_test_scaled) # shape (n_test, k)
    lambda_i = pca.explained_variance_ # shape (k,)
    
    # T^2 statistic
    T2 = np.sum((X_test_pca ** 2) / lambda_i, axis=1)
    
    # Q statistic (SPE): sum of squared residuals
    X_test_recon = pca.inverse_transform(X_test_pca)
    Q = np.sum((X_test_scaled - X_test_recon) ** 2, axis=1)
    
    return T2, Q

def run_cv(n_components_list=[3, 4, 5], n_splits=5):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    results = {
        k: {'T2': [], 'Q': [], 'T2_Q': []} for k in n_components_list
    }
    
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
            pca.fit(X_train_scaled)
            
            T2, Q = compute_pca_monitoring_stats(X_train_scaled, X_test_scaled, pca, k)
            
            # Normalize T2 and Q for combination if desired, or test individually
            # To combine T2 and Q, min-max or standardization based on training set or test set
            # Let's compute AUC for T2, Q, and simple sum of standardized T2 and Q
            
            # For combination, let's standardize T2 and Q using training fold statistics
            X_train_pca = pca.transform(X_train_scaled)
            lambda_i = pca.explained_variance_
            T2_train = np.sum((X_train_pca ** 2) / lambda_i, axis=1)
            X_train_recon = pca.inverse_transform(X_train_pca)
            Q_train = np.sum((X_train_scaled - X_train_recon) ** 2, axis=1)
            
            t2_mean, t2_std = np.mean(T2_train), np.std(T2_train)
            q_mean, q_std = np.mean(Q_train), np.std(Q_train)
            
            T2_norm = (T2 - t2_mean) / (t2_std + 1e-8)
            Q_norm = (Q - q_mean) / (q_std + 1e-8)
            T2_Q_combined = T2_norm + Q_norm
            
            auc_t2 = roc_auc_score(y_test, T2)
            auc_q = roc_auc_score(y_test, Q)
            auc_comb = roc_auc_score(y_test, T2_Q_combined)
            
            results[k]['T2'].append(auc_t2)
            results[k]['Q'].append(auc_q)
            results[k]['T2_Q'].append(auc_comb)
            
    print("=== PCA Fault Monitoring AUC Results (Cross-Validation) ===")
    for k in n_components_list:
        print(f"\n--- k = {k} ---")
        print(f"Hotelling's T^2 AUC: {np.mean(results[k]['T2']):.4f} +/- {np.std(results[k]['T2']):.4f}")
        print(f"Q-statistic (SPE) AUC: {np.mean(results[k]['Q']):.4f} +/- {np.std(results[k]['Q']):.4f}")
        print(f"Combined (T^2 + Q) AUC: {np.mean(results[k]['T2_Q']):.4f} +/- {np.std(results[k]['T2_Q']):.4f}")

if __name__ == '__main__':
    run_cv()
