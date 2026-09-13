from pathlib import Path
import ast,json,numpy as np
from scipy.special import expit
p=Path(__file__).resolve().parent.parent/'project/lab3_logistic.py'
tree=ast.parse(p.read_text());body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))];ns={};exec(compile(ast.Module(body=body,type_ignores=[]),str(p),'exec'),ns)
rng=np.random.default_rng(90213);X=np.column_stack([rng.normal(size=(100,64)),np.ones(100)]);y=rng.integers(0,2,100);w=rng.normal(size=65)*.1
expected=X.T@(expit(X@w)-y)/100
analytic=float(np.max(np.abs(expected-ns['grad'](w,X,y))))
g=ns['finite_diff_grad'](lambda u:ns['loss'](u,X,y),w,1e-5)
numeric=float(np.max(np.abs(expected-g)))
assert analytic<1e-12 and numeric<1e-8
result={'analytic_vs_scipy_expit':analytic,'central_difference_all65':numeric,'status':'PASS'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
