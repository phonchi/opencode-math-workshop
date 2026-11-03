#!/usr/bin/env python3
"""Rebuild the workshop figures; no reference script is imported or executed."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PAPER, INDIGO, TERRACOTTA = "#f6f2e9", "#2a3c78", "#b8503c"


class Tee:
    def __init__(self, stream, log):
        self.stream, self.log = stream, log

    def write(self, text):
        self.stream.write(text)
        self.log.write(text)
        self.log.flush()

    def flush(self):
        self.stream.flush()
        self.log.flush()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def table_csv(path, rows, fields):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in rows)


def generate(out, evidence):
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    os.environ["MPLCONFIGDIR"] = str(evidence / "runtime" / "matplotlib-cache")
    os.environ["XDG_CACHE_HOME"] = str(evidence / "runtime" / "cache")
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import sklearn
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score, silhouette_score
    from sklearn.preprocessing import StandardScaler
    from PIL import Image, ImageDraw, ImageOps

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 13,
        "axes.titlesize": 17, "axes.labelsize": 14,
        "figure.facecolor": PAPER, "axes.facecolor": PAPER,
        "text.color": INDIGO, "axes.labelcolor": INDIGO,
        "xtick.color": INDIGO, "ytick.color": INDIGO,
        "axes.edgecolor": "#a6a8ae", "svg.fonttype": "none",
        "svg.hashsalt": "opencode-math-workshop",
        "savefig.facecolor": PAPER,
    })
    data = ROOT / "assets" / "data"
    X = np.genfromtxt(data / "shops_daily.csv", delimiter=",", skip_header=1)
    store = np.genfromtxt(data / "reveal" / "shops_daily_store.csv", delimiter=",", skip_header=1)
    Z = StandardScaler().fit_transform(X)
    provenance = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join([sys.executable, *sys.argv]),
        "script_sha256": sha(Path(__file__)),
        "data_sha256": {p.name: sha(p) for p in sorted(data.rglob("*.csv"))},
        "versions": {"python": sys.version, "numpy": np.__version__,
                     "matplotlib": matplotlib.__version__, "scikit_learn": sklearn.__version__},
        "parameters": {"k": list(range(2, 13)), "random_state": 0, "n_init": 10},
        "limitations": ["Instructor-designed data; results do not generalize to other data."],
    }

    def save(fig, name):
        fig.savefig(out / f"{name}.png", dpi=120)
        fig.savefig(out / f"{name}.svg", metadata={"Date": None})
        plt.close(fig)
        print(f"Saved {name}.png and {name}.svg")

    results = []
    for k in range(2, 13):
        row = {"k": k}
        for tag, A in (("raw", X), ("standardized", Z)):
            labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(A)
            row[f"{tag}_silhouette"] = float(silhouette_score(A, labels))
            row[f"{tag}_ari"] = float(adjusted_rand_score(store, labels))
        results.append(row)
        print(json.dumps(row))
    dump(out / "lab1-k-selection.json", results)
    table_csv(out / "lab1-k-selection.csv", results, list(results[0]))
    ks = [row["k"] for row in results]

    def curves(name, size, ticks):
        fig, axes = plt.subplots(2, 1, figsize=size, layout="constrained")
        for ax, key, title in ((axes[0], "silhouette", "Mean silhouette (no store labels)"),
                               (axes[1], "ari", "ARI against the 10 stores (revealed later)")):
            ax.plot(ks, [r[f"raw_{key}"] for r in results], "o-", color=INDIGO, lw=2.2, label="Raw units")
            ax.plot(ks, [r[f"standardized_{key}"] for r in results], "o-", color=TERRACOTTA, lw=2.2, label="Standardized")
            ax.set(title=title, xlabel="Number of clusters, k", xticks=ticks)
            ax.grid(axis="y", color=INDIGO, alpha=0.12)
            ax.spines[["top", "right"]].set_visible(False)
        axes[0].legend(frameon=False, fontsize=11)
        save(fig, name)

    curves("lab1-k-selection", (7.5, 7), ks)
    with plt.rc_context({"font.size": 12, "axes.labelsize": 12, "axes.titlesize": 13}):
        curves("lab1-k-selection-mobile", (4.4, 6.4), [2, 4, 6, 8, 9, 10, 12])

    names = ["lab1-k-selection", "lab1-k-selection-mobile"]
    panels = [(n, ImageOps.contain(Image.open(out / f"{n}.png").convert("RGB"), (1000, 900))) for n in names]
    montage = Image.new("RGB", (1040, sum(i.height + 50 for _, i in panels) + 20), PAPER)
    draw = ImageDraw.Draw(montage)
    top = 20
    for name, panel in panels:
        draw.text((20, top), name, fill=INDIGO)
        montage.paste(panel, ((1040 - panel.width) // 2, top + 25))
        top += panel.height + 50
    montage.save(evidence / "all-figures-montage.png")
    provenance["output_sha256"] = {p.name: sha(p) for p in sorted(out.iterdir())
                                   if p.is_file() and p.suffix in (".png", ".svg", ".json", ".csv")}
    dump(out / "provenance.json", provenance)
    dump(evidence / "provenance.json", provenance)
    (out / "README.md").write_text("""# 工作坊教學圖

以 `starter/.venv/bin/python tools/make_figs.py --out assets/figures --evidence-dir tools/test-runs/20261104-life-data/figures` 重建。資料由 `tools/make_lab_data.py` 產生，是為工作坊設計的合成資料。

- **lab1-k-selection**：原始尺度與標準化各掃 k=2..12（random_state=0、n_init=10）的 silhouette，以及揭曉後與 10 家分店比對的 ARI。

結果只適用於這份資料，不代表其他資料有相同排序。
""")
    print("PASS: figures, provenance and montage saved.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="Explicit directory for figures and data")
    parser.add_argument("--evidence-dir", type=Path, required=True, help="Explicit directory for log and montage")
    args = parser.parse_args()
    out, evidence = args.out.resolve(), args.evidence_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    with (evidence / "run.log").open("w") as log:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = Tee(stdout, log), Tee(stderr, log)
        try:
            generate(out, evidence)
        except Exception:
            traceback.print_exc()
            raise SystemExit(1)
        finally:
            sys.stdout, sys.stderr = stdout, stderr


if __name__ == "__main__":
    main()
