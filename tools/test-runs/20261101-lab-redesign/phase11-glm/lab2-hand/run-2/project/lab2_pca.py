"""手刻 PCA（只用 numpy.eigh）對照 sklearn，data/line_channels.csv。
支援 bug 參數：none / ratio_topk / denom_n / no_center / rows，
對每種 bug 跑同一組檢查，輸出「檢查 × 錯誤」表。"""
import numpy as np
from sklearn.decomposition import PCA

CSV = "data/line_channels.csv"
K = 4

X_raw = np.genfromtxt(CSV, delimiter=",", skip_header=1)
n, d = X_raw.shape

# 每欄除以標準差（母體, ddof=0），不做中心化
std = X_raw.std(axis=0)
X = X_raw / std

pca = PCA(n_components=K, svd_solver="full")
sk_scores = pca.fit_transform(X)

CHECKS = [
    "特徵值 vs sklearn explained_variance_",
    "解釋變異比例",
    "主成分方向(取絕對值)",
    "投影分數(對齊符號)",
    "重建資料",
]


def run_pca(bug):
    mu = X.mean(axis=0)
    Xc = X if bug == "no_center" else X - mu
    denom = n if bug == "denom_n" else n - 1
    C = Xc.T @ Xc / denom
    w, V = np.linalg.eigh(C)
    idx = np.argsort(w)[::-1]
    eigvals = w[idx][:K]
    if bug == "rows":
        comps = V[:K, :].T          # 錯：取前 4 列，不是前 4 個特徵向量
    else:
        comps = V[:, idx][:, :K]    # 每行一個主成分方向
    scores = Xc @ comps
    ratio_denom = eigvals.sum() if bug == "ratio_topk" else w.sum()
    expl = eigvals / ratio_denom
    return eigvals, expl, comps, scores


def check_val(a, b, tol=1e-8):
    diff = np.max(np.abs(a - b))
    return diff, diff < tol


def run_checks(bug):
    eigvals, expl, comps, scores = run_pca(bug)
    results = {}
    d_, ok_ = check_val(eigvals, pca.explained_variance_)
    results[CHECKS[0]] = (d_, ok_)
    d_, ok_ = check_val(expl, pca.explained_variance_ratio_)
    results[CHECKS[1]] = (d_, ok_)
    d_, ok_ = check_val(np.abs(comps.T), np.abs(pca.components_))
    results[CHECKS[2]] = (d_, ok_)
    signs = np.sign(np.sum(scores * sk_scores, axis=0))
    d_, ok_ = check_val(scores * signs, sk_scores)
    results[CHECKS[3]] = (d_, ok_)
    recon = scores @ comps.T
    recon_sk = sk_scores @ pca.components_
    d_, ok_ = check_val(recon, recon_sk)
    results[CHECKS[4]] = (d_, ok_)
    return results


BUGS = ["none", "ratio_topk", "denom_n", "no_center", "rows"]
all_results = {b: run_checks(b) for b in BUGS}

print(f"資料形狀: {n} x {d}\n")
print("檢查 × 錯誤 表（每格：max|diff| -> PASS/FAIL）\n")


def disp(s):
    return sum(2 if ord(c) > 0x2E7F else 1 for c in s)


def pad(s, width):
    return s + " " * (width - disp(s))


COL = 18
header = pad("檢查", 40) + "".join(f"{b:<{COL}}" for b in BUGS)
print(header)
print("-" * disp(header))
for name in CHECKS:
    row = pad(name, 40)
    for b in BUGS:
        diff, ok_ = all_results[b][name]
        cell = f"{diff:.2e} {'PASS' if ok_ else 'FAIL'}"
        row += pad(cell, COL)
    print(row)

print()
eigvals, expl, comps, scores = run_pca("none")
print("none 情境特徵值:", np.round(eigvals, 6))
print("none 情境解釋變異比例:", np.round(expl, 6))
print("none 情境累積解釋變異:", np.round(np.cumsum(expl), 6))
print("\n整體結果:", "PASS" if all_results["none"] and all(
    ok for ok, in [(v[1],) for v in all_results["none"].values()]) else "FAIL")
