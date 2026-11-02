"""手刻 PCA（digits），取前 10 主成分，支援 bug 參數與檢查表。"""
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

digits = load_digits()
X = digits.data.astype(float)
y = digits.target

BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]


def manual_pca(X, n_components, bug="none"):
    if bug == "no_center":
        mean = np.zeros(X.shape[1])
        Xc = X
    else:
        mean = X.mean(axis=0)
        Xc = X - mean

    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)

    if bug == "rows":
        components = Vt.T[:n_components]          # 取矩陣前 10 列（錯方向）
    else:
        components = Vt[:n_components]

    if bug == "denom_n":
        ev = (s ** 2) / X.shape[0]
    else:
        ev = (s ** 2) / (X.shape[0] - 1)

    explained_variance = ev[:n_components]
    if bug == "ratio_topk":
        total_var = ev[:n_components].sum()       # 分母只用前 10 個
    else:
        total_var = ev.sum()
    explained_variance_ratio = explained_variance / total_var

    X_proj = Xc @ components.T
    return {
        "mean": mean,
        "components": components,
        "explained_variance": explained_variance,
        "explained_variance_ratio": explained_variance_ratio,
        "X_proj": X_proj,
        "singular_values": s[:n_components],
    }


def run_checks(res, X_sk, X_sk_proj):
    cosines = [abs(res["components"][i] @ skc) / (np.linalg.norm(res["components"][i]) * np.linalg.norm(skc))
               for i, skc in enumerate(sk.components_)]
    corr = [np.corrcoef(res["X_proj"][:, i], X_sk_proj[:, i])[0, 1] for i in range(10)]
    cos_min = min(cosines)
    corr_minabs = min(abs(c) for c in corr)
    evr_maxdiff = float(np.max(np.abs(res["explained_variance_ratio"] - sk.explained_variance_ratio_)))
    cos_pass = all(c > 1 - 1e-9 for c in cosines)
    corr_pass = all(abs(c) > 1 - 1e-9 for c in corr)
    evr_pass = bool(np.allclose(res["explained_variance_ratio"], sk.explained_variance_ratio_))
    return {
        "cos_min": cos_min, "cos_pass": cos_pass,
        "corr_minabs": corr_minabs, "corr_pass": corr_pass,
        "evr_maxdiff": evr_maxdiff, "evr_pass": evr_pass,
    }


sk = PCA(n_components=10)
X_sk_proj = sk.fit_transform(X)

results = {}
for bug in BUGS:
    res = manual_pca(X, 10, bug=bug)
    results[bug] = run_checks(res, sk, X_sk_proj)

# 印表：檢查 × 錯誤
checks = [("components cos (min)", "cos_min", "cos_pass"),
          ("transform |corr| (min)", "corr_minabs", "corr_pass"),
          ("evr maxdiff", "evr_maxdiff", "evr_pass")]

header = ["check"] + BUGS
print("\t".join(header))
for name, valkey, passkey in checks:
    row = [name]
    for bug in BUGS:
        r = results[bug]
        val = r[valkey]
        status = "PASS" if r[passkey] else "FAIL"
        row.append(f"{val:.3e} {status}")
    print("\t".join(row))

# 仍存 none 的圖
res_none = manual_pca(X, 10, bug="none")
plt.figure(figsize=(8, 6))
sc = plt.scatter(res_none["X_proj"][:, 0], res_none["X_proj"][:, 1], c=y, cmap="tab10", s=8, alpha=0.7)
plt.colorbar(sc, ticks=range(10))
plt.xlabel("PC1"); plt.ylabel("PC2"); plt.title("Manual PCA on digits (first 2 of 10)")
plt.tight_layout()
plt.savefig("figs/pca_digits.png", dpi=120)
print("saved figs/pca_digits.png")
