import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

X = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/data/line_channels.csv')
y = pd.read_csv('/home/phonchi/.cache/oc-lab-redesign/runs/phase11-gemini/lab2-accept-2/project/data/line_channels_fault.csv')['fault'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA()
pca.fit(X_scaled)

print("Explained variance ratio:", pca.explained_variance_ratio_)
print("Cumulative explained variance ratio:", np.cumsum(pca.explained_variance_ratio_))
