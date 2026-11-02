import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

X = pd.read_csv("data/line_channels.csv").values
y = pd.read_csv("data/line_channels_fault.csv")["fault"].values

def stats(Xt, pca, Xsc_ref_mean, Xsc_ref_scale):
    # Xt 已標準化
    scores = Xt @ pca.components_.T  # (n, k)
    t2 = np.sum(scores**2 / pca.explained_variance_, axis=1)
    recon = scores @ pca.components_ + pca.mean_
    spe = np.sum((Xt - recon) ** 2, axis=1)
    return t2, spe

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
res = {k: {"T2": [], "SPE": [], "T2+SPE": []} for k in (3, 4, 5)}

for tr, te in skf.split(X, y):
    for k in (3, 4, 5):
        sc = StandardScaler().fit(X[tr])
        Xt, Xe = sc.transform(X[tr]), sc.transform(X[te])
        pca = PCA(n_components=k).fit(Xt)
        t2_e, spe_e = stats(Xe, pca, None, None)
        res[k]["T2"].append(roc_auc_score(y[te], t2_e))
        res[k]["SPE"].append(roc_auc_score(y[te], spe_e))
        comb = t2_e / np.percentile(t2_e, 95) + spe_e / np.percentile(spe_e, 95)
        res[k]["T2+SPE"].append(roc_auc_score(y[te], comb))

for k in (3, 4, 5):
    for s in ("T2", "SPE", "T2+SPE"):
        a = np.array(res[k][s])
        print(f"k={k} {s:>7}: AUC = {a.mean():.3f} ± {a.std():.3f}  folds={np.round(a,3)}")
