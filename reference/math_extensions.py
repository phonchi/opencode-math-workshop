"""Deterministic reference for the three optional mathematics exercises.

Run from a fresh exercise directory:
  uv run python /path/to/reference/math_extensions.py --task all --out .
Each result includes exact parameters, numerical checks, figure and notes.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def low_rank(out):
    q = np.linspace(-1, 1, 48)
    x, y = np.meshgrid(q, q)
    a = np.exp(-5 * (x * x + y * y)) + .2 * np.cos(6 * x + 3 * y)
    u, s, vt = np.linalg.svd(a, full_matrices=False)
    result = {"grid": 48, "ks": [1, 2, 4], "formula": "exp(-5*(x*x+y*y))+0.2*cos(6*x+3*y)", "checks": []}
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.5))
    axs[0].imshow(a, cmap="gray", vmin=a.min(), vmax=a.max())
    axs[0].set_title("Original")
    previous = np.inf
    for ax, k in zip(axs[1:], result["ks"]):
        reconstructed = (u[:, :k] * s[:k]) @ vt[:k]
        error = float(np.sum((a - reconstructed) ** 2))
        tail = float(np.sum(s[k:] ** 2))
        assert np.isclose(error, tail, atol=1e-10)
        assert error <= previous + 1e-10
        previous = error
        result["checks"].append({"k": k, "squared_error": error, "tail_energy": tail})
        ax.imshow(reconstructed, cmap="gray", vmin=a.min(), vmax=a.max())
        ax.set_title(f"k={k}")
    assert np.allclose((u * s) @ vt, a, atol=1e-12)
    for ax in axs:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out / "figs/low_rank.png", dpi=150)
    plt.close(fig)
    (out / "notes/low_rank.md").write_text("# 低秩近似\n\n原矩陣由三個秩一圖樣組成，k=4 已能在浮點誤差內重建。平方誤差與尾端奇異值平方和一致；這個結論不代表任意影像都只需四個成分。\n", encoding="utf-8")
    return result


def descent(out):
    steps, start = 30, 0.
    trajectories, results = {}, []
    for eta in [.1, .8, 1.1]:
        values = [start]
        for _ in range(steps):
            values.append(values[-1] - eta * 2 * (values[-1] - 3))
        values = np.asarray(values)
        exact = 3 + (1 - 2 * eta) ** np.arange(steps + 1) * (start - 3)
        np.testing.assert_allclose(values, exact, rtol=1e-10, atol=1e-12)
        loss = (values - 3) ** 2
        if eta < 1:
            assert np.all(np.diff(loss) <= 1e-12)
        else:
            assert np.all(np.diff(loss) > 0)
        trajectories[str(eta)] = values.tolist()
        results.append({"eta": eta, "final_x": float(values[-1]), "final_loss": float(loss[-1])})
        plt.semilogy(np.arange(steps + 1), loss, label=f"step={eta}")
    for x in [0., 1., 4.]:
        h = 1e-5
        numerical = (((x + h) - 3) ** 2 - ((x - h) - 3) ** 2) / (2 * h)
        assert abs(numerical - 2 * (x - 3)) < 1e-8
    plt.xlabel("Iteration")
    plt.ylabel("f(x) = (x - 3)^2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "figs/gradient_steps.png", dpi=150)
    plt.close()
    (out / "notes/gradient_steps.md").write_text("# 梯度下降\n\n0.1 單側收斂；0.8 振盪收斂；1.1 振盪發散。每一步的誤差乘上 1-2η，可用此解析式獨立檢查迴圈。中央差分檢查只針對指定位置與步長。\n", encoding="utf-8")
    return {"steps": steps, "x0": start, "h": 1e-5, "checks": results, "trajectories": trajectories}


def graph(out):
    edges = [("A", "B", 2), ("A", "C", 5), ("B", "C", 1), ("B", "D", 4), ("C", "D", 1), ("C", "E", 5), ("D", "E", 1)]
    g = nx.Graph()
    g.add_weighted_edges_from(edges)
    route = nx.dijkstra_path(g, "A", "E")
    distance = nx.dijkstra_path_length(g, "A", "E")
    enumerated = [{"path": path, "length": sum(g[a][b]["weight"] for a, b in zip(path, path[1:]))} for path in nx.all_simple_paths(g, "A", "E")]
    assert min(item["length"] for item in enumerated) == distance == 5
    assert route == ["A", "B", "C", "D", "E"]
    pos = {"A": (0, 1), "B": (1, 2), "C": (1, 0), "D": (2, 1), "E": (3, 1)}
    nx.draw_networkx(g, pos, node_color="#f6f2e9", edge_color="#7d7a72", node_size=900)
    nx.draw_networkx_edges(g, pos, edgelist=list(zip(route, route[1:])), edge_color="#b8503c", width=3)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=nx.get_edge_attributes(g, "weight"))
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out / "figs/shortest_path.png", dpi=150)
    plt.close()
    g.add_node("F")
    try:
        nx.dijkstra_path(g, "A", "F")
    except nx.NetworkXNoPath:
        unreachable = True
    else:
        raise AssertionError("A to F must be unreachable")
    (out / "notes/shortest_path.md").write_text("# 最短路徑\n\nA → B → C → D → E，距離 5。列舉所有簡單路徑確認最小值；A 到 F 沒有路徑。列舉僅適合小圖，不能當成大型路網的一般求解方法。\n", encoding="utf-8")
    return {"edges": edges, "positions": pos, "route": route, "distance": distance, "all_simple_paths": enumerated, "unreachable_checked": unreachable}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["all", "low-rank", "descent", "graph"], default="all")
    parser.add_argument("--out", type=Path, default=Path.cwd())
    args = parser.parse_args()
    for folder in ["figs", "notes"]:
        (args.out / folder).mkdir(parents=True, exist_ok=True)
    tasks = {"low-rank": low_rank, "descent": descent, "graph": graph}
    result = {name: fn(args.out) for name, fn in tasks.items() if args.task in ("all", name)}
    (args.out / "math-results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("PASS: mathematics exercises and independent checks")


if __name__ == "__main__":
    main()
