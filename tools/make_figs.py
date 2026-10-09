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
    # Restrict parallel native libraries for deterministic settings and modest CPU use.
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    os.environ["MPLCONFIGDIR"] = str(evidence / "runtime" / "matplotlib-cache")
    os.environ["XDG_CACHE_HOME"] = str(evidence / "runtime" / "cache")
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import sklearn
    from sklearn.datasets import load_digits
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from PIL import Image, ImageOps, ImageDraw

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
    sources = ["reference/lab1_cluster.py", "reference/lab3_logistic.py",
               "tools/body_lab1-cluster.html", "tools/body_lab3-notes.html"]
    source_text = {name: (ROOT / name).read_text() for name in sources}
    source_hashes = {name: hashlib.sha256(text.encode()).hexdigest()
                     for name, text in source_text.items()}
    provenance = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join([sys.executable, *sys.argv]),
        "working_directory": str(Path.cwd()), "script_sha256": sha(Path(__file__)),
        "source_sha256": source_hashes,
        "versions": {"python": sys.version, "numpy": np.__version__,
                     "matplotlib": matplotlib.__version__, "scikit_learn": sklearn.__version__},
        "native_thread_environment": {key: os.environ[key] for key in
                                      ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
        "parameters": {"dataset": "sklearn.datasets.load_digits()", "scaling": "none",
                       "k": list(range(2, 13)), "random_state": 0, "n_init": 10,
                       "other_kmeans_parameters": "installed sklearn defaults (saved per model)",
                       "silhouette": "all 1797 samples, Euclidean distance, no sampling"},
        "limitations": ["Lab 1 uses fixed data and installed package versions; no cross-version bitwise guarantee.",
                        "Lab 3 is a historical displayed example, not a new gradient or training run.",
                        "Lab 3 connects only the seven displayed points; no h=1e-8 datum is invented."]}
    print(json.dumps(provenance, ensure_ascii=False, indent=2))
    X, y = load_digits(return_X_y=True)
    np.savez_compressed(out / "digits-dataset.npz", X=X, y=y)
    provenance["dataset"] = {"shape": list(X.shape), "X_dtype": str(X.dtype),
                              "X_raw_sha256": hashlib.sha256(X.tobytes()).hexdigest(),
                              "y_raw_sha256": hashlib.sha256(y.tobytes()).hexdigest()}

    def save(fig, name):
        fig.savefig(out / f"{name}.png", dpi=120)
        fig.savefig(out / f"{name}.svg", metadata={"Date": None})
        plt.close(fig)
        print(f"Saved {name}.png and {name}.svg")

    samples = []
    fig, axes = plt.subplots(1, 10, figsize=(10, 1.9), layout="constrained")
    for label, ax in enumerate(axes):
        index = int(np.flatnonzero(y == label)[0])
        pixels = X[index].reshape(8, 8)
        samples.append({"label": label, "index_zero_based": index,
                        "pixels_8x8": pixels.tolist()})
        ax.imshow(pixels, cmap="gray", vmin=0, vmax=16, interpolation="nearest")
        ax.set_title(str(label), fontsize=17, pad=9)
        ax.set_axis_off()
    save(fig, "digits-samples")
    dump(out / "digits-samples.json", samples)
    fig, axes = plt.subplots(2, 5, figsize=(4, 2.5), layout="constrained")
    for sample, ax in zip(samples, axes.ravel()):
        ax.imshow(sample["pixels_8x8"], cmap="gray", vmin=0, vmax=16, interpolation="nearest")
        ax.set_title(str(sample["label"]), fontsize=16, pad=5)
        ax.set_axis_off()
    save(fig, "digits-samples-mobile")

    # Parse the existing displayed results, so a mismatch cannot pass silently.
    lab1_pattern = r"k=\s*(\d+)\s+inertia=\s*([\d.]+)\s+silhouette=([\d.]+)"
    displayed = {int(k): (float(inertia), float(score)) for k, inertia, score in
                 re.findall(lab1_pattern, source_text["tools/body_lab1-cluster.html"])}
    if set(displayed) != set(range(2, 13)):
        raise ValueError("Cannot parse exactly the k=2..12 Lab 1 displayed result rows")
    results, all_labels = [], {}
    for k in range(2, 13):
        model = KMeans(n_clusters=k, random_state=0, n_init=10).fit(X)
        score = float(silhouette_score(X, model.labels_))
        inertia = float(model.inertia_)
        expected_inertia, expected_score = displayed[k]
        row = {"k": k, "inertia": inertia, "silhouette": score,
               "displayed_inertia": expected_inertia, "displayed_silhouette": expected_score,
               "inertia_matches_display_precision": abs(inertia-expected_inertia) < 0.050001,
               "silhouette_matches_display_precision": abs(score-expected_score) < 0.000050001}
        print(json.dumps(row))
        results.append(row)
        all_labels[str(k)] = model.labels_.tolist()
        if k == 2:
            provenance["kmeans_parameters"] = model.get_params()
        if not row["inertia_matches_display_precision"] or not row["silhouette_matches_display_precision"]:
            raise ValueError(f"k={k}: recomputation disagrees with the displayed precision; investigate versions/settings")
    dump(out / "lab1-k-selection.json", results)
    dump(out / "lab1-cluster-labels.json", all_labels)
    table_csv(out / "lab1-k-selection.csv", results, list(results[0]))
    best = max(results, key=lambda row: row["silhouette"])
    provenance["lab1_validation"] = {"all_11_rows_match_display_precision": True,
                                     "highest_silhouette_k_in_this_sweep": best["k"]}
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7), layout="constrained")
    ks = [row["k"] for row in results]
    for ax, key, color, title, ylabel in [
        (axes[0], "inertia", INDIGO, "Within-cluster distances", "Inertia (squared-distance sum)"),
        (axes[1], "silhouette", TERRACOTTA, "Separation relative to compactness", "Mean silhouette score")]:
        ax.plot(ks, [row[key] for row in results], "o-", color=color, lw=2.3, ms=6)
        ax.set(title=title, ylabel=ylabel, xlabel="Number of clusters, k", xticks=ks)
        ax.grid(axis="y", color=INDIGO, alpha=0.12)
        ax.spines[["top", "right"]].set_visible(False)
        for k, c in ((9, TERRACOTTA), (10, INDIGO)):
            ax.axvline(k, color=c, ls=":", lw=1.5, alpha=0.6)
    axes[0].ticklabel_format(axis="y", style="sci", scilimits=(6, 6))
    for k, offset in ((9, (-180, -10)), (10, (14, -40))):
        row = results[k-2]
        axes[1].annotate(f"k = {k}: {row['silhouette']:.4f}",
                         (k, row["silhouette"]), xytext=offset, textcoords="offset points",
                         fontsize=12, color=TERRACOTTA if k == 9 else INDIGO,
                         bbox={"facecolor": PAPER, "edgecolor": "none", "alpha": 0.9})
    save(fig, "lab1-k-selection")
    with plt.rc_context({"font.size": 12, "axes.labelsize": 12,
                         "axes.titlesize": 14, "xtick.labelsize": 11, "ytick.labelsize": 11}):
        fig, axes = plt.subplots(2, 1, figsize=(4, 6), layout="constrained")
        for ax, key, color, title, ylabel in [
            (axes[0], "inertia", INDIGO, "Within-cluster distances", "Inertia (distance² sum)"),
            (axes[1], "silhouette", TERRACOTTA, "Separation / compactness", "Mean silhouette score")]:
            ax.plot(ks, [row[key] for row in results], "o-", color=color, lw=2, ms=5)
            ax.set(title=title, ylabel=ylabel, xlabel="Number of clusters, k",
                   xticks=[2, 4, 6, 8, 9, 10, 12])
            ax.grid(axis="y", color=INDIGO, alpha=0.12)
            ax.spines[["top", "right"]].set_visible(False)
            for k, c in ((9, TERRACOTTA), (10, INDIGO)):
                ax.axvline(k, color=c, ls=":", lw=1.5, alpha=0.6)
        axes[0].ticklabel_format(axis="y", style="sci", scilimits=(6, 6))
        for k, pos in ((9, (0.03, 0.90)), (10, (0.48, 0.29))):
            row = results[k-2]
            axes[1].text(*pos, f"k={k}: {row['silhouette']:.4f}", transform=axes[1].transAxes,
                         fontsize=12, color=TERRACOTTA if k == 9 else INDIGO,
                         bbox={"facecolor": PAPER, "edgecolor": "none", "alpha": 0.9})
        save(fig, "lab1-k-selection-mobile")

    lab3 = source_text["tools/body_lab3-notes.html"]
    pattern = r'<div class="o">\s*(1e-\d+)\s+([\d.]+e[-+]\d+)\s+([\d.]+e[-+]\d+)\s+(PASS|FAIL)\s*</div>'
    matches = list(re.finditer(pattern, lab3))
    required = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-9]
    gradient = [{"h": float(m[1]), "max_absolute_error": float(m[2]),
                 "max_relative_error": float(m[3]), "displayed_verdict": m[4]} for m in matches]
    if [row["h"] for row in gradient] != required:
        raise ValueError("Cannot parse exactly the seven expected Lab 3 historical gradient rows")
    (evidence / "lab3-source-excerpt.html").write_text("\n".join(m[0] for m in matches) + "\n")
    dump(out / "lab3-gradient-error.json", {"status": "historical displayed example",
         "source": "tools/body_lab3-notes.html", "source_sha256": source_hashes["tools/body_lab3-notes.html"],
         "caption": "既有範例表的七個步長，線只連接資料點。", "rows": gradient})
    table_csv(out / "lab3-gradient-error.csv", gradient, list(gradient[0]))
    fig, ax = plt.subplots(figsize=(7.5, 4.8), layout="constrained")
    rows = sorted(gradient, key=lambda row: row["h"])
    ax.loglog([row["h"] for row in rows], [row["max_absolute_error"] for row in rows],
              "o-", color=INDIGO, lw=2.3, ms=7, label="Seven displayed values")
    ax.axhline(1e-8, color=TERRACOTTA, ls="--", lw=2, label="Check threshold: $10^{-8}$")
    ax.set(title="Step size and gradient-check error", xlabel="Finite-difference step size, h",
           ylabel="Maximum absolute error")
    ax.grid(which="major", color=INDIGO, alpha=0.12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower left", fontsize=11, frameon=False)
    save(fig, "lab3-gradient-error")
    from matplotlib.ticker import NullLocator
    with plt.rc_context({"font.size": 12, "axes.labelsize": 12,
                         "axes.titlesize": 14, "xtick.labelsize": 11, "ytick.labelsize": 11}):
        fig, ax = plt.subplots(figsize=(4, 4), layout="constrained")
        ax.loglog([row["h"] for row in rows], [row["max_absolute_error"] for row in rows],
                  "o-", color=INDIGO, lw=2, ms=6, label="Seven displayed values")
        ax.axhline(1e-8, color=TERRACOTTA, ls="--", lw=2, label="Threshold: $10^{-8}$")
        ax.set(title="Step size and\ngradient-check error", xlabel="Step size, h",
               ylabel="Maximum absolute error", xticks=[1e-9, 1e-7, 1e-5, 1e-3],
               yticks=[1e-11, 1e-9, 1e-7])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_minor_locator(NullLocator())
        ax.grid(which="major", color=INDIGO, alpha=0.12)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="upper center", fontsize=10, frameon=False)
        save(fig, "lab3-gradient-error-mobile")
    print("Lab 3: extracted exactly seven historical displayed rows; no training or gradient recomputation.")

    names = [name + variant for name in ("digits-samples", "lab1-k-selection", "lab3-gradient-error")
             for variant in ("", "-mobile")]
    pngs = [out / f"{name}.png" for name in names]
    provenance["figure_variants"] = {name: {"png_dimensions": list(Image.open(out / f"{name}.png").size)}
                                      for name in names}
    panels = []
    for path in pngs:
        with Image.open(path) as im:
            panel = ImageOps.contain(im.convert("RGB"), (1000, 900))
            panels.append((path.stem, panel.copy()))
    montage = Image.new("RGB", (1040, sum(im.height + 50 for _, im in panels) + 20), PAPER)
    draw = ImageDraw.Draw(montage)
    top = 20
    for name, panel in panels:
        draw.text((20, top), name, fill=INDIGO)
        montage.paste(panel, ((1040-panel.width)//2, top+25))
        top += panel.height+50
    montage.save(evidence / "all-figures-montage.png")
    provenance["output_sha256"] = {p.name: sha(p) for p in sorted(out.iterdir())
                                    if p.is_file() and p.suffix in (".png", ".svg", ".json", ".csv", ".npz")
                                    and p.name != "provenance.json"}
    dump(out / "provenance.json", provenance)
    dump(evidence / "provenance.json", provenance)
    (out / "README.md").write_text("""# 工作坊教學圖

以 `starter/.venv/bin/python tools/make_figs.py --out assets/figures --evidence-dir tools/test-runs/20261009-site-refine/figures` 重建。
套件版本、資料與來源 hash、實際指令、參數及逐列核對結果見 `provenance.json` 與 evidence 目錄的 `run.log`。三組圖皆提供桌機與 `-mobile` 手機版 PNG／SVG，兩版使用相同資料。手機版以較少刻度和較大字呈現；digits 改為兩列五張。原始資料附於同目錄。

- **digits-samples**：digits 資料集每個標籤的第一筆樣本；索引從 0 開始，記於 JSON。這是輸入資料示意，並非模型產生的影像。顯示範圍固定為 0 到 16。
- **lab1-k-selection**：未縮放的 1797×64 原始像素，k=2..12、random_state=0、n_init=10；上下兩圖分別呈現群內距離平方和與 silhouette。全資料、每次分群標籤及指標均保存。9 是本次搜尋的 silhouette 最高值；10 是數字標籤數，兩者回答不同問題。這不保證其他版本、初始化或資料有相同排序。
- **lab3-gradient-error**：既有範例表的七個步長，線只連接資料點。門檻為最大絕對誤差 1e-8；沒有補入 1e-8 步長的資料，也沒有重新訓練或執行梯度檢查。這是 historical displayed example，不是新跑的 Lab 3 結果；誤差趨勢不能當成所有函數或資料的通則。

英文字軸避免依賴額外字型；圖說可沿用以上繁體中文說明。Lab 3 原表節錄與全部圖的 montage 存於 evidence 目錄。
""")
    print("PASS: figures, data, provenance and all-item montage saved.")


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
