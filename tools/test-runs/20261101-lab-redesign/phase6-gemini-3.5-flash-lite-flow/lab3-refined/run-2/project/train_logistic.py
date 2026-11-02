import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from scipy.optimize import minimize

# 1. 載入資料並篩選 3 與 8
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y = (digits.target[mask] == 8).astype(int)

# 標準化特徵
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1.0
X_scaled = (X - X_mean) / X_std

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# 2. 使用 scipy.optimize.minimize (L-BFGS-B) 手刻 Logistic 迴歸 (與 sklearn 使用相同的優化演算法)
class CustomLogisticRegression:
    def __init__(self, C=1.0):
        self.C = C
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        n_samples, n_features = X.shape

        def cost_func(theta):
            w = theta[:-1]
            b = theta[-1]
            z = np.dot(X, w) + b
            z = np.clip(z, -500, 500)
            p = 1.0 / (1.0 + np.exp(-z))
            
            eps = 1e-15
            p = np.clip(p, eps, 1 - eps)
            bce = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
            
            # L2 正則化 (對齊 sklearn 目標函數)
            l2_reg = 0.5 * (1.0 / (self.C * n_samples)) * np.sum(w ** 2) if self.C else 0.0
            return bce + l2_reg

        def grad_func(theta):
            w = theta[:-1]
            b = theta[-1]
            z = np.dot(X, w) + b
            z = np.clip(z, -500, 500)
            p = 1.0 / (1.0 + np.exp(-z))
            
            dw = (1 / n_samples) * np.dot(X.T, (p - y))
            if self.C:
                dw += (1.0 / self.C) * w
            db = (1 / n_samples) * np.sum(p - y)
            
            return np.hstack([dw, db])

        init_theta = np.zeros(n_features + 1)
        res = minimize(cost_func, init_theta, jac=grad_func, method='L-BFGS-B', options={'maxiter': 2000})
        
        self.coef_ = res.x[:-1].reshape(1, -1)
        self.intercept_ = np.array([res.x[-1]])
        return self

    def predict_proba(self, X):
        z = np.dot(X, self.coef_[0]) + self.intercept_[0]
        z = np.clip(z, -500, 500)
        p = 1.0 / (1.0 + np.exp(-z))
        return np.vstack([1 - p, p]).T

    def predict(self, X, threshold=0.5):
        probs = self.predict_proba(X)[:, 1]
        return (probs >= threshold).astype(int)

# 訓練手刻模型
custom_lr = CustomLogisticRegression(C=1.0)
custom_lr.fit(X_train, y_train)

# 訓練 sklearn 模型
sk_lr = LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=2000, random_state=42)
sk_lr.fit(X_train, y_train)

# 3. 比較與驗證
y_pred_custom = custom_lr.predict(X_test)
y_pred_sk = sk_lr.predict(X_test)

acc_custom = accuracy_score(y_test, y_pred_custom)
acc_sk = accuracy_score(y_test, y_pred_sk)

print(f"Custom Model Accuracy: {acc_custom:.6f}")
print(f"Sklearn Model Accuracy: {acc_sk:.6f}")

# 比較權重與截距差異
weight_diff = np.max(np.abs(custom_lr.coef_ - sk_lr.coef_))
bias_diff = np.abs(custom_lr.intercept_ - sk_lr.intercept_)
print(f"Max Weight Difference: {weight_diff:.2e}")
print(f"Bias Difference: {bias_diff[0]:.2e}")

# 比較預測機率
proba_custom = custom_lr.predict_proba(X_test)
proba_sk = sk_lr.predict_proba(X_test)
proba_diff = np.max(np.abs(proba_custom - proba_sk))
print(f"Max Probability Difference: {proba_diff:.2e}")

# 4. 繪製權重比較圖並存至 figs/
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 權重對比散布圖
axes[0].scatter(sk_lr.coef_[0], custom_lr.coef_[0], alpha=0.7, color='purple', edgecolors='k')
min_val = min(sk_lr.coef_[0].min(), custom_lr.coef_[0].min())
max_val = max(sk_lr.coef_[0].max(), custom_lr.coef_[0].max())
axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', label='Ideal Match (y=x)')
axes[0].set_title('Weights Comparison: Sklearn vs Custom')
axes[0].set_xlabel('Sklearn Weights')
axes[0].set_ylabel('Custom Weights')
axes[0].legend()
axes[0].grid(True)

# 預測機率對比散布圖
axes[1].scatter(proba_sk[:, 1], proba_custom[:, 1], alpha=0.7, color='teal', edgecolors='k')
axes[1].plot([0, 1], [0, 1], 'r--', label='Ideal Match (y=x)')
axes[1].set_title('Predicted Probabilities Comparison')
axes[1].set_xlabel('Sklearn Probabilities (Class 8)')
axes[1].set_ylabel('Custom Probabilities (Class 8)')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('figs/logistic_comparison.png', dpi=300)
print("Plot saved to figs/logistic_comparison.png")
