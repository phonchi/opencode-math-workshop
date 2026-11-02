import numpy as np,warnings
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
warnings.filterwarnings('ignore')
X=load_digits().data
s={k:silhouette_score(X,KMeans(k,n_init=10,random_state=0).fit_predict(X)) for k in range(2,26)}
for hi in (12,15,20,25):
    b=max((k for k in s if k<=hi),key=s.get); print(f'range 2..{hi}: best k={b} sil={s[b]:.4f}')
print({k:round(s[k],4) for k in (9,10,12,15,20,25)})
