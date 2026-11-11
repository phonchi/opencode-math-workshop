# -*- coding: utf-8 -*-
"""lab2_pca.py

用 numpy 的 eigh 在樣本共變異數矩陣上手刻 PCA（取前 4 個主成分），
對照組為 sklearn 的 PCA(n_components=4, svd_solver='full')。

資料：data/orders.csv（800 筆 × 11 個數值欄位）。
本實驗不用 orders_complaint.csv：PCA 是無監督降維，不需要標籤。

前處理（依題目指定）：
- 每欄除以自己的樣本標準差（ddof=1，同 pandas .std() 預設），不減平均。
- 中心化留給 PCA 本身：手刻版扣掉「縮放後的欄平均」；sklearn PCA 內建
  centering，因此對照組餵同一份「已除標準差、未中心化」的矩陣，
  兩邊唯一的差異就是 PCA 演算法（eigh 譜分解 vs full SVD）。
- 副作用（拿來當檢查 4）：除 ddof=1 標準差再中心化後，每欄樣本變異數
  恰為 1，總變異 trace(C) = 欄數 11。

手刻流程（bug = none 時）：
1. Xs = X / std(X)            僅縮放
2. Xc = Xs - mean(Xs)          中心化（在 PCA 內部做）
3. C = Xc.T @ Xc / (n - 1)     樣本共變異數矩陣，對稱半正定；
                                分母 n-1 與 sklearn explained_variance_ 一致
4. np.linalg.eigh(C)            對稱矩陣專用的譜分解，特徵值升冪回傳 → 反轉成降冪
5. 取前 4 個特徵向量（矩陣前 4 行）當負載 W；分數 Z = Xc @ W
6. 變異解釋比 = λ_k / Σλ        分母 = 全部 11 個特徵值

符號約定：特徵向量正負號任意（±v 同為合法解），sklearn 另用 svd_flip
固定符號。比較前先以「與 sklearn 分量的點積」對齊每一軸的正負號再比數值。

bug 參數（可選；只注入、不修，檢查定義與門檻完全不動）：
- none        無 bug（原版）
- ratio_topk  變異解釋比的分母只用前 4 個特徵值的和
- denom_n     共變異數矩陣的變異數分母用 n，不是 n-1
- no_center   算共變異數矩陣時不中心化（整個流程直接用未中心化的縮放矩陣）
- rows        主成分取錯方向：取特徵向量矩陣的前 4 列，不是前 4 個特徵向量（行）

每一種 bug 各跑一次「同一組 10 項檢查」（定義與門檻與原版相同），
彙整成「檢查 × 錯誤」表，每格印出實際數值與 PASS/FAIL。
"""

from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

DATA_PATH = Path("data") / "orders.csv"
N_COMPONENTS = 4

BUG_MODES = ["none", "ratio_topk", "denom_n", "no_center", "rows"]

# 門檻（與原版相同；各 bug 共用，不因 bug 改動）。
TOL_MIN_EIGVAL = -1e-10     # 檢查 2：特徵值下界（C 半正定）
TOL_TRACE_REL = 1e-12       # 檢查 3：Σλ 對 trace(C) 的相對差
TOL_UNIT_REL = 1e-10        # 檢查 4：trace(C) 對欄數的相對差
TOL_EIGVAL_REL = 1e-10      # 檢查 5：λ 對 sklearn 的最大相對差
TOL_RATIO_ABS = 1e-10       # 檢查 6：解釋比對 sklearn 的最大絕對差
TOL_VECTOR_ABS = 1e-8       # 檢查 7：負載對 sklearn 的最大絕對差
TOL_SCORE_ABS = 1e-8        # 檢查 8：分數對 sklearn 的最大絕對差
TOL_ORTHOGONAL = 1e-10      # 檢查 9：WᵀW = I 的最大偏離
TOL_VAR_REL = 1e-10         # 檢查 10：主成分樣本變異數對 λ 的最大相對差

# 表格左欄的短標籤（完整檢查名稱與門檻見 main() 印出的檢查清單）。
ROW_LABELS = {
    1: "資料完整",
    2: "半正定 min(λ)",
    3: "Σλ = trace",
    4: "trace = 11",
    5: "λ vs sklearn",
    6: "解釋比 vs sklearn",
    7: "負載 vs sklearn",
    8: "分數 vs sklearn",
    9: "正交 WᵀW = I",
    10: "變異數 = λ",
}


class CheckResult(NamedTuple):
    """一項檢查的結果：頭線數值 actual、門檻字串、PASS/FAIL。"""

    idx: int
    name: str
    actual: float
    threshold: str
    passed: bool


def run_pca(df: pd.DataFrame, bug: str = "none") -> list[CheckResult]:
    """跑一次「手刻 PCA + 10 項檢查」。bug 只注入手刻流程；檢查與門檻不變。"""
    if bug not in BUG_MODES:
        raise ValueError(f"未知的 bug：{bug}（可選：{BUG_MODES}）")

    results: list[CheckResult] = []
    n, p = df.shape

    # ===== 檢查 1：輸入資料（決定要不要丟欄位）=====
    n_nan = int(df.isna().sum().sum())
    non_numeric = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    sigma = df.std(ddof=1)
    zero_var = sigma[sigma <= 0].index.tolist()
    results.append(
        CheckResult(
            1,
            "輸入資料完整（無 NaN／非數值／零變異欄位 → 不丟欄位）",
            n_nan + len(non_numeric) + len(zero_var),
            "三者皆 = 0",
            n_nan == 0 and not non_numeric and not zero_var,
        )
    )

    # ===== 手刻 PCA（標註 [bug] 的行是注入點，其餘與原版相同）=====
    X = df.to_numpy(dtype=float)
    s = sigma.to_numpy(dtype=float)
    Xs = X / s                    # 只除標準差、不減平均
    mu = Xs.mean(axis=0)          # 中心化留給 PCA 這一步做
    Xc = Xs - mu
    if bug == "no_center":        # [bug] no_center：不中心化
        Xc = Xs

    denom = n if bug == "denom_n" else n - 1   # [bug] denom_n：分母用 n
    C = Xc.T @ Xc / denom

    eigvals, eigvecs = np.linalg.eigh(C)   # 特徵值升冪
    eigvals = eigvals[::-1]               # 反轉成降冪：變異解釋量大的在前
    eigvecs = eigvecs[:, ::-1]

    lam = eigvals[:N_COMPONENTS]  # 前 4 個特徵值（降冪）
    if bug == "rows":             # [bug] rows：取前 4「列」，不是前 4 個特徵向量（行）
        W = eigvecs[:N_COMPONENTS, :].T
    else:
        W = eigvecs[:, :N_COMPONENTS]  # 負載矩陣 (p, 4)，每欄一個主成分方向
    Z = Xc @ W                    # 投影分數 (n, 4)

    # 變異解釋比
    if bug == "ratio_topk":       # [bug] ratio_topk：分母只用前 4 個特徵值之和
        ratio_denom = lam.sum()
    else:
        ratio_denom = eigvals.sum()   # 分母 = 全譜 11 個特徵值
    ratio = lam / ratio_denom

    # ===== 對照組：sklearn（餵同一份「未中心化」的縮放矩陣；各 bug 下都維持正確）=====
    pca = PCA(n_components=N_COMPONENTS, svd_solver="full").fit(Xs)
    Z_sk = pca.transform(Xs)

    # 特徵向量符號任意：以與 sklearn 分量的點積對齊每軸正負號，再比數值
    dots = np.einsum("ij,ij->j", pca.components_.T, W)
    signs = np.where(np.sign(dots) == 0.0, 1.0, np.sign(dots))
    W_al = W * signs
    Z_al = Z * signs

    # ===== 檢查 2-10（定義與門檻與原版完全相同）=====
    results.append(
        CheckResult(
            2,
            "共變異數矩陣半正定（最小特徵值 ≥ 0，容許浮點負值）",
            float(eigvals.min()),
            f"≥ {TOL_MIN_EIGVAL:.0e}",
            eigvals.min() >= TOL_MIN_EIGVAL,
        )
    )

    trace = float(np.trace(C))
    rel_trace = abs(eigvals.sum() - trace) / trace
    results.append(
        CheckResult(
            3,
            "頻譜完整：Σλ（全部 11 個特徵值）= trace(C)",
            rel_trace,
            f"< {TOL_TRACE_REL:.0e}",
            rel_trace < TOL_TRACE_REL,
        )
    )

    rel_unit = abs(trace - p) / p
    results.append(
        CheckResult(
            4,
            "縮放自洽：trace(C) = 欄數（每欄除以樣本標準差後變異數恰為 1）",
            rel_unit,
            f"< {TOL_UNIT_REL:.0e}",
            rel_unit < TOL_UNIT_REL,
        )
    )

    rel_eig = float(np.max(np.abs(lam - pca.explained_variance_) / pca.explained_variance_))
    results.append(
        CheckResult(
            5,
            "特徵值 = sklearn explained_variance_（前 4 個）",
            rel_eig,
            f"< {TOL_EIGVAL_REL:.0e}",
            rel_eig < TOL_EIGVAL_REL,
        )
    )

    abs_ratio = float(np.max(np.abs(ratio - pca.explained_variance_ratio_)))
    results.append(
        CheckResult(
            6,
            "變異解釋比 = sklearn explained_variance_ratio_（前 4 個）",
            abs_ratio,
            f"< {TOL_RATIO_ABS:.0e}",
            abs_ratio < TOL_RATIO_ABS,
        )
    )

    abs_vec = float(np.max(np.abs(W_al - pca.components_.T)))
    results.append(
        CheckResult(
            7,
            "負載向量 = sklearn components_（對齊正負號後）",
            abs_vec,
            f"< {TOL_VECTOR_ABS:.0e}",
            abs_vec < TOL_VECTOR_ABS,
        )
    )

    abs_score = float(np.max(np.abs(Z_al - Z_sk)))
    results.append(
        CheckResult(
            8,
            "投影分數 = sklearn transform()（對齊正負號後）",
            abs_score,
            f"< {TOL_SCORE_ABS:.0e}",
            abs_score < TOL_SCORE_ABS,
        )
    )

    abs_ortho = float(np.max(np.abs(W.T @ W - np.eye(N_COMPONENTS))))
    results.append(
        CheckResult(
            9,
            "負載正交：WᵀW = I₄（主成分軸互相垂直且單位長）",
            abs_ortho,
            f"< {TOL_ORTHOGONAL:.0e}",
            abs_ortho < TOL_ORTHOGONAL,
        )
    )

    rel_var = float(np.max(np.abs(Z.var(axis=0, ddof=1) - lam) / lam))
    results.append(
        CheckResult(
            10,
            "PCA 定義性質：第 k 個主成分分數的樣本變異數 = λ_k（不依賴 sklearn）",
            rel_var,
            f"< {TOL_VAR_REL:.0e}",
            rel_var < TOL_VAR_REL,
        )
    )

    return results


def disp_len(s: str) -> int:
    """終端機顯示寬度（CJK 全形算 2、其他算 1），只為了表格對齊。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def disp_pad(s: str, width: int) -> str:
    """補空格到指定顯示寬度（只為了表格對齊）。"""
    return s + " " * max(1, width - disp_len(s))


def fmt_cell(r: CheckResult) -> str:
    """表格格子：實際數值（3 位有效數字）+ PASS/FAIL。"""
    return f"{r.actual:.3g} {'PASS' if r.passed else 'FAIL'}".rjust(16)


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    print(f"資料：{DATA_PATH}，{df.shape[0]} 筆 × {df.shape[1]} 欄")
    print("前處理：每欄除以樣本標準差（ddof=1），不減平均；中心化由 PCA 內部處理")
    print(f"手刻：eigh 於樣本共變異數矩陣；對照：sklearn PCA(n_components={N_COMPONENTS}, svd_solver='full')")
    print(f"bug 模式：{'、'.join(BUG_MODES)}（只注入不修；檢查定義與門檻不變）\n")

    # 每種 bug 各跑一次同一組 10 項檢查
    runs = {bug: run_pca(df, bug) for bug in BUG_MODES}

    # 檢查清單：完整名稱與門檻（各 bug 共用、與原版相同）
    print("== 檢查清單（名稱｜門檻；各 bug 共用同一組檢查與門檻）==")
    for r in runs[BUG_MODES[0]]:
        print(f"{r.idx:>2}. {r.name}｜門檻：{r.threshold}")
    print()

    # 檢查 × 錯誤 表
    print("== 檢查 × 錯誤 表（每格：實際數值 PASS/FAIL）==")
    header = disp_pad("檢查", 22) + "".join(f"{bug:>16}" for bug in BUG_MODES)
    print(header)
    print("-" * disp_len(header))
    for i in range(len(runs[BUG_MODES[0]])):
        label = f"{i + 1} {ROW_LABELS[i + 1]}"
        cells = "".join(fmt_cell(runs[bug][i]) for bug in BUG_MODES)
        print(disp_pad(label, 22) + cells)
    print("-" * disp_len(header))
    tally = disp_pad("PASS 合計", 22) + "".join(
        f"{sum(r.passed for r in runs[bug])}/{len(runs[bug])}".rjust(16) for bug in BUG_MODES
    )
    print(tally)


if __name__ == "__main__":
    main()
