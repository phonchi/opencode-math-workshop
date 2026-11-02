"""Lab 2 參考程式：手刻 PCA，與 sklearn 對照；看尺度如何決定「幾個主成分就夠」。

line_channels.csv 是講師設計的資料。故障標籤只在揭曉時使用。
"""
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).resolve().parents[1] / "assets" / "data"
X = np.genfromtxt(DATA / "line_channels.csv", delimiter=",", skip_header=1)
fault = np.genfromtxt(DATA / "reveal" / "line_channels_fault.csv", delimiter=",", skip_header=1)
K = 3


def manual_pca(A):
    mu = A.mean(0)
    Ac = A - mu
    vals, vecs = np.linalg.eigh(Ac.T @ Ac / (len(A) - 1))
    order = np.argsort(vals)[::-1]
    return vals[order], vecs[:, order], mu


for name, A in [("原始尺度", X), ("標準化", StandardScaler().fit_transform(X))]:
    vals, vecs, mu = manual_pca(A)
    ratio = vals / vals.sum()
    k90 = int(np.searchsorted(np.cumsum(ratio), 0.9)) + 1
    sk = PCA(K, svd_solver="full").fit(A)
    z = (A - mu) @ vecs
    corr = [abs(np.corrcoef(z[:, i], fault)[0, 1]) for i in range(A.shape[1])]
    print(f"== {name}")
    print("前 5 個解釋變異比例:", np.round(ratio[:5], 6).tolist())
    print("累積達 90% 需要的主成分數:", k90)
    print("與 sklearn 的比例最大差:", f"{np.abs(ratio[:K] - sk.explained_variance_ratio_).max():.2e}")
    print("|cos| 最大偏離 1:", f"{np.abs(np.abs((vecs[:, :K].T * sk.components_).sum(1)) - 1).max():.2e}")
    print("PC1 權重最大的欄位索引:", int(np.argmax(np.abs(vecs[:, 0]))), "權重", round(float(np.abs(vecs[:, 0]).max()), 4))
    print("達 90% 的主成分與故障的最大 |相關|:", round(float(np.max(corr[:k90])), 3), "（第", int(np.argmax(corr[:k90])) + 1, "個）")


def auc(F, *steps):
    # 前處理、PCA 與分類器都只在各訓練折擬合，測試折不參與。
    model = make_pipeline(*steps, LogisticRegression(max_iter=2000))
    score = cross_val_predict(model, F, fault, cv=5, method="decision_function")
    return roc_auc_score(fault, score)


Z = StandardScaler().fit_transform(X)
vals, vecs, mu = manual_pca(Z)
ratio = vals / vals.sum()
scores = (Z - mu) @ vecs
print("保留幾個主成分｜累積變異｜用它們辨識故障的 AUC（揭曉後才算）")
for k in range(1, 6):
    print(f"{k}  {ratio[:k].sum():.3f}  {auc(X, StandardScaler(), PCA(k, svd_solver='full')):.3f}")
print("拿掉 ch09、ch10、ch11 後用其餘通道的 AUC:", round(auc(np.delete(X, [8, 9, 10], 1), StandardScaler()), 3))
print("原始尺度 1 個主成分的 AUC:", round(auc(X, PCA(1, svd_solver="full")), 3))
print("PC4 權重最大的兩欄索引:", np.argsort(-np.abs(vecs[:, 3]))[:2].tolist(), "PC5 權重最大的欄索引:", int(np.argmax(np.abs(vecs[:, 4]))))
