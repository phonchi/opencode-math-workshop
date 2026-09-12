"""Lab 1 參考解答 — 加速器：k-means 分群與 k 的選擇

驗收重點（經跨模型獨立審查後修正措辭）：
  * random_state=0 固定初始化的隨機來源；n_init=10 是「跑 10 次取較佳」，
    本身不是可重現性保證。同資料、同版本、同運算設定下可在容差內重現，
    但不保證跨版本或跨硬體逐位元相同。
  * 不直接比較 cluster **編號**（編號可任意置換）。要比較分群結構時，
    用 ARI、共同分群關係，或先做 label 對齊。
  * inertia 相同也不保證分群相同。
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

RANDOM_STATE = 0
X, y = load_digits(return_X_y=True)
print(f"資料形狀 X={X.shape}, 真實類別數={len(np.unique(y))}")

ks = list(range(2, 13))
inertias, sils = [], []
for k in ks:
    km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(X)
    inertias.append(km.inertia_)
    sils.append(silhouette_score(X, km.labels_))
    print(f"k={k:2d}  inertia={km.inertia_:10.1f}  silhouette={sils[-1]:.4f}")

best_k = ks[int(np.argmax(sils))]
print(f"\nsilhouette 最高的 k = {best_k}")
print("注意：10 是**標註的數字類別數**，不保證原始像素空間恰好有 10 個")
print("      符合 k-means 幾何假設的群。silhouette 偏好 k=9 只代表：")
print("      在這份資料、歐氏距離與本次搜尋設定下，k=9 的幾何分群品質較好。")
print("      『幾何分群品質』與『辨識 10 種數字』是兩個不同的評估目標。")

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(ks, inertias, "o-"); ax[0].set_xlabel("k"); ax[0].set_ylabel("inertia")
ax[0].set_title("Elbow: inertia vs k")
ax[1].plot(ks, sils, "o-", color="tab:orange")
ax[1].axvline(best_k, ls="--", color="gray")
ax[1].set_xlabel("k"); ax[1].set_ylabel("silhouette"); ax[1].set_title("Silhouette vs k")
fig.tight_layout(); fig.savefig("../tools/test-runs/lab1_k_selection.png", dpi=110)
print("圖已存至 tools/test-runs/lab1_k_selection.png")

# 可重現性檢查：固定資料、套件版本與運算設定下，inertia 應在容差內重現
a = KMeans(n_clusters=10, random_state=RANDOM_STATE, n_init=10).fit(X)
b = KMeans(n_clusters=10, random_state=RANDOM_STATE, n_init=10).fit(X)
tol = 1e-6 * max(1.0, abs(a.inertia_))
print(f"\n可重現性：兩次 inertia 差 = {abs(a.inertia_-b.inertia_):.3e}（容差 {tol:.3e}） -> "
      f"{'PASS' if abs(a.inertia_-b.inertia_) < tol else 'FAIL'}")
# 分群結構是否也一致（忽略編號置換）——用 ARI 比對兩次結果
from sklearn.metrics import adjusted_rand_score
ari = adjusted_rand_score(a.labels_, b.labels_)
print(f"兩次分群結構 ARI = {ari:.6f}  -> {'PASS' if ari > 1-1e-9 else 'FAIL'}"
      "   （ARI 忽略編號置換，這才是真正該比的）")
