import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, confusion_matrix, roc_auc_score, roc_curve

# ---------------- 資料：digits 3 vs 8 ----------------
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask].astype(float)
y = (digits.target[mask] == 8).astype(int)   # 8 -> 1, 3 -> 0

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

sc = StandardScaler()
Xtr_s = sc.fit_transform(Xtr)
Xte_s = sc.transform(Xte)

n, d = Xtr_s.shape
C = 1.0  # sklearn default

# ---------------- sklearn ----------------
sk = LogisticRegression(l1_ratio=0, C=C, solver="lbfgs", max_iter=10000, tol=1e-12)
sk.fit(Xtr_s, ytr)
w_sk = sk.coef_.ravel()
b_sk = float(sk.intercept_[0])
psk_tr = sk.predict_proba(Xtr_s)[:, 1]
psk_te = sk.predict_proba(Xte_s)[:, 1]

# ---------------- 手刻：L2 正則化 logistic，Newton (IRLS) ----------------
# 目標與 sklearn 對齊：min 0.5||w||^2 + C * sum_i log(1+exp(-y_i z_i))
# 等價 mean 形式：mean logloss + (1/(2 C n))||w||^2
lam = 1.0 / (C * n)          # 對 w 的 L2 係數 (gradient 加 lam*w)
Xb = np.column_stack([Xtr_s, np.ones(n)])   # [X, 1]，bias 不正則化

def sigmoid(z):
    return np.where(z >= 0, 1/(1+np.exp(-z)), np.exp(z)/(1+np.exp(z)))

beta = np.zeros(d + 1)
for it in range(50):
    z = Xb @ beta
    p = sigmoid(z)
    # gradient (mean form): Xb^T(p-y)/n + lam*[w;0]
    g = Xb.T @ (p - ytr) / n
    g[:d] += lam * beta[:d]
    # Hessian: Xb^T diag(p(1-p)) Xb / n + lam*diag([1..1,0])
    W = p * (1 - p)
    H = (Xb.T * W) @ Xb / n
    H[:d, :d] += lam * np.eye(d)
    step = np.linalg.solve(H, g)
    beta -= step
    if np.linalg.norm(step) < 1e-12:
        break

w_hand = beta[:d]
b_hand = float(beta[d])
ph_tr = sigmoid(Xtr_s @ w_hand + b_hand)
ph_te = sigmoid(Xte_s @ w_hand + b_hand)

# ---------------- 比較 ----------------
print("=== sklearn ===")
print("train acc", accuracy_score(ytr, sk.predict(Xtr_s)),
      "test acc", accuracy_score(yte, sk.predict(Xte_s)))
print("train loss", log_loss(ytr, psk_tr), "test loss", log_loss(yte, psk_te))
print("AUC test", roc_auc_score(yte, psk_te))
print("=== hand (Newton, L2 aligned) ===")
print("train acc", accuracy_score(ytr, (ph_tr >= 0.5).astype(int)),
      "test acc", accuracy_score(yte, (ph_te >= 0.5).astype(int)))
print("train loss", log_loss(ytr, np.clip(ph_tr, 1e-15, 1-1e-15)),
      "test loss", log_loss(yte, np.clip(ph_te, 1e-15, 1-1e-15)))
print("AUC test", roc_auc_score(yte, ph_te))
print("=== 差異 ===")
print("max |w diff|", np.max(np.abs(w_hand - w_sk)))
print("||w diff||2", np.linalg.norm(w_hand - w_sk))
print("|b diff|", abs(b_hand - b_sk))
print("max |p diff train|", np.max(np.abs(ph_tr - psk_tr)))
print("max |p diff test|", np.max(np.abs(ph_te - psk_te)))
print("pred agreement train", np.mean((ph_tr>=0.5)==(psk_tr>=0.5)))
print("pred agreement test", np.mean((ph_te>=0.5)==(psk_te>=0.5)))

# ---------------- 圖 ----------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
# 係數圖
vmax = max(np.abs(w_sk).max(), np.abs(w_hand).max())
for ax, w, title in zip(axes[:2], [w_sk, w_hand], ["sklearn weights", "hand weights"]):
    im = ax.imshow(w.reshape(8, 8), cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax.set_title(title); ax.axis("off")
    plt.colorbar(im, ax=ax, fraction=0.046)
# 機率散佈
axes[2].scatter(psk_te, ph_te, s=12, alpha=0.6)
axes[2].plot([0, 1], [0, 1], "k--", lw=1)
axes[2].set_xlabel("sklearn p"); axes[2].set_ylabel("hand p")
axes[2].set_title("test proba scatter")
fig.tight_layout()
fig.savefig("figs/logistic_weights_proba.png", dpi=150)
plt.close(fig)

# ROC
fpr_s, tpr_s, _ = roc_curve(yte, psk_te)
fpr_h, tpr_h, _ = roc_curve(yte, ph_te)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr_s, tpr_s, label="sklearn")
ax.plot(fpr_h, tpr_h, label="hand", linestyle="--")
ax.plot([0, 1], [0, 1], "k:", lw=1)
ax.set_xlabel("FPR"); ax.set_ylabel("TPR"); ax.set_title("ROC (test)")
ax.legend()
fig.tight_layout()
fig.savefig("figs/logistic_roc.png", dpi=150)
plt.close(fig)

# confusion matrices
print("sklearn cm (test):\n", confusion_matrix(yte, sk.predict(Xte_s)))
print("hand   cm (test):\n", confusion_matrix(yte, (ph_te >= 0.5).astype(int)))
