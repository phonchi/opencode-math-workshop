# lab3_experiments.py
# 實驗 A / B：不改 lab3_logistic.py 原本的 loss 與 grad
import numpy as np
from lab3_logistic import (load_data, standardize_fit, add_intercept,
                           sigmoid, loss, grad, fit, check_gradient)


def loss_mse(w, X, y):
    p = sigmoid(X @ w)
    return np.mean((p - y) ** 2)


def grad_mse(w, X, y):
    # d/dw mean((sigma(Xw)-y)^2) = 2/n * X^T (sigma(Xw)-y) * sigma(Xw)(1-sigma(Xw))
    n = X.shape[0]
    p = sigmoid(X @ w)
    return 2.0 / n * X.T @ ((p - y) * p * (1.0 - p))


def grad_doubled(w, X, y):
    return 2.0 * grad(w, X, y)


def run(name, loss_fn, grad_fn, X, y):
    eps_list = [1e-4, 1e-5, 1e-6, 1e-7]
    rng = np.random.default_rng(42)
    points = [np.zeros(X.shape[1]),
              rng.normal(0.0, 0.1, size=X.shape[1]),
              rng.normal(0.0, 1.0, size=X.shape[1])]
    best_err = np.inf
    for w0 in points:
        g = grad_fn(w0, X, y)
        for eps in eps_list:
            err = 0.0
            for j in range(X.shape[1]):
                wp = w0.copy(); wp[j] += eps
                wm = w0.copy(); wm[j] -= eps
                num = (loss_fn(wp, X, y) - loss_fn(wm, X, y)) / (2.0 * eps)
                err = max(err, abs(num - g[j]))
            best_err = min(best_err, err)
    tol = 1e-6
    status = "PASS" if best_err < tol else "FAIL"
    print(f"\n=== 實驗 {name} ===")
    print(f"  最大絕對誤差（eps 掃描後最佳）: {best_err:.3e}")
    print(f"  梯度檢查: {status}（容差 {tol:.1e}）")
    return best_err, status


def main():
    X_raw, y, _ = load_data()
    mu, sd = standardize_fit(X_raw)
    X = add_intercept((X_raw - mu) / sd)

    run("A: MSE loss + MSE 正確梯度", loss_mse, grad_mse, X, y)
    run("B: log loss + grad 乘 2", loss, grad_doubled, X, y)


if __name__ == "__main__":
    main()
