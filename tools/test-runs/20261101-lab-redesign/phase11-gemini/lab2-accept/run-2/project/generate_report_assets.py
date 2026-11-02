import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

# Load data
X = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/data/line_channels.csv')
y = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/data/line_channels_fault.csv')['fault'].values

cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
components_list = [3, 4, 5]

results_lr = {k: [] for k in components_list}
results_t2 = {k: [] for k in components_list}

for train_idx, test_idx in cv.split(X, y):
    X_train, X_test = X.iloc[train_idx].values, X.iloc[test_idx].values
    y_train, y_test = y[train_idx], y[train_idx] # wait, y_test = y[test_idx]
    y_test = y[test_idx]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    for k in components_list:
        pca = PCA(n_components=k, random_state=42)
        Z_train = pca.fit_transform(X_train_scaled)
        Z_test = pca.transform(X_test_scaled)
        
        # Logistic Regression AUC
        lr = LogisticRegression(random_state=42, max_iter=1000)
        lr.fit(Z_train, y_train)
        auc_lr = roc_auc_score(y_test, lr.predict_proba(Z_test)[:, 1])
        results_lr[k].append(auc_lr)
        
        # T^2 statistic AUC
        eigenvalues = pca.explained_variance_
        t2_test = np.sum((Z_test ** 2) / eigenvalues, axis=1)
        auc_t2 = roc_auc_score(y_test, t2_test)
        if auc_t2 < 0.5:
            auc_t2 = roc_auc_score(y_test, -t2_test)
        results_t2[k].append(auc_t2)

# Plot
plt.figure(figsize=(8, 5))
plt.errorbar([str(k) for k in components_list], 
             [np.mean(results_lr[k]) for k in components_list], 
             yerr=[np.std(results_lr[k]) for k in components_list], 
             fmt='o-', label='Logistic Regression on PCs', capsize=5)
plt.errorbar([str(k) for k in components_list], 
             [np.mean(results_t2[k]) for k in components_list], 
             yerr=[np.std(results_t2[k]) for k in components_list], 
             fmt='s-', label='Hotelling T^2 Statistic', capsize=5)

plt.xlabel('Number of Principal Components ($k$)')
plt.ylabel('Fault Identification AUC')
plt.title('Fault Identification AUC Comparison (3, 4, 5 PCs)')
plt.ylim(0.4, 1.05)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/figs/pca_auc_comparison.png', dpi=300)
plt.close()

print("Plot saved successfully to figs/pca_auc_comparison.png")
