import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
from sklearn.metrics import accuracy_score

# 1. 載入 digits 資料集，挑選 3 與 8
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y = (digits.target[mask] == 8).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 2. 手刻 Logistic Regression 類別 (帶 L2 正則化)
class CustomLogisticRegression:
    def __init__(self, learning_rate=0.1, max_iters=5000, tol=1e-8, C=1.0):
        self.learning_rate = learning_rate
        self.max_iters = max_iters
        self.tol = tol
        self.C = C  # 與 sklearn 的 C 參數對應 (正規化強度的倒數)
        self.weights = None
        self.bias = None
        self.loss_history = []
        
    def _sigmoid(self, z):
        z = np.clip(z, -500, 500)
        return 1.0 / (1.0 + np.exp(-z))
        
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0
        
        prev_loss = float('inf')
        
        # sklearn 的目標函數： min 0.5 * ||w||^2 + C * sum(log loss)
        # 對應到梯度下降：
        # Loss = (1/N) sum(...) + (1 / (2 * C * N)) ||w||^2  (注意 sklearn 定義與常見教科書定義略有不同)
        # 為了精確對齊 sklearn，我們使用 sklearn 的 L2 目標函數梯度
        for i in range(self.max_iters):
            linear_pred = np.dot(X, self.weights) + self.bias
            predictions = self._sigmoid(linear_pred)
            
            epsilon = 1e-15
            predictions = np.clip(predictions, epsilon, 1 - epsilon)
            
            # 依據 sklearn 的 L2 邏輯斯迴歸損失定義：
            # Loss = 0.5 * ||w||^2 + C * sum(- [y log p + (1-y) log (1-p)])
            # 這裡我們用標準梯度：dw = w + C * (1/N) * X^T (p - y)
            # 為了讓 learning rate 穩定，我們用標準化損失
            bce_loss = -np.mean(y * np.log(predictions) + (1 - y) * np.log(1 - predictions))
            l2_loss = 0.5 * np.sum(self.weights ** 2) / (self.C * n_samples)
            loss = bce_loss + l2_loss
            self.loss_history.append(loss)
            
            dw = (1 / n_samples) * np.dot(X.T, (predictions - y)) + (1.0 / self.C) * (self.weights / n_samples)
            db = (1 / n_samples) * np.sum(predictions - y)
            
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            if abs(prev_loss - loss) < self.tol:
                print(f"Custom model converged at iteration {i}, loss: {loss:.8f}")
                break
            prev_loss = loss
            
    def predict_proba(self, X):
        linear_pred = np.dot(X, self.weights) + self.bias
        return self._sigmoid(linear_pred)
        
    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

C_val = 1.0
custom_lr = CustomLogisticRegression(learning_rate=0.1, max_iters=10000, tol=1e-9, C=C_val)
custom_lr.fit(X_train_scaled, y_train)

sklearn_lr = SklearnLogisticRegression(C=C_val, penalty='l2', solver='lbfgs', max_iter=10000, random_state=42)
sklearn_lr.fit(X_train_scaled, y_train)

custom_preds = custom_lr.predict(X_test_scaled)
sklearn_preds = sklearn_lr.predict(X_test_scaled)

print(f"Custom Model Accuracy: {accuracy_score(y_test, custom_preds):.4f}")
print(f"Sklearn Model Accuracy: {accuracy_score(y_test, sklearn_preds):.4f}")

weight_diff = np.linalg.norm(custom_lr.weights - sklearn_lr.coef_[0])
bias_diff = abs(custom_lr.bias - sklearn_lr.intercept_[0])
print(f"Weight L2 Difference: {weight_diff:.6f}")
print(f"Bias Difference: {bias_diff:.6f}")

custom_probs = custom_lr.predict_proba(X_test_scaled)
sklearn_probs = sklearn_lr.predict_proba(X_test_scaled)[:, 1]
max_prob_diff = np.max(np.abs(custom_probs - sklearn_probs))
print(f"Max Probability Difference: {max_prob_diff:.6e}")
