"""lab2_pca.py — 手刻 PCA（前 10 個主成分），資料：sklearn digits。

只用 numpy 實作；sklearn.decomposition.PCA 僅作為對照組，不參與計算。

bug 參數（可選）：none / ratio_topk / denom_n / no_center / rows
  none       : 正確實作
  ratio_topk : explained_variance_ratio_ 分母只用前 10 個特徵值的和
  denom_n    : 共變異數矩陣分母用 n（而非 n-1）
  no_center  : 不做中心化
  rows       : 用 evecs[:K] 取列而非取欄

無參數執行：對 5 種 bug 各跑一次所有檢查，印出「檢查 × 錯誤」表。
帶參數執行：只跑指定 bug，印出詳細檢查。

檢查項目（比什麼量、容差）：
1. components shape == (10, 64)。容差：exact。
2. explained_variance（特徵值前 10）：np.allclose(rtol=1e-6, atol=1e-8)。
3. explained_variance_ratio_ 前 10：np.allclose(rtol=1e-6, atol=1e-8)。
4. 主成分向量（components_）：符號對齊後 np.allclose(rtol=1e-6, atol=1e-8)；
   另印最小 |cos| 需 >= 1-1e-6。
5. 轉換後分數（transform）：符號對齊後 np.allclose(rtol=1e-5, atol=1e-6)。
6. 重建 MSE（inverse_transform）：np.allclose(rtol=1e-5, atol=1e-6)。
7. 主成分正交性：||components @ components.T - I||_F <= 1e-8。
8. 轉換後每欄平均 ≈ 0：max |mean| <= 1e-8。
"""

import sys
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]

CHECK_NAMES = [
    "1.shape",
    "2.var",
    "3.ratio",
    "4.comp",
    "5.score",
    "6.recon",
    "7.ortho",
    "8.zmean",
]


def run_bug(bug):
    digits = load_digits()
    X = digits.data.astype(float)
    n, p = X.shape
    k = 10

    # 中心化（no_center bug：不中心化）
    if bug == "no_center":
        mean = np.zeros(p)
        Xc = X.copy()
    else:
        mean = X.mean(axis=0)
        Xc = X - mean

    # 共變異數矩陣（denom_n bug：分母用 n）
    denom = n if bug == "denom_n" else (n - 1)
    C = (Xc.T @ Xc) / denom

    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    w = w[order]
    V = V[:, order]
    eigvals_k = w[:k]

    # 取主成分（rows bug：取列而非取欄）
    if bug == "rows":
        components = V[:k, :]  # (k, p)
    else:
        components = V[:, :k].T  # (k, p)

    # explained_variance_ratio（ratio_topk bug：分母只用前 10 個）
    if bug == "ratio_topk":
        explained_variance_ratio = eigvals_k / eigvals_k.sum()
    else:
        explained_variance_ratio = eigvals_k / w.sum()

    explained_variance = eigvals_k
    scores = Xc @ components.T  # (n, k)
    X_recon = scores @ components + mean

    # 對照組
    sk = SklearnPCA(n_components=k, svd_solver="full")
    sk.fit(X)
    sk_scores = sk.transform(X)
    sk_recon = sk.inverse_transform(sk_scores)

    # 符號對齊
    signs = np.sign(np.sum(components * sk.components_, axis=1))
    signs[signs == 0] = 1.0
    components_aligned = components * signs[:, None]
    scores_aligned = scores * signs[None, :]

    results = []

    # 1. shape
    shape_ok = components.shape == (k, p)
    results.append(("1.shape", str(components.shape), shape_ok))

    # 2. explained_variance
    ev_ok = np.allclose(explained_variance, sk.explained_variance_, rtol=1e-6, atol=1e-8)
    ev_maxdiff = np.max(np.abs(explained_variance - sk.explained_variance_))
    results.append(("2.var", f"{ev_maxdiff:.2e}", ev_ok))

    # 3. explained_variance_ratio
    evr_ok = np.allclose(explained_variance_ratio, sk.explained_variance_ratio_, rtol=1e-6, atol=1e-8)
    evr_maxdiff = np.max(np.abs(explained_variance_ratio - sk.explained_variance_ratio_))
    results.append(("3.ratio", f"{evr_maxdiff:.2e}", evr_ok))

    # 4. components
    comp_ok = np.allclose(components_aligned, sk.components_, rtol=1e-6, atol=1e-8)
    comp_maxdiff = np.max(np.abs(components_aligned - sk.components_))
    cos = np.abs(np.sum(components_aligned * sk.components_, axis=1))
    min_cos = cos.min()
    comp_pass = comp_ok and (min_cos >= 1 - 1e-6)
    results.append(("4.comp", f"{comp_maxdiff:.2e}", comp_pass))

    # 5. scores
    sc_ok = np.allclose(scores_aligned, sk_scores, rtol=1e-5, atol=1e-6)
    sc_maxdiff = np.max(np.abs(scores_aligned - sk_scores))
    results.append(("5.score", f"{sc_maxdiff:.2e}", sc_ok))

    # 6. reconstruction MSE
    mse_hand = np.mean((X - X_recon) ** 2)
    mse_sk = np.mean((X - sk_recon) ** 2)
    recon_ok = np.allclose(mse_hand, mse_sk, rtol=1e-5, atol=1e-6)
    results.append(("6.recon", f"{abs(mse_hand-mse_sk):.2e}", recon_ok))

    # 7. orthogonality
    ortho = components @ components.T
    ortho_err = np.linalg.norm(ortho - np.eye(k), ord="fro")
    ortho_ok = ortho_err <= 1e-8
    results.append(("7.ortho", f"{ortho_err:.2e}", ortho_ok))

    # 8. zero mean
    maxabs_mean = np.max(np.abs(scores_aligned.mean(axis=0)))
    zm_ok = maxabs_mean <= 1e-8
    results.append(("8.zmean", f"{maxabs_mean:.2e}", zm_ok))

    return results


def print_detail(bug):
    res = run_bug(bug)
    print(f"bug={bug}")
    print("=" * 60)
    for name, actual, passed in res:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {actual}")
    print("=" * 60)
    print(f"OVERALL: {'PASS' if all(r[2] for r in res) else 'FAIL'} ({sum(r[2] for r in res)}/{len(res)})")


def print_table():
    all_res = {bug: run_bug(bug) for bug in BUGS}
    # header
    colw = 16
    header = "check".ljust(10) + "".join(b.ljust(colw) for b in BUGS)
    print("檢查 × 錯誤（每格：實際數值 PASS/FAIL）")
    print("=" * (10 + colw * len(BUGS)))
    print(header)
    print("-" * (10 + colw * len(BUGS)))
    for i, cname in enumerate(CHECK_NAMES):
        row = cname.ljust(10)
        for bug in BUGS:
            actual, passed = all_res[bug][i][1], all_res[bug][i][2]
            cell = f"{actual} {'P' if passed else 'F'}"
            row += cell.ljust(colw)
        print(row)
    print("=" * (10 + colw * len(BUGS)))


def main():
    if len(sys.argv) > 1:
        bug = sys.argv[1]
        if bug not in BUGS:
            print(f"unknown bug: {bug}; choose from {BUGS}")
            sys.exit(2)
        print_detail(bug)
    else:
        print_table()


if __name__ == "__main__":
    main()
