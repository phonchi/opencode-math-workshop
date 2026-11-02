import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK TC"
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

df = pd.read_csv("data/line_channels.csv")
X = StandardScaler().fit_transform(df)

pca = PCA().fit(X)
evr = pca.explained_variance_ratio_
cum = np.cumsum(evr)

for i in range(len(evr)):
    print(f"PC{i+1}: {evr[i]:.4f}  累積: {cum[i]:.4f}")

n90 = int(np.searchsorted(cum, 0.90) + 1)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(range(1, len(evr)+1), evr, alpha=0.6, label="個別變異")
ax.plot(range(1, len(evr)+1), cum, "o-", color="crimson", label="累積變異")
ax.axhline(0.90, ls="--", color="gray")
ax.axvline(n90, ls="--", color="gray")
ax.set_xlabel("主成分")
ax.set_ylabel("解釋變異比例")
ax.set_title(f"PCA Scree Plot（達 90% 需 {n90} 個主成分）")
fig.tight_layout()
fig.savefig("figs/pca_scree.png", dpi=150)

loadings = pd.DataFrame(pca.components_[:3].T, index=df.columns,
                        columns=["PC1", "PC2", "PC3"])
print("\n前 3 個主成分的負荷量：")
print(loadings.round(3))
