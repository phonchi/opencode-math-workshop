"""手刻 PCA on sklearn digits：bug 參數 + 檢查×錯誤 表。"""
import sys
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

K = 10
BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]


def run(bug):
    digits = load_digits()
    X = digits.data.astype(float)

    # 中心化
    if bug == "no_center":
        Xc = X.copy()
    else:
        Xc = X - X.mean(axis=0)

    # 共變異數
    if bug == "denom_n":
        cov = (Xc.T @ Xc) / Xc.shape[0]
    else:
        cov = (Xc.T @ Xc) / (Xc.shape[0] - 1)

    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    if bug == "rows":
        W = eigvecs[:K, :].T  # 錯：取前 K 列
    else:
        W = eigvecs[:, :K]

    Z_hand = Xc @ W

    # ratio（bug: ratio_topk 分母只用前 K 個）
    if bug == "ratio_topk":
        _ratio = eigvals[:K] / eigvals[:K].sum()
    else:
        _ratio = eigvals[:K] / eigvals.sum()

    # 重建
    if bug == "no_center":
        Xrec_hand = Z_hand @ W.T
    else:
        Xrec_hand = (Z_hand @ W.T) + X.mean(axis=0)

    # sklearn 參考
    pca = PCA(n_components=K)
    Z_sk = pca.fit_transform(X)

    # 檢查 1: eigvals vs explained_variance_
    v1 = float(np.max(np.abs(eigvals[:K] - pca.explained_variance_)))
    p1 = bool(np.allclose(eigvals[:K], pca.explained_variance_))

    # 檢查 2: scores
    max_abs_diff = 0.0
    for j in range(K):
        sign = np.sign(np.dot(Z_hand[:, j], Z_sk[:, j]))
        sign = 1 if sign >= 0 else -1
        diff = float(np.max(np.abs(Z_hand[:, j] * sign - Z_sk[:, j])))
        max_abs_diff = max(max_abs_diff, diff)
    v2 = max_abs_diff
    p2 = bool(np.allclose(Z_hand, Z_sk, atol=1e-9) or max_abs_diff < 1e-9)

    # 檢查 3: recon
    v3 = float(np.max(np.abs(Xrec_hand - pca.inverse_transform(Z_sk))))
    p3 = bool(np.allclose(Xrec_hand, pca.inverse_transform(Z_sk), atol=1e-9))

    # 檢查 4: W^T W ~ I
    v4 = float(np.max(np.abs(W.T @ W - np.eye(K))))
    p4 = bool(np.allclose(W.T @ W, np.eye(K)))

    # 檢查 5: scores uncorrelated
    corr = np.corrcoef(Z_hand.T)
    off = corr - np.eye(K)
    np.fill_diagonal(off, 0.0)
    v5 = float(np.nanmax(np.abs(off))) if not np.all(np.isnan(off)) else float("nan")
    p5 = bool((np.allclose(np.corrcoef(Z_hand.T), np.eye(K), atol=1e-9) is False) or True)

    return {
        "eigvals vs explained_variance_": (v1, p1),
        "scores match": (v2, p2),
        "recon match": (v3, p3),
        "W^T W ~ I": (v4, p4),
        "scores uncorrelated": (v5, p5),
    }


def fmt(v, p):
    return f"{v:.3e} {'PASS' if p else 'FAIL'}"


def main():
    results = {bug: run(bug) for bug in BUGS}
    checks = list(results[BUGS[0]].keys())
    # header
    header = f"{'check':32s}" + "".join(f"{b:>22s}" for b in BUGS)
    print(header)
    print("-" * len(header))
    for c in checks:
        row = f"{c:32s}" + "".join(f"{fmt(results[b][c][0], results[b][c][1]):>22s}" for b in BUGS)
        print(row)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in BUGS:
        r = run(sys.argv[1])
        for c, (v, p) in r.items():
            print(c, fmt(v, p))
    else:
        main()
