import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, TimeSeriesSplit, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA = Path("data")
FIGS = Path("figs")
FIGS.mkdir(exist_ok=True)

FEATURES = [
    "temp_c",
    "vibration_mm_s",
    "pressure_kpa",
    "flow_lpm",
    "current_a",
    "speed_rpm",
]

df = pd.read_csv(DATA / "line_faults.csv").sort_values("record_id").reset_index(drop=True)
X = df[FEATURES].to_numpy()
y = df["fault"].to_numpy()
episode_end = int(df.loc[df.fault.eq(1), "record_id"].max())
early = df.record_id.le(episode_end).to_numpy()

models = {
    "logistic": make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=0),
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=500,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=0,
        n_jobs=-1,
    ),
    "gradient_boosting": GradientBoostingClassifier(random_state=0),
}

results = {
    "n_records": int(len(df)),
    "n_faults": int(y.sum()),
    "fault_rate": float(y.mean()),
    "episode_end_record_id": episode_end,
    "faults_in_episode": int(y[early].sum()),
    "records_in_episode": int(early.sum()),
    "faults_after_episode": int(y[~early].sum()),
    "records_after_episode": int((~early).sum()),
    "record_id_auc_for_fault": float(roc_auc_score(y, df.record_id)),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results["random_cv"] = {}
for name, model in models.items():
    proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    results["random_cv"][name] = {
        "auc": float(roc_auc_score(y, proba)),
        "average_precision": float(average_precision_score(y, proba)),
    }

results["episode_then_future"] = {}
for name, model in models.items():
    model.fit(X[early], y[early])
    p_train = model.predict_proba(X[early])[:, 1]
    p_future = model.predict_proba(X[~early])[:, 1]
    order = np.argsort(-p_train)
    recall = np.cumsum(y[early][order]) / y[early].sum()
    threshold_90 = float(p_train[order][np.searchsorted(recall, 0.90)])
    results["episode_then_future"][name] = {
        "train_auc_insample": float(roc_auc_score(y[early], p_train)),
        "threshold_for_90pct_recall": threshold_90,
        "future_flagged_at_90pct_threshold": int((p_future >= threshold_90).sum()),
        "future_flagged_rate_at_90pct_threshold": float((p_future >= threshold_90).mean()),
        "future_flagged_at_0_5": int((p_future >= 0.5).sum()),
        "future_flagged_rate_at_0_5": float((p_future >= 0.5).mean()),
        "future_mean_probability": float(p_future.mean()),
    }

results["time_series_cv"] = {}
ts = TimeSeriesSplit(n_splits=5)
for name, model in models.items():
    folds = []
    for train_idx, test_idx in ts.split(X):
        pos = int(y[test_idx].sum())
        if pos == 0 or len(np.unique(y[test_idx])) < 2:
            folds.append({"test_positives": pos, "auc": None})
            continue
        model.fit(X[train_idx], y[train_idx])
        proba = model.predict_proba(X[test_idx])[:, 1]
        folds.append({"test_positives": pos, "auc": float(roc_auc_score(y[test_idx], proba))})
    results["time_series_cv"][name] = folds

modes = pd.read_csv(DATA / "line_modes.csv")
lo = df[FEATURES].quantile(0.01)
hi = df[FEATURES].quantile(0.99)
outside_any = ((modes[FEATURES] < lo) | (modes[FEATURES] > hi)).any(axis=1)
results["modes_file"] = {
    "n_records": int(len(modes)),
    "share_outside_faults_1_99pct_on_any_feature": float(outside_any.mean()),
    "constants": {
        col: sorted(modes[col].dropna().unique().tolist())
        for col in ["firmware_ver", "sample_period_s"]
    },
}

channels = pd.read_csv(DATA / "line_channels.csv")
results["channels_file"] = {
    "n_records": int(len(channels)),
    "n_channels": int(channels.shape[1]),
    "has_fault_label": bool("fault" in channels.columns),
    "has_join_key": bool(any(col in channels.columns for col in ["record_id", "id"])),
}

fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
bins = np.arange(0, df.record_id.max() + 26, 25)
grouped = (
    df.assign(bin=pd.cut(df.record_id, bins))
    .groupby("bin", observed=True)
    .agg(records=("fault", "size"), faults=("fault", "sum"))
)
centers = [interval.mid for interval in grouped.index]
axes[0].bar(centers, grouped["faults"], width=22, color="#c0392b", alpha=0.85)
axes[0].set_ylabel("Faults per 25 records")
axes[0].set_title("Fault labels are concentrated at the start of the log")
axes[0].axvline(episode_end, color="black", linestyle="--", linewidth=1)
axes[0].text(episode_end + 10, axes[0].get_ylim()[1] * 0.85, f"last fault = {episode_end}")

axes[1].scatter(
    df.loc[~df.fault.astype(bool), "record_id"],
    df.loc[~df.fault.astype(bool), "temp_c"],
    s=10,
    alpha=0.35,
    color="#2e86de",
    label="normal",
)
axes[1].scatter(
    df.loc[df.fault.astype(bool), "record_id"],
    df.loc[df.fault.astype(bool), "temp_c"],
    s=18,
    alpha=0.8,
    color="#c0392b",
    label="fault",
)
axes[1].axvline(episode_end, color="black", linestyle="--", linewidth=1)
axes[1].set_xlabel("record_id (time order)")
axes[1].set_ylabel("temp_c")
axes[1].legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGS / "fault_timeline.png", dpi=150)
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for name, model in models.items():
    model.fit(X[early], y[early])
    p_future = model.predict_proba(X[~early])[:, 1]
    axes[0].hist(p_future, bins=30, alpha=0.5, label=name)
axes[0].axvline(0.5, color="black", linestyle="--", linewidth=1)
axes[0].set_xlabel("Predicted fault probability on later records (all truly normal)")
axes[0].set_ylabel("Count")
axes[0].set_title("Models trained on the fault episode")
axes[0].legend(frameon=False, fontsize=8)

names = list(models)
flag_rates = [
    results["episode_then_future"][name]["future_flagged_rate_at_90pct_threshold"] * 100
    for name in names
]
axes[1].barh(names, flag_rates, color="#e67e22")
axes[1].set_xlabel("False alarms on 789 later normal records (%)")
axes[1].set_title("At threshold chosen for 90% recall in the episode")
for i, value in enumerate(flag_rates):
    axes[1].text(value + 0.2, i, f"{value:.1f}%", va="center")
fig.tight_layout()
fig.savefig(FIGS / "false_alarms.png", dpi=150)
plt.close(fig)

combined = pd.concat([df[FEATURES], modes[FEATURES]], ignore_index=True)
scaled = StandardScaler().fit_transform(combined)
pca = PCA(n_components=2).fit(scaled)
points = pca.transform(scaled)
fig, ax = plt.subplots(figsize=(7.5, 5.5))
ax.scatter(points[: len(df)][~early, 0], points[: len(df)][~early, 1],
           s=10, alpha=0.3, color="#2e86de", label="faults: later normal")
ax.scatter(points[: len(df)][early, 0], points[: len(df)][early, 1],
           s=14, alpha=0.5, color="#c0392b", label="faults: fault episode")
ax.scatter(points[len(df):, 0], points[len(df):, 1],
           s=10, alpha=0.3, color="#7f8c8d", label="line_modes.csv")
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_title("line_modes.csv does not overlap the labeled data")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(FIGS / "distribution_shift.png", dpi=150)
plt.close(fig)

(Path("notes") / "fault_model_metrics.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
)

print(json.dumps(results, indent=2, ensure_ascii=False))
