"""訓練與評估產線故障分類器（data/line_faults.csv）。

重點：檔案中的列是打亂的，真正的時間順序要看 record_id。評估除了隨機切分，
也做了「依時間分組」與「時間外推」兩種切分，用來檢查模型能不能上線。
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "line_faults.csv"
FIGS = ROOT / "figs"
MODELS = ROOT / "models"

FEATURES = [
    "temp_c",
    "vibration_mm_s",
    "pressure_kpa",
    "flow_lpm",
    "current_a",
    "speed_rpm",
]


def load_data():
    raw = np.genfromtxt(DATA, delimiter=",", names=True)
    X = np.column_stack([raw[f] for f in FEATURES])
    y = raw["fault"].astype(int)
    record_id = raw["record_id"].astype(int)
    order = np.argsort(record_id)  # 還原時間順序
    return X[order], y[order], record_id[order]


def make_model(kind="logreg"):
    if kind == "logreg":
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced"),
        )
    return RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=0,
        n_jobs=-1,
    )


def metrics(y_true, prob, threshold=0.5):
    out = {
        "roc_auc": float(roc_auc_score(y_true, prob)),
        "pr_auc": float(average_precision_score(y_true, prob)),
    }
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    out.update(
        {"threshold": float(threshold), "tp": int(tp), "fp": int(fp),
         "fn": int(fn), "tn": int(tn)}
    )
    return out


def threshold_for_recall(y_true, prob, target=0.90):
    precision, recall, thresholds = precision_recall_curve(y_true, prob)
    ok = np.where(recall[:-1] >= target)[0]
    return float(thresholds[ok[-1]]) if len(ok) else 0.5


def main():
    FIGS.mkdir(exist_ok=True)
    MODELS.mkdir(exist_ok=True)
    X, y, record_id = load_data()
    results = {"n": int(len(y)), "n_fault": int(y.sum()),
               "fault_record_id_min": int(record_id[y == 1].min()),
               "fault_record_id_max": int(record_id[y == 1].max())}

    # 1) 隨機分層交叉驗證：數字最漂亮，但會偷看到同一段故障事件
    random_cv = {}
    for kind in ("logreg", "rf"):
        prob = cross_val_predict(
            make_model(kind), X, y,
            cv=StratifiedKFold(5, shuffle=True, random_state=0),
            method="predict_proba",
        )[:, 1]
        random_cv[kind] = metrics(y, prob)
        precision, recall, _ = precision_recall_curve(y, prob)
        f1 = 2 * precision[:-1] * recall[:-1] / (
            precision[:-1] + recall[:-1] + 1e-12
        )
        random_cv[kind]["best_f1"] = float(np.max(f1))
    results["random_cv"] = random_cv

    # 2) 依連續時間區塊分組：避免同一段時間的資料同時出現在訓練與測試
    blocks = (record_id - 1) // 100
    group_cv = {}
    for kind in ("logreg", "rf"):
        prob = cross_val_predict(
            make_model(kind), X, y,
            cv=GroupKFold(n_splits=9), groups=blocks, method="predict_proba",
        )[:, 1]
        group_cv[kind] = metrics(y, prob)
    results["group_cv_100_record_blocks"] = group_cv
    results["faults_per_block"] = {
        str(int(b)): int(y[blocks == b].sum()) for b in np.unique(blocks)
    }

    # 3) 時間外推：用前 600 筆訓練，預測後 300 筆（完全沒有故障）
    model = make_model("logreg").fit(X[record_id <= 600], y[record_id <= 600])
    prob_future = model.predict_proba(X[record_id > 600])[:, 1]
    cv_prob = cross_val_predict(
        make_model("logreg"), X[record_id <= 600], y[record_id <= 600],
        cv=StratifiedKFold(5, shuffle=True, random_state=0),
        method="predict_proba",
    )[:, 1]
    thr90 = threshold_for_recall(y[record_id <= 600], cv_prob, 0.90)
    results["time_holdout"] = {
        "train_faults": int(y[record_id <= 600].sum()),
        "test_faults": int(y[record_id > 600].sum()),
        "false_alarm_rate_at_0.5": float((prob_future >= 0.5).mean()),
        "threshold_for_90pct_recall": thr90,
        "false_alarm_rate_at_threshold": float((prob_future >= thr90).mean()),
    }

    # 4) 最終模型（全部資料）與係數
    final = make_model("logreg").fit(X, y)
    coef = final.named_steps["logisticregression"].coef_[0]
    results["standardized_coefficients"] = dict(
        zip(FEATURES, [round(float(c), 3) for c in coef])
    )
    dump(final, MODELS / "fault_model.joblib")

    # 圖一：時間軸上的故障事件與特徵
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    axes[0].scatter(record_id[y == 0], y[y == 0], s=10, c="#4C78A8",
                    label="normal")
    axes[0].scatter(record_id[y == 1], y[y == 1], s=14, c="#E45756",
                    label="fault")
    axes[0].set_yticks([0, 1])
    axes[0].set_ylabel("fault")
    axes[0].legend(loc="upper right")
    axes[0].set_title("Fault labels are concentrated in record_id 1-111")
    axes[1].scatter(record_id, X[:, 0], s=6, c=np.where(y == 1, "#E45756", "#4C78A8"))
    axes[1].set_ylabel("temp_c")
    axes[2].scatter(record_id, X[:, 1], s=6, c=np.where(y == 1, "#E45756", "#4C78A8"))
    axes[2].set_ylabel("vibration_mm_s")
    axes[2].set_xlabel("record_id (time order)")
    for ax in axes:
        ax.axvline(111.5, color="black", linestyle="--", linewidth=1)
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGS / "fault_timeline.png", dpi=160)
    plt.close(fig)

    # 圖二：隨機 CV vs 時間分組 CV 的 ROC / PR
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for kind, color, label in [("logreg", "#E45756", "LogReg"),
                               ("rf", "#4C78A8", "RandomForest")]:
        prob = cross_val_predict(
            make_model(kind), X, y,
            cv=StratifiedKFold(5, shuffle=True, random_state=0),
            method="predict_proba",
        )[:, 1]
        fpr, tpr, _ = roc_curve(y, prob)
        axes[0].plot(fpr, tpr, color=color,
                     label=f"{label} random CV (AUC={roc_auc_score(y, prob):.3f})")
    prob = cross_val_predict(
        make_model("logreg"), X, y,
        cv=GroupKFold(n_splits=9), groups=blocks, method="predict_proba",
    )[:, 1]
    fpr, tpr, _ = roc_curve(y, prob)
    axes[0].plot(fpr, tpr, color="#54A24B", linestyle="--",
                 label=f"LogReg time-block CV (AUC={roc_auc_score(y, prob):.3f})")
    axes[0].plot([0, 1], [0, 1], "k:", linewidth=0.8)
    axes[0].set_xlabel("False positive rate")
    axes[0].set_ylabel("True positive rate")
    axes[0].set_title("ROC: random split vs time-block split")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.25)

    prob = cross_val_predict(
        make_model("logreg"), X, y,
        cv=StratifiedKFold(5, shuffle=True, random_state=0),
        method="predict_proba",
    )[:, 1]
    prec, rec, _ = precision_recall_curve(y, prob)
    axes[1].plot(rec, prec, color="#E45756",
                 label=f"random CV (PR-AUC={average_precision_score(y, prob):.3f})")
    prob = cross_val_predict(
        make_model("logreg"), X, y,
        cv=GroupKFold(n_splits=9), groups=blocks, method="predict_proba",
    )[:, 1]
    prec, rec, _ = precision_recall_curve(y, prob)
    axes[1].plot(rec, prec, color="#54A24B", linestyle="--",
                 label=f"time-block CV (PR-AUC={average_precision_score(y, prob):.3f})")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].set_title("Precision-Recall")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGS / "evaluation_random_vs_temporal.png", dpi=160)
    plt.close(fig)

    (MODELS / "metrics.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
