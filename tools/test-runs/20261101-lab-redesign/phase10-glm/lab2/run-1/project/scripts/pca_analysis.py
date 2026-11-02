import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

df = pd.read_csv("data/line_channels.csv")
X = StandardScaler().fit_transform(df)

pca = PCA().fit(X)
evr = pca.explained_variance_ratio_

print("各主成分解釋變異比例：")
for i, (v, c) in enumerate(zip(evr, evr.cumsum()), 1):
    print(f"PC{i:2d}: {v:.4f}  累積 {c:.4f}")

plt.figure(figsize=(7, 4.5))
plt.plot(range(1, len(evr) + 1), evr.cumsum(), marker="o")
plt.axhline(0.9, color="r", ls="--", label="90%")
plt.xlabel("Number of components")
plt.ylabel("Cumulative explained variance")
plt.xticks(range(1, len(evr) + 1))
plt.legend()
plt.tight_layout()
plt.savefig("figs/pca_cumvar.png", dpi=150)
