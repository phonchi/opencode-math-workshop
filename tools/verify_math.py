#!/usr/bin/env python3
"""重算教材用到的數字；任何一項不符就失敗。

用法：starter/.venv/bin/python tools/verify_math.py --out <輸出資料夾>
"""
import argparse
import contextlib
import json
import os
import runpy
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.chdir(out)
    scopes = {}
    for name in ["lab1_cluster", "lab2_pca", "lab2_pca_bugs", "lab3_logistic", "lab3_gradcheck_bugs"]:
        with (out / f"{name}.log").open("w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            scopes[name] = runpy.run_path(str(repo / "reference" / f"{name}.py"))
        print(f"RUN {name}")

    l1 = scopes["lab1_cluster"]
    assert max(l1["raw"], key=lambda k: l1["raw"][k][1]) == 3
    assert max(l1["std"], key=lambda k: l1["std"][k][1]) == 9
    assert l1["std"][9][1] - l1["std"][10][1] > 0.05
    assert l1["std"][10][2] > l1["std"][9][2] + 0.05

    b = scopes["lab2_pca_bugs"]
    table = {bug: b["checks"](bug) for bug in b["NAMES"]}
    assert all(v < b["TOL"] for v in table[None].values())
    assert table["denom_n"]["特徵值"] >= b["TOL"] and table["denom_n"]["比例"] < b["TOL"]
    assert table["no_center"]["比例"] >= b["TOL"]
    assert table["rows"]["|cos|"] >= b["TOL"]
    assert table["ratio_topk"]["比例"] >= b["TOL"]

    g = scopes["lab3_gradcheck_bugs"]
    assert g["check"](g["loss"], g["grad"]) < 1e-8
    assert g["check"](g["mse"], g["mse_grad"]) < 1e-8
    assert g["check"](g["loss"], lambda w: 2 * g["grad"](w)) > 1e-3

    ext = runpy.run_path(str(repo / "reference/math_extensions.py"))
    (out / "summary.json").write_text(json.dumps({"status": "PASS", "numpy": np.__version__}), encoding="utf-8")
    print("PASS: all checks;", "math_extensions loaded" if ext else "")


if __name__ == "__main__":
    main()
