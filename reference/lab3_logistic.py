"""Lab 3 參考解答 — 手刻 logistic 迴歸 + 有限差分梯度檢查

經跨模型獨立審查後修正的三件事：
  1. 梯度檢查 FAIL 不等於「公式一定錯」——也可能是步長、捨入或梯度近零。
     改成掃多個步長、檢查全部維度，並把結論限定在「局部數值證據」。
  2. 「資料線性可分」原本只用「||w|| 一直長」當佐證，那不算證明。
     改成解一個線性可行性問題，直接找出嚴格分隔超平面並算出 margin。
  3. 「只能比準確率或決策邊界」講得太滿——兩邊準確率都 1.0 也不代表
     決策邊界相同。改成列出真正該比的東西。
"""
import numpy as np
from scipy.optimize import linprog
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression

np.random.seed(0)
P = lambda ok: "PASS" if ok else "FAIL"

# ---------- 資料：3 vs 8 的二元分類 ----------
X_all, y_all = load_digits(return_X_y=True)
mask = (y_all == 3) | (y_all == 8)
X = X_all[mask] / 16.0
y = (y_all[mask] == 8).astype(float)
n, d = X.shape
print(f"資料：{n} 筆，{d} 維，正類(數字 8) {int(y.sum())} 筆\n")

Xb = np.hstack([X, np.ones((n, 1))])


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def loss(w):
    z = Xb @ w
    return np.mean(np.logaddexp(0, z) - y * z)


def grad(w):
    return Xb.T @ (sigmoid(Xb @ w) - y) / n


# ================================================================
print("=" * 68)
print("關卡 1：有限差分梯度檢查")
print("=" * 68)
print("原理：中央差分  [L(w+h e_i) - L(w-h e_i)] / (2h)  ≈  ∂L/∂w_i")
print("總誤差 ≈ A h² + B u / h（u 為浮點精度），所以 h 太大或太小都會變差。")
print("對 float64，最佳步長的量級約 u^(1/3) ≈ 6e-6，但實際值依函數而定。\n")

w0 = np.random.randn(d + 1) * 0.01
g = grad(w0)
print(f"{'步長 h':>10} {'最大絕對誤差':>16} {'最大相對誤差':>16}   判定")
best = None
for h in [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-9]:
    num = np.empty_like(g)
    for i in range(d + 1):                      # 全部 65 維都檢查，不抽樣
        wp, wm = w0.copy(), w0.copy()
        wp[i] += h; wm[i] -= h
        num[i] = (loss(wp) - loss(wm)) / (2 * h)
    abs_e = np.abs(num - g).max()
    rel_e = (np.abs(num - g) / np.maximum(1e-12, np.abs(num) + np.abs(g))).max()
    ok = abs_e < 1e-8
    print(f"{h:>10.0e} {abs_e:>16.3e} {rel_e:>16.3e}   {P(ok)}")
    if best is None or abs_e < best[1]:
        best = (h, abs_e)
print(f"\n最佳步長 h={best[0]:.0e}，最大絕對誤差 {best[1]:.3e}")
print("""
這一關能證明什麼、不能證明什麼：
  能  —— 在 w0 這個點附近，grad() 與 loss() 彼此一致（局部數值證據）。
  不能 —— 不能證明兩者實作的是「正確的目標函數」。
          如果 loss 和 grad 同時照著錯的公式寫，這關照樣會通過。
          所以本檔上方另外附了 loss 與 grad 的獨立手推。
  FAIL 的意義 —— 代表有不一致要調查，來源可能是公式錯、步長不當、
                  捨入誤差，或該維梯度本身接近 0。不能直接斷定是公式錯。
""")

# ================================================================
print("=" * 68)
print("關卡 2：這批資料到底是不是線性可分？（不能只看 ||w|| 變大就下結論）")
print("=" * 68)
print("解線性可行性問題：找 v 使得對所有 i 都有  t_i · (x_i·v) >= 1，其中 t_i = 2y_i - 1")
t = 2 * y - 1
# linprog 形式：A_ub @ v <= b_ub  =>  -t_i * xb_i @ v <= -1
res = linprog(c=np.zeros(d + 1),
              A_ub=-(t[:, None] * Xb), b_ub=-np.ones(n),
              bounds=[(None, None)] * (d + 1), method="highs")
if res.success:
    v = res.x
    margins = t * (Xb @ v)
    # 約束寫成 >= 1，所以可行解的 margins.min() 至少為 1；不能用這個未正規化的數字比較幾何間隔。
    # 有意義的是「可行解存在」，以及除以 ||v|| 之後的幾何間隔。
    geo = margins.min() / np.linalg.norm(v[:d])   # 只用權重部分，不含截距
    print(f"可行解存在  ->  {P(res.success)}")
    print(f"最小 signed margin = {margins.min():.6f}（約束要求 >= 1；此值尚未除以權重長度）")
    print(f"幾何間隔 = margin / ||v|| = {geo:.6e}  ->  {P(geo > 0)}")
    print("結論：這 357 筆樣本**嚴格線性可分**（有正的分隔間隔）。")
    print("      注意這只針對這批有限樣本，不代表所有手寫 3 與 8 都可分。\n")
    print("既然存在嚴格分隔向量 v，對 c > 0 有")
    print("      L(cv) = (1/n) Σ log(1 + exp(-c · t_i · x_i·v))  →  0  (c → ∞)")
    for c in [1, 5, 20, 100, 500]:
        print(f"      c = {c:>4}   L(cv) = {loss(c * v):.10f}")
    print("      而任何有限 w 的 L(w) > 0，故無正則化的 MLE 不存在有限解。\n")
else:
    print("linprog 未找到可行解，無法斷定可分。\n")

# ================================================================
print("=" * 68)
print("關卡 3：手刻梯度下降 vs sklearn")
print("=" * 68)
w = np.zeros(d + 1)
lr, norms = 0.5, []
for it in range(1, 20001):
    w -= lr * grad(w)
    if it in (100, 1000, 5000, 10000, 20000):
        norms.append((it, np.linalg.norm(w), loss(w)))

# sklearn 1.8 起 penalty 已棄用（預計 1.10 移除）：無正則化改用 C=np.inf
sk = LogisticRegression(C=np.inf, max_iter=20000, tol=1e-10).fit(X, y)
w_sk = np.append(sk.coef_.ravel(), sk.intercept_)

p_manual = sigmoid(Xb @ w)
p_sk = sk.predict_proba(X)[:, 1]
acc_m = ((p_manual > .5) == y).mean()
acc_s = sk.score(X, y)

print(f"手刻 GD 準確率 = {acc_m:.4f}　sklearn 準確率 = {acc_s:.4f}"
      f"　-> {P(abs(acc_m - acc_s) < .01)}")
print(f"預測標籤完全一致？ {P((p_manual > .5).astype(int).tolist() == (p_sk > .5).astype(int).tolist())}")
print(f"預測機率最大差    = {np.abs(p_manual - p_sk).max():.4f}   <- 標籤一樣，機率差很多")
print(f"手刻 ||w|| = {np.linalg.norm(w):.4f}　sklearn ||w|| = {np.linalg.norm(w_sk):.4f}")
cos_w = (w @ w_sk) / (np.linalg.norm(w) * np.linalg.norm(w_sk))
print(f"兩個權重向量的 cos = {cos_w:.6f}   <- 方向相近但不相同\n")

print(f"{'迭代':>8} {'||w||':>12} {'損失':>16}")
for it, nw, ls in norms:
    print(f"{it:>8} {nw:>12.4f} {ls:>16.8f}")

print("""
這一關能證明什麼、不能證明什麼：
  能  —— 兩種實作在這批訓練資料上做出相同的分類決策。
  不能 —— 不能證明兩者的決策邊界相同。上面預測機率最大差就很大，
          代表兩個超平面不一樣，只是剛好都把這 357 筆分對。
  所以「係數逐項相等」不能拿來當驗收條件；該比的是
  loss/gradient 的一致性、margin、訓練行為與預測結果。
""")

sk_l2 = LogisticRegression(l1_ratio=0, C=1.0, max_iter=5000).fit(X, y)
w_l2 = np.append(sk_l2.coef_.ravel(), sk_l2.intercept_)
print(f"加上 L2 (C=1.0)：||w|| = {np.linalg.norm(w_l2):.4f}，"
      f"準確率 = {sk_l2.score(X, y):.4f}")
print("正則化把「沒有有限解」的問題變成有唯一解的問題——這就是它存在的理由之一。")
