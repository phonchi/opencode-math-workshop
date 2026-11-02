"""手刻 logistic regression（digits 3 vs 8）並與 sklearn 對照。

執行：uv run python logreg_digits.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figs"
FIG_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42


# ---------------------------------------------------------------------------
# 手刻模型：sigmoid、損失、梯度、Hessian、GD、Newton/IRLS
# ---------------------------------------------------------------------------
def sigmoid(z):
    z = np.asarray(z, dtype=float)
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def add_intercept(X):
    return np.column_stack([np.ones(X.shape[0]), X])


def loss_grad_hess(w, X, y, lam=0.0):
    """平均 NLL + (lam/2)||w_1:||^2，截距不懲罰。

    X 已含截距欄。回傳 (loss, grad, Hessian)。
    """
    n = X.shape[0]
    z = X @ w
    # log(1 + exp(z)) - y*z，數值穩定版
    loss = np.mean(np.logaddexp(0.0, z) - y * z)
    loss += 0.5 * lam * np.dot(w[1:], w[1:])

    p = sigmoid(z)
    grad = X.T @ (p - y) / n
    grad[1:] += lam * w[1:]

    s = p * (1.0 - p)
    H = (X.T * s) @ X / n
    H[1:, 1:] += lam * np.eye(X.shape[1] - 1)
    return loss, grad, H


def fit_newton(X, y, lam=0.0, max_iter=100, tol=1e-12):
    """Newton / IRLS with backtracking line search。"""
    w = np.zeros(X.shape[1])
    losses, grad_norms = [], []
    for _ in range(max_iter):
        loss, grad, H = loss_grad_hess(w, X, y, lam)
        losses.append(loss)
        gnorm = np.linalg.norm(grad)
        grad_norms.append(gnorm)
        if gnorm < tol:
            break
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, grad, rcond=None)[0]

        # backtracking：確保 loss 真的下降
        alpha = 1.0
        while alpha > 1e-12:
            w_new = w - alpha * step
            loss_new, _, _ = loss_grad_hess(w_new, X, y, lam)
            if loss_new <= loss - 1e-4 * alpha * np.dot(grad, step):
                break
            alpha *= 0.5
        w = w_new
    else:
        loss, grad, _ = loss_grad_hess(w, X, y, lam)
        losses.append(loss)
        grad_norms.append(np.linalg.norm(grad))
    return w, np.array(losses), np.array(grad_norms)


def fit_gd(X, y, lam=0.0, lr=1.0, n_iter=20000, tol=1e-12):
    """全批量梯度下降（標準化特徵後使用）。"""
    w = np.zeros(X.shape[1])
    losses, grad_norms = [], []
    for _ in range(n_iter):
        loss, grad, _ = loss_grad_hess(w, X, y, lam)
        losses.append(loss)
        gnorm = np.linalg.norm(grad)
        grad_norms.append(gnorm)
        if gnorm < tol:
            break
        w = w - lr * grad
    return w, np.array(losses), np.array(grad_norms)


# ---------------------------------------------------------------------------
# 比較工具
# ---------------------------------------------------------------------------
def compare(name, w_hand, w_sk, X, y):
    """比較兩組參數在同一份資料上的預測。"""
    dh = X @ w_hand
    ds = X @ w_sk
    ph = sigmoid(dh)
    ps = sigmoid(ds)
    yh = (ph >= 0.5).astype(int)
    ys = (ps >= 0.5).astype(int)
    return {
        "name": name,
        "max_abs_coef_diff": float(np.max(np.abs(w_hand[1:] - w_sk[1:]))),
        "intercept_diff": float(abs(w_hand[0] - w_sk[0])),
        "max_abs_logit_diff": float(np.max(np.abs(dh - ds))),
        "max_abs_proba_diff": float(np.max(np.abs(ph - ps))),
        "n_pred_diff": int(np.sum(yh != ys)),
        "n": int(len(y)),
        "acc_hand": float(accuracy_score(y, yh)),
        "acc_sklearn": float(accuracy_score(y, ys)),
        "auc_hand": float(roc_auc_score(y, ph)),
        "auc_sklearn": float(roc_auc_score(y, ps)),
        "logloss_hand": float(log_loss(y, ph)),
        "logloss_sklearn": float(log_loss(y, ps)),
    }


def print_report(rows):
    hdr = (
        f"{'比較':<20}{'max|Δw|':>11}{'|Δb|':>10}{'max|Δz|':>11}"
        f"{'max|Δp|':>11}{'預測不同':>11}{'acc(hand/sk)':>20}"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['name']:<20}{r['max_abs_coef_diff']:>11.3e}"
            f"{r['intercept_diff']:>10.3e}{r['max_abs_logit_diff']:>11.3e}"
            f"{r['max_abs_proba_diff']:>11.3e}"
            f"{r['n_pred_diff']:>7d}/{r['n']:<3d}"
            f"{r['acc_hand']:>9.4f}/{r['acc_sklearn']:<9.4f}"
        )


# ---------------------------------------------------------------------------
def main():
    digits = load_digits()
    mask = np.isin(digits.target, [3, 8])
    X_raw = digits.data[mask]
    y = (digits.target[mask] == 8).astype(int)  # 1 = 數字 8

    X_tr, X_te, y_tr, y_te = train_test_split(
        X_raw, y, test_size=0.3, stratify=y, random_state=RANDOM_STATE
    )
    scaler = StandardScaler().fit(X_tr)
    Xtr = scaler.transform(X_tr)
    Xte = scaler.transform(X_te)
    Xtr_i = add_intercept(Xtr)
    Xte_i = add_intercept(Xte)
    n_tr = len(y_tr)

    print(f"資料：3 vs 8，train={n_tr}，test={len(y_te)}，特徵={X_raw.shape[1]}")
    print(f"train 類別比例（8 的比例）={y_tr.mean():.3f}")

    # ------------------------------------------------------------------
    # 1) 主要對照：L2 正則化，對應 sklearn 預設 C=1
    # ------------------------------------------------------------------
    C = 1.0
    lam = 1.0 / (n_tr * C)
    w_l2, loss_l2, grad_l2 = fit_newton(Xtr_i, y_tr, lam=lam)
    sk_l2 = LogisticRegression(
        C=C, solver="lbfgs", max_iter=100000, tol=1e-12
    ).fit(Xtr, y_tr)
    w_sk_l2 = np.r_[sk_l2.intercept_[0], sk_l2.coef_[0]]

    # ------------------------------------------------------------------
    # 2) 無正則化 MLE（64 維）。這份資料線性可分，MLE 不存在，僅示範。
    # ------------------------------------------------------------------
    w_mle, loss_mle, grad_mle = fit_newton(Xtr_i, y_tr, lam=0.0)
    sk_mle = LogisticRegression(
        C=np.inf, solver="lbfgs", max_iter=100000, tol=1e-12
    ).fit(Xtr, y_tr)
    w_sk_mle = np.r_[sk_mle.intercept_[0], sk_mle.coef_[0]]

    # ------------------------------------------------------------------
    # 3) 無正則化但降到 3 維 PCA，讓 MLE 存在，用來驗證 lam=0 的實作。
    # ------------------------------------------------------------------
    pca3 = PCA(n_components=3, random_state=RANDOM_STATE).fit(Xtr)
    Ptr, Pte = pca3.transform(Xtr), pca3.transform(Xte)
    Ptr_i, Pte_i = add_intercept(Ptr), add_intercept(Pte)
    w_pca, loss_pca, grad_pca = fit_newton(Ptr_i, y_tr, lam=0.0)
    sk_pca = LogisticRegression(
        C=np.inf, solver="lbfgs", max_iter=100000, tol=1e-12
    ).fit(Ptr, y_tr)
    w_sk_pca = np.r_[sk_pca.intercept_[0], sk_pca.coef_[0]]

    # ------------------------------------------------------------------
    # 4) 手刻 GD，解同一個 L2 問題
    # ------------------------------------------------------------------
    w_gd, loss_gd, grad_gd = fit_gd(Xtr_i, y_tr, lam=lam, lr=1.0, n_iter=20000)

    rows = [
        compare("L2 C=1（主對照）", w_l2, w_sk_l2, Xte_i, y_te),
        compare("GD(L2) vs sklearn", w_gd, w_sk_l2, Xte_i, y_te),
        compare("PCA3 MLE（可辨識）", w_pca, w_sk_pca, Pte_i, y_te),
        compare("64D MLE（不可辨識）", w_mle, w_sk_mle, Xte_i, y_te),
    ]
    print()
    print_report(rows)

    # 訓練/測試指標
    print("\n模型品質（test）：")
    for label, w, X in [
        ("L2 C=1", w_l2, Xte_i),
        ("GD(L2)", w_gd, Xte_i),
        ("PCA3 MLE", w_pca, Pte_i),
    ]:
        p = sigmoid(X @ w)
        pred = (p >= 0.5).astype(int)
        print(
            f"  {label:<9} acc={accuracy_score(y_te, pred):.4f}  "
            f"logloss={log_loss(y_te, p):.4f}  auc={roc_auc_score(y_te, p):.4f}"
        )

    # 目標函數與梯度
    obj_l2 = loss_grad_hess(w_l2, Xtr_i, y_tr, lam)[0]
    obj_sk_l2 = loss_grad_hess(w_sk_l2, Xtr_i, y_tr, lam)[0]
    obj_mle = loss_grad_hess(w_mle, Xtr_i, y_tr, 0.0)[0]
    obj_sk_mle = loss_grad_hess(w_sk_mle, Xtr_i, y_tr, 0.0)[0]
    print("\n目標函數（train）：")
    print(
        f"  L2 C=1  hand={obj_l2:.12f}  sklearn={obj_sk_l2:.12f}  "
        f"diff={abs(obj_l2 - obj_sk_l2):.3e}"
    )
    print(
        f"  64D MLE hand={obj_mle:.3e}  sklearn={obj_sk_mle:.3e}  "
        f"diff={abs(obj_mle - obj_sk_mle):.3e}"
    )
    print(
        f"  64D MLE ||w||: hand={np.linalg.norm(w_mle[1:]):.3f}  "
        f"sklearn={np.linalg.norm(w_sk_mle[1:]):.3f}（線性可分 → 不唯一）"
    )
    print(
        f"  GD 最終 |grad|={grad_gd[-1]:.3e}；"
        f"Newton(L2) |grad|={np.linalg.norm(loss_grad_hess(w_l2, Xtr_i, y_tr, lam)[1]):.3e}"
    )

    cm = confusion_matrix(y_te, (sigmoid(Xte_i @ w_l2) >= 0.5).astype(int))
    print("\nL2 C=1 混淆矩陣（test，列=真實 0/1，欄=預測 0/1）：")
    print(cm)

    # ------------------------------------------------------------------
    # 圖 1：GD / Newton 收斂
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(loss_gd, label=f"GD (lr=1.0, {len(loss_gd)} iters)")
    axes[0].axhline(
        loss_l2[-1],
        color="tab:orange",
        ls="--",
        label=f"Newton ({len(loss_l2) - 1} iters)",
    )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("iteration")
    axes[0].set_ylabel("objective (log scale)")
    axes[0].set_title("Convergence on the L2 problem")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(grad_gd, label="GD")
    axes[1].axhline(1e-12, color="tab:orange", ls="--", label=r"tolerance $10^{-12}$")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("iteration")
    axes[1].set_ylabel(r"$\|\nabla L\|_2$")
    axes[1].set_title("Gradient norm")
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "logreg_convergence.png", dpi=150)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 圖 2：係數與測試機率對照（L2 C=1）
    # ------------------------------------------------------------------
    p_hand = sigmoid(Xte_i @ w_l2)
    p_sk = sigmoid(Xte_i @ w_sk_l2)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].scatter(w_sk_l2[1:], w_l2[1:], s=14, alpha=0.75)
    lo = min(w_sk_l2[1:].min(), w_l2[1:].min()) - 0.1
    hi = max(w_sk_l2[1:].max(), w_l2[1:].max()) + 0.1
    axes[0].plot([lo, hi], [lo, hi], "k--", lw=1)
    axes[0].set_xlabel("sklearn coefficient")
    axes[0].set_ylabel("hand-coded coefficient")
    axes[0].set_title(r"L2, $C=1$: coefficients")
    axes[0].grid(alpha=0.3)

    axes[1].scatter(p_sk, p_hand, s=22, alpha=0.8)
    axes[1].plot([0, 1], [0, 1], "k--", lw=1)
    axes[1].set_xlabel("sklearn P(8 | x)")
    axes[1].set_ylabel("hand-coded P(8 | x)")
    axes[1].set_title("L2, test predicted probabilities")
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "logreg_coef_compare.png", dpi=150)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 圖 3：PCA 2D 投影 + 決策邊界（以 L2 為例）
    # ------------------------------------------------------------------
    pca = PCA(n_components=2, random_state=RANDOM_STATE).fit(Xtr)
    Ztr = pca.transform(Xtr)
    Zte = pca.transform(Xte)
    # 原 64 維空間的線性邊界，投影到前兩個主成分
    V = pca.components_.T
    w2 = V.T @ w_l2[1:]
    b2 = w_l2[0] + pca.mean_ @ w_l2[1:]

    xx, yy = np.meshgrid(
        np.linspace(Ztr[:, 0].min() - 2, Ztr[:, 0].max() + 2, 300),
        np.linspace(Ztr[:, 1].min() - 2, Ztr[:, 1].max() + 2, 300),
    )
    prob = sigmoid(w2[0] * xx + w2[1] * yy + b2)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    cs = ax.contourf(
        xx, yy, prob, levels=np.linspace(0, 1, 21), cmap="RdBu_r", alpha=0.45
    )
    fig.colorbar(cs, ax=ax, label="P(8 | x) (PCA subspace)")
    ax.contour(xx, yy, prob, levels=[0.5], colors="k", linewidths=1.5)
    ax.scatter(
        Ztr[y_tr == 0, 0],
        Ztr[y_tr == 0, 1],
        s=22,
        c="tab:blue",
        edgecolor="w",
        label="3 (train)",
    )
    ax.scatter(
        Ztr[y_tr == 1, 0],
        Ztr[y_tr == 1, 1],
        s=22,
        c="tab:red",
        edgecolor="w",
        label="8 (train)",
    )
    ax.scatter(
        Zte[:, 0], Zte[:, 1], s=42, facecolors="none", edgecolors="k", label="test"
    )
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_title("Decision boundary projected onto PCA subspace")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "logreg_pca_boundary.png", dpi=150)
    plt.close(fig)

    print(f"\n圖已存到 {FIG_DIR}")


if __name__ == "__main__":
    main()
