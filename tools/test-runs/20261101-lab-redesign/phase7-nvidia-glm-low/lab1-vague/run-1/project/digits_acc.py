import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix

X, y = load_digits(return_X_y=True)
Xs = StandardScaler().fit_transform(X)
Xp = PCA(n_components=0.90, random_state=0).fit_transform(Xs)
lab = KMeans(n_clusters=10, n_init=20, random_state=0).fit_predict(Xp)

cm = confusion_matrix(y, lab)
# 最適標籤對應（Hungarian，最大化對角和）
row, col = linear_sum_assignment(-cm)
acc = cm[row, col].sum() / len(y)
print(f"k=10 分群對應到數字後的準確率: {acc:.4f}")

per_class = {}
for r, c in zip(row, col):
    digit = y[np.where(y == r)[0][0]]
    print(f"cluster {c:2d} -> digit {digit}: {cm[r, c]:3d}/{cm[r].sum():3d} = {cm[r, c]/cm[r].sum():.3f}")
