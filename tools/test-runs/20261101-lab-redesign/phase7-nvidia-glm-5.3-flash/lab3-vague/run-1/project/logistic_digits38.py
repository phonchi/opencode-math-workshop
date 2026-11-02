"""在 sklearn digits 的 3 與 8 上手刻 logistic 迴歸（GD + Newton/IRLS），
與 sklearn.linear_model.LogisticRegression 比較。

Phase A：無正則化。訓練集可分離 -> MLE 不存在（theta 沿分離方向發散），
         兩個 solver 只是停在不同地方，係數比較無意義。
Phase B：兩邊使用完全相同的 L2 正則（sklearn C=1.0，對應
         lambda = 1/(C*n)，bias 不正則）。目標強凸、解唯一，
         手刻 Newton 應與 sklearn 完全吻合。
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import expit
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split

RNG = 42

# --------------------------------------------------------------- 資料
X_all, y_all = load_digits(return_X_y=True)
mask = (y_all == 3) | (y_all == 8)
X = X_all[mask] / 16.0                      # 像素 0~16 -> [0,1]，兩邊用同一份
y = (y_all[mask] == 8).astype(float)        # 正類 = 8

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, random_state=RNG, stratify=y
)

# 設計矩陣補一欄 1，把 bias 併進 theta，theta = [w ; b]
Xt = np.hstack([X_tr, np.ones((len(y_tr), 1))])
Xs = np.hstack([X_te, np.ones((len(y_te), 1))])
n, d = Xt.shape
reg_mask = np.r_[np.ones(d - 1), 0.0]       # bias 不正則
print(f"n_train={len(y_tr)}  n_test={len(y_te)}  d={d} (含 bias)  "
      f"常數(全 0)特徵數={int(np.sum(np.ptp(X_tr, axis=0) == 0))}")


# --------------------------------------------------------------- 手刻目標函數（可切換正則）
def make_problem(lam):
    def loss(theta):
        p = np.clip(expit(Xt @ theta), 1e-12, 1 - 1e-12)
        ce = -np.mean(y_tr * np.log(p) + (1 - y_tr) * np.log(1 - p))
        return ce + 0.5 * lam * np.sum(reg_mask * theta**2)

    def grad(theta):
        g = Xt.T @ (expit(Xt @ theta) - y_tr) / n
        return g + lam * reg_mask * theta

    def hess(theta):
        p = expit(Xt @ theta)
        H = (Xt * (p * (1 - p))[:, None]).T @ Xt / n
        return H + lam * np.diag(reg_mask)

    return loss, grad, hess


def fit_gd(grad, loss, lam, max_iter=1000000, tol=1e-9):
    """梯度下降，步長 1/L，L = lambda_max(X^T X)/(4n) + lambda。"""
    L = np.linalg.eigvalsh(Xt.T @ Xt / (4 * n))[-1] + lam
    eta = 1.0 / L
    theta = np.zeros(d)
    hist = [loss(theta)]
    for k in range(1, max_iter + 1):
        g = grad(theta)
        theta -= eta * g
        hist.append(loss(theta))
        if np.linalg.norm(g) < tol:
            break
    return theta, np.array(hist), k


def fit_newton(grad, loss, hess, max_iter=50, tol=1e-12):
    """Newton 法（即 IRLS），附簡單回溯線搜尋保險。"""
    theta = np.zeros(d)
    for k in range(1, max_iter + 1):
        g = grad(theta)
        if np.linalg.norm(g) < tol:
            break
        step = np.linalg.lstsq(hess(theta), -g, rcond=None)[0]
        t = 1.0
        while t > 2.0**-30 and loss(theta + t * step) > loss(theta):
            t /= 2.0
        theta = theta + t * step
    return theta, k


def evaluate(name, loss, grad, theta):
    p_te = expit(Xs @ theta)
    y_hat = (p_te >= 0.5).astype(int)
    print(f"{name:<12s} train_loss={loss(theta):.6e}  "
          f"grad_norm={np.linalg.norm(grad(theta)):.2e}  "
          f"||theta||={np.linalg.norm(theta):.3f}  "
          f"test_acc={accuracy_score(y_te, y_hat):.4f}  "
          f"test_logloss={log_loss(y_te, p_te, labels=[0, 1]):.6f}  "
          f"test_auc={roc_auc_score(y_te, p_te):.6f}")
    return p_te


def compare(name, theta, p, theta_ref, p_ref):
    rel = np.linalg.norm(theta - theta_ref) / np.linalg.norm(theta_ref)
    print(f"{name:<12s} vs sklearn: 相對係數誤差={rel:.3e}  "
          f"max|Δtheta|={np.max(np.abs(theta - theta_ref)):.3e}  "
          f"max|Δp|={np.max(np.abs(p - p_ref)):.3e}  "
          f"預測不一致比例={np.mean((p >= 0.5) != (p_ref >= 0.5)):.3f}")


# =============================================================== Phase A：無正則化
print("\n===== Phase A：無正則化（可分離資料，MLE 不存在）=====")
loss0, grad0, hess0 = make_problem(lam=0.0)
theta_nt0, it0 = fit_newton(grad0, loss0, hess0, max_iter=40, tol=1e-14)
sk0 = LogisticRegression(C=np.inf, max_iter=20000, tol=1e-10)
sk0.fit(X_tr, y_tr)
theta_sk0 = np.r_[sk0.coef_[0], sk0.intercept_[0]]
p_nt0 = evaluate("Newton(unreg)", loss0, grad0, theta_nt0)
p_sk0 = evaluate("sklearn(C=inf)", loss0, grad0, theta_sk0)
compare("Newton(unreg)", theta_nt0, p_nt0, theta_sk0, p_sk0)

# =============================================================== Phase B：相同 L2 正則
print("\n===== Phase B：sklearn 預設 L2, C=1.0（lambda = 1/(C*n)）=====")
C = 1.0
lam = 1.0 / (C * n)
print(f"lambda = 1/(C*n) = {lam:.6e}")
loss1, grad1, hess1 = make_problem(lam=lam)
theta_nt, it_nt = fit_newton(grad1, loss1, hess1)
theta_gd, gd_hist, it_gd = fit_gd(grad1, loss1, lam)
sk = LogisticRegression(max_iter=20000, tol=1e-10)   # 預設 l2, C=1.0
sk.fit(X_tr, y_tr)
theta_sk = np.r_[sk.coef_[0], sk.intercept_[0]]
print(f"GD 迭代 {it_gd} 次；Newton 迭代 {it_nt} 次；sklearn lbfgs n_iter_={sk.n_iter_[0]}\n")
p_gd = evaluate("GD", loss1, grad1, theta_gd)
p_nt = evaluate("Newton", loss1, grad1, theta_nt)
p_sk = evaluate("sklearn", loss1, grad1, theta_sk)
print()
compare("GD", theta_gd, p_gd, theta_sk, p_sk)
compare("Newton", theta_nt, p_nt, theta_sk, p_sk)
print(f"我的目標函數在 sklearn 解上的梯度範數: {np.linalg.norm(grad1(theta_sk)):.3e}")

# --------------------------------------------------------------- 圖（Phase B）
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

axes[0].semilogy(gd_hist, lw=2, label="hand-coded GD")
axes[0].axhline(loss1(theta_sk), color="tab:red", ls="--", label="sklearn (lbfgs)")
axes[0].set_xlabel("iteration")
axes[0].set_ylabel("objective J(theta)")
axes[0].set_title("GD convergence (L2, C=1)")
axes[0].legend()

axes[1].scatter(p_sk, p_nt, s=18, c=y_te, cmap="coolwarm", alpha=0.8)
axes[1].plot([0, 1], [0, 1], "k--", lw=1)
axes[1].set_xlabel("sklearn  P(y=8|x)")
axes[1].set_ylabel("hand-coded  P(y=8|x)")
axes[1].set_title("test probabilities (Newton)")

axes[2].scatter(theta_sk, theta_nt, s=18, alpha=0.8)
lims = [min(theta_sk.min(), theta_nt.min()), max(theta_sk.max(), theta_nt.max())]
axes[2].plot(lims, lims, "k--", lw=1)
axes[2].set_xlabel("sklearn  theta")
axes[2].set_ylabel("hand-coded  theta")
axes[2].set_title("coefficients (incl. bias)")

fig.tight_layout()
fig.savefig("figs/logistic_digits38_comparison.png", dpi=150)
print("\n已存圖 figs/logistic_digits38_comparison.png")
