import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

class HandcraftedPCAWithBug:
    def __init__(self, n_components=10, bug="none"):
        self.n_components = n_components
        self.bug = bug
        self.mean = None
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        
    def fit(self, X):
        n_samples, n_features = X.shape
        
        # Bug: no_center (不中心化)
        if self.bug == "no_center":
            self.mean = np.zeros(n_features)
            X_centered = X
        else:
            self.mean = np.mean(X, axis=0)
            X_centered = X - self.mean
            
        # SVD
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        
        # Bug: denom_n (變異數分母用 n，不是 n-1)
        if self.bug == "denom_n":
            eigenvalues = (S ** 2) / n_samples
        else:
            eigenvalues = (S ** 2) / (n_samples - 1)
            
        # Bug: ratio_topk (比例分母只用前 10 個特徵值的和)
        if self.bug == "ratio_topk":
            total_variance = np.sum(eigenvalues[:self.n_components])
        else:
            total_variance = np.sum(eigenvalues)
            
        self.explained_variance_ = eigenvalues[:self.n_components]
        self.explained_variance_ratio_ = self.explained_variance_ / total_variance
        
        # Bug: rows (主成分取錯方向：取矩陣的前 10 列，不是前 10 個特徵向量)
        if self.bug == "rows":
            self.components_ = X[:self.n_components, :]
        else:
            self.components_ = Vt[:self.n_components, :]
            
        return self
        
    def transform(self, X):
        X_centered = X - self.mean
        return np.dot(X_centered, self.components_.T)
        
    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

def main():
    digits = load_digits()
    X = digits.data
    
    bugs = ["none", "ratio_topk", "denom_n", "no_center", "rows"]
    check_names = [
        "Explained Variance Ratio Diff (threshold < 1e-7)",
        "Component Weights Diff (threshold < 1e-7)",
        "Projected Data Diff (threshold < 1e-5)"
    ]
    
    thresholds = [1e-7, 1e-7, 1e-5]
    
    results = {}
    
    for bug in bugs:
        # Sklearn reference
        sk_pca = SklearnPCA(n_components=10)
        X_projected_sk = sk_pca.fit_transform(X)
        
        my_pca = HandcraftedPCAWithBug(n_components=10, bug=bug)
        try:
            X_projected_my = my_pca.fit_transform(X)
            
            # 1. Ratio check
            ratio_diff = np.max(np.abs(my_pca.explained_variance_ratio_ - sk_pca.explained_variance_ratio_))
            
            # 2. Components check (with sign alignment if shapes match and no severe corruption)
            components_my = my_pca.components_.copy()
            projected_my = X_projected_my.copy()
            
            if components_my.shape == sk_pca.components_.shape:
                for i in range(10):
                    # avoid zero vector dot product error
                    norm_prod = np.linalg.norm(components_my[i]) * np.linalg.norm(sk_pca.components_[i])
                    if norm_prod > 1e-12:
                        if np.dot(components_my[i], sk_pca.components_[i]) < 0:
                            components_my[i] *= -1
                            projected_my[:, i] *= -1
                comp_diff = np.max(np.abs(components_my - sk_pca.components_))
                proj_diff = np.max(np.abs(projected_my - X_projected_sk))
            else:
                comp_diff = float('inf')
                proj_diff = float('inf')
                
        except Exception as e:
            ratio_diff = float('inf')
            comp_diff = float('inf')
            proj_diff = float('inf')
            
        results[bug] = [ratio_diff, comp_diff, proj_diff]

    # Print Markdown Table
    print("\n# 檢查 × 錯誤表 (Check × Bug Table)\n")
    header = "| 檢查項目 / Bug | " + " | ".join(bugs) + " |"
    separator = "|---|" + "---|".join(["" for _ in bugs]) + "---|"
    print(header)
    print(separator)
    
    for idx, check_name in enumerate(check_names):
        thresh = thresholds[idx]
        row_str = f"| {check_name} |"
        for bug in bugs:
            val = results[bug][idx]
            passed = val < thresh
            status = "PASS" if passed else "FAIL"
            row_str += f" {val:.2e} ({status}) |"
        print(row_str)

if __name__ == "__main__":
    main()
