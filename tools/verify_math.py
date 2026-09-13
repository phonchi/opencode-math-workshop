"""Run bounded, independent mathematical acceptance in a named output directory."""
import argparse
import ast
import contextlib
import json
import os
from pathlib import Path
import platform
import re
import runpy
import sys

import numpy as np
import sklearn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.chdir(out)
    checks = {}
    for slug, file in [("lab1", "lab1_cluster.py"), ("lab2", "lab2_pca.py"), ("lab3", "lab3_logistic.py")]:
        with (out / f"{slug}.log").open("w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            scope = runpy.run_path(str(repo / "reference" / file))
        if slug == "lab1":
            assert abs(scope["a"].inertia_ - scope["b"].inertia_) < scope["tol"]
            assert scope["ari"] > 1 - 1e-9
            assert scope["best_k"] == 9
        elif slug == "lab2":
            for key, tol in [("e1", 1e-8), ("e2", 1e-6), ("e3", 1e-8), ("e4", 1e-10), ("e5", 1e-6)]:
                assert scope[key] < tol, (key, scope[key])
            assert abs(scope["theory"] - scope["a"]) < 1e-8
            assert max(scope["r1"], scope["r2"], scope["r3"], scope["r4"]) < 1e-6
            assert scope["r5"] > .09
        else:
            assert scope["best"][1] < 1e-8
            assert scope["res"].success and scope["geo"] > 0
            assert np.array_equal(scope["p_manual"] > .5, scope["p_sk"] > .5)
            assert np.isfinite(scope["w_l2"]).all()
        checks[slug] = "PASS"
        print(f"PASS: {slug} (full output in {slug}.log)")

    ext = runpy.run_path(str(repo / "reference/math_extensions.py"))
    extension_dir = out / "extensions"
    for folder in ["figs", "notes"]:
        (extension_dir / folder).mkdir(parents=True, exist_ok=True)
    extensions = {name: ext[name](extension_dir) for name in ["low_rank", "descent", "graph"]}
    (extension_dir / "math-results.json").write_text(json.dumps(extensions, indent=2, ensure_ascii=False), encoding="utf-8")
    checks["extensions"] = "PASS"
    print("PASS: low rank / gradient descent / shortest path")

    # Independent NumPy reference for the authored JavaScript illustration.
    snippet = (repo / "tools/pca-explorer.html").read_text(encoding="utf-8")
    points = np.asarray(ast.literal_eval(re.search(r"const points=(\[[^\n]+\]);", snippet)[1]), dtype=float)
    np.testing.assert_allclose(points.mean(axis=0), 0, atol=1e-15)
    covariance = np.cov(points, rowvar=False)
    vals, vecs = np.linalg.eigh(covariance)
    principal_angle = float(np.degrees(np.arctan2(vecs[1, -1], vecs[0, -1])) % 180)
    sample = []
    for angle in [0., 45., 90., 180., principal_angle]:
        direction = np.array([np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
        projection = points @ direction
        variance = float(np.var(projection, ddof=1))
        error = float(np.mean(np.sum((points - np.outer(projection, direction)) ** 2, axis=1)))
        sample.append({"angle": angle, "variance": variance, "error": error})
    np.testing.assert_allclose([sample[0]["variance"], sample[0]["error"]], [sample[3]["variance"], sample[3]["error"]], atol=1e-12)
    assert abs(sample[-1]["variance"] - vals[-1]) < 1e-12
    assert abs(sample[-1]["error"] - vals[0] * (len(points) - 1) / len(points)) < 1e-12
    assert all(item["variance"] <= sample[-1]["variance"] + 1e-12 for item in sample)
    (out / "pca-browser-reference.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")
    checks["pca_reference"] = "PASS"
    print("PASS: independent PCA illustration reference")
    provenance = {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "sklearn": sklearn.__version__, "checks": checks}
    (out / "result.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
