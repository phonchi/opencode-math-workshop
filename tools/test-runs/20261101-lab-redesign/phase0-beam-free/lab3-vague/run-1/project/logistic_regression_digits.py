"""手刻 logistic 迴歸：digits 3 vs 8，並與 sklearn 比較。

執行：uv run python logistic_regression_digits.py
"""
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


class ManualLogisticRegression:
    """以 Newton-Raphson (IRLS) 求解 L2 正則化 logistic 迴歸。

    目標函數 (與 sklearn C 對齊)：
        J(w,b) = (1/n) Σ ℓ_i + (1/(2 C n)) ||w||^2
    其中 ℓ_i = -[y_i log p_i + (1-y_i) log(1-p_i)]。
    """

    def __init__(self, C=1.0, max_iter=100, tol=1e-12):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).ravel()
        n, p = X.shape
        self.keep_ = X.std(axis=0) > 0  # 常數特徵無法識別，係數固定為 0
        Xk = X[:, self.keep_]
        pk = Xk.shape[1]
        Xb = np.hstack([np.ones((n, 1)), Xk])
        lam = 1.0 / (self.C * n)  # 對齊 sklearn 的 C

        w = np.zeros(pk + 1)
        history = []
        for it in range(self.max_iter):
            z = Xb @ w
            pr = sigmoid(z)
            # 梯度：資料部分 + 正則化部分 (intercept 不正則化)
            g = Xb.T @ (pr - y) / n
            g[1:] += lam * w[1:]
            # Hessian
            W = pr * (1.0 - pr)
            H = Xb.T @ (Xb * W[:, None]) / n
            H[1:, 1:] += lam * np.eye(pk)
            delta = np.linalg.lstsq(H, g, rcond=None)[0]
            w -= delta
            loss = -np.mean(
                y * np.log(pr + 1e-15) + (1 - y) * np.log(1 - pr + 1e-15)
            ) + 0.5 * lam * np.sum(w[1:] ** 2)
            history.append(loss)
            if np.linalg.norm(delta) < self.tol:
                break

        self.intercept_ = float(w[0])
        self.coef_ = np.zeros(p)
        self.coef_[self.keep_] = w[1:]
        self.n_iter_ = it + 1
        self.loss_history_ = history
        return self

    def decision_function(self, X):
        X = np.asarray(X, dtype=float)
        return X @ self.coef_ + self.intercept_

    def predict_proba(self, X):
        p = sigmoid(self.decision_function(X))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

    def fit_gradient_descent(self, X, y, lr=0.01, n_iter=5000):
        """以 batch gradient descent 求解 (供推導/收斂曲線展示)。"""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).ravel()
        n, p = X.shape
        keep = X.std(axis=0) > 0
        Xk = X[:, keep]
        pk = Xk.shape[1]
        Xb = np.hstack([np.ones((n, 1)), Xk])
        lam = 1.0 / (self.C * n)
        w = np.zeros(pk + 1)
        losses = []
        for _ in range(n_iter):
            z = Xb @ w
            pr = sigmoid(z)
            g = Xb.T @ (pr - y) / n
            g[1:] += lam * w[1:]
            w -= lr * g
            loss = -np.mean(
                y * np.log(pr + 1e-15) + (1 - y) * np.log(1 - pr + 1e-15)
            ) + 0.5 * lam * np.sum(w[1:] ** 2)
            losses.append(loss)
        self._gd_w = w
        self._gd_keep = keep
        self._gd_losses = losses
        return losses


def main():
    digits = load_digits()
    mask = (digits.target == 3) | (digits.target == 8)
    X = digits.data[mask].astype(float)
    y = (digits.target[mask] == 8).astype(int)
    print(f"樣本數: {X.shape[0]}, 特徵數: {X.shape[1]}, 類別比例 (8): {y.mean():.3f}")
    print(f"常數特徵數: {int((X.std(0) == 0).sum())}")

    # --- 係數比較：在全資料上擬合 ---
    manual = ManualLogisticRegression(C=1.0)
    manual.fit(X, y)
    sklearn_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=100000, tol=1e-12)
    sklearn_model.fit(X, y)

    sk_coef = np.concatenate([[sklearn_model.intercept_[0]], sklearn_model.coef_[0].ravel()])
    man_coef = np.concatenate([[manual.intercept_], manual.coef_])
    keep_idx = np.concatenate([[0], np.where(X.std(0) > 0)[0] + 1])
    diff = man_coef[keep_idx] - sk_coef[keep_idx]
    cos = np.dot(man_coef[keep_idx], sk_coef[keep_idx]) / (
        np.linalg.norm(man_coef[keep_idx]) * np.linalg.norm(sk_coef[keep_idx])
    )
    print("\n=== 係數比較 (非常數特徵) ===")
    print(f"Newton 迭代次數: {manual.n_iter_}")
    print(f"intercept 差異: {diff[0]:.3e}")
    print(f"係數最大絕對差異: {np.max(np.abs(diff[1:])):.3e}")
    print(f"係數 cosine 相似度: {cos:.10f}")

    # --- 預測比較 ---
    p_man = manual.predict_proba(X)[:, 1]
    p_sk = sklearn_model.predict_proba(X)[:, 1]
    pred_man = manual.predict(X)
    pred_sk = sklearn_model.predict(X)
    print("\n=== 預測比較 (全資料) ===")
    print(f"manual accuracy:  {accuracy_score(y, pred_man):.6f}")
    print(f"sklearn accuracy: {accuracy_score(y, pred_sk):.6f}")
    print(f"預測一致率: {np.mean(pred_man == pred_sk):.6f}")
    print(f"機率最大絕對差異: {np.max(np.abs(p_man - p_sk)):.3e}")
    print(f"機率 RMSE: {np.sqrt(np.mean((p_man - p_sk) ** 2)):.3e}")
    print(f"機率 Pearson r: {np.corrcoef(p_man, p_sk)[0, 1]:.10f}")

    # --- train/test split 評估 ---
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    m2 = ManualLogisticRegression(C=1.0).fit(Xtr, ytr)
    s2 = LogisticRegression(C=1.0, solver="lbfgs", max_iter=100000, tol=1e-12).fit(Xtr, ytr)
    print("\n=== 測試集 (20% hold-out) ===")
    print(f"manual test acc:  {accuracy_score(yte, m2.predict(Xte)):.6f}")
    print(f"sklearn test acc: {accuracy_score(yte, s2.predict(Xte)):.6f}")
    print(f"預測一致率: {np.mean(m2.predict(Xte) == s2.predict(Xte)):.6f}")

    # --- 混淆矩陣 ---
    cm_man = confusion_matrix(y, pred_man)
    cm_sk = confusion_matrix(y, pred_sk)
    print("\nmanual confusion matrix:\n", cm_man)
    print("sklearn confusion matrix:\n", cm_sk)

    # --- 圖 1：係數散點圖 ---
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(sk_coef[keep_idx], man_coef[keep_idx], s=20, alpha=0.7)
    lims = [min(sk_coef[keep_idx].min(), man_coef[keep_idx].min()),
            max(sk_coef[keep_idx].max(), man_coef[keep_idx].max())]
    ax.plot(lims, lims, "r--", lw=1)
    ax.set_xlabel("sklearn 係數")
    ax.set_ylabel("手刻 (Newton) 係數")
    ax.set_title(f"係數比較 (cosine={cos:.6f})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("figs/logistic_coef_compare.png", dpi=150)
    plt.close(fig)

    # --- 圖 2：GD 收斂曲線 ---
    gd_losses = ManualLogisticRegression(C=1.0).fit_gradient_descent(X, y, lr=0.01, n_iter=3000)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(gd_losses)
    ax.set_xlabel("iteration")
    ax.set_ylabel("loss (BCE + L2)")
    ax.set_title("Batch gradient descent 收斂曲線")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("figs/logistic_gd_loss.png", dpi=150)
    plt.close(fig)

    # --- 圖 3：機率散點 ---
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(p_sk, p_man, s=12, alpha=0.6)
    ax.plot([0, 1], [0, 1], "r--", lw=1)
    ax.set_xlabel("sklearn P(y=1)")
    ax.set_ylabel("手刻 P(y=1)")
    ax.set_title("預測機率比較")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("figs/logistic_proba_compare.png", dpi=150)
    plt.close(fig)

    print("\n圖檔已存到 figs/")


if __name__ == "__main__":
    main()
