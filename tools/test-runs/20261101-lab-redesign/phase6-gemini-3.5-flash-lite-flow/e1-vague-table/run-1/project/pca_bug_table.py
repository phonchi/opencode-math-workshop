import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA as SklearnPCA

class ManualPCA:
    def __init__(self, n_components=10, bug='none'):
        self.n_components = n_components
        self.bug = bug
        self.mean_ = None
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None

    def fit(self, X):
        X = np.array(X, dtype=float)
        N, D = X.shape

        # 1. 均值中心化 (bug: no_center)
        if self.bug == 'no_center':
            self.mean_ = np.zeros(D)
            X_centered = X
        else:
            self.mean_ = np.mean(X, axis=0)
            X_centered = X - self.mean_

        # 2. SVD
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        # 3. 主成分 (bug: rows)
        if self.bug == 'rows':
            self.components_ = X_centered[:self.n_components, :]
        else:
            self.components_ = Vt[:self.n_components, :]

        # 4. 變異數分母 (bug: denom_n)
        if self.bug == 'denom_n':
            denom = N
        else:
            denom = N - 1

        self.explained_variance_ = (S ** 2) / denom

        # 5. 比例分母 (bug: ratio_topk)
        if self.bug == 'ratio_topk':
            total_var = np.sum(S[:self.n_components] ** 2) / denom
        else:
            total_var = np.sum(S ** 2) / denom

        self.explained_variance_ratio_ = self.explained_variance_[:self.n_components] / total_var
        self.explained_variance_ = self.explained_variance_[:self.n_components]

        return self

    def transform(self, X):
        X = np.array(X, dtype=float)
        if self.bug == 'no_center':
            X_centered = X
        else:
            X_centered = X - self.mean_
        return np.dot(X_centered, self.components_.T)

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

def run_checks(bug_name, X, sklearn_pca, n_comp=10):
    # 初始化並執行手刻 PCA
    manual_pca = ManualPCA(n_components=n_comp, bug=bug_name)
    manual_pca.fit(X)

    # 檢查 1: 解釋變異量比例誤差 (門檻: < 1e-10)
    var_diff = np.max(np.abs(manual_pca.explained_variance_ratio_ - sklearn_pca.explained_variance_ratio_))
    pass_check1 = var_diff < 1e-10

    # 檢查 2: 主成分方向內積檢驗 (門檻: abs(abs(dot) - 1.0) < 1e-5 對所有 10 個主成分)
    comp_manual = manual_pca.components_
    comp_sklearn = sklearn_pca.components_
    
    max_comp_err = 0.0
    all_comp_pass = True
    for i in range(n_comp):
        dot_val = np.dot(comp_manual[i], comp_sklearn[i])
        err = np.abs(np.abs(dot_val) - 1.0)
        if err > max_comp_err:
            max_comp_err = err
        if err >= 1e-5:
            all_comp_pass = False

    return {
        'var_diff': var_diff,
        'check1_pass': pass_check1,
        'max_comp_err': max_comp_err,
        'check2_pass': all_comp_pass
    }

def main():
    digits = load_digits()
    X = digits.data
    n_comp = 10

    # 訓練 sklearn PCA 作為標準答案
    sklearn_pca = SklearnPCA(n_components=n_comp)
    sklearn_pca.fit(X)

    bugs = ['none', 'ratio_topk', 'denom_n', 'no_center', 'rows']
    results = {}

    for b in bugs:
        results[b] = run_checks(b, X, sklearn_pca, n_comp=n_comp)

    # 印出「檢查 × 錯誤」表
    print("=" * 95)
    print(f"{'檢查項目':<30} | " + " | ".join([f"{b:<12}" for b in bugs]))
    print("-" * 95)

    # Check 1 Row
    row1_vals = []
    for b in bugs:
        v = results[b]['var_diff']
        status = "PASS" if results[b]['check1_pass'] else "FAIL"
        row1_vals.append(f"{v:.2e} ({status})")
    print(f"{'Check 1: Var Ratio Diff (<1e-10)':<30} | " + " | ".join([f"{val:<12}" for val in row1_vals]))

    # Check 2 Row
    row2_vals = []
    for b in bugs:
        v = results[b]['max_comp_err']
        status = "PASS" if results[b]['check2_pass'] else "FAIL"
        row2_vals.append(f"{v:.2e} ({status})")
    print(f"{'Check 2: Component Err (<1e-5)':<30} | " + " | ".join([f"{val:<12}" for val in row2_vals]))
    print("=" * 95)

if __name__ == '__main__':
    main()
