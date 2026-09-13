"""Lab 2 參考解答 — 數學驗證：手刻 PCA vs sklearn

這一題的重點不是「寫出 PCA」，而是「怎麼設計一組真的抓得到錯的驗證」。

關鍵教學點（經跨模型獨立審查後補強）：
  * 驗證套件會有盲點。本檔示範一組「四關全過、卻抓不出 n vs n-1 錯誤」
    的驗證，再補上能抓到的第五關。
  * |cos| 比對只在「特徵值單純且間隔足夠」時有效；重根時失效。
  * sklearn 的 svd_solver='auto' 在這份資料上其實會選 covariance_eigh，
    跟手刻同路數。要真的交叉驗證兩種演算法，必須明寫 svd_solver='full'。
"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

np.set_printoptions(precision=4, suppress=True)
K = 10
X, _ = load_digits(return_X_y=True)
n, d = X.shape
print(f"資料形狀 X={X.shape}，取前 {K} 個主成分\n")

# ---------- 手刻 PCA：共變異數矩陣 + 特徵分解 ----------
mu = X.mean(axis=0)
Xc = X - mu
C = Xc.T @ Xc / (n - 1)           # 分母 n-1，與 sklearn 的 explained_variance_ 一致
evals, evecs = np.linalg.eigh(C)   # eigh 回傳由小到大
order = np.argsort(evals)[::-1]
evals, evecs = evals[order], evecs[:, order]
W_manual = evecs[:, :K].T          # (K, d)，每列一個主成分
evr_manual = evals[:K] / evals.sum()

# ---------- sklearn：明確指定 full（走 SVD），才是真正的第二種演算法 ----------
pca = PCA(n_components=K, svd_solver="full", random_state=0).fit(X)
print(f"sklearn 實際使用的 solver: {pca._fit_svd_solver}"
      f"　（若用預設 auto，這份資料會選 covariance_eigh，跟手刻同路數）\n")
W_sk = pca.components_
evr_sk = pca.explained_variance_ratio_

P = lambda ok: "PASS" if ok else "FAIL"

print("=" * 66)
print("關卡 1：解釋變異比例")
print("=" * 66)
e1 = np.abs(evr_manual - evr_sk).max()
print(f"手刻   : {evr_manual}")
print(f"sklearn: {evr_sk}")
print(f"最大差異 = {e1:.3e}  ->  {P(e1 < 1e-8)}\n")

print("=" * 66)
print("關卡 2：主成分方向（用 |cos|，因為特徵向量正負號任意）")
print("=" * 66)
cos = np.abs(np.sum(W_manual * W_sk, axis=1))
flips = [i + 1 for i in range(K) if np.dot(W_manual[i], W_sk[i]) < 0]
e2 = np.abs(cos - 1).max()
print(f"最大偏離 1 = {e2:.3e}  ->  {P(e2 < 1e-6)}")
print(f"方向相反的主成分：PC{flips}　（正常現象，不是錯誤）")
# 這一關的適用條件：特徵值必須單純且間隔夠大
gaps = np.diff(evals[:K + 1])
print(f"前 {K} 個特徵值：{evals[:K]}")
print(f"相鄰最小間隔 = {np.abs(gaps).min():.4f}  ->  "
      f"{'遠離重根，|cos| 適用' if np.abs(gaps).min() > 1e-6 else '接近重根，|cos| 不適用'}\n")

print("=" * 66)
print("關卡 3：重建誤差")
print("=" * 66)
rec_manual = (Xc @ W_manual.T) @ W_manual + mu
rec_sk = pca.inverse_transform(pca.transform(X))
a, b = np.mean((X - rec_manual) ** 2), np.mean((X - rec_sk) ** 2)
e3 = abs(a - b)
print(f"手刻 MSE = {a:.10f}　sklearn MSE = {b:.10f}")
print(f"差異 = {e3:.3e}  ->  {P(e3 < 1e-8)}")
# 用尾端特徵值獨立核算，不依賴 sklearn
theory = (n - 1) / (n * d) * evals[K:].sum()
print(f"理論值 (n-1)/(nd) * sum(λ_j, j>K) = {theory:.10f}  -> "
      f"{P(abs(theory - a) < 1e-8)}（不靠對照組的獨立核算）\n")

print("=" * 66)
print("關卡 4：正交性 W W^T = I")
print("=" * 66)
e4 = np.abs(W_manual @ W_manual.T - np.eye(K)).max()
print(f"與單位矩陣最大差 = {e4:.3e}  ->  {P(e4 < 1e-10)}")
print("注意：這只是**必要條件**。任何一組單位正交向量都會通過，")
print("      包括『取到最小的那幾個特徵向量』這種錯誤。\n")

print("#" * 66)
print("# 關卡 5：直接比特徵值本身　←　這一關是後來才補上的，原因見下")
print("#" * 66)
e5 = np.abs(evals[:K] - pca.explained_variance_).max()
print(f"手刻 λ  : {evals[:K]}")
print(f"sklearn : {pca.explained_variance_}")
print(f"最大差異 = {e5:.3e}  ->  {P(e5 < 1e-6)}\n")

print("=" * 66)
print("為什麼需要關卡 5：關卡 1-4 有一個共同盲點")
print("=" * 66)
print("如果把共變異數的分母 n-1 誤寫成 n，會發生什麼事？\n")
C_wrong = Xc.T @ Xc / n                      # 只差一個常數倍
ev_w, V_w = np.linalg.eigh(C_wrong)
o = np.argsort(ev_w)[::-1]
ev_w, V_w = ev_w[o], V_w[:, o]
W_w = V_w[:, :K].T
r1 = np.abs(ev_w[:K] / ev_w.sum() - evr_sk).max()
r2 = np.abs(np.abs(np.sum(W_w * W_sk, axis=1)) - 1).max()
rec_w = (Xc @ W_w.T) @ W_w + mu
r3 = abs(np.mean((X - rec_w) ** 2) - b)
r4 = np.abs(W_w @ W_w.T - np.eye(K)).max()
r5 = np.abs(ev_w[:K] - pca.explained_variance_).max()
print(f"  關卡 1（比例）     {P(r1 < 1e-8)}")
print(f"  關卡 2（方向）     {P(r2 < 1e-6)}")
print(f"  關卡 3（重建）     {P(r3 < 1e-8)}")
print(f"  關卡 4（正交）     {P(r4 < 1e-10)}")
print(f"  關卡 5（特徵值）   {P(r5 < 1e-6)}   差 = {r5:.4f}   <-- 只有這關抓到")
print("""
原因：C 乘上任意正常數 c，特徵向量完全不變、特徵值同乘 c。
      比例 λ_i / Σλ 中的 c 被約掉；方向不變；重建只用到特徵向量；
      正交性也只看特徵向量。所以前四關對這個錯誤完全免疫。

教訓：**驗證全部通過，只代表「這組驗證抓不到錯」，不代表程式正確。**
      設計驗證時要問的是「什麼樣的錯誤會被我漏掉」，
      而不是「我的檢查通過了幾項」。
""")

print("=" * 66)
print("附帶示範：為什麼不能直接比 components_")
print("=" * 66)
naive = np.abs(W_manual - W_sk).max()
sign = np.sign(np.sum(W_manual * W_sk, axis=1))[:, None]
aligned = np.abs(W_manual * sign - W_sk).max()
print(f"直接相減的最大差        = {naive:.4f}   <- 看起來大錯特錯")
print(f"對齊正負號後的最大差    = {aligned:.3e}  <- 其實完全正確")
print("這個對比成立，是因為上面還有其他關卡佐證。")
print("單看『差 0.94』這個數字本身，並不能證明原因就是正負號。")
