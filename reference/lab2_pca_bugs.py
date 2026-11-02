"""Lab 2 講師備援：把講師注入的錯誤放進手刻 PCA，列出「檢查 × 錯誤」表。

學生現場可請 AI 自己做這張表；若來不及，講師用本檔示範。
所有錯誤都是講師注入，不是 AI 自己犯的。
"""
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA

K, TOL = 4, 1e-6
DATA = Path(__file__).resolve().parents[1] / "assets" / "data"
X = np.genfromtxt(DATA / "line_channels.csv", delimiter=",", skip_header=1)
# 只除以標準差、不減平均，中心化留給 PCA 本身，「忘記中心化」才測得出來。
X = X / X.std(0)
n = len(X)
mu = X.mean(0)
Xc = X - mu
sk = PCA(K, svd_solver="full", random_state=0).fit(X)
sk_mse = np.mean((X - sk.inverse_transform(sk.transform(X))) ** 2)


def pca(bug=None):
    A = X if bug == "no_center" else Xc
    C = A.T @ A / (n if bug == "denom_n" else n - 1)
    vals, vecs = np.linalg.eigh(C)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    W = vecs[:K].copy() if bug == "rows" else vecs[:, :K].T
    total = vals[:K].sum() if bug == "ratio_topk" else vals.sum()
    return vals[:K], W, vals[:K] / total


def checks(bug):
    vals, W, ratio = pca(bug)
    return {
        "比例": np.abs(ratio - sk.explained_variance_ratio_).max(),
        "|cos|": np.abs(np.abs((W * sk.components_).sum(1)) - 1).max(),
        "重建": abs(np.mean((X - ((Xc @ W.T) @ W + mu)) ** 2) - sk_mse),
        "正交": np.abs(W @ W.T - np.eye(K)).max(),
        "特徵值": np.abs(vals - sk.explained_variance_).max(),
    }


NAMES = {None: "正確版本", "ratio_topk": "比例分母只用前 4 個", "denom_n": "共變異數分母用 n",
         "no_center": "忘記中心化", "rows": "用 evecs[:K] 取列"}
labels = list(checks(None))
print(f"{'錯誤（講師注入）':<24}" + "".join(f"{x:>10}" for x in labels))
for bug, name in NAMES.items():
    r = checks(bug)
    print(f"{name:<24}" + "".join(f"{'PASS' if r[x] < TOL else 'FAIL':>10}" for x in labels))
    print(f"{'':<24}" + "".join(f"{r[x]:>10.1e}" for x in labels))
print(f"\n比例分母只用前 4 個時，比例總和 = {pca('ratio_topk')[2].sum():.6f}；正確應為 {pca()[2].sum():.6f}")
print(f"用 evecs[:K] 取列時，最小 |cos| = {np.abs((pca('rows')[1] * sk.components_).sum(1)).min():.6f}")
