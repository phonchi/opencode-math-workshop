"""計算 k=10 分群與真實標籤的準確率。

分群標籤與真實標籤沒有先驗對應，需先用 Hungarian algorithm
（linear_sum_assignment）找最佳一一對應後再算 accuracy。
另附 purity（每群取最多數字的比例加權）供對照。
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix
from scipy.optimize import linear_sum_assignment

digits = load_digits()
X, y = digits.data, digits.target
n = len(y)

spaces = {
    "raw（標準化 64 維）": StandardScaler().fit_transform(X),
    "PCA 40 維": PCA(n_components=0.95, random_state=42).fit_transform(
        StandardScaler().fit_transform(X)),
    "cosine（L2 正規化）": normalize(StandardScaler().fit_transform(X)),
}

for name, Xs in spaces.items():
    km = KMeans(n_clusters=10, n_init=20, random_state=42)
    pred = km.fit_predict(Xs)

    cm = confusion_matrix(y, pred)  # rows = true digit, cols = cluster

    # Hungarian：找讓對角線和最大的 cluster->digit 指派
    row_ind, col_ind = linear_sum_assignment(-cm)
    mapping = {cluster: digit for digit, cluster in zip(row_ind, col_ind)}
    matched = np.array([mapping[c] for c in pred])
    acc = (matched == y).mean()

    # purity
    purity = sum(np.bincount(y[pred == c], minlength=10).max() for c in range(10)) / n

    print(f"{name}")
    print(f"  Hungarian 對配後 accuracy = {acc:.4f}（{int(acc * n)}/{n}）")
    print(f"  purity                    = {purity:.4f}")
    print(f"  cluster -> digit 對應: {mapping}\n")
