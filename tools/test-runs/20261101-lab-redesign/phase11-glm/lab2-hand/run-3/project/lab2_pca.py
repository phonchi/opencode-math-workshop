"""手刻 PCA（只用 numpy.eigh），對照 sklearn（svd_solver='full'）。

資料：data/line_channels.csv（表頭 ch01..ch11）
前處理：每欄除以該欄標準差，但不減平均（中心化在 PCA 內部做）。

bug 模式（教學用，刻意植入錯誤，不修）：
  none       正確版本
  ratio_topk explained_variance_ratio_ 的分母只用前 4 個特徵值的和
  denom_n    共變異矩陣分母用 n，不是 n-1
  no_center  完全不中心化
  rows       主成分取錯方向：取特徵向量矩陣的前 4 列，不是前 4 個特徵向量（欄）
"""

import numpy as np

CSV = "data/line_channels.csv"
N_COMPONENTS = 4

BUG_MODES = ["none", "ratio_topk", "denom_n", "no_center", "rows"]


def load_data(path: str) -> np.ndarray:
    return np.genfromtxt(path, delimiter=",", skip_header=1)


def std_scale(X: np.ndarray) -> np.ndarray:
    """每欄除以樣本標準差（ddof=0，與 sklearn StandardScaler 相同），不減平均。"""
    std = np.std(X, axis=0)
    return X / std


class HandPCA:
    """eigh 版 PCA：中心化後取共變異矩陣，用特徵分解求主成分。

    bug 參數刻意植入指定錯誤，保持原樣不修正。
    """

    def __init__(self, n_components: int, bug: str = "none"):
        assert bug in BUG_MODES
        self.n_components = n_components
        self.bug = bug

    def fit(self, X: np.ndarray) -> "HandPCA":
        self.mean_ = X.mean(axis=0)
        Xc = X - self.mean_ if self.bug != "no_center" else X
        denom = X.shape[0] if self.bug == "denom_n" else X.shape[0] - 1
        cov = (Xc.T @ Xc) / denom
        eigvals, eigvecs = np.linalg.eigh(cov)  # eigh 回傳由小到大
        order = np.argsort(eigvals)[::-1]
        self.explained_variance_ = eigvals[order][: self.n_components]
        if self.bug == "rows":
            self.components_ = eigvecs[: self.n_components, :]  # 錯：取前 4 列
        else:
            self.components_ = eigvecs[:, order][:, : self.n_components].T
        self.eigvals_sorted_ = eigvals[order]
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        Xc = X - self.mean_ if self.bug != "no_center" else X
        return Xc @ self.components_.T

    def explained_variance_ratio(self, X: np.ndarray) -> np.ndarray:
        n = X.shape[0]
        if self.bug == "ratio_topk":
            denom = np.sum(self.eigvals_sorted_[: self.n_components])
        else:
            denom = np.sum(
                np.linalg.eigvalsh(
                    (X - X.mean(axis=0)).T @ (X - X.mean(axis=0)) / (n - 1)
                )
            )
        return self.explained_variance_ / denom


CHECK_NAMES = [
    "explained_variance_",
    "components_（對齊正負號）",
    "transform 投影分數（對齊正負號）",
    "explained_variance_ratio_",
]


def run_checks(X: np.ndarray, pca_hand: "HandPCA", T_hand: np.ndarray,
               pca_sk, T_sk) -> list:
    """跑原本那組 4 項檢查，回傳 (名稱, 實際數值字串, PASS/FAIL)。"""
    n, d = X.shape
    results = []

    def check(name: str, actual, expect, tol: float = 1e-8) -> None:
        err = float(np.max(np.abs(actual - expect)))
        status = "PASS" if err <= tol else "FAIL"
        results.append((name, f"{err:.3e}", status))

    # 檢查 1：explained variance
    check(
        CHECK_NAMES[0],
        pca_hand.explained_variance_,
        pca_sk.explained_variance_,
    )

    # 檢查 2：components_（特徵向量正負號不定，對齊後比較）
    sign = np.sign(np.sum(pca_hand.components_ * pca_sk.components_, axis=1))
    sign[sign == 0] = 1.0
    check(CHECK_NAMES[1], pca_hand.components_ * sign[:, None], pca_sk.components_)

    # 檢查 3：投影分數（同樣對齊正負號）
    check(CHECK_NAMES[2], T_hand * sign[None, :], T_sk)

    # 檢查 4：解释變異比例
    evr_hand = pca_hand.explained_variance_ratio(X)
    check(CHECK_NAMES[3], evr_hand, pca_sk.explained_variance_ratio_)

    return results


def main() -> None:
    X = std_scale(load_data(CSV))
    n, d = X.shape
    print(f"資料形狀: {n} x {d}（已除以欄標準差，未減平均）\n")

    # 對照組：sklearn（svd_solver='full'）
    from sklearn.decomposition import PCA

    pca_sk = PCA(n_components=N_COMPONENTS, svd_solver="full").fit(X)
    T_sk = pca_sk.transform(X)

    table = {}  # bug -> [(name, value, status), ...]
    for bug in BUG_MODES:
        pca_hand = HandPCA(N_COMPONENTS, bug=bug).fit(X)
        T_hand = pca_hand.transform(X)
        table[bug] = run_checks(X, pca_hand, T_hand, pca_sk, T_sk)

    # 「檢查 × 錯誤」表：每格印實際數值與 PASS/FAIL
    name_w = max(len(s) for s in CHECK_NAMES) + 2
    col_w = 20
    header = "檢查".ljust(name_w) + "".join(b.center(col_w) for b in BUG_MODES)
    print(header)
    print("-" * len(header))
    for i, name in enumerate(CHECK_NAMES):
        row = name.ljust(name_w)
        for bug in BUG_MODES:
            _, val, status = table[bug][i]
            cell = f"{val} {status}"
            row += cell.center(col_w)
        print(row)

    print("\n各錯誤模式的前 4 個主成分解释變異比例（手刻版）:")
    for bug in BUG_MODES:
        pca_hand = HandPCA(N_COMPONENTS, bug=bug).fit(X)
        evr = pca_hand.explained_variance_ratio(X)
        print(f"  {bug:10s}: " + " ".join(f"PC{i}={r:.6f}" for i, r in enumerate(evr, 1)))


if __name__ == "__main__":
    main()
