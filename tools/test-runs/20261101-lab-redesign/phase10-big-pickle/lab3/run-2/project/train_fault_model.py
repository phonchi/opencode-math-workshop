"""line_faults.csv 故障預測：模型訓練與上線可行性檢查。

重點不是把 random CV 的分數衝高，而是檢查這個資料集能不能支撐
「未來產線」的部署決策。執行：uv run python train_fault_model.py
"""

import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "temp_c",
    "vibration_mm_s",
    "pressure_kpa",
    "flow_lpm",
    "current_a",
    "speed_rpm",
]
DATA = "data/line_faults.csv"


def load():
    with open(DATA, newline="") as fh:
        rows = list(csv.DictReader(fh))
    X = np.array([[float(r[k]) for k in FEATURES] for r in rows])
    y = np.array([int(r["fault"]) for r in rows])
    rid = np.array([int(r["record_id"]) for r in rows])
    order = np.argsort(rid)
    return X[order], y[order], rid[order]


def make_models():
    return {
        "logreg": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")
        ),
        "rf": RandomForestClassifier(
            n_estimators=500,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=0,
            n_jobs=-1,
        ),
    }


def random_cv(X, y):
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    out = {}
    for name, clf in make_models().items():
        p = cross_val_predict(clf, X, y, cv=cv, method="predict_proba")[:, 1]
        out[name] = {
            "roc_auc": roc_auc_score(y, p),
            "pr_auc": average_precision_score(y, p),
            "brier": brier_score_loss(y, p),
            "pred_pos_at_0.5": int((p > 0.5).sum()),
            "proba": p,
        }
    return out


def temporal_check(X, y, rid):
    """用時間切分，模擬真正的上線情境：用過去預測未來。"""
    checks = []
    for cut in (100, 150, 200):
        train = np.arange(cut)
        test = np.arange(cut, len(y))
        clf = RandomForestClassifier(
            n_estimators=500, min_samples_leaf=3, class_weight="balanced",
            random_state=0, n_jobs=-1,
        ).fit(X[train], y[train])
        p = clf.predict_proba(X[test])[:, 1]
        checks.append(
            {
                "train_records": f"1-{cut}",
                "train_faults": int(y[train].sum()),
                "test_records": f"{cut + 1}-{len(y)}",
                "test_faults": int(y[test].sum()),
                "test_roc_auc": None if y[test].sum() == 0 else float(roc_auc_score(y[test], p)),
                "test_pr_auc": None if y[test].sum() == 0 else float(average_precision_score(y[test], p)),
                "pred_pos_at_0.5": int((p > 0.5).sum()),
                "max_prob": float(p.max()),
            }
        )
    return checks


def main():
    X, y, rid = load()
    n, n_fault = len(y), int(y.sum())
    bins = []
    for lo in range(1, n + 1, 100):
        m = (rid >= lo) & (rid < lo + 100)
        bins.append(
            {
                "records": f"{lo}-{min(lo + 99, n)}",
                "n": int(m.sum()),
                "faults": int(y[m].sum()),
                "rate": float(y[m].mean()),
            }
        )

    cv = random_cv(X, y)
    temporal = temporal_check(X, y, rid)

    # record_id 本身的洩漏程度：只靠時間索引能多準？
    Xid = rid.reshape(-1, 1)
    p_id = cross_val_predict(
        RandomForestClassifier(n_estimators=300, random_state=0, n_jobs=-1),
        Xid, y, cv=StratifiedKFold(5, shuffle=True, random_state=42),
        method="predict_proba",
    )[:, 1]

    summary = {
        "n_records": n,
        "n_faults": n_fault,
        "fault_rate": float(y.mean()),
        "fault_rate_by_100": bins,
        "random_cv": {
            k: {kk: vv for kk, vv in v.items() if kk != "proba"}
            for k, v in cv.items()
        },
        "record_id_only": {
            "roc_auc": roc_auc_score(y, p_id),
            "pr_auc": average_precision_score(y, p_id),
        },
        "temporal_holdout": temporal,
        "corr_record_id_fault": float(np.corrcoef(rid, y)[0, 1]),
        "feature_drift_sd": {
            c: float((X[200:, i].mean() - X[:200, i].mean()) / X[:200, i].std())
            for i, c in enumerate(FEATURES)
        },
    }

    # ---- 圖 ----
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    ax = axes[0, 0]
    centers = [np.mean([int(b["records"].split("-")[0]), int(b["records"].split("-")[1])]) for b in bins]
    ax.bar(centers, [b["rate"] for b in bins], width=80, color="#c0392b")
    ax.set_xlabel("record_id (time order)")
    ax.set_ylabel("fault rate")
    ax.set_title("Fault rate by record_id bin: all faults are early")
    ax.set_ylim(0, 0.8)

    ax = axes[0, 1]
    for name, res in cv.items():
        fpr, tpr, _ = roc_curve(y, res["proba"])
        ax.plot(fpr, tpr, label=f"{name} AUC={res['roc_auc']:.3f}")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("false positive rate")
    ax.set_ylabel("true positive rate")
    ax.set_title("Random 5-fold CV (leaky: ignores time)")
    ax.legend(loc="lower right")

    ax = axes[1, 0]
    clf = RandomForestClassifier(
        n_estimators=500, min_samples_leaf=3, class_weight="balanced",
        random_state=0, n_jobs=-1,
    ).fit(X[:200], y[:200])
    p_all = clf.predict_proba(X)[:, 1]
    ax.scatter(rid[y == 0], p_all[y == 0], s=6, alpha=0.4, label="normal")
    ax.scatter(rid[y == 1], p_all[y == 1], s=14, color="#c0392b", label="fault")
    ax.axvline(200, color="k", ls="--", lw=0.8)
    ax.set_xlabel("record_id (time order)")
    ax.set_ylabel("predicted fault probability")
    ax.set_title("Trained on records 1-200, scored on all: false alarms later")
    ax.legend()

    ax = axes[1, 1]
    frac_pos, mean_pred = calibration_curve(y, cv["rf"]["proba"], n_bins=8, strategy="quantile")
    ax.plot(mean_pred, frac_pos, "o-", label="RF random CV")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("mean predicted probability")
    ax.set_ylabel("observed fault fraction")
    ax.set_title("Calibration (random CV)")
    ax.legend()

    fig.tight_layout()
    fig.savefig("figs/fault_model_diagnostics.png", dpi=150)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\nsaved figs/fault_model_diagnostics.png")


if __name__ == "__main__":
    main()
