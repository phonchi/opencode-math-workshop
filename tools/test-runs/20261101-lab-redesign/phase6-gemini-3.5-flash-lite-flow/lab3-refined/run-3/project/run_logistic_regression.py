import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize

# 1. 載入資料並過濾數字 3 與 8
digits = load_digits()
X_all = digits.data
y_all = digits.target

mask = (y_all == 3) | (y_all == 8)
X = X_all[mask]
y_raw = y_all[mask]

# 將標籤轉為二元：3 -> 0, 8 -> 1
y = np.where(y_raw == 8, 1, 0)

print(f"資料集形狀 (Digits 3 & 8): X={X.shape}, y={y.shape}")
print(f"類別分佈: 3 的數量={np.sum(y == 0)}, 8 的數量={np.sum(y == 1)}")

# 標準化特徵
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 切割訓練集與測試集
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# 2. 手刻 Logistic 迴歸 (使用 SciPy L-BFGS-B 最佳化以對齊 sklearn)
def sigmoid(z):
    # 防止溢位
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))

class CustomLogisticRegression:
    def __init__(self, fit_intercept=True, C=1.0):
        self.fit_intercept = fit_intercept
        self.C = C
        self.coef_ = None
        self.intercept_ = None
        
    def _cost_and_grad(self, params, X, y):
        m = X.shape[0]
        if self.fit_intercept:
            w = params[:-1]
            b = params[-1]
        else:
            w = params
            b = 0.0
            
        z = np.dot(X, w) + b
        y_pred = sigmoid(z)
        
        # Binary Cross Entropy Loss
        # 避免 log(0)
        eps = 1e-15
        y_pred = np.clip(y_pred, eps, 1 - eps)
        cost = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
        
        # L2 Regularization (sklearn style: penalty = 1/(2C) * ||w||^2)
        if self.C is not None and self.C > 0:
            reg_cost = 0.5 / (self.C * m) * np.sum(w ** 2)
            cost += reg_cost
            
        # Gradients
        grad_w = np.dot(X.T, (y_pred - y)) / m
        if self.C is not None and self.C > 0:
            grad_w += (1.0 / (self.C * m)) * w
            
        grad_b = np.sum(y_pred - y) / m
        
        if self.fit_intercept:
            grad = np.append(grad_w, grad_b)
        else:
            grad = grad_w
            
        return cost, grad

    def fit(self, X, y):
        m, d = X.shape
        init_params = np.zeros(d + 1 if self.fit_intercept else d)
        
        res = minimize(
            fun=self._cost_and_grad,
            x0=init_params,
            args=(X, y),
            jac=True,
            method='L-BFGS-B',
            options={'maxiter': 1000}
        )
        
        if self.fit_intercept:
            self.coef_ = res.x[:-1].reshape(1, -1)
            self.intercept_ = np.array([res.x[-1]])
        else:
            self.coef_ = res.x.reshape(1, -1)
            self.intercept_ = np.array([0.0])
            
        return self

    def predict_proba(self, X):
        z = np.dot(X, self.coef_.T) + self.intercept_
        p1 = sigmoid(z).ravel()
        return np.vstack([1 - p1, p1]).T

    def predict(self, X):
        proba = self.predict_proba(X)[:, 1]
        return (proba >= 0.5).astype(int)

# 3. 訓練手刻模型與 Sklearn 模型
# 為了完美對比，使用相同的 C 與 penalty='l2' (預設)
C_val = 1.0

custom_lr = CustomLogisticRegression(fit_intercept=True, C=C_val)
custom_lr.fit(X_train, y_train)

sklearn_lr = LogisticRegression(C=C_val, penalty='l2', solver='lbfgs', max_iter=1000)
sklearn_lr.fit(X_train, y_train)

# 4. 模型比較與驗證 (How to verify and compare)
custom_pred = custom_lr.predict(X_test)
sklearn_pred = sklearn_lr.predict(X_test)

custom_proba = custom_lr.predict_proba(X_test)[:, 1]
sklearn_proba = sklearn_lr.predict_proba(X_test)[:, 1]

acc_custom = np.mean(custom_pred == y_test)
acc_sklearn = np.mean(sklearn_pred == y_test)

coef_diff = np.max(np.abs(custom_lr.coef_ - sklearn_lr.coef_))
intercept_diff = np.max(np.abs(custom_lr.intercept_ - sklearn_lr.intercept_))
proba_diff = np.max(np.abs(custom_proba - sklearn_proba))

print("=== 模型比較結果 ===")
print(f"手刻模型 Accuracy: {acc_custom:.4f}")
print(f"Sklearn 模型 Accuracy: {acc_sklearn:.4f}")
print(f"權重最大絕對差異 (Max Coef Diff): {coef_diff:.2e}")
print(f"截距最大絕對差異 (Max Intercept Diff): {intercept_diff:.2e}")
print(f"預測機率最大絕對差異 (Max Proba Diff): {proba_diff:.2e}")
print(f"預測標籤是否完全一致: {np.array_equal(custom_pred, sklearn_pred)}")

# 5. 繪製並儲存圖表到 figs/
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 權重熱力圖 (Custom)
im0 = axes[0].imshow(custom_lr.coef_.reshape(8, 8), cmap='coolwarm', interpolation='nearest')
axes[0].set_title("Custom LR Weights (8x8)")
fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

# 權重熱力圖 (Sklearn)
im1 = axes[1].imshow(sklearn_lr.coef_.reshape(8, 8), cmap='coolwarm', interpolation='nearest')
axes[1].set_title("Sklearn LR Weights (8x8)")
fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

# 預測機率散布圖對比
axes[2].scatter(sklearn_proba, custom_proba, alpha=0.7, color='purple', edgecolors='k')
axes[2].plot([0, 1], [0, 1], 'k--', label='y = x')
axes[2].set_xlabel("Sklearn Predicted Probability")
axes[2].set_ylabel("Custom Predicted Probability")
axes[2].set_title("Predicted Probabilities Comparison")
axes[2].legend()
axes[2].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("figs/logistic_regression_comparison.png", dpi=300)
print("圖表已成功儲存至 figs/logistic_regression_comparison.png")
