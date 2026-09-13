"""Independently check generated PCA projection and logistic derivatives."""
from pathlib import Path
import ast,contextlib,io,json,runpy
import numpy as np
from scipy.special import expit
from sklearn.datasets import load_digits
root=Path(__file__).resolve().parent
pca=runpy.run_path(str(root/'agent-lab2-pca-auto/lab2_pca.py'))
X=load_digits().data;mine=pca['hand_pca'](X)
Xc=X-X.mean(axis=0);_,s,vt=np.linalg.svd(Xc,full_matrices=False)
projector_diff=float(np.max(np.abs(mine['axes']@mine['axes'].T-vt[:10].T@vt[:10])))
assert projector_diff < 1e-10
# Load definitions only, avoiding rerunning the agent's optional training side effects.
source=ast.parse((root/'agent-lab3-notes-auto/lab3_logistic.py').read_text(encoding='utf-8'))
module=ast.Module(body=[node for node in source.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[])
ns={};exec(compile(module,'generated-logistic-functions','exec'),ns)
rng=np.random.default_rng(90212);A=np.column_stack([rng.normal(size=(100,64)),np.ones(100)]);y=rng.integers(0,2,100);w=rng.normal(size=65)*.2
expected=A.T@(expit(A@w)-y)/len(y)
analytic=float(np.max(np.abs(ns['grad'](w,A,y)-expected)))
fd=ns['finite_diff_grad'](w,A,y,1e-5)
numeric=float(np.max(np.abs(fd-expected)))
assert analytic<1e-12 and numeric<1e-8
result={'pca_projector_vs_independent_svd_maxabs':projector_diff,'logistic_grad_vs_scipy_expit_maxabs':analytic,'logistic_all65_central_diff_maxabs':numeric,'status':'PASS'}
(root/'evidence/generated-independent.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
