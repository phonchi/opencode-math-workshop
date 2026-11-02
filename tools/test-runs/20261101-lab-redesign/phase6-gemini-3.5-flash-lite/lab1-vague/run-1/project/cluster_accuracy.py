import numpy as np
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import confusion_matrix

digits = load_digits()
X = digits.data
y = digits.target

def clustering_accuracy(y_true, y_pred):
    """
    Calculate clustering accuracy using the Hungarian algorithm 
    to find the optimal one-to-one mapping between cluster labels and true labels.
    """
    cm = confusion_matrix(y_true, y_pred)
    # Find optimal mapping using linear sum assignment on negative confusion matrix
    row_ind, col_ind = linear_sum_assignment(-cm)
    return cm[row_ind, col_ind].sum() / y_true.size

print("Clustering Accuracy for different k values:")
for k in range(2, 16):
    kmeans = KMeans(n_init=10, n_clusters=k, random_state=42)
    y_pred = kmeans.fit_predict(X)
    
    # If k < 10 or k >= 10, confusion matrix works if we pad or handle shapes, 
    # but linear_sum_assignment requires a cost/profit matrix. 
    # If k != 10, cm might not be square. linear_sum_assignment handles rectangular matrices (min(n_rows, n_cols)).
    acc = clustering_accuracy(y, y_pred)
    print(f"k = {k:2d}: Accuracy = {acc:.4f} ({acc * 100:.2f}%)")
