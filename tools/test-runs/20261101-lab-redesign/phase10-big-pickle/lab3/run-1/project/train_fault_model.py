"""產線故障預測：可重現的訓練與驗證腳本。

用法：uv run python train_fault_model.py
輸出：figs/fault_model_*.png、notes/line_fault_metrics.csv
"""
import csv
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK TC", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA = Path("data/line_faults.csv")
FIGS = Path("figs")
NOTES = Path("notes")
FIGS.mkdir(exist_ok=True)
NOTES.mkdir(exist_ok=True)

FEATURES = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]


def load():
    rows = list(csv.DictReader(DATA.open()))
    for r in rows:
        r["record_id"] = int(r["record_id"])
        r["fault"] = int(r["fault"])
    rows.sort(key=lambda r: r["record_id"])
    X = np.array([[float(r[c]) for c in FEATURES] for r in rows])
    y = np.array([r["fault"] for r in rows])
    rid = np.array([r["record_id"] for r in rows])
    return X, y, rid


def model(name):
    return {
        "logistic": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=0),
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            random_state=0,
            n_jobs=-1,
        ),
        "hist_gbdt": HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.05, max_leaf_nodes=15, random_state=0
        ),
    }[name]


def threshold_at_recall(y, p, target):
    """在訓練資料上挑選可達到 target recall 的最低門檻。"""
    pos = np.sort(p[y == 1])
    k = max(1, int(np.ceil(target * len(pos))))
    return pos[-k]


def prf(y, p, thr):
    pred = p >= thr
    tp = int((pred & (y == 1)).sum())
    fp = int((pred & (y == 0)).sum())
    fn = int((~pred & (y == 1)).sum())
    tn = int((~pred & (y == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return prec, rec, f1, fpr, tp, fp, fn, tn


def random_cv(X, y, use_id=False):
    xx = np.column_stack([X, np.arange(len(y))]) if use_id else X
    out = {}
    for m in ["logistic", "random_forest", "hist_gbdt"]:
        p = cross_val_predict(
            model(m), xx, y, cv=StratifiedKFold(5, shuffle=True, random_state=0),
            method="predict_proba",
        )[:, 1]
        # 以 F1 最佳門檻呈現（僅供與時間切分對照）
        best = max(
            (prf(y, p, t)[2], t) for t in np.linspace(0.01, 0.99, 99)
        )
        prec, rec, f1, fpr, *_ = prf(y, p, best[1])
        out[m] = dict(auc=roc_auc_score(y, p), ap=average_precision_score(y, p),
                      brier=brier_score_loss(y, p), thr=best[1], precision=prec,
                      recall=rec, f1=f1, fpr=fpr, probs=p)
    return out


def main():
    X, y, rid = load()
    n = len(y)
    print(f"資料：{n} 筆，故障 {y.sum()} 筆（{y.mean():.1%}），record_id {rid.min()}-{rid.max()}")
    fault_ids = rid[y == 1]
    print(f"故障記錄全部分布在 record_id {fault_ids.min()}-{fault_ids.max()}")
    for lo in range(0, n, 50):
        print(f"  id {rid[lo]:3d}-{rid[min(lo+49, n-1)]:3d}: 故障率 {y[lo:lo+50].mean():.2f}")

    metrics = []

    # 1) 隨機切分（忽略時間）——常見但在此資料會高估
    rand = random_cv(X, y)
    rand_leak = random_cv(X, y, use_id=True)
    for m, d in rand.items():
        metrics.append(dict(scheme="random_5fold", model=m, auc=d["auc"], ap=d["ap"],
                            brier=d["brier"], threshold=d["thr"], precision=d["precision"],
                            recall=d["recall"], f1=d["f1"], fpr=d["fpr"]))
    for m, d in rand_leak.items():
        metrics.append(dict(scheme="random_5fold_with_record_id", model=m, auc=d["auc"],
                            ap=d["ap"], brier=d["brier"], threshold=d["thr"],
                            precision=d["precision"], recall=d["recall"], f1=d["f1"],
                            fpr=d["fpr"]))

    # 2) 時間切分：前 60% 訓練、後 40% 測試（測試期完全沒有故障）
    cut = int(0.6 * n)
    oot = {}
    for m in ["logistic", "random_forest", "hist_gbdt"]:
        mm = model(m).fit(X[:cut], y[:cut])
        p_tr = mm.predict_proba(X[:cut])[:, 1]
        p_te = mm.predict_proba(X[cut:])[:, 1]
        thr = threshold_at_recall(y[:cut], p_tr, 0.9)
        fpr = float((p_te >= thr).mean())
        oot[m] = dict(threshold=thr, alarms=int((p_te >= thr).sum()),
                      test_n=len(p_te), test_pos=int(y[cut:].sum()), fpr=fpr,
                      probs=p_te)
        metrics.append(dict(scheme="time_holdout_last40pct", model=m, auc=np.nan,
                            ap=np.nan, brier=np.nan, threshold=thr, precision=np.nan,
                            recall=np.nan, f1=np.nan, fpr=fpr))

    # 3) 故障期後上線：前 200 筆訓練（含全部 71 個故障），之後 700 筆全正常
    train_end = 200
    post = {}
    for m in ["logistic", "random_forest", "hist_gbdt"]:
        mm = model(m).fit(X[:train_end], y[:train_end])
        p_tr = mm.predict_proba(X[:train_end])[:, 1]
        p_te = mm.predict_proba(X[train_end:])[:, 1]
        thr = threshold_at_recall(y[:train_end], p_tr, 0.9)
        fpr = float((p_te >= thr).mean())
        post[m] = dict(threshold=thr, alarms=int((p_te >= thr).sum()),
                       test_n=len(p_te), test_pos=0, fpr=fpr, probs=p_te)
        metrics.append(dict(scheme="deploy_after_fault_episode", model=m, auc=np.nan,
                            ap=np.nan, brier=np.nan, threshold=thr, precision=np.nan,
                            recall=np.nan, f1=np.nan, fpr=fpr))

    # 指標 CSV
    with (NOTES / "line_fault_metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(metrics[0].keys()))
        w.writeheader()
        w.writerows(metrics)

    # 圖 1：時間軸上的故障與溫度
    fig, ax = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    ax[0].scatter(rid[y == 0], X[y == 0, 1], s=8, c="#9aa5b1", label="正常")
    ax[0].scatter(rid[y == 1], X[y == 1, 1], s=12, c="#d1495b", label="故障")
    ax[0].axvspan(1, 111, color="#d1495b", alpha=0.08)
    ax[0].set_ylabel("振動 (mm/s)")
    ax[0].legend(loc="upper right")
    ax[1].plot(rid, X[:, 0], lw=0.8, c="#2e6f95")
    ax[1].axvspan(1, 111, color="#d1495b", alpha=0.08)
    ax[1].set_ylabel("溫度 (°C)")
    ax[1].set_xlabel("record_id（原始時間順序）")
    fig.suptitle("故障標籤集中在開頭 111 筆，之後 789 筆全為正常")
    fig.tight_layout()
    fig.savefig(FIGS / "fault_model_timeline.png", dpi=150)
    plt.close(fig)

    # 圖 2：隨機切分 vs 時間切分（測試期無故障）
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    names = list(rand)
    xx = np.arange(len(names))
    ax[0].bar(xx - 0.2, [rand[m]["auc"] for m in names], 0.4, label="隨機 5-fold（無 id）")
    ax[0].bar(xx + 0.2, [rand_leak[m]["auc"] for m in names], 0.4, label="隨機 5-fold（含 id）")
    ax[0].set_xticks(xx, names, rotation=15)
    ax[0].set_ylim(0.8, 1.02)
    ax[0].set_ylabel("AUC")
    ax[0].axhline(0.5, ls="--", c="k", lw=0.8)
    ax[0].legend(fontsize=8)
    ax[0].set_title("隨機切分：看似很準，實為時間洩漏")
    ax[1].bar(xx - 0.2, [oot[m]["fpr"] for m in names], 0.4, label="後 40% 全正常期")
    ax[1].bar(xx + 0.2, [post[m]["fpr"] for m in names], 0.4, label="故障期後 700 筆")
    ax[1].set_xticks(xx, names, rotation=15)
    ax[1].set_ylabel("誤報率（測試期無故障可抓）")
    ax[1].set_title("時間切分：只能量到誤報，量不到召回率")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "fault_model_validation.png", dpi=150)
    plt.close(fig)

    # 螢幕摘要
    print("\n=== 隨機 5-fold（忽略時間；高估）===")
    for m, d in rand.items():
        print(f"{m:14s} AUC={d['auc']:.3f} AP={d['ap']:.3f} F1={d['f1']:.3f} "
              f"(P={d['precision']:.2f}, R={d['recall']:.2f})")
    print("=== 同一資料加入 record_id（洩漏示範）===")
    for m, d in rand_leak.items():
        print(f"{m:14s} AUC={d['auc']:.3f} AP={d['ap']:.3f}")
    print("\n=== 時間切分（前 60% 訓練 / 後 40% 測試）===")
    for m, d in oot.items():
        print(f"{m:14s} 測試故障數=0  門檻={d['threshold']:.3f}  "
              f"誤報={d['alarms']}/{d['test_n']} ({d['fpr']:.1%})")
    print("=== 故障期後上線（前 200 訓練 / 後 700 測試）===")
    for m, d in post.items():
        print(f"{m:14s} 測試故障數=0  門檻={d['threshold']:.3f}  "
              f"誤報={d['alarms']}/{d['test_n']} ({d['fpr']:.1%})")
    print(f"\n已輸出：{FIGS}/fault_model_*.png、{NOTES}/line_fault_metrics.csv")


if __name__ == "__main__":
    main()
