"""二元 logistic 迴歸手刻（lab3）— 資料定義 + loss(w) + grad(w) + 有限差分梯度檢查。

損失函數衡量什麼：L(w) = (1/n) Σ [log(1+e^z) - y z] 是「平均負對數概似」，
衡量模型用權重 w 對資料預測得多準、多有把握——分數愈低，預測愈貼近真實標籤。
梯度告訴我們什麼：∇L(w) = (1/n) Xb^T (σ(Xb w) - y) 是損失在 w 處上升最快的方向，
各分量代表「把該權重調高一點，損失會增加多少」；負梯度是損失下降最快的方向。

推導（單樣本 z = x^T w，y ∈ {0,1}）：
p(y|x) = σ(z)^y (1-σ(z))^(1-y)
-log likelihood = y log σ(z) + (1-y) log(1-σ(z))
                = y[-log(1+e^{-z})] + (1-y)[-log(1+e^z)]
                = y[log(1+e^z) - z] + (1-y) log(1+e^z)
                = log(1+e^z) - y z
∂/∂w_j [-log p] = (σ(z) - y) x_j  →  ∇L = (1/n) Xb^T (σ(Xb w) - y)
"""
import numpy as np
from sklearn.datasets import load_digits


def sigmoid(z):
    """數值穩定的 sigmoid：z 很大用 1/(1+e^{-z})，z 很小用 e^z/(1+e^z)。"""
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    out[~pos] = np.exp(z[~pos]) / (1.0 + np.exp(z[~pos]))
    return out


def loss(w, Xb, y):
    """L(w) = (1/n) Σ [log(1+e^z) - y z]，z = Xb w，取平均。"""
    z = Xb @ w
    return np.mean(np.logaddexp(0.0, z) - y * z)


def grad(w, Xb, y):
    """∇L(w) = (1/n) Xb^T (σ(Xb w) - y)。"""
    z = Xb @ w
    return (Xb.T @ (sigmoid(z) - y)) / len(y)


def finite_diff_grad(f, w, h):
    """中央差分梯度：g_j = (f(w+h e_j) - f(w-h e_j)) / (2h)。"""
    g = np.zeros_like(w)
    for j in range(w.size):
        e = np.zeros_like(w)
        e[j] = 1.0
        g[j] = (f(w + h * e) - f(w - h * e)) / (2.0 * h)
    return g


# ---------- 資料定義：全部 digits 的 3 與 8 ----------
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
Xpix = digits.data[mask] / 16.0                      # 像素除以 16
y = (digits.target[mask] == 8).astype(float)         # 8 設為 1、3 設為 0
Xb = np.hstack([np.ones((Xpix.shape[0], 1)), Xpix])  # 加一欄 1 當截距
n, d = Xb.shape
print(f"Xb shape = {Xb.shape}  (n={n}, d={d})")


# ---------- 有限差分梯度檢查（中央差分，全部 65 維） ----------
w0 = np.random.RandomState(0).normal(size=d) * 0.01
print(f"檢查點 w0 = {np.array2string(w0, precision=6)}")

g_anal = grad(w0, Xb, y)
print("\n      h       max|Δg|      max rel err   判定")
for h in np.logspace(-2, -9, 8):
    g_num = finite_diff_grad(lambda w: loss(w, Xb, y), w0, h)
    abs_err = np.max(np.abs(g_num - g_anal))
    rel_err = np.max(np.abs(g_num - g_anal) / np.maximum(np.abs(g_anal), 1e-12))
    verdict = "PASS" if abs_err < 1e-8 else "需調查"
    print(f"{h:9.1e}  {abs_err:12.3e}  {rel_err:12.3e}  {verdict}")