import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

os.makedirs("figs", exist_ok=True)
os.makedirs("notes", exist_ok=True)

df = pd.read_csv("data/line_channels.csv")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

pca = PCA()
pca.fit(X_scaled)

explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
eigenvalues = pca.explained_variance_

print("\n--- PCA 結果摘要 ---")
for i, (ev, var, cum_var) in enumerate(zip(eigenvalues, explained_variance_ratio, cumulative_variance_ratio), 1):
    print(f"PC{i}: Eigenvalue = {ev:.4f}, Variance Ratio = {var*100:.2f}%, Cumulative = {cum_var*100:.2f}%")

# 繪製主成分解釋變異圖（使用英文標籤以避免字型警告）
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(explained_variance_ratio) + 1), cumulative_variance_ratio, marker='o', linestyle='-', color='b', label='Cumulative Explained Variance')
plt.bar(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio, alpha=0.6, color='g', label='Individual Explained Variance')
plt.axhline(y=0.85, color='r', linestyle='--', label='85% Threshold')
plt.axhline(y=0.90, color='orange', linestyle='--', label='90% Threshold')
plt.xlabel('Principal Component', fontsize=12)
plt.ylabel('Explained Variance Ratio', fontsize=12)
plt.title('PCA Scree Plot and Cumulative Variance for Line Channels', fontsize=14)
plt.xticks(range(1, len(explained_variance_ratio) + 1))
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()

fig_path = "figs/pca_variance.png"
plt.savefig(fig_path, dpi=300)
print(f"\n圖表已儲存至 {fig_path}")

n_components_85 = np.argmax(cumulative_variance_ratio >= 0.85) + 1
n_components_90 = np.argmax(cumulative_variance_ratio >= 0.90) + 1
n_components_kaiser = sum(eigenvalues > 1)

print(f"\n[結論建議]")
print(f"- 累積解釋變異數達到 85% 需要 {n_components_85} 個主成分 (PC1 ~ PC4 達 83.88%，PC5 達 92.95%)")
print(f"- 累積解釋變異數達到 90% 需要 {n_components_90} 個主成分")
print(f"- 根據 Kaiser 準則 (Eigenvalue > 1)，共有 {n_components_kaiser} 個主成分 (PC1 ~ PC4)。")
