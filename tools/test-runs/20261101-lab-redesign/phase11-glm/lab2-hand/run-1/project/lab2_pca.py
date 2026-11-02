"""手刻 PCA（只能用 numpy 的 eigh），sklearn 當對照組。"""
import numpy as np
from sklearn.decomposition import PCA

TOL = 1e-6

def load_standardize(path):
    X = np.loadtxt(path, delimiter=",", skiprows=1)
    std = X.std(axis=0, ddof=0)
    return X / std  # 只除以標準差，不減平均

BUGS = ("none", "ratio_topk", "denom_n", "no_center", "rows")

def my_pca(X, k, bug="none"):
    # 中心化在 PCA 內部做
    if bug == "no_center":
        Xc = X
    else:
        Xc = X - X.mean(axis=0)
    n = X.shape[0]
    denom = n if bug == "denom_n" else n - 1
    C = (Xc.T @ Xc) / denom  # 樣本共變異數矩陣
    w, V = np.linalg.eigh(C)  # eigh 回傳由小到大
    idx = np.argsort(w)[::-1]
    w = w[idx]
    V = V[:, idx]
    if bug == "rows":
        components = V[:k, :]            # bug：取前 4 列，不是前 4 個特徵向量
    else:
        components = V[:, :k].T          # (k, n_features)
    explained_variance = w[:k]
    if bug == "ratio_topk":
        total = w[:k].sum()
    else:
        total = w.sum()
    explained_variance_ratio = explained_variance / total
    # 投影：用原始資料（未標準化中心前的 X）扣平均再投影
    if bug == "no_center":
        scores = X @ components.T
    else:
        scores = (X - X.mean(axis=0)) @ components.T
    return components, explained_variance, explained_variance_ratio, scores

def check(name, a, b):
    diff = np.max(np.abs(a - b))
    ok = diff < TOL
    print(f"{name:<35} max|diff| = {diff:.3e}  ->  {'PASS' if ok else 'FAIL'}")
    return ok

def main():
    X = load_standardize("data/line_channels.csv")
    k = 4

    my_comp, my_ev, my_evr, my_scores = my_pca(X, k, bug="none")

    sk = PCA(n_components=k, svd_solver="full")
    sk_scores = sk.fit_transform(X)

    print("我的 explained_variance_ratio:", np.round(my_evr, 6))
    print("sklearn explained_variance_ratio:", np.round(sk.explained_variance_ratio_, 6))
    print("我的 components[0]:", np.round(my_comp[0], 6))
    print("sklearn components[0]:", np.round(sk.components_[0], 6))
    print()

    all_ok = True
    all_ok &= check("components (含符號校正)", np.abs(my_comp), np.abs(sk.components_))
    all_ok &= check("explained_variance", my_ev, sk.explained_variance_)
    all_ok &= check("explained_variance_ratio", my_evr, sk.explained_variance_ratio_)
    all_ok &= check("transform (scores, |abs|)", np.abs(my_scores), np.abs(sk_scores))

    print("\n全部結果:", "PASS" if all_ok else "FAIL")

    # 檢查 × 錯誤 表：每種 bug 各跑一次原本那組檢查（不准修 bug、不改檢查與門檻）
    check_names = [
        "components (含符號校正)",
        "explained_variance",
        "explained_variance_ratio",
        "transform (scores, |abs|)",
    ]
    print("\n===== 檢查 × 錯誤 表 =====")
    for bug in BUGS:
        comp, ev, evr, scores = my_pca(X, k, bug=bug)
        print(f"\n--- bug = {bug} ---")
        check("components (含符號校正)", np.abs(comp), np.abs(sk.components_))
        check("explained_variance", ev, sk.explained_variance_)
        check("explained_variance_ratio", evr, sk.explained_variance_ratio_)
        check("transform (scores, |abs|)", np.abs(scores), np.abs(sk_scores))

if __name__ == "__main__":
    main()
