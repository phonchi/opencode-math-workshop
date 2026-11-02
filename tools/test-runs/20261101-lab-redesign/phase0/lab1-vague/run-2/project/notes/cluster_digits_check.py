from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import numpy as np

rng = np.random.default_rng(0)
X, y = load_digits(return_X_y=True)
Xs = StandardScaler().fit_transform(X)
Xp = PCA(n_components=0.90, random_state=0).fit_transform(Xs)

ks = list(range(2, 26))
inertia = []
for k in ks:
    inertia.append(KMeans(n_clusters=k, n_init=20, random_state=0).fit(Xp).inertia_)
inertia = np.array(inertia)
# 相對下降幅度：肘部看的是下降率突然變小
d = inertia[:-1] - inertia[1:]
print("k -> k+1  inertia drop, and ratio to previous drop")
for i, k in enumerate(ks[:-1]):
    ratio = d[i + 1] / d[i] if i + 1 < len(d) else np.nan
    print(f"{k:>2}->{k+1:<2} drop={d[i]:>8.1f}  ratio(next/this)={ratio:>5.3f}")

# 穩定性：80% 子樣本重跑，比較同一批樣本兩次的共分群一致性(ARI)
def subsample_labels(k, seed):
    r = np.random.default_rng(seed)
    idx = r.choice(len(Xp), size=int(0.8 * len(Xp)), replace=False)
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(Xp[idx])
    return idx, km.predict(Xp[idx])

print("\nstability (mean pairwise ARI over 5 subsamples, k=6..15)")
for k in range(6, 16):
    labs = [subsample_labels(k, s) for s in range(5)]
    scores = []
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            a = dict(zip(labs[i][0], labs[i][1]))
            b = dict(zip(labs[j][0], labs[j][1]))
            common = list(set(a) & set(b))
            if len(common) > 1:
                scores.append(adjusted_rand_score(
                    [a[c] for c in common], [b[c] for c in common]))
    print(f"k={k:>2}  stability ARI={np.mean(scores):.4f}")

# k=10 時每個 cluster 對到哪些數字
km = KMeans(n_clusters=10, n_init=50, random_state=0).fit(Xp)
print("\nk=10 cluster -> digit distribution")
for c in range(10):
    cnt = np.bincount(y[km.labels_ == c], minlength=10)
    top = np.argsort(cnt)[::-1][:3]
    print(f"cluster {c}: " + ", ".join(f"{t}({cnt[t]})" for t in top if cnt[t] > 0))
