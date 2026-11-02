"""手刻 logistic 迴歸（digits 3 vs 8），與 sklearn 比較。"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)

digits = load_digits()
mask = np.isin(digits.target, [3, 8])
X, y = digits.data[mask], (digits.target[mask] == 8).astype(float)

scaler = StandardScaler()
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 加截距
def add_bias(X):
    return np.hstack([X, np.ones((X.shape[0], 1))])

Xb_train, Xb_test = add_bias(X_train), add_bias(X_test)

# ---- 手刻：牛頓法 + L2 正則化（與 sklearn 預設 penalty='l2', C=1 對齊）----
# 目標函數：J(w) = -(1/n) sum[y log p + (1-y) log(1-p)] + w^T w / (2 n)
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

lam = 1.0 / (1.0 * len(y_train))   # sklearn 的 L2 項 = w^T w / (2*C*n)，不懲罰截距
w = np.zeros(Xb_train.shape[1])
reg_mask = np.ones(len(w)); reg_mask[-1] = 0.0   # 截距（最後一維）不加入正則化
for it in range(100):
    p = sigmoid(Xb_train @ w)
    grad = Xb_train.T @ (p - y_train) / len(y_train) + lam * reg_mask * w
    H = (Xb_train.T @ (Xb_train * (p * (1 - p))[:, None])) / len(y_train) + lam * np.diag(reg_mask)
    step = np.linalg.solve(H, grad)
    w -= step
    if np.linalg.norm(step) < 1e-12:
        break

y_prob_hand = sigmoid(Xb_test @ w)
y_pred_hand = (y_prob_hand >= 0.5).astype(int)
acc_hand = (y_pred_hand == y_test).mean()

nll_hand = -np.mean(
    y_test * np.log(y_prob_hand + 1e-15)
    + (1 - y_test) * np.log(1 - y_prob_hand + 1e-15)
)

# ---- sklearn：預設 penalty='l2', C=1，與手刻同一個目標函數 ----
clf = LogisticRegression(max_iter=1_000_000, tol=1e-15)
clf.fit(X_train, y_train)
w_sk = np.append(clf.coef_[0], clf.intercept_[0])

y_prob_sk = clf.predict_proba(X_test)[:, 1]
acc_sk = clf.score(X_test, y_test)
nll_sk = -np.mean(
    y_test * np.log(y_prob_sk + 1e-15)
    + (1 - y_test) * np.log(1 - y_prob_sk + 1e-15)
)

print(f"手刻牛頓法收斂迭代數: {it + 1}")
print(f"\n||w_hand - w_sk||_2 = {np.linalg.norm(w - w_sk):.3e}")
print(f"max |w_hand - w_sk| = {np.max(np.abs(w - w_sk)):.3e}")
print(f"corr(w_hand, w_sk)  = {np.corrcoef(w, w_sk)[0, 1]:.8f}")
print(f"\n手刻 accuracy = {acc_hand:.4f}, sklearn accuracy = {acc_sk:.4f}")
print(f"手刻 log-loss = {nll_hand:.6f}, sklearn log-loss = {nll_sk:.6f}")

# 用 train 集上的目標函數值比（比 test 更能判斷「解到同一個點」）
p_tr_h = sigmoid(Xb_train @ w)
p_tr_s = clf.predict_proba(X_train)[:, 1]
nll_tr_h = -np.mean(y_train * np.log(p_tr_h) + (1 - y_train) * np.log(1 - p_tr_h))
nll_tr_s = -np.mean(y_train * np.log(p_tr_s) + (1 - y_train) * np.log(1 - p_tr_s))
print(f"\ntrain NLL  手刻 = {nll_tr_h:.10f}, sklearn = {nll_tr_s:.10f}, 差 = {abs(nll_tr_h - nll_tr_s):.2e}")

np.save("figs/w_hand.npy", w)
np.save("figs/w_sk.npy", w_sk)
