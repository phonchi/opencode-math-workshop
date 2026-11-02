import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

# 1. 載入資料並過濾數字 3 與 8
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y_raw = digits.target[mask]

# 將標籤 3 轉為 0，8 轉為 1
y = np.where(y_raw == 8, 1, 0)

# 2. 資料分割與標準化
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. 手刻 Logistic 迴歸類別 (加入 L2 正則化參數以對齊 sklearn 預設的 L2 regularization)
class CustomLogisticRegression:
    def __init__(self, lr=0.1, epochs=3000, C=1.0, tol=1e-7):
        self.lr = lr
        self.epochs = epochs
        self.C = C  # C 是正則化強度的倒數 (lambda = 1/C)
        self.tol = tol
        self.weights = None
        self.bias = None
        self.loss_history = []

    def _sigmoid(self, z):
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0

        lam = 1.0 / self.C if self.C > 0 else 0.0
        prev_loss = float('inf')

        for epoch in range(self.epochs):
            linear_model = np.dot(X, self.weights) + self.bias
            y_pred = self._sigmoid(linear_model)

            # 包含 L2 懲罰項的 Loss
            eps = 1e-15
            y_pred_clipped = np.clip(y_pred, eps, 1 - eps)
            bce_loss = -np.mean(y * np.log(y_pred_clipped) + (1 - y) * np.log(1 - y_pred_clipped))
            l2_loss = (0.5 * lam / n_samples) * np.sum(self.weights ** 2)
            loss = bce_loss + l2_loss
            self.loss_history.append(loss)

            # 梯度 (包含 L2 項)
            dw = (1 / n_samples) * np.dot(X.T, (y_pred - y)) + (lam / n_samples) * self.weights
            db = (1 / n_samples) * np.sum(y_pred - y)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db

            if abs(prev_loss - loss) < self.tol:
                break
            prev_loss = loss

    def predict_proba(self, X):
        linear_model = np.dot(X, self.weights) + self.bias
        return self._sigmoid(linear_model)

    def predict(self, X, threshold=0.5):
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)

# 4. 訓練手刻模型與 sklearn 模型 (使用相同的 C=1.0)
C_val = 1.0
custom_lr = CustomLogisticRegression(lr=0.1, epochs=5000, C=C_val)
custom_lr.fit(X_train_scaled, y_train)

sk_lr = LogisticRegression(C=C_val, solver='lbfgs', max_iter=5000)
sk_lr.fit(X_train_scaled, y_train)

# 5. 驗證比較
cust_test_preds = custom_lr.predict(X_test_scaled)
cust_test_proba = custom_lr.predict_proba(X_test_scaled)

sk_test_preds = sk_lr.predict(X_test_scaled)
sk_test_proba = sk_lr.predict_proba(X_test_scaled)[:, 1]

print("--- 相同超參數 (C=1.0, L2 Regularization) 比較 ---")
print(f"手刻模型測試集準確率: {accuracy_score(y_test, cust_test_preds):.4f}")
print(f"sklearn 模型測試集準確率: {accuracy_score(y_test, sk_test_preds):.4f}")

weight_diff = np.linalg.norm(custom_lr.weights - sk_lr.coef_[0])
bias_diff = abs(custom_lr.bias - sk_lr.intercept_[0])
proba_diff = np.max(np.abs(cust_test_proba - sk_test_proba))

print(f"權重 L2 差異 (||w_hand - w_sk||_2): {weight_diff:.6f}")
print(f"偏差差異 (|b_hand - b_sk|): {bias_diff:.6f}")
print(f"測試集預測機率最大絕對差異: {proba_diff:.6f}")

# 6. 繪製圖表並存至 figs/
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(custom_lr.loss_history, color='blue', lw=2)
axes[0].set_title('Custom Logistic Regression Training Loss (with L2)')
axes[0].set_xlabel('Epochs')
axes[0].set_ylabel('Loss')
axes[0].grid(True)

axes[1].scatter(sk_lr.coef_[0], custom_lr.weights, alpha=0.7, color='purple', edgecolors='k')
axes[1].plot([min(sk_lr.coef_[0]), max(sk_lr.coef_[0])], 
             [min(sk_lr.coef_[0]), max(sk_lr.coef_[0])], 'r--', label='Ideal y=x')
axes[1].set_title('Weight Comparison (sklearn vs Custom)')
axes[1].set_xlabel('sklearn Weights')
axes[1].set_ylabel('Custom Weights')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig('figs/logistic_comparison.png', dpi=300)
plt.close()
