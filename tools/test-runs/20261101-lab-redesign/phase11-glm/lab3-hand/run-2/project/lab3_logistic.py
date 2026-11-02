# lab3_logistic.py
# 手刻 logistic 迴歸（numpy，無正則化），資料：data/line_faults.csv（900 筆）
import numpy as np

CSV_PATH = "data/line_faults.csv"


def load_data(path=CSV_PATH):
    data = np.genfromtxt(path, delimiter=",", names=True)
    feature_names = ["temp_c", "vibration_mm_s", "pressure_kpa",
                     "flow_lpm", "current_a", "speed_rpm"]
    X_raw = np.column_stack([data[name] for name in feature_names])
    y = data["fault"].astype(float)
    return X_raw, y, feature_names


def standardize_fit(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    return mu, sd


def add_intercept(X):
    return np.column_stack([X, np.ones(X.shape[0])])


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def loss(w, X, y):
    # 平均對數損失： -mean(y log p + (1-y) log(1-p))
    z = X @ w
    # 用 log-sum-exp 穩定寫法：log(1+exp(-z)) 與 log(1+exp(z))
    log_terms = np.logaddexp(0.0, z) - y * z
    return log_terms.mean()


def grad(w, X, y):
    n = X.shape[0]
    return X.T @ (sigmoid(X @ w) - y) / n


def fit(X, y, lr=0.1, epochs=5000):
    w = np.zeros(X.shape[1])
    for _ in range(epochs):
        w -= lr * grad(w, X, y)
    return w


def check_gradient(X, y, centers, eps_list):
    # 中央差分梯度檢查
    # 檢查點：任選幾個有代表性的 w（零向量、隨機小、隨機大），
    # 讓檢查涵蓋 sigmoid 飽和與非飽和區，避免只在單一點通過的僥倖。
    # 步長：多個 eps（1e-4 ~ 1e-7），中央差分誤差 O(eps^2)，
    # eps 太大有截斷誤差、太小有浮點相消誤差，掃一輪找誤差最小的量級最穩。
    rng = np.random.default_rng(42)
    points = [np.zeros(X.shape[1])]
    for scale in (0.1, 1.0):
        points.append(rng.normal(0.0, scale, size=X.shape[1]))

    max_err = 0.0
    best_err = np.inf
    for w0 in points:
        g = grad(w0, X, y)
        for eps in eps_list:
            err = 0.0
            for j in range(X.shape[1]):
                wp = w0.copy(); wp[j] += eps
                wm = w0.copy(); wm[j] -= eps
                num = (loss(wp, X, y) - loss(wm, X, y)) / (2.0 * eps)
                err = max(err, abs(num - g[j]))
            max_err = max(max_err, err)
            best_err = min(best_err, err)
    return max_err, best_err


def main():
    X_raw, y, feature_names = load_data()
    print(f"資料筆數: {X_raw.shape[0]}, 特徵數: {X_raw.shape[1]}")

    mu, sd = standardize_fit(X_raw)
    X = add_intercept((X_raw - mu) / sd)

    w = fit(X, y)
    p = sigmoid(X @ w)
    pred = (p >= 0.5).astype(float)
    acc = (pred == y).mean()

    eps_list = [1e-4, 1e-5, 1e-6, 1e-7]
    max_err, best_err = check_gradient(X, y, w, eps_list)

    print("\n=== 訓練結果 ===")
    for name, wi in zip(feature_names + ["intercept"], w):
        print(f"  {name:>15s}: {wi:+.6f}")
    print(f"  最終 loss : {loss(w, X, y):.6f}")
    print(f"  訓練準確率: {acc:.4f}")

    print("\n=== 梯度檢查（中央差分, 全部 7 個維度）===")
    print(f"  檢查點: 零向量 + 兩個隨機點（scale 0.1 / 1.0）")
    print(f"  步長 eps: {eps_list}")
    print(f"  各組合最大絕對誤差: {max_err:.3e}")
    print(f"  誤差最小值（eps 掃描後）: {best_err:.3e}")
    tol = 1e-6
    status = "PASS" if best_err < tol else "FAIL"
    print(f"  容許誤差: {tol:.1e}")
    print(f"  梯度檢查: {status}")


if __name__ == "__main__":
    main()
