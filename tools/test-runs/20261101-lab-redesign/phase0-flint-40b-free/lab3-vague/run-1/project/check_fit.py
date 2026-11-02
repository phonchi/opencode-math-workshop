"""手刻 Newton 解 vs sklearn：objective 與梯度驗證"""

import numpy as np

from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from logistic_digits import C, CLASS_POS, fit_newton, sigmoid


def main():
    digits = load_digits()
    X_all, y_all = digits.data, digits.target
    mask = np.isin(y_all, [3, 8])
    X, y = X_all[mask], y_all[mask]
    t = (y == CLASS_POS).astype(float)
    X_tr, X_te, t_tr, t_te = train_test_split(X, t, test_size=0.25, stratify=t, random_state=42)
    scaler = StandardScaler().fit(X_tr)
    X_tr_s = scaler.transform(X_tr)
    X_te_s = scaler.transform(X_te)

    w_hand, losses, n_iter_hand = fit_newton(X_tr_s, t_tr, C=C)
    w_hand_full = np.append(w_hand[: X_tr_s.shape[1]], w_hand[-1])

    lr = LogisticRegression(C=C, solver="newton-cholesky", max_iter=100, tol=1e-10, random_state=0).fit(X_tr_s, t_tr.astype(int))
    w_sk = np.append(lr.coef_.ravel(), lr.intercept_.ravel()[0])

    n = X_tr_s.shape[0]
    lam = 1.0 / (C * n)

    def objective(w):
        Xa = np.hstack([X_tr_s, np.ones((n, 1))])
        p = sigmoid(Xa @ w)
        loss = -np.sum(t_tr * np.log(np.clip(p, 1e-12, 1 - 1e-12)) + (1 - t_tr) * np.log(np.clip(1 - p, 1e-12, 1 - 1e-12))) / n + 0.5 * lam * np.dot(w, w)
        return loss

    def grad(w):
        Xa = np.hstack([X_tr_s, np.ones((n, 1))])
        p = sigmoid(Xa @ w)
        return (Xa.T @ (p - t_tr)) / n + lam * w

    print("hand objective:", objective(w_hand_full), " grad inf-norm:", np.max(np.abs(grad(w_hand_full))))
    print("sk   objective:", objective(w_sk), " grad inf-norm:", np.max(np.abs(grad(w_sk))))
    print("loss curve tail (hand):", losses[-3:])
    print("w_sk[:5]:", w_sk[:5], " w_hand[:5]:", w_hand_full[:5])
    print("intercept hand/sk:", w_hand_full[-1], lr.intercept_.ravel())
    print("coef diff norm:", np.linalg.norm(w_hand_full - w_sk))
    print("sklearn n_iter_:", lr.n_iter_)


if __name__ == "__main__":
    main()
