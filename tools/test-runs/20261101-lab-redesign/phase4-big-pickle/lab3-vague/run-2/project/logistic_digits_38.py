# 用 digits 的 3 和 8 手刻 logistic 迴歸
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 載入資料
digits = load_digits()
X = digits.data
y = digits.target

# 篩選 3 和 8（二元分類）
mask = (y == 3) | (y == 8)
X = X[mask]
y = y[mask]
# 將標籤轉換為 0/1（方便手刻推導，這裡以 3 為 0，8 為 1）
y_binary = np.where(y == 8, 1, 0)

# 標準化（有助於收斂）
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1
X_norm = (X - X_mean) / X_std

# 加上 bias 項
m, n = X_norm.shape
X_b = np.column_stack([np.ones(m), X_norm])

# Sigmoid 函數
def sigmoid(z):
    # 避免 overflow
    z = np.clip(z, -250, 250)
    return 1.0 / (1.0 + np.exp(-z))

# 手刻 Logistic Regression（梯度下降）
class LogisticRegressionScratch:
    def __init__(self, lr=0.01, max_iter=10000, tol=1e-7):
        self.lr = lr
        self.max_iter = max_iter
        self.tol = tol
        self.theta = None
        self.loss_history = []
    
    def fit(self, X_b, y):
        m, n = X_b.shape
        self.theta = np.zeros(n)
        for i in range(self.max_iter):
            z = X_b @ self.theta
            h = sigmoid(z)
            # 損失函數：Binary Cross Entropy
            eps = 1e-15
            loss = -np.mean(y * np.log(h + eps) + (1 - y) * np.log(1 - h + eps))
            self.loss_history.append(loss)
            # 梯度： (1/m) X^T (h - y)
            gradient = (1/m) * X_b.T @ (h - y)
            self.theta = self.theta - self.lr * gradient
            if i > 0 and abs(self.loss_history[-1] - self.loss_history[-2]) < self.tol:
                break
        return self
    
    def predict_proba(self, X_b):
        z = X_b @ self.theta
        h = sigmoid(z)
        return np.column_stack([1-h, h])
    
    def predict(self, X_b, threshold=0.5):
        return (self.predict_proba(X_b)[:, 1] >= threshold).astype(int)

# 訓練手刻模型
lr_scratch = LogisticRegressionScratch(lr=0.1, max_iter=20000)
lr_scratch.fit(X_b, y_binary)
y_pred_scratch = lr_scratch.predict(X_b)
acc_scratch = accuracy_score(y_binary, y_pred_scratch)
print(f"手刻 Logistic Regression 準確率: {acc_scratch:.6f}")
print(f"手刻 theta (前5項): {lr_scratch.theta[:5]}")

# sklearn 比較
lr_sk = LogisticRegression(solver='lbfgs', max_iter=10000)
lr_sk.fit(X_norm, y_binary)
y_pred_sk = lr_sk.predict(X_norm)
acc_sk = accuracy_score(y_binary, y_pred_sk)
print(f"sklearn LogisticRegression 準確率: {acc_sk:.6f}")
# sklearn 的 coef_ 和 intercept_ 對應手刻的 theta[1:] 和 theta[0]
print(f"sklearn coef_ (前5項): {lr_sk.coef_[0][:5]}")
print(f"sklearn intercept_: {lr_sk.intercept_[0]:.6f}")
print(f"手刻 theta[0] (bias): {lr_scratch.theta[0]:.6f}")
