import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

np.random.seed(0)


def sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    out[~pos] = np.exp(z[~pos]) / (1.0 + np.exp(z[~pos]))
    return out


def softplus(z):
    return np.maximum(z, 0.0) + np.log1p(np.exp(-np.abs(z)))


def add_intercept(X):
    return np.column_stack([X, np.ones(X.shape[0])])


def loss(w, X, y):
    z = X @ w
    return np.mean(softplus(z) - y * z)


def grad(w, X, y):
    p = sigmoid(X @ w)
    return X.T @ (p - y) / X.shape[0]


def finite_diff_grad(w, X, y, h):
    g = np.zeros_like(w)
    for j in range(w.size):
        wp = w.copy()
        wm = w.copy()
        wp[j] += h
        wm[j] -= h
        g[j] = (loss(wp, X, y) - loss(wm, X, y)) / (2.0 * h)
    return g


def predict(w, X):
    return (sigmoid(X @ w) >= 0.5).astype(int)


def irls(X, y, n_iter=100, tol=1e-12, eps=1e-10):
    w = np.zeros(X.shape[1])
    for it in range(n_iter):
        p = sigmoid(X @ w)
        w_prev = w.copy()
        H = X.T @ (X * (p * (1 - p))[:, None])
        g = X.T @ (p - y)
        w = w_prev - np.linalg.solve(H + eps * np.eye(H.shape[0]), g)
        if np.linalg.norm(g) < tol:
            return w, it + 1, True
    return w, n_iter, False


digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X_raw = digits.data[mask] / 16.0
y = (digits.target[mask] == 8).astype(float)

X_train, X_test, y_train, y_test = train_test_split(
    X_raw, y, test_size=0.3, random_state=0)

X1 = add_intercept(X_train)
X1t = add_intercept(X_test)
d = X1.shape[1]

rng = np.random.RandomState(0)
w0 = rng.normal(0.0, 0.5, d)
g_analytic = grad(w0, X1, y_train)

print("hand-coded logistic regression on digits {3, 8}")
print(f"train n = {X1.shape[0]}, dimension (64 features + 1 intercept) = {d}")
print("gradient check point w0 ~ N(0, 0.5), central difference over ALL dims")
print()
print(f"{'h':>8}  {'max |fd - analytic|':>20}  {'max |rel err|':>14}")
print("-" * 52)
for p in range(2, 10):
    h = 10.0 ** (-p)
    g_fd = finite_diff_grad(w0, X1, y_train, h)
    abs_err = np.abs(g_fd - g_analytic)
    rel_err = abs_err / np.maximum(np.abs(g_analytic), 1e-12)
    print(f"{h:8.1e}  {abs_err.max():20.3e}  {rel_err.max():14.3e}")

w_fit, iters, conv = irls(X1, y_train)
clf = LogisticRegression(C=1e10, max_iter=5000).fit(X_train, y_train)
w_sk = np.concatenate([clf.coef_.ravel(), clf.intercept_])

print()
print("training results (hand-coded IRLS / Newton on 65-dim model)")
print(f"IRLS iterations = {iters} (converged by grad norm < 1e-12: {conv})")
print(f"final train loss = {loss(w_fit, X1, y_train):.8f}")
print(f"grad norm at w_fit = {np.linalg.norm(grad(w_fit, X1, y_train)):.3e}")
print(f"train accuracy   = {np.mean(predict(w_fit, X1) == y_train):.4f}")
print(f"test  accuracy   = {np.mean(predict(w_fit, X1t) == y_test):.4f}")
print(f"sklearn test accuracy = {clf.score(X_test, y_test):.4f}")
print(f"sklearn train loss (for reference) = {loss(w_sk, X1, y_train):.8f}")
print("note: digits 3/8 are highly separable -> many near-optimal w,")
print("      coefficient-wise comparison is done on the synthetic set below.")

rng7 = np.random.RandomState(7)
n_s, p_s = 400, 4
w_true = rng7.normal(size=p_s + 1)
X_s = rng7.normal(size=(n_s, p_s))
X1s = add_intercept(X_s)
y_s = (rng7.rand(n_s) < sigmoid(X1s @ w_true)).astype(float)

w_s, iters_s, conv_s = irls(X1s, y_s)
clf_s = LogisticRegression(C=1e10, max_iter=5000).fit(X_s, y_s)
w_s_sk = np.concatenate([clf_s.coef_.ravel(), clf_s.intercept_])

print()
print("synthetic non-separable check (true model w_true, n=400, p=4)")
print(f"IRLS iterations = {iters_s} (converged by grad norm < 1e-12: {conv_s})")
print(f"||w_ours - w_true||    = {np.linalg.norm(w_s - w_true):.3e}")
print(f"||w_ours - w_sklearn|| = {np.linalg.norm(w_s - w_s_sk):.3e}")
print(f"loss(w_ours) vs loss(w_sklearn) = {loss(w_s, X1s, y_s):.8f} vs {loss(w_s_sk, X1s, y_s):.8f}")
print(f"w_true = {np.round(w_true, 3)}")
print(f"w_ours = {np.round(w_s, 3)}")
print(f"w_sk   = {np.round(w_s_sk, 3)}")