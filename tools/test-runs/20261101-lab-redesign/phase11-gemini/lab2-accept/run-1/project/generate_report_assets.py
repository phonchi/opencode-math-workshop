import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

# Load data
df_channels = pd.read_csv('data/line_channels.csv')
df_fault = pd.read_csv('data/line_channels_fault.csv')

X = df_channels.values
y = df_fault['fault'].values

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
components = [3, 4, 5]

lr_auc = {k: [] for k in components}
rf_auc = {k: [] for k in components}
t2_auc = {k: [] for k in components}
q_auc = {k: [] for k in components}

for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    for k in components:
        pca = PCA(n_components=k, random_state=42)
        X_train_pca = pca.fit_transform(X_train_scaled)
        X_test_pca = pca.transform(X_test_scaled)
        
        # Logistic Regression
        lr = LogisticRegression(random_state=42)
        lr.fit(X_train_pca, y_train)
        lr_auc[k].append(roc_auc_score(y_test, lr.predict_proba(X_test_pca)[:, 1]))
        
        # Random Forest
        rf = RandomForestClassifier(random_state=42)
        rf.fit(X_train_pca, y_train)
        rf_auc[k].append(roc_auc_score(y_test, rf.predict_proba(X_test_pca)[:, 1]))
        
        # Hotelling's T^2
        lambda_i = pca.explained_variance_
        T2 = np.sum((X_test_pca ** 2) / lambda_i, axis=1)
        t2_auc[k].append(roc_auc_score(y_test, T2))
        
        # Q-statistic (SPE)
        X_test_recon = pca.inverse_transform(X_test_pca)
        Q = np.sum((X_test_scaled - X_test_recon) ** 2, axis=1)
        q_auc[k].append(roc_auc_score(y_test, Q))

# Plotting
fig, ax = plt.subplots(figsize=(8, 5))

x = np.array(components)
width = 0.2

means_lr = [np.mean(lr_auc[k]) for k in components]
means_rf = [np.mean(rf_auc[k]) for k in components]
means_t2 = [np.mean(t2_auc[k]) for k in components]
means_q = [np.mean(q_auc[k]) for k in components]

ax.bar(x - 1.5*width, means_lr, width, label='Logistic Regression (PCA features)')
ax.bar(x - 0.5*width, means_rf, width, label='Random Forest (PCA features)')
ax.bar(x + 0.5*width, means_t2, width, label="Hotelling's T^2 ($T^2$)")
ax.bar(x + 1.5*width, means_q, width, label='Q-statistic (SPE)')

ax.set_xlabel('Number of Principal Components ($k$)')
ax.set_ylabel('Mean AUC')
ax.set_title('Fault Detection AUC Comparison across 3, 4, 5 Principal Components')
ax.set_xticks(components)
ax.set_ylim(0, 1.05)
ax.legend(loc='lower left', fontsize=9)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('figs/pca_fault_auc_comparison.png', dpi=300)
plt.close()

print("Plot saved to figs/pca_fault_auc_comparison.png successfully.")
