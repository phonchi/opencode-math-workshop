import numpy as np
from sklearn.datasets import load_digits


def sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    out[~pos] = np.exp(z[~pos]) / (1.0 + np.exp(z[~pos]))
    return out


def softplus(z):
    return np.maximum(z, 0.0) + np.log1p(np.exp(-np.abs(z)))


def loss(w, Xb, y):
    z = Xb @ w
    return np.mean(softplus(z) - y * z)


def grad(w, Xb, y):
    p = sigmoid(Xb @ w)
    return Xb.T @ (p - y) / Xb.shape[0]


def finite_diff_grad(w, Xb, y, h):
    g = np.zeros_like(w)
    for j in range(w.size):
        wp = w.copy()
        wm = w.copy()
        wp[j] += h
        wm[j] -= h
        g[j] = (loss(wp, Xb, y) - loss(wm, Xb, y)) / (2.0 * h)
    return g


digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask] / 16.0
y = (digits.target[mask] == 8).astype(float)
Xb = np.column_stack([X, np.ones(X.shape[0])])

print("X shape  =", X.shape)
print("y shape  =", y.shape)
print("Xb shape =", Xb.shape)
print("d =", Xb.shape[1], "(64 features + 1 intercept)")

w0 = np.random.RandomState(0).normal(size=Xb.shape[1]) * 0.01
g_analytic = grad(w0, Xb, y)

print()
print("central-difference gradient check over ALL 65 dims,")
print("checkpoint w0 = np.random.RandomState(0).normal(size=65) * 0.01")
print()
print(f"{'h':>8}  {'max |fd - analytic|':>20}  {'max |rel err|':>14}")
print("-" * 52)
for p in range(2, 10):
    h = 10.0 ** (-p)
    g_fd = finite_diff_grad(w0, Xb, y, h)
    abs_err = np.abs(g_fd - g_analytic)
    rel_err = abs_err / np.maximum(np.abs(g_analytic), 1e-12)
    print(f"{h:8.1e}  {abs_err.max():20.3e}  {rel_err.max():14.3e}")