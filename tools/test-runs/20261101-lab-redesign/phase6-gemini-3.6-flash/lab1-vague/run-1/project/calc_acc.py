import numpy as np
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score, homogeneity_completeness_v_measure
from scipy.optimize import linear_sum_assignment

digits = load_digits()
X, y = digits.data, digits.target

# Fit KMeans with k=10
kmeans = KMeans(n_clusters=10, random_state=42, n_init=20)
y_pred = kmeans.fit_predict(X)

# Hungarian Algorithm to compute Clustering Accuracy (ACC)
def cluster_accuracy(y_true, y_pred):
    D = max(y_pred.max(), y_true.max()) + 1
    cost_matrix = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        cost_matrix[y_pred[i], y_true[i]] += 1
    row_ind, col_ind = linear_sum_assignment(cost_matrix.max() - cost_matrix)
    acc = cost_matrix[row_ind, col_ind].sum() / y_pred.size
    return acc, dict(zip(row_ind, col_ind))

acc, mapping = cluster_accuracy(y, y_pred)
ari = adjusted_rand_score(y, y_pred)
ami = adjusted_mutual_info_score(y, y_pred)
homo, comp, v_meas = homogeneity_completeness_v_measure(y, y_pred)

print(f"Clustering Accuracy (ACC): {acc:.4f} ({acc*100:.2f}%)")
print(f"Adjusted Rand Index (ARI): {ari:.4f}")
print(f"Adjusted Mutual Information (AMI): {ami:.4f}")
print(f"Homogeneity: {homo:.4f}")
print(f"Completeness: {comp:.4f}")
print(f"V-measure: {v_meas:.4f}")
