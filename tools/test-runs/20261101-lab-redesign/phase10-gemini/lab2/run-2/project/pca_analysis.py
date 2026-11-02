import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 載入資料
file_path = 'data/line_channels.csv'
with open(file_path, mode='r') as f:
    reader = csv.reader(f)
    header = next(reader)
    data = [list(map(float, row)) for row in reader]

X = np.array(data)
feature_names = header

# 標準化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance_ratio)

print("各主成分解釋變異數比例：")
for i, ratio in enumerate(explained_variance_ratio):
    print(f"PC{i+1}: {ratio*100:.2f}% (累積: {cumulative_variance[i]*100:.2f}%)")

# 繪製解釋變異數圖
plt.figure(figsize=(10, 6), dpi=300)
plt.bar(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio * 100, alpha=0.6, color='b', label='Individual Explained Variance (%)')
plt.step(range(1, len(cumulative_variance) + 1), cumulative_variance * 100, where='mid', color='r', marker='o', label='Cumulative Explained Variance (%)')
plt.axhline(y=90, color='g', linestyle='--', label='90% Threshold')
plt.axhline(y=95, color='orange', linestyle='--', label='95% Threshold')

plt.xlabel('Principal Components', fontsize=12)
plt.ylabel('Explained Variance Ratio (%)', fontsize=12)
plt.title('PCA Explained Variance Analysis for Production Line Sensors', fontsize=14)
plt.xticks(range(1, len(explained_variance_ratio) + 1))
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()

plt.savefig('figs/pca_explained_variance.png')
plt.close()

# 繪製特徵載荷量熱力圖 (Loadings)
loadings = pca.components_[:5, :].T # 前5個主成分的載荷量
plt.figure(figsize=(10, 8), dpi=300)
plt.imshow(loadings, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
plt.colorbar(label='Loading Value')
plt.yticks(range(len(feature_names)), feature_names)
plt.xticks(range(5), [f'PC{i+1}' for i in range(5)])
plt.title('Feature Loadings for Top 5 Principal Components', fontsize=14)
plt.tight_layout()
plt.savefig('figs/pca_loadings.png')
plt.close()
print("圖表已成功更新至 figs/ 目錄。")
