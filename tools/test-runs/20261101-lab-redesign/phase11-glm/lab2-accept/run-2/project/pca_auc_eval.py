import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

X = pd.read_csv("data/line_channels.csv")
y = pd.read_csv("data/line_channels_fault.csv")["fault"].values

def make_pipe(k):
    return Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=k)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = {}
for k in (3, 4, 5):
    aucs = []
    for tr, te in cv.split(X, y):
        pipe = make_pipe(k)
        pipe.fit(X.iloc[tr], y[tr])          # 前處理+PCA 只在訓練折擬合
        p = pipe.predict_proba(X.iloc[te])[:, 1]
        aucs.append(roc_auc_score(y[te], p))
    aucs = np.array(aucs)
    results[k] = aucs
    print(f"k={k}: fold AUCs={np.round(aucs,4)}  mean={aucs.mean():.4f} ± {aucs.std():.4f}")

a3, a4, a5 = results[3].mean(), results[4].mean(), results[5].mean()
print(f"\n4 vs 5 差距: {a5 - a4:+.4f} (5 較高表示 4 個可能不夠)")
print(f"3 vs 4 差距: {a4 - a3:+.4f}")
