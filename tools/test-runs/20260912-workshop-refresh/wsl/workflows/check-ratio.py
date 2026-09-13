from pathlib import Path
import runpy,contextlib,json,numpy as np
p=Path(__file__).resolve().parent
with (p/'lab2-ratio-independent.log').open('w') as log,contextlib.redirect_stdout(log):d=runpy.run_path(str(p.parent/'project/lab2_pca.py'))
total=float(np.var(d['X'],axis=0,ddof=1).sum());expected=d['var_hand']/total
np.testing.assert_allclose(d['ratio_hand'],expected,rtol=1e-12,atol=1e-12)
np.testing.assert_allclose(d['ratio_sk'],d['ref'].explained_variance_ratio_,rtol=0,atol=0)
assert .738<expected.sum()<.739
r={'status':'PASS','independent_total_variance':total,'top10_ratio':float(expected.sum()),'max_ratio_diff':float(np.max(np.abs(d['ratio_hand']-d['ratio_sk'])))}
(p/'lab2-ratio-independent.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
