import numpy as np
from lab3_logistic import X, y, n, sigmoid, check_gradients

# 實驗 A：均方誤差損失 mean((σ(z)-y)^2) 與其正確梯度
# L = (1/n) Σ (σ(z_i) - y_i)^2
# dL/dz_i = (2/n)(σ(z_i) - y_i) σ(z_i)(1 - σ(z_i))
# 故 grad_A = (2/n) X^T [(s - y) * s * (1 - s)]


def loss_mse(w):
    return np.mean((sigmoid(X @ w) - y) ** 2)


def grad_mse(w):
    s = sigmoid(X @ w)
    return (2.0 / n) * X.T @ ((s - y) * s * (1 - s))


check_gradients(loss_mse, grad_mse, name="A: MSE")


# 實驗 B：loss 不變（logistic），grad 錯誤地乘以 2 → 應該 FAIL


def grad_x2(w):
    return 2.0 * (X.T @ (sigmoid(X @ w) - y) / n)


check_gradients(lambda w: -np.mean(y * np.log(sigmoid(X @ w) + 1e-12)
                                  + (1 - y) * np.log(1 - sigmoid(X @ w) + 1e-12)),
                grad_x2, name="B: grad x2")
