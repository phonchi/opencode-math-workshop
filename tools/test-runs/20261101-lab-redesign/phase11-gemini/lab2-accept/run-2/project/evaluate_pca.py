import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy.stats import ttest_rel, wilcoxon

# Load data
X = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/data/line_channels.csv')
y = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/data/line_channels_fault.csv')['fault'].values

print(f"Data shape X: {X.shape}, y shape: {y.shape}")
print(f"Class distribution: {np.bincount(y)}")

# Evaluation methods
# 1. Logistic Regression on PC scores
# 2. Random Forest on PC scores
# 3. PCA reconstruction error (Q statistic) using k components
# 4. T^2 statistic using k components

n_splits = 10
cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

components_list = [3, 4, 5]

results_lr = {k: [] for k in components_list}
results_rf = {k: [] for k in components_list}
results_q = {k: [] for k in components_list}
results_t2 = {k: [] for k in components_list}

for train_idx, test_idx in cv.split(X, y):
    X_train, X_test = X.iloc[train_idx].values, X.iloc[test_idx].values
    y_train, y_test = y[train_idx], y[test_idx]
    
    # Preprocessing: StandardScaler fitted only on train
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    for k in components_list:
        # PCA fitted only on train
        pca = PCA(n_components=k, random_state=42)
        Z_train = pca.fit_transform(X_train_scaled)
        Z_test = pca.transform(X_test_scaled)
        
        # 1. Logistic Regression
        lr = LogisticRegression(random_state=42, max_iter=1000)
        lr.fit(Z_train, y_train)
        y_pred_lr = lr.predict_proba(Z_test)[:, 1]
        auc_lr = roc_auc_score(y_test, y_pred_lr)
        results_lr[k].append(auc_lr)
        
        # 2. Random Forest
        rf = RandomForestClassifier(random_state=42)
        rf.fit(Z_train, y_train)
        y_pred_rf = rf.predict_proba(Z_test)[:, 1]
        auc_rf = roc_auc_score(y_test, y_pred_rf)
        results_rf[k].append(auc_rf)
        
        # 3. PCA Q statistic (reconstruction error)
        # X_reconstructed = Z * W + mean
        X_test_recon = pca.inverse_transform(Z_test)
        q_stat = np.sum((X_test_scaled - X_test_recon) ** 2, axis=1)
        # Q stat can be used directly as anomaly score for AUC
        try:
            auc_q = roc_auc_score(y_test, q_stat)
            # If AUC < 0.5, invert q_stat
            if auc_q < 0.5:
                auc_q = roc_auc_score(y_test, -q_stat)
        except:
            auc_q = 0.5
        results_q[k].append(auc_q)
        
        # 4. T^2 statistic: Z @ inv(Lambda) @ Z.T
        # Lambda is explained variance (eigenvalues)
        eigenvalues = pca.explained_variance_
        t2_stat = np.sum((Z_test ** 2) / eigenvalues, axis=1)
        try:
            auc_t2 = roc_auc_score(y_test, t2_stat)
            if auc_t2 < 0.5:
                auc_t2 = roc_auc_score(y_test, -t2_stat)
        except:
            auc_t2 = 0.5
        results_t2[k].append(auc_t2)

print("\n--- Mean AUC Results over 10-fold CV ---")
for k in components_list:
    print(f"k = {k}:")
    print(f"  Logistic Regression AUC: {np.mean(results_lr[k]):.4f} ± {np.std(results_lr[k]):.4f}")
    print(f"  Random Forest AUC:       {np.mean(results_rf[k]):.4f} ± {np.std(results_rf[k]):.4f}")
    print(f"  PCA Q-statistic AUC:     {np.mean(results_q[k]):.4f} ± {np.std(results_q[k]):.4f}")
    print(f"  PCA T^2-statistic AUC:   {np.mean(results_t2[k]):.4f} ± {np.std(results_t2[k]):.4f}")

print("\n--- Statistical Tests (Paired t-test between k=4 and k=5) ---")
for name, res_dict in [("Logistic Regression", results_lr), ("Random Forest", results_rf), ("Q-stat", results_q), ("T^2-stat", results_t2)]:
    auc_4 = np.array(res_dict[4])
    auc_5 = np.array(res_dict[5])
    auc_3 = np.array(res_dict[3])
    
    t_stat, p_val = ttest_rel(auc_4, auc_5)
    print(f"{name}:")
    print(f"  k=3 mean AUC: {np.mean(auc_3):.4f}")
    print(f"  k=4 mean AUC: {np.mean(auc_4):.4f}")
    print(f"  k=5 mean AUC: {np.mean(auc_5):.4f}")
    print(f"  Paired t-test (4 vs 5): t={t_stat:.4f}, p={p_val:.4f}")
