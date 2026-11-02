import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score

RNG = 42
digits = load_digits()
X, y = digits.data, digits.target
Xs = StandardScaler().fit_transform(X)

pca = PCA(n_components=0.95, random_state=RNG).fit(Xs)
Xp = pca.transform(Xs)
print("PCA 保留維度（95% 變異）:", Xp.shape[1])

# 1) 擴大到 k=25，看 silhouette 是否真的沒有峰值
ks = list(range(2, 26))
sil_full, sil_pca, ch_pca = [], [], []
inertia = []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=RNG)
    lab = km.fit_predict(Xs)
    sil_full.append(silhouette_score(Xs, lab, sample_size=1500, random_state=RNG))
    inertia.append(km.inertia_)
    km2 = KMeans(n_clusters=k, n_init=10, random_state=RNG)
    lab2 = km2.fit_predict(Xp)
    sil_pca.append(silhouette_score(Xp, lab2, sample_size=1500, random_state=RNG))
    ch_pca.append((lab2,))
print(f"\n{'k':>3} {'sil_full':>9} {'sil_pca':>9}")
for k, a, b in zip(ks, sil_full, sil_pca):
    print(f"{k:3d} {a:9.4f} {b:9.4f}")

print(f"\nsil_full 最大: k={ks[int(np.argmax(sil_full))]} ({max(sil_full):.4f})")
print(f"sil_pca  最大: k={ks[int(np.argmax(sil_pca))]} ({max(sil_pca):.4f})")

# 2) 穩定性：不同隨機種子重跑的 ARI（k 固定）
print("\n穩定性 (KMeans 不同 seed 的兩兩 ARI)：")
for k in [4, 6, 8, 10, 11, 12, 15]:
    runs = []
    for s in range(5):
        lab = KMeans(n_clusters=k, n_init=1, random_state=s).fit_predict(Xs)
        runs.append(lab)
    aris = [adjusted_rand_score(runs[i], runs[j]) for i in range(5) for j in range(i + 1, 5)]
    print(f"  k={k:2d}: mean ARI={np.mean(aris):.3f}")

# 3) 階層式（Ward）在 PCA 空間，k=2..20，對照 true labels
print("\nWard (PCA 空間) vs 真值：")
ward_ari = []
for k in range(2, 21):
    lab = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Xp)
    ward_ari.append(adjusted_rand_score(y, lab))
    if k in (8, 9, 10, 11, 12, 15):
        print(f"  k={k:2d}: ARI={ward_ari[-1]:.4f} NMI={normalized_mutual_info_score(y, lab):.4f}")
kk = list(range(2, 21))
print(f"  Ward ARI 最大: k={kk[int(np.argmax(ward_ari))]} ({max(ward_ari):.4f})")

# 4) 圖
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(ks, sil_full, "o-", label="64D standardized")
ax[0].plot(ks, sil_pca, "s-", label=f"PCA {Xp.shape[1]}D (95%)")
ax[0].axvline(10, color="red", ls="--", alpha=0.5, label="k=10")
ax[0].set_xlabel("k"); ax[0].set_ylabel("silhouette"); ax[0].legend()
ax[0].set_title("Silhouette vs k (higher=better)")
ax[1].plot(kk, ward_ari, "o-")
ax[1].axvline(10, color="red", ls="--", alpha=0.5)
ax[1].set_xlabel("k"); ax[1].set_ylabel("ARI vs true digits")
ax[1].set_title("Ward clustering agreement with true classes")
fig.tight_layout()
fig.savefig("figs/digits_cluster_extended.png", dpi=150)
print("\n圖已存：figs/digits_cluster_extended.png")
