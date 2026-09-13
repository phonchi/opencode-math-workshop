import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

N_COMPONENTS = 10
TOL = 1e-9


def hand_pca(X, n_components=N_COMPONENTS):
    n_samples, _ = X.shape
    mu = X.mean(axis=0)
    Xc = X - mu
    cov = (Xc.T @ Xc) / (n_samples - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvals_sorted = eigvals[order]
    axes = eigvecs[:, order][:, :n_components]
    scores = Xc @ axes
    evar = eigvals_sorted[:n_components]
    return {
        "mean": mu,
        "axes": axes,
        "scores": scores,
        "explained_variance": evar,
        "explained_variance_ratio": evar / eigvals_sorted.sum(),
    }


def align_axes(W, W_ref):
    aligned = np.empty_like(W)
    signs = np.empty(W.shape[1])
    for i in range(W.shape[1]):
        s = np.sign(W[:, i] @ W_ref[:, i])
        if s == 0.0:
            s = 1.0
        aligned[:, i] = W[:, i] * s
        signs[i] = s
    return aligned, signs


def verify():
    X, y = load_digits(return_X_y=True)
    np.random.seed(0)

    mine = hand_pca(X)

    pca = PCA(n_components=N_COMPONENTS, svd_solver="full", random_state=0)
    pca.fit(X)
    scores_ref = pca.transform(X)

    evar_diff = np.abs(mine["explained_variance"] - pca.explained_variance_).max()
    ratio_diff = np.abs(mine["explained_variance_ratio"] - pca.explained_variance_ratio_).max()

    aligned_axes, signs = align_axes(mine["axes"], pca.components_.T)
    colinearity = np.abs((aligned_axes * pca.components_.T).sum(axis=0))
    axes_diff = np.abs(aligned_axes - pca.components_.T).max()

    Pc = ((aligned_axes * pca.components_.T).sum(axis=0) /
          (np.linalg.norm(aligned_axes, axis=0) * np.linalg.norm(pca.components_.T, axis=0)))
    angles = np.degrees(np.arccos(np.clip(Pc, -1.0, 1.0)))

    scores_aligned = mine["scores"] @ np.diag(signs)
    scores_diff = np.abs(scores_aligned - scores_ref).max()

    X_ref_hat = pca.inverse_transform(scores_ref)
    X_hat = scores_aligned @ aligned_axes.T + mine["mean"]
    recon_diff = np.abs(X_ref_hat - X_hat).max()

    print(f"資料集: sklearn digits, X 形狀 = {X.shape} (n={X.shape[0]}, d={X.shape[1]})")
    print(f"取前 {N_COMPONENTS} 個主成分，效能公差 = {TOL:.0e}\n")

    print("== 驗證 1: explained_variance（手刻特徵值 vs sklearn 奇異值平方/(n-1)）==")
    for i in range(N_COMPONENTS):
        ev_ref = pca.explained_variance_[i]
        ev_mine = mine["explained_variance"][i]
        print(f"  PC{i + 1:>2}: 手刻={ev_mine:.12f}  sklearn={ev_ref:.12f}  "
              f"diff={abs(ev_mine - ev_ref):.3e}")
    print(f"  max|diff| = {evar_diff:.3e} -> {'PASS' if evar_diff < TOL else 'FAIL'}\n")

    print("== 驗證 2: explained_variance_ratio（手刻 λi/Σλ vs sklearn）==")
    for i in range(N_COMPONENTS):
        r_mine = mine["explained_variance_ratio"][i]
        r_ref = pca.explained_variance_ratio_[i]
        print(f"  PC{i + 1:>2}: 手刻={r_mine:.10f}  sklearn={r_ref:.10f}  "
              f"diff={abs(r_mine - r_ref):.3e}")
    print(f"  手刻 ratio 總和={mine['explained_variance_ratio'].sum():.10f}  "
          f"sklearn ratio 總和={pca.explained_variance_ratio_.sum():.10f}")
    print(f"  max|diff| = {ratio_diff:.3e} -> {'PASS' if ratio_diff < TOL else 'FAIL'}\n")

    print("== 驗證 3: 載入向量（符號對齊後）==")
    for i in range(N_COMPONENTS):
        print(f"  PC{i + 1:>2}: 手刻符號={signs[i]:+.0f}, 對齊後夾角={angles[i]:.6f} deg, "
              f"|內積|={colinearity[i]:.12f}")
    print(f"  max|diff|(對齊後矩陣) = {axes_diff:.3e} -> {'PASS' if axes_diff < TOL else 'FAIL'}\n")

    print("== 驗證 4: 主成分得分（符號對齊後）==")
    print("  前 5 列 in PC1..PC3: 手刻 vs sklearn")
    for i in range(5):
        print(f"    row{i}: 手刻={scores_aligned[i, :3]}  ref={scores_ref[i, :3]}")
    print(f"  max|diff|(全部 {X.shape[0]}x{N_COMPONENTS}) = {scores_diff:.3e} "
          f"-> {'PASS' if scores_diff < TOL else 'FAIL'}\n")

    print("== 驗證 5: 重建 X ≈ pca.inverse_transform(得分) ==")
    print(f"  手刻重建 vs sklearn 重建 max|diff| = {recon_diff:.3e} "
          f"-> {'PASS' if recon_diff < TOL else 'FAIL'}")

    all_pass = (evar_diff < TOL and ratio_diff < TOL and axes_diff < TOL and
                scores_diff < TOL and recon_diff < TOL)
    print("\n總結:", "全部 PASS：手刻 PCA 與 sklearn PCA 一致" if all_pass else "部分 FAIL")


if __name__ == "__main__":
    verify()