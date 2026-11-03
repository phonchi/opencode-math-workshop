import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

with open("data/orders.csv") as f:
    r = csv.reader(f)
    header = next(r)
    rows = list(r)
X = np.array(rows, dtype=float)

Xs = StandardScaler().fit_transform(X)
pca = PCA()
pca.fit(Xs)
ev = pca.explained_variance_ratio_
cum = np.cumsum(ev)

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(range(1, len(ev) + 1), ev, label="Individual")
ax.plot(range(1, len(ev) + 1), cum, marker="o", color="C1", label="Cumulative")
ax.axhline(0.9, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Principal Component")
ax.set_ylabel("Explained variance ratio")
ax.set_xticks(range(1, len(ev) + 1))
ax.legend()
fig.tight_layout()
fig.savefig("figs/pca_scree.png", dpi=150)
plt.close(fig)

k90 = int(np.argmax(cum >= 0.9) + 1)
k80 = int(np.argmax(cum >= 0.8) + 1)
print("individual", [round(float(x) * 100, 2) for x in ev])
print("cumulative", [round(float(x) * 100, 2) for x in cum])
print("k80", k80, "k90", k90)
