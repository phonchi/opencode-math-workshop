import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]
TOLS = [1e-8, 1e-8, 1e-6, 1e-6, 1e-6, 1e-10, 1e-10]
CHECK_NAMES = [
    "explained_variance (eig) max|diff|",
    "explained_variance_ratio max|diff|",
    "components max|diff| (sign aligned)",
    "transformed scores max|diff| (sign aligned)",
    "reconstruction max|diff|",
    "orthogonality max|C C^T - I|",
    "score mean max|.|",
]

def run_pca(X, bug):
    n, d = X.shape
    if bug == "no_center":
        mean = np.zeros(d)
        Xc = X.copy()
    else:
        mean = X.mean(axis=0)
        Xc = X - mean

    denom = n if bug == "denom_n" else (n - 1)
    C = (Xc.T @ Xc) / denom

    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    w = w[order]
    V = V[:, order]

    k = 10
    if bug == "rows":
        components = V[:k, :].copy()
        explained_variance = w[:k].copy()
        X_pca = Xc @ components.T
    else:
        components = V[:, :k].T.copy()
        explained_variance = w[:k].copy()
        X_pca = Xc @ V[:, :k]

    if bug == "ratio_topk":
        explained_variance_ratio = explained_variance / explained_variance.sum()
    else:
        explained_variance_ratio = explained_variance / w.sum()

    # reference (always sklearn PCA)
    pca = PCA(n_components=k)
    X_ref = pca.fit_transform(X)

    # sign alignment
    for i in range(k):
        if np.dot(components[i], pca.components_[i]) < 0:
            components[i] = -components[i]
            X_pca[:, i] = -X_pca[:, i]

    X_recon = X_pca @ components + mean
    X_ref_recon = pca.inverse_transform(X_ref)

    actuals = [
        np.max(np.abs(explained_variance - pca.explained_variance_)),
        np.max(np.abs(explained_variance_ratio - pca.explained_variance_ratio_)),
        np.max(np.abs(components - pca.components_)),
        np.max(np.abs(X_pca - X_ref)),
        np.max(np.abs(X_recon - X_ref_recon)),
        np.max(np.abs(components @ components.T - np.eye(k))),
        np.max(np.abs(X_pca.mean(axis=0))),
    ]
    return actuals

def main():
    X = load_digits().data.astype(float)
    k = 10
    results = {bug: run_pca(X, bug) for bug in BUGS}

    # table: rows = checks, cols = bugs
    colw = 17
    header = f"{'check':45s}" + "".join(f"{b:>{colw}s}" for b in BUGS)
    print("PCA 檢查 × 錯誤 表（每格：實際值 PASS/FAIL）")
    print(f"資料: digits, X shape={X.shape}, k={k}")
    print("-" * (45 + colw * len(BUGS)))
    print(header)
    print("-" * (45 + colw * len(BUGS)))
    for ci, name in enumerate(CHECK_NAMES):
        row = f"{name:45s}"
        for bug in BUGS:
            a = results[bug][ci]
            tol = TOLS[ci]
            pf = "PASS" if a <= tol else "FAIL"
            cell = f"{a:.2e}{pf[0]}"
            row += f"{cell:>{colw}s}"
        print(row)
    print("-" * (45 + colw * len(BUGS)))
    print("圖例: 格內 '...e-xxP' = PASS, '...e-xxF' = FAIL")

if __name__ == "__main__":
    main()
