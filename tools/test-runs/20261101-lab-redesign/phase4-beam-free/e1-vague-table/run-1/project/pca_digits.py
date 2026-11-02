import argparse
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA


BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]


def manual_pca(X, n_components, bug="none"):
    """手刻 PCA：中心化後 SVD，取前 n_components 個右奇異向量。"""
    X = np.asarray(X, dtype=float)
    n = X.shape[0]

    if bug == "no_center":
        mean = np.zeros(X.shape[1])
        Xc = X
    else:
        mean = X.mean(axis=0)
        Xc = X - mean

    # full_matrices=False：U (n,k), s (k,), Vt (k,d)
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)

    if bug == "rows":
        components = Xc[:n_components].copy()  # 錯誤：取矩陣前 10 列
    else:
        components = Vt[:n_components].copy()  # (k, d)

    if bug == "denom_n":
        explained_variance = (s[:n_components] ** 2) / n
    else:
        explained_variance = (s[:n_components] ** 2) / (n - 1)

    total_var = np.var(X, axis=0, ddof=1).sum()
    if bug == "ratio_topk":
        explained_variance_ratio = explained_variance / explained_variance.sum()
    else:
        explained_variance_ratio = explained_variance / total_var

    X_proj = Xc @ components.T  # (n, k)
    return {
        "mean": mean,
        "components": components,
        "singular_values": s[:n_components],
        "explained_variance": explained_variance,
        "explained_variance_ratio": explained_variance_ratio,
        "projection": X_proj,
    }


def run_one(bug):
    digits = load_digits()
    X = digits.data
    n_components = 10

    manual = manual_pca(X, n_components, bug=bug)

    sk = PCA(n_components=n_components, svd_solver="full")
    sk.fit(X)
    sk_proj = sk.transform(X)

    # 對齊奇異向量符號（PCA 主成分方向符號不固定）
    aligned_manual_proj = manual["projection"].copy()
    aligned_components = manual["components"].copy()
    for j in range(n_components):
        if np.dot(aligned_manual_proj[:, j], sk_proj[:, j]) < 0:
            aligned_manual_proj[:, j] *= -1
            aligned_components[j] *= -1

    evr_diff = float(np.max(np.abs(manual["explained_variance_ratio"] - sk.explained_variance_ratio_)))
    corr = [float(np.corrcoef(aligned_manual_proj[:, j], sk_proj[:, j])[0, 1])
            for j in range(n_components)]
    min_corr = float(min(corr))

    X_rec_manual = aligned_manual_proj @ aligned_components + manual["mean"]
    X_rec_sk = sk_proj @ sk.components_ + sk.mean_
    recon_diff = float(np.mean((X - X_rec_manual) ** 2) - np.mean((X - X_rec_sk) ** 2))
    # 以 MSE 差的絕對值作為檢查值
    recon_check = float(abs(recon_diff))

    M = aligned_components
    S = sk.components_
    U1, _, _ = np.linalg.svd(M.T, full_matrices=False)
    U2, _, _ = np.linalg.svd(S.T, full_matrices=False)
    cos_angles = np.linalg.svd(U1[:, :n_components].T @ U2[:, :n_components])[1]
    min_cos = float(cos_angles.min())

    return {
        "evr_max_diff": evr_diff,
        "min_proj_corr": min_corr,
        "recon_mse_diff": recon_check,
        "subspace_min_cos": min_cos,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bug", choices=BUGS, default=None)
    args = parser.parse_args()

    bugs = [args.bug] if args.bug else BUGS

    results = {bug: run_one(bug) for bug in bugs}

    checks = [
        ("evr_max_diff", 1e-10, "max |evr 差| < 1e-10"),
        ("min_proj_corr", 0.999999, "min proj corr > 0.999999"),
        ("recon_mse_diff", 1e-10, "|MSE 差| < 1e-10"),
        ("subspace_min_cos", 0.999999, "min cos > 0.999999"),
    ]

    # 以 bug 為欄、檢查為列的表
    header = "check".ljust(20) + "".join(b.ljust(26) for b in bugs)
    print(header)
    print("-" * len(header))
    for key, thr, _ in checks:
        row = key.ljust(20)
        for b in bugs:
            val = results[b][key]
            if key in ("evr_max_diff", "recon_mse_diff"):
                passed = val < thr
            else:
                passed = val > thr
            cell = f"{val:.3e} {'PASS' if passed else 'FAIL'}"
            row += cell.ljust(26)
        print(row)


if __name__ == "__main__":
    main()
