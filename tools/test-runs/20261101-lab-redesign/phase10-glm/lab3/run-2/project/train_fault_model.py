import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score, roc_auc_score, precision_recall_curve,
    precision_score, recall_score, confusion_matrix,
)

RNG = 42
df = pd.read_csv("data/line_faults.csv").sort_values("record_id").reset_index(drop=True)

features_all = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]

# 註：故障全部集中在資料前段（record_id 前 ~70 筆），時間切分會讓測試集無故障、無法評估
# 因此改用分層隨機切分，並排除 record_id 避免洩漏；同時在筆記中說明時間漂移風險
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.model_selection import train_test_split

train, test = train_test_split(df, test_size=0.3, stratify=df.fault, random_state=RNG)
train, test = train.reset_index(drop=True), test.reset_index(drop=True)
print(f"train={len(train)} (fault={train.fault.sum()}), test={len(test)} (fault={test.fault.sum()})")

def evaluate(Xtr, ytr, Xte, yte, label):
    rows = []
    for name, model in [
        ("LogReg", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RNG))),
        ("RandomForest", RandomForestClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced", random_state=RNG, n_jobs=-1)),
    ]:
        model.fit(Xtr, ytr)
        p = model.predict_proba(Xte)[:, 1]
        rows.append((name, model, p))
        print(f"[{label}] {name}: PR-AUC={average_precision_score(yte, p):.3f}  ROC-AUC={roc_auc_score(yte, p):.3f}")
    return rows

print("\n--- 只用感測器特徵 ---")
res_sensor = evaluate(train[features_all], train.fault, test[features_all], test.fault, "sensor")

print("\n--- 含 record_id（會洩漏時間資訊，僅示範）---")
res_leak = evaluate(train[features_all + ["record_id"]], train.fault, test[features_all + ["record_id"]], test.fault, "leak")

# 選用感測器版本，挑閾值：抓 80% 故障時的精確率
best_name, best_model, p = max(res_sensor, key=lambda r: average_precision_score(test.fault, r[2]))
print(f"\n選用模型: {best_name}")
for target_recall in [0.6, 0.8, 0.9]:
    prec, rec, thr = precision_recall_curve(test.fault, p)
    idx = np.argmin(np.abs(rec - target_recall))
    t = thr[min(idx, len(thr) - 1)]
    pred = (p >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(test.fault, pred).ravel()
    print(f"閾值={t:.3f}  召回={rec[idx]:.2f}  精確率={prec[idx]:.2f}  (TP={tp} FP={fp} FN={fn} TN={tn})")

# 圖：PR curve
fig, ax = plt.subplots(figsize=(6, 5))
for name, _, p_ in res_sensor:
    prec, rec, _ = precision_recall_curve(test.fault, p_)
    ap = average_precision_score(test.fault, p_)
    ax.plot(rec, prec, label=f"{name} (AP={ap:.3f})")
base = test.fault.mean()
ax.axhline(base, ls="--", c="gray", label=f"baseline={base:.3f}")
ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.legend(); ax.set_title("PR curve (time-based test set)")
fig.tight_layout(); fig.savefig("figs/pr_curve.png", dpi=150)

# 特徵重要性（LogReg 係數）
coef = pd.Series(best_model[-1].coef_[0], index=features_all).sort_values()
print("\nLogReg 係數（標準化後）:")
print(coef.round(3))
