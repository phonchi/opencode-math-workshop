"""穩健性檢查：elbow、bootstrap 穩定度、以及不同前處理下的一致性。"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

RNG = 42
digits = load_digits()
X_raw, y = digits.data.astype(float), digits.target

PREPS = {
    "raw/255 + PCA40": lambda: PCA(n_components=40, random_state=RNG).fit_transform(X_raw / 255.0),
    "standardized + PCA40": lambda: PCA(n_components=40, random_state=RNG).fit_transform(
        StandardScaler().fit_transform(X_raw)
    ),
}
ks = list(range(2, 21))


def stability(Xp, k, n_boot=20, frac=0.8, seed=RNG):
    """子取樣重跑的 ARI 平均：越高代表該 k 的結構越穩定。"""
    rng = np.random.default_rng(seed)
    base = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(Xp)
    scores = []
    n = len(Xp)
    for b in range(n_boot):
        idx = rng.choice(n, size=int(n * frac), replace=False)
        sub = Xp[idx]
        lab = KMeans(n_clusters=k, n_init=10, random_state=seed + b).fit_predict(sub)
        scores.append(adjusted_rand_score(base[idx], lab))
    return float(np.mean(scores)), float(np.std(scores))


results = {}
for name, fn in PREPS.items():
    Xp = fn()
    inertia, sil, stab = [], [], []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=RNG).fit(Xp)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(Xp, km.labels_))
        stab.append(stability(Xp, k)[0])
    results[name] = dict(inertia=inertia, sil=sil, stab=stab)

    # 相對慣性下降率（elbow）
    drop = -np.diff(inertia) / inertia[:-1]
    print(f"\n=== {name} ===")
    print(f"{'k':>3} {'inertia':>9} {'rel_drop':>9} {'sil':>7} {'stability':>10}")
    for i, k in enumerate(ks):
        d = drop[i - 1] if i > 0 else float("nan")
        print(f"{k:>3} {inertia[i]:>9.0f} {d:>9.3f} {sil[i]:>7.3f} {stab[i]:>10.3f}")
    print(
        f"best sil k={ks[int(np.argmax(sil))]}, best stability k={ks[int(np.argmax(stab))]}"
    )

fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
for ax, key, title in zip(
    axes,
    ("inertia", "sil", "stab"),
    ("Inertia (elbow)", "Silhouette", "Bootstrap stability (ARI)"),
):
    for name, style in zip(results, ("o-", "s--")):
        ax.plot(ks, results[name][key], style, label=name)
    ax.axvline(10, color="gray", ls=":", lw=1)
    ax.set_xlabel("k")
    ax.set_title(title)
    ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("figs/digits_k_robustness.png", dpi=150)
print("\nsaved figs/digits_k_robustness.png")
