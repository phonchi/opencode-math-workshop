# -*- coding: utf-8 -*-
"""手刻 PCA（前 10 主成分），資料用 sklearn digits。支援 --bug 注入錯誤。"""
import argparse
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]

# ---------- 資料 ----------
digits = load_digits()
X = digits.data.astype(float)
n, d = X.shape


def run_pca(bug="none"):
    # ---------- 手刻 PCA ----------
    if bug == "no_center":
        X_mean = np.zeros(d)
        Xc = X.copy()
    else:
        X_mean = X.mean(axis=0)
        Xc = X - X_mean

    denom = n if bug == "denom_n" else (n - 1)
    C = (Xc.T @ Xc) / denom

    eigvals, eigvecs = np.linalg.eigh(C)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    k = 10
    if bug == "rows":
        W = eigvecs[:k].T
    else:
        W = eigvecs[:, :k]
    vals = eigvals[:k]
    X_t = Xc @ W

    # ---------- 對照組 ----------
    pca = PCA(n_components=k)
    X_sk = pca.fit_transform(X)

    # ---------- 檢查 ----------
    TOL = {
        "center_mean": 1e-10,
        "cov": 1e-10,
        "eig_nonneg": 1e-10,
        "eig_order": 0.0,
        "orthonormal": 1e-10,
        "variance": 1e-6,
        "components": 1e-6,
        "var_ratio": 1e-6,
        "transform": 1e-6,
        "recon": 1e-6,
        "resid_orth": 1e-8,
    }

    results = []

    def check(name, actual, tol, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        results.append((name, float(actual), float(tol), status, detail))

    # 1. centered column means
    max_mean = np.max(np.abs(Xc.mean(axis=0)))
    check("centered column means", max_mean, TOL["center_mean"],
          max_mean < TOL["center_mean"])

    # 2. covariance matrix
    C_ref = np.cov(X, rowvar=False, ddof=1)
    max_cov = np.max(np.abs(C - C_ref))
    check("covariance matrix", max_cov, TOL["cov"], max_cov < TOL["cov"])

    # 3. eigenvalues non-negative
    min_val = eigvals.min()
    check("eigenvalues non-negative", min(min_val, 0.0) if min_val < 0 else 0.0,
          TOL["eig_nonneg"], min_val >= -TOL["eig_nonneg"],
          f"(min eig={eigvals.min():.3e})")

    # 4. descending
    monotone10 = bool(np.all(np.diff(vals) <= 0))
    max_diff = float(np.max(np.diff(vals)))
    check("eigenvalues descending (top10)", max_diff, TOL["eig_order"],
          monotone10 and max_diff <= 0)

    # 5. orthonormality
    orth_err = np.max(np.abs(W.T @ W - np.eye(k)))
    check("W orthonormality", orth_err, TOL["orthonormal"],
          orth_err < TOL["orthonormal"])

    # 6. explained_variance
    ev_sk = pca.explained_variance_
    max_ev = np.max(np.abs(vals - ev_sk))
    check("explained_variance vs sklearn", max_ev, TOL["variance"],
          max_ev < TOL["variance"])

    # 7. components
    comps_sk = pca.components_
    max_comp = 0.0
    for i in range(k):
        v = W[:, i]
        s = comps_sk[i]
        sign = np.sign(v @ s)
        if sign == 0:
            sign = 1.0
        aligned = v * sign
        max_comp = max(max_comp, np.max(np.abs(aligned - s)))
    check("components_ vs sklearn", max_comp, TOL["components"],
          max_comp < TOL["components"])

    # 8. ratio
    if bug == "ratio_topk":
        ratio_ours = vals / vals.sum()
    else:
        ratio_ours = vals / eigvals.sum()
    ratio_sk = pca.explained_variance_ratio_
    max_ratio = np.max(np.abs(ratio_ours - ratio_sk))
    check("explained_variance_ratio_", max_ratio, TOL["var_ratio"],
          max_ratio < TOL["var_ratio"])

    # 9. transform
    X_t_aligned = X_t.copy()
    for i in range(k):
        sign = np.sign(W[:, i] @ comps_sk[i])
        if sign == 0:
            sign = 1.0
        X_t_aligned[:, i] *= sign
    max_t = np.max(np.abs(X_t_aligned - X_sk))
    check("transform vs sklearn", max_t, TOL["transform"],
          max_t < TOL["transform"])

    # 10. reconstruction
    X_recon_ours = X_t @ W.T + X_mean
    recon_err_ours = np.mean((X - X_recon_ours) ** 2)
    X_recon_sk = pca.inverse_transform(X_sk)
    recon_err_sk = np.mean((X - X_recon_sk) ** 2)
    max_recon = abs(recon_err_ours - recon_err_sk)
    check("reconstruction MSE vs sklearn", max_recon, TOL["recon"],
          max_recon < TOL["recon"], f"(ours={recon_err_ours:.6e},sk={recon_err_sk:.6e})")

    # 11. residual orth
    resid = Xc - X_t @ W.T
    orth_proj = np.max(np.abs(resid @ W))
    check("residual orthogonal to PCs", orth_proj, TOL["resid_orth"],
          orth_proj < TOL["resid_orth"])

    return results


def print_single(bug):
    print(f"=== bug={bug} ===")
    results = run_pca(bug)
    for name, actual, tol, status, detail in results:
        print(f"{status:4s} | {name:28s} | actual={actual:.6e} | tol={tol:.0e} {detail}")
    n_pass = sum(1 for r in results if r[3] == "PASS")
    print(f"SUMMARY: {n_pass}/{len(results)} PASS\n")


def print_all():
    all_res = {b: run_pca(b) for b in BUGS}
    names = [r[0] for r in all_res[BUGS[0]]]
    # header
    colw = 26
    header = f"{'check':34s}" + "".join(f"{b:>{colw}s}" for b in BUGS)
    print(header)
    print("-" * len(header))
    for idx, name in enumerate(names):
        row = f"{name:34s}"
        for b in BUGS:
            actual, tol, status = all_res[b][idx][1], all_res[b][idx][2], all_res[b][idx][3]
            cell = f"{actual:.2e} {status}"
            row += f"{cell:>{colw}s}"
        print(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bug", choices=BUGS, default="none")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.all:
        print_all()
    else:
        print_single(args.bug)


if __name__ == "__main__":
    main()
