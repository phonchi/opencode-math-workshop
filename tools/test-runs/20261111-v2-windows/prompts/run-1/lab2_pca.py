# -*- coding: utf-8 -*-
"""lab2_pca.py — 用 numpy.linalg.eigh 手刻 PCA，和 sklearn PCA 對照（可注入 bug）。

流程：
1. 讀 data/orders.csv（800 列 x 11 個數值欄），沿用 lab1 的防呆：丟 std=0 欄位
   （這份資料沒有觸發，11 欄全保留）。
2. 前處理：每欄除以自己的標準差（ddof=0），不減平均 — 中心化留給 PCA 自己做
   （手刻版和 sklearn 版都在 PCA 內部減平均，兩邊吃同一份縮放後矩陣）。
3. 手刻：共變異數矩陣 C = Xc.T @ Xc / (n-1)，eigh 解特徵值/向量，
   降冪排（eigh 原生是升冪）取前 4 個主成分。
4. 對照組：sklearn PCA(n_components=4, svd_solver='full')。
5. 檢查（每項印實際數值、門檻、PASS/FAIL）：
   - 對照 sklearn：特徵值、變異解釋比、主成分向量、投影分數。
   - 不依賴 sklearn 的內部一致性：主成分單正交、分數去相關、
     Eckart-Young 重構殘差、總變異守恆。

bug 模式（只注入在手刻 pca_eigh；sklearn 對照組、8 項檢查、門檻都不動）：
  none        無 bug（正確版）
  ratio_topk  變異解釋比的分母只用前 4 個特徵值的和
  denom_n     共變異數矩陣的分母用 n，不是 n-1
  no_center   算共變異數矩陣前沒中心化
  rows        主成分取錯方向：取 V 的前 4 列（row）再轉置，不是前 4 個特徵向量

用法：
  uv run python lab2_pca.py           # 五種模式各跑一次原檢查，最後印「檢查 x 錯誤」表
  uv run python lab2_pca.py <bug>     # 只跑一種模式（none/ratio_topk/denom_n/no_center/rows）

注意：特徵向量的正負號本來就不唯一（eigh 和 SVD 各自決定符號），
      比較前先用內積對齊成同號，這是數學上唯一有意義的比法。
"""

import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

X_CSV = "data/orders.csv"
K = 4  # 取前幾個主成分

BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]
BUG_DESC = {
    "none": "無 bug（正確版）",
    "ratio_topk": "變異解釋比的分母只用前 K 個特徵值的和",
    "denom_n": "共變異數矩陣的分母用 n，不是 n-1",
    "no_center": "算共變異數矩陣前沒中心化",
    "rows": "主成分取 V 的前 K 列（row）再轉置，不是前 K 個特徵向量（column）",
}

# 彙總表用的檢查簡稱（完整檢查名稱見各段輸出）
SHORT_LABELS = [
    "1. 特徵值（vs sklearn）",
    "2. 變異解釋比（vs sklearn）",
    "3. 主成分向量（vs sklearn）",
    "4. 投影分數（vs sklearn）",
    "5. 主成分單正交",
    "6. 分數去相關",
    "7. Eckart-Young 重構殘差",
    "8. 總變異守恆",
]

# 門檻：實測差異都在 1e-14 以下（機器精度級），門檻比實際誤差寬約兩個數量級，
# 但仍緊到能抓出真正的錯（中心化錯、ddof 錯、排序錯都會差 1e-2 以上）。
TOL_SCALED = 1e-10    # 帶尺度的量：特徵值 O(1)、投影分數 O(10)
TOL_DIMLESS = 1e-12   # 無因次量：解釋比、單正交、去相關、總變異
TOL_RECON_REL = 1e-10  # Eckart-Young 重構殘差的相對誤差


def pca_eigh(X, k, bug="none"):
    """手刻 PCA：中心化 -> 共變異數矩陣 -> eigh，回前 k 個（降冪）。

    bug="none" 是正確版；其他模式是刻意注入的錯誤（見模組 docstring），
    用來驗證那組檢查抓不抓得到。

    回傳 dict：
      mean            中心化用的平均（p,）
      eigenvalues     全部特徵值，降冪（p,）
      ratio           變異解釋比（p,）
      components      前 k 個主成分當「欄」（p, k），和 sklearn 的列向量互為轉置
      scores          投影分數（n, k）
    """
    n = len(X)
    mean = X.mean(axis=0)
    if bug == "no_center":
        Xc = X  # bug：沒有中心化
    else:
        Xc = X - mean  # 中心化在 PCA 內部做，不在前處理做
    if bug == "denom_n":
        C = Xc.T @ Xc / n  # bug：分母用 n
    else:
        C = Xc.T @ Xc / (n - 1)  # 分母 n-1，對齊 sklearn explained_variance_ 的定義
    w, V = np.linalg.eigh(C)  # eigh 只吃對稱矩陣，回傳升冪
    order = np.argsort(w)[::-1]  # 改成降冪
    w, V = w[order], V[:, order]
    if bug == "rows":
        comp = V[:k, :].T  # bug：拿到 V 的前 k 列（row）再轉置，不是前 k 個特徵向量
    else:
        comp = V[:, :k]
    if bug == "ratio_topk":
        ratio = w / w[:k].sum()  # bug：分母只加前 k 個特徵值
    else:
        ratio = w / w.sum()
    return {
        "mean": mean,
        "eigenvalues": w,
        "ratio": ratio,
        "components": comp,
        "scores": Xc @ comp,
    }


def check(label, value, threshold):
    """印一項檢查的實際數值、門檻和 PASS/FAIL，回傳是否通過。"""
    ok = value < threshold
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    print(f"         實際 {value:.3e}，門檻 < {threshold:.0e}")
    return ok


def run_bug(Xs, bug):
    """對一種 bug 跑一次完整流程（原本那組檢查，沒有新增或修改）。

    回傳 cells：8 個 (實際數值, 門檻, PASS/FAIL)，順序同檢查 1-8。
    """
    n = len(Xs)
    mine = pca_eigh(Xs, K, bug)
    ref = PCA(n_components=K, svd_solver="full").fit(Xs)

    lam = mine["eigenvalues"][:K]
    ratio = mine["ratio"]

    # --- 特徵向量符號對齊：翻成和 sklearn 同號，分數跟著向量一起翻 ---
    V = mine["components"]
    signs = np.sign(np.sum(V * ref.components_.T, axis=0))
    signs[signs == 0] = 1.0
    V_aligned = V * signs
    S = mine["scores"] * signs

    print(f"\n前 {K} 個主成分（手刻 eigh vs sklearn）：")
    header = (
        f"{'#':>2} | {'特徵值(手刻)':>13} | {'特徵值(sklearn)':>15}"
        f" | {'解釋比(手刻)':>12} | {'解釋比(sklearn)':>14}"
    )
    print(header)
    print("-" * len(header))
    for i in range(K):
        print(
            f"{i + 1:>2} | {lam[i]:>13.6f} | {ref.explained_variance_[i]:>15.6f}"
            f" | {ratio[i]:>12.4%} | {ref.explained_variance_ratio_[i]:>14.4%}"
        )
    cum = ratio[:K].sum()
    print(f"累積變異（前 {K} 個）：手刻 {cum:.2%}，sklearn {ref.explained_variance_ratio_.sum():.2%}")

    # --- 檢查（同 none 模式那組） ---
    print(f"\n檢查（{Xs.shape[1]} 欄標準化後、取前 {K} 個主成分）：")
    results = []
    cells = []

    v1 = np.abs(lam - ref.explained_variance_).max()
    ok1 = check(
        f"1. 特徵值 vs sklearn explained_variance_（前 {K} 個，max |diff|）",
        v1,
        TOL_SCALED,
    )
    results.append(ok1)
    cells.append((v1, TOL_SCALED, ok1))

    v2 = np.abs(ratio[:K] - ref.explained_variance_ratio_).max()
    ok2 = check(
        "2. 變異解釋比 vs sklearn explained_variance_ratio_（max |diff|）",
        v2,
        TOL_DIMLESS,
    )
    results.append(ok2)
    cells.append((v2, TOL_DIMLESS, ok2))

    v3 = np.abs(V_aligned - ref.components_.T).max()
    ok3 = check(
        "3. 主成分向量 vs sklearn components_（符號對齊後，max |diff|）",
        v3,
        TOL_DIMLESS,
    )
    results.append(ok3)
    cells.append((v3, TOL_DIMLESS, ok3))

    v4 = np.abs(S - ref.transform(Xs)).max()
    ok4 = check(
        "4. 投影分數 vs sklearn transform()（符號對齊後，max |diff|）",
        v4,
        TOL_SCALED,
    )
    results.append(ok4)
    cells.append((v4, TOL_SCALED, ok4))

    v5 = np.abs(V_aligned.T @ V_aligned - np.eye(K)).max()
    ok5 = check(
        "5. 主成分單正交：max |V^T V - I|",
        v5,
        TOL_DIMLESS,
    )
    results.append(ok5)
    cells.append((v5, TOL_DIMLESS, ok5))

    Sc = S - S.mean(axis=0)
    cov_S = Sc.T @ Sc / (n - 1)
    v6 = np.abs(cov_S - np.diag(lam)).max()
    ok6 = check(
        "6. 分數去相關：max |cov(S) - diag(前 k 個特徵值)|",
        v6,
        TOL_DIMLESS,
    )
    results.append(ok6)
    cells.append((v6, TOL_DIMLESS, ok6))

    # Eckart-Young：扣掉前 k 個主成分的重構殘差，平方和 = (n-1) * 其餘特徵值和
    Xc = Xs - mine["mean"]
    resid = Xc - S @ V_aligned.T
    ey_target = (n - 1) * mine["eigenvalues"][K:].sum()
    ey_relerr = abs(np.sum(resid**2) - ey_target) / ey_target
    ok7 = check(
        f"7. Eckart-Young：||Xc - S V^T||_F^2 = (n-1) * 第 {K + 1} 個起特徵值和（相對誤差）",
        ey_relerr,
        TOL_RECON_REL,
    )
    results.append(ok7)
    cells.append((ey_relerr, TOL_RECON_REL, ok7))

    v8 = abs(mine["eigenvalues"].sum() - np.var(Xc, axis=0, ddof=1).sum())
    ok8 = check(
        "8. 總變異守恆：|sum(所有特徵值) - 各欄變異( ddof=1)總和|",
        v8,
        TOL_DIMLESS,
    )
    results.append(ok8)
    cells.append((v8, TOL_DIMLESS, ok8))

    print()
    if all(results):
        print(f"全部 {len(results)} 項檢查 PASS：手刻 eigh PCA 與 sklearn 一致（在門檻內）。")
    else:
        print(f"有 {sum(not r for r in results)} 項 FAIL，請檢查實作。")

    return cells


def disp_w(s):
    """字串的終端顯示寬度（CJK 算 2），讓中文表對得整齊。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def pad(s, w):
    return s + " " * max(0, w - disp_w(s))


def print_summary_table(cells_by_bug):
    """印「檢查 x 錯誤」彙總表：每格 = 實際數值 + PASS/FAIL，門檻列在「門檻」欄。"""
    bug_w = max(disp_w(b) for b in BUGS)
    label_w = max(disp_w(s) for s in SHORT_LABELS)
    thr_w = disp_w("<1e-10")
    cell_w = max(bug_w, disp_w("0.00e+00 FAIL")) + 3  # 每格「數值 + PASS/FAIL」的寬度

    print(f"\n{'=' * 72}")
    print("檢查 x 錯誤彙總表（每格：實際數值 + PASS/FAIL；門檻見「門檻」欄）")
    print(f"{'=' * 72}")
    header = (
        pad("檢查", label_w + 2)
        + pad("門檻", thr_w + 3)
        + "".join(pad(b, cell_w) for b in BUGS)
    )
    print(header)
    print("-" * disp_w(header))
    for i, label in enumerate(SHORT_LABELS):
        thr = cells_by_bug["none"][i][1]
        row = pad(label, label_w + 2) + pad(f"<{thr:.0e}", thr_w + 3)
        for b in BUGS:
            v, _, ok = cells_by_bug[b][i]
            row += pad(f"{v:.2e} {'PASS' if ok else 'FAIL'}", cell_w)
        print(row)
    print("-" * disp_w(header))
    fail_row = pad("FAIL 項數 / 8", label_w + 2) + " " * (thr_w + 3)
    for b in BUGS:
        n_fail = sum(1 for _, _, ok in cells_by_bug[b] if not ok)
        fail_row += pad(str(n_fail), cell_w)
    print(fail_row)


def main():
    bug_mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if bug_mode != "all" and bug_mode not in BUGS:
        raise SystemExit(f"未知 bug 模式：{bug_mode}（可選：{'/'.join(BUGS + ['all'])}）")

    df = pd.read_csv(X_CSV)
    drop_cols = [c for c in df.columns if df[c].std() == 0]
    df = df.drop(columns=drop_cols)
    X = df.to_numpy(dtype=float)
    if drop_cols:
        print(f"丟掉 std=0 欄位：{drop_cols}")
    print(f"資料：{X.shape[0]} 列 x {X.shape[1]} 個特徵欄位（{X_CSV}）")

    # --- 前處理：只除以標準差（ddof=0），不減平均 ---
    Xs = X / X.std(axis=0, ddof=0)

    if bug_mode == "all":
        print(f"bug 模式：全部（{', '.join(BUGS)}），每種各跑一次原檢查後彙總成表")
        cells_by_bug = {}
        for b in BUGS:
            print(f"\n{'=' * 72}")
            print(f"bug = {b}：{BUG_DESC[b]}")
            print(f"{'=' * 72}")
            cells_by_bug[b] = run_bug(Xs, b)
        print_summary_table(cells_by_bug)
    else:
        print(f"bug = {bug_mode}：{BUG_DESC[bug_mode]}")
        run_bug(Xs, bug_mode)


if __name__ == "__main__":
    main()
