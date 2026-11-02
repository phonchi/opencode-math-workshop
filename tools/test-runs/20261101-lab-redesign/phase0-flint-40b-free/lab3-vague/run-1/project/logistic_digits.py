"""digits 資料集的 3 與 8：手刻 logistic 迴歸 + sklearn 比較"""

import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
TEST_SIZE = 0.25
C = 1.0  # L2 正則化係數之倒數（sklearn 的 C）

CLASS_POS = 8  # 正類：digit 8；負類：digit 3


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_newton(X, t, C=1.0, max_iter=100, tol=1e-12):
    """用 Newton-Raphson（IRLS）解手刻 logistic 迴歸（含截距，L2 penalty）"""
    n, d = X.shape
    Xa = np.hstack([X, np.ones((n, 1))])  # 截距併入設計矩陣，末端為截數
    lam = 1.0 / (C * n)
    w = np.zeros(d + 1)
    losses = []
    n_iter = 0
    for i in range(max_iter):
        eta = Xa @ w
        p = sigmoid(eta)
        loss = -np.sum(t * np.log(np.clip(p, 1e-12, 1 - 1e-12)) + (1 - t) * np.log(np.clip(1 - p, 1e-12, 1 - 1e-12))) / n + 0.5 * lam * np.dot(w, w)
        losses.append(loss)
        grad = (Xa.T @ (p - t)) / n + lam * w
        Wd = p * (1 - p)
        H = (Xa.T * Wd) @ Xa / n + lam * np.eye(d + 1)
        delta = np.linalg.solve(H, -grad)
        w = w + delta
        n_iter = i + 1
        if np.max(np.abs(delta)) < tol:
            break
    return w, losses, n_iter


def main():
    digits = load_digits()
    X_all, y_all = digits.data, digits.target
    mask = np.isin(y_all, [3, 8])
    X, y = X_all[mask], y_all[mask]
    t = (y == CLASS_POS).astype(float)  # 1 = digit 8, 0 = digit 3

    X_tr, X_te, t_tr, t_te = train_test_split(
        X, t, test_size=TEST_SIZE, stratify=t, random_state=RANDOM_STATE
    )

    scaler = StandardScaler().fit(X_tr)
    X_tr_s = scaler.transform(X_tr)
    X_te_s = scaler.transform(X_te)

    w_hand, losses, n_iter_hand = fit_newton(X_tr_s, t_tr, C=C)
    w_hand_full = np.append(w_hand[: X_tr_s.shape[1]], w_hand[-1])

    lr = LogisticRegression(C=C, solver="lbfgs", max_iter=5000, tol=1e-12, random_state=0)
    lr.fit(X_tr_s, t_tr.astype(int))
    w_sk_full = np.append(lr.coef_.ravel(), lr.intercept_.ravel()[0])

    n = X_tr_s.shape[0]
    lam = 1.0 / (C * n)
    Xa = np.hstack([X_tr_s, np.ones((n, 1))])
    loss_hand = log_loss(t_tr, Xa @ w_hand_full) + 0.5 * lam * np.dot(w_hand_full, w_hand_full)
    loss_sk = log_loss(t_tr, Xa @ w_sk_full) + 0.5 * lam * np.dot(w_sk_full, w_sk_full)

    p_te_hand = sigmoid(X_te_s @ w_hand[: X_tr_s.shape[1]] + w_hand[-1])
    p_te_sk = lr.predict_proba(X_te_s)[:, 1]
    y_pred_hand = (p_te_hand >= 0.5).astype(int)
    y_pred_sk = lr.predict(X_te_s.astype(float))

    acc_hand = float(np.mean(y_pred_hand == t_te))
    acc_sk = float(lr.score(X_te_s, t_te.astype(int)))
    agree = float(np.mean(y_pred_hand == y_pred_sk))
    max_prob_diff = float(np.max(np.abs(p_te_hand - p_te_sk)))
    max_w_diff = float(np.max(np.abs(w_hand_full - w_sk_full)))

    print(f"train n={X_tr_s.shape[0]}, test n={X_te_s.shape[0]}")
    print(f"hand   : n_iter={n_iter_hand}, final loss={losses[-1]:.6f}, acc={acc_hand:.4f}")
    print(f"sklearn: n_iter={int(np.ravel(lr.n_iter_)[0])}, loss={loss_sk:.6f}, acc={acc_sk:.4f}")
    print(f"J(hand) = {loss_hand:.8f}   J(sk) = {loss_sk:.8f}")
    print(f"label agreement: {agree:.4f}")
    print(f"max |P_hand - P_sk| = {max_prob_diff:.3e}")
    print(f"max |w_hand - w_sk| = {max_w_diff:.3e}")

    plt.figure()
    plt.plot(losses, marker="o")
    plt.xlabel("Newton iteration")
    plt.ylabel("loss")
    plt.savefig("figs/logistic_digits_loss.png")
    plt.close()


if __name__ == "__main__":
    main()
