import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

# 讀取資料
df = pd.read_csv('data/line_channels.csv')
print(f"資料形狀: {df.shape}")
print(df.head())

# 標準化特徵
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# 執行 PCA
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

explained_variance = pca.explained_variance_
explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance_ratio = np.cumsum(explained_variance_ratio)

print("\n各主成分解釋變異數比例：")
for i, (var, cum_var) in enumerate(zip(explained_variance_ratio, cumulative_variance_ratio)):
    print(f"PC{i+1}: 單獨 = {var*100:.2f}%, 累積 = {cum_var*100:.2f}% (特徵值: {explained_variance[i]:.4f})")

# 繪製主成分解釋變異數圖
os.makedirs('figs', exist_ok=True)
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(explained_variance_ratio) + 1), cumulative_variance_ratio, marker='o', linestyle='-', color='b', label='累積解釋變異比例')
plt.bar(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio, alpha=0.5, color='g', label='個別解釋變異比例')
plt.axhline(y=0.90, color='r', linestyle='--', label='90% 門檻')
plt.axhline(y=0.95, color='orange', linestyle='--', label='95% 門檻')
plt.xlabel('主成分個數 (Principal Components)')
plt.ylabel('解釋變異數比例 (Explained Variance Ratio)')
plt.title('產線感測資料 PCA 降維分析 - 解釋變異比例圖')
plt.xticks(range(1, len(explained_variance_ratio) + 1))
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('figs/pca_variance.png', dpi=300)
plt.close()
print("\n圖檔已儲存至 figs/pca_variance.png")
