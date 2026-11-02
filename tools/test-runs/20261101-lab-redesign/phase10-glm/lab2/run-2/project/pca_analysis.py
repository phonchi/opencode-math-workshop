import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK HK", "Droid Sans Fallback"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data/line_channels.csv")
X = StandardScaler().fit_transform(df.values)

pca = PCA().fit(X)
evr = pca.explained_variance_ratio_
cum = np.cumsum(evr)

for i, (v, c) in enumerate(zip(evr, cum), 1):
    print(f"PC{i:2d}: {v*100:6.2f}%  累積 {c*100:6.2f}%")

n90 = int(np.searchsorted(cum, 0.90) + 1)
n95 = int(np.searchsorted(cum, 0.95) + 1)
print(f"\n達 90% 變異需要 {n90} 個主成分；達 95% 需要 {n95} 個")

plt.figure(figsize=(7, 4.5))
plt.bar(range(1, len(evr) + 1), evr * 100, alpha=0.7, label="個別解釋變異")
plt.step(range(1, len(evr) + 1), cum * 100, where="mid", c="crimson", label="累積解釋變異")
plt.axhline(90, ls="--", c="gray", lw=1)
plt.axvline(n90, ls="--", c="gray", lw=1)
plt.xlabel("主成分")
plt.ylabel("解釋變異比 (%)")
plt.title("PCA Scree Plot")
plt.legend()
plt.tight_layout()
plt.savefig("figs/pca_scree.png", dpi=150)
print("已存 figs/pca_scree.png")

loadings = pd.DataFrame(
    pca.components_[:n90].T,
    index=df.columns,
    columns=[f"PC{i+1}" for i in range(n90)],
)
print("\n前幾個主成分的負荷量（|值|>0.4 以 * 標記）:")
print(loadings.map(lambda v: f"{v:.3f}" + ("*" if abs(v) > 0.4 else "")))
