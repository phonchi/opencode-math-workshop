import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

digits = load_digits()
X = digits.data.astype(np.float64)
n, d = X.shape
k = 10

mean = X.mean(axis=0)
Xc = X - mean
S = Xc.T @ Xc / (n - 1)
w, V = np.linalg.eigh(S)
order = np.argsort(w)[::-1]
w = w[order]
V = V[:, order]
hand_evals = w[:k]
hand_components = V[:, :k].T.copy()

for i in range(k):
    j = np.argmax(np.abs(hand_components[i]))
    if hand_components[i, j] < 0:
        hand_components[i] *= -1

hand_Z = Xc @ hand_components.T
hand_Xhat = hand_Z @ hand_components + mean

pca = PCA(n_components=k, svd_solver="full")
pca.fit(X)
ref_components = pca.components_
ref_Z = pca.transform(X)
ref_Xhat = pca.inverse_transform(ref_Z)

val1 = np.max(np.abs(Xc.mean(axis=0)))
print(f"1. centering: max_abs_mean={val1:.3e} tol=1e-12 -> {'PASS' if val1 <= 1e-12 else 'FAIL'}")

val2 = np.max(np.abs(S - (Xc.T @ Xc) / (n - 1)))
print(f"2. covariance: max_abs_diff={val2:.3e} tol=1e-10 -> {'PASS' if val2 <= 1e-10 else 'FAIL'}")

abs3 = np.max(np.abs(hand_evals - pca.explained_variance_))
rel3 = np.max(np.abs((hand_evals - pca.explained_variance_) / pca.explained_variance_))
ok3 = np.allclose(hand_evals, pca.explained_variance_, rtol=1e-6, atol=1e-8)
print(f"3. eigenvalues: max_abs={abs3:.3e} max_rel={rel3:.3e} rtol=1e-6 atol=1e-8 -> {'PASS' if ok3 else 'FAIL'}")

hand_ratio = hand_evals / w.sum()
abs4 = np.max(np.abs(hand_ratio - pca.explained_variance_ratio_))
ok4 = np.allclose(hand_ratio, pca.explained_variance_ratio_, rtol=1e-8, atol=1e-12)
print(f"4. explained_variance_ratio: max_abs={abs4:.3e} rtol=1e-8 atol=1e-12 -> {'PASS' if ok4 else 'FAIL'}")

cos_vals = np.array([np.abs(hand_components[i] @ ref_components[i]) for i in range(k)])
min_cos = float(cos_vals.min())
max_dev = float(np.max(1.0 - cos_vals))
ok5 = min_cos >= 1.0 - 1e-6
print(f"5. component_alignment: min_abs_cos={min_cos:.15f} max_dev={max_dev:.3e} tol=1e-6 -> {'PASS' if ok5 else 'FAIL'}")

orth = float(np.linalg.norm(hand_components @ hand_components.T - np.eye(k), ord="fro"))
ok6 = orth <= 1e-10
print(f"6. orthogonality: frobenius={orth:.3e} tol=1e-10 -> {'PASS' if ok6 else 'FAIL'}")

mismatches = 0
for i in range(k):
    jh = np.argmax(np.abs(hand_components[i]))
    jr = np.argmax(np.abs(ref_components[i]))
    if np.sign(hand_components[i, jh]) != np.sign(ref_components[i, jr]):
        mismatches += 1
ok7 = mismatches == 0
print(f"7. sign_convention: mismatches={mismatches} tol=0 -> {'PASS' if ok7 else 'FAIL'}")

align = np.sign(np.diag(hand_components @ ref_components.T))
align[align == 0] = 1
aligned_components = align[:, None] * hand_components
aligned_Z = Xc @ aligned_components.T
abs8 = float(np.max(np.abs(aligned_Z - ref_Z)))
ok8 = abs8 <= 1e-5
print(f"8. transform: max_abs={abs8:.3e} tol=1e-5 -> {'PASS' if ok8 else 'FAIL'}")

aligned_Xhat = aligned_Z @ aligned_components + mean
abs9 = float(np.max(np.abs(aligned_Xhat - ref_Xhat)))
ok9 = abs9 <= 1e-5
print(f"9. inverse_transform: max_abs={abs9:.3e} tol=1e-5 -> {'PASS' if ok9 else 'FAIL'}")

pc_var = np.var(aligned_Z, axis=0, ddof=1)
abs10 = float(np.max(np.abs(pc_var - hand_evals)))
rel10 = float(np.max(np.abs((pc_var - hand_evals) / hand_evals)))
ok10 = np.allclose(pc_var, hand_evals, rtol=1e-6, atol=1e-8)
print(f"10. pc_variance: max_abs={abs10:.3e} max_rel={rel10:.3e} rtol=1e-6 atol=1e-8 -> {'PASS' if ok10 else 'FAIL'}")

Zc = aligned_Z - aligned_Z.mean(axis=0)
covZ = Zc.T @ Zc / (n - 1)
offdiag = covZ - np.diag(np.diag(covZ))
val11 = float(np.max(np.abs(offdiag)))
ok11 = val11 <= 1e-8
print(f"11. pc_uncorrelated: max_abs_offdiag={val11:.3e} tol=1e-8 -> {'PASS' if ok11 else 'FAIL'}")

invalid_count = 0
invalid_count += int(np.count_nonzero(~np.isfinite(hand_components)))
invalid_count += int(np.count_nonzero(~np.isfinite(aligned_Z)))
invalid_count += int(np.count_nonzero(~np.isfinite(aligned_Xhat)))
shapes_ok = hand_components.shape == (k, d) and aligned_Z.shape == (n, k) and aligned_Xhat.shape == (n, d)
ok12 = shapes_ok and invalid_count == 0
print(f"12. shape_finite: components_shape={hand_components.shape} transform_shape={aligned_Z.shape} invalid={invalid_count} -> {'PASS' if ok12 else 'FAIL'}")
