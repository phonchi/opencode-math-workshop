import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

X = pd.read_csv("data/line_channels.csv").values
y = pd.read_csv("data/line_channels_fault.csv")["fault"].values

print(f"n={len(y)}, fault rate={y.mean():.3f}")

kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

def t2_and_q(pca, Xs):
    scores = pca.transform(Xs)
    t2 = np.sum(scores**2 / pca.explained_variance_, axis=1)
    rec = pca.inverse_transform(scores)
    q = np.sum((Xs - rec) ** 2, axis=1)
    return t2, q

for k in (3, 4, 5):
    t2_aucs, q_aucs = [], []
    for tr, te in kf.split(X, y):
        sc = StandardScaler().fit(X[tr])
        pca = PCA(n_components=k, random_state=0).fit(sc.transform(X[tr]))
        t2_tr, q_tr = t2_and_q(pca, sc.transform(X[tr]))
        t2_te, q_te = t2_and_q(pca, sc.transform(X[te]))
        t2_aucs.append(roc_auc_score(y[te], t2_te))
        q_aucs.append(roc_auc_score(y[te], q_te))
    print(f"k={k}: T2 AUC={np.mean(t2_aucs):.4f}±{np.std(t2_aucs):.4f}  "
          f"Q AUC={np.mean(q_aucs):.4f}±{np.std(q_aucs):.4f}  "
          f"T2 folds={[f'{a:.3f}' for a in t2_aucs]}")

p_full = PCA(random_state=0).fit(StandardScaler().fit_transform(X))
print("\n解釋變異比(全資料，僅供參考):", np.round(np.cumsum(p_full.explained_variance_ratio_), 4))
