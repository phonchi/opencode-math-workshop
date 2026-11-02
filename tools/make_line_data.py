#!/usr/bin/env python3
"""產生工作坊三關用的講師設計資料（固定 seed，可重現）。

用法：starter/.venv/bin/python tools/make_line_data.py
輸出：
  assets/data/line_modes.csv、line_channels.csv、line_faults.csv   學生下載
  assets/data/reveal/*.csv                                          揭曉時才提供
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "data"
REVEAL = OUT / "reveal"


def save(path, names, rows, fmt):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, rows, delimiter=",", header=",".join(names), comments="", fmt=fmt)


def modes(seed=20261103, n_sensors=6, close_gap=4.0, min_sep=9.0):
    """10 個批次，其中第 0、9 批接近；另有 2 欄常數。"""
    rng = np.random.default_rng(seed)
    centers = []
    while len(centers) < 9:
        c = rng.uniform(-14, 14, n_sensors)
        if all(np.linalg.norm(c - x) > min_sep for x in centers):
            centers.append(c)
    u = rng.normal(size=n_sensors)
    centers.append(centers[0] + close_gap * u / np.linalg.norm(u))
    sizes = rng.integers(55, 95, 10)
    z, batch = [], []
    for i, (c, n) in enumerate(zip(centers, sizes)):
        z.append(c + rng.normal(size=(n, n_sensors)) * rng.uniform(0.8, 1.2, n_sensors))
        batch += [i + 1] * n
    z, batch = np.vstack(z), np.array(batch)
    order = rng.permutation(len(batch))
    z, batch = z[order], batch[order]
    offset = np.array([65.0, 3.0, 420.0, 180.0, 12.0, 1500.0])
    scale = np.array([1.2, 0.08, 6.0, 2.5, 0.25, 40.0])
    x = offset + z * scale
    names = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]
    n = len(batch)
    # 兩欄不會變的欄位：韌體版本與取樣週期。
    x = np.column_stack([x, np.full(n, 3.0), np.full(n, 0.5)])
    names += ["firmware_ver", "sample_period_s"]
    return names, x, batch


def channels(seed=20261104, n=800):
    """一欄大單位脈衝數壓過其他欄；故障只反映在兩個微弱的高頻通道。"""
    rng = np.random.default_rng(seed)
    fault = (rng.random(n) < 0.08).astype(int)
    factors = rng.normal(size=(n, 3))
    load = rng.normal(size=(3, 8))
    scale = np.array([1.5, 0.3, 8.0, 3.0, 0.5, 2.0, 12.0, 1.0])
    process = (factors @ load + 0.4 * rng.normal(size=(n, 8))) * scale
    process += np.array([60, 3, 420, 180, 12, 40, 900, 25])
    hf = np.column_stack(
        [
            0.02 + 0.03 * fault + 0.006 * rng.normal(size=n),
            0.05 + 0.06 * fault + 0.012 * rng.normal(size=n),
        ]
    )
    pulse = 800000 + 300000 * rng.normal(size=n)
    x = np.column_stack([process, hf, pulse])
    names = [f"ch{i:02d}" for i in range(1, 12)]
    return names, x, fault


def faults(seed=20261105, n=900, n_new=300):
    """罕見故障；record_id 因「先登錄異常案例」而與標籤相關。"""
    rng = np.random.default_rng(seed)
    w = np.array([1.2, -0.8, 0.6, 0.0, 0.0, 0.4])

    def sample(m):
        x = rng.normal(size=(m, 6))
        y = ((x @ w - 2.6 + 0.8 * rng.normal(size=m)) > 0).astype(int)
        return x, y

    x, y = sample(n)
    order = np.argsort(-y + rng.normal(0, 0.3, size=n))
    rid = np.empty(n, dtype=int)
    rid[order] = np.arange(1, n + 1)
    xn, yn = sample(n_new)
    rid_new = np.arange(n + 1, n + n_new + 1)
    offset = np.array([65.0, 3.0, 420.0, 180.0, 12.0, 1500.0])
    scale = np.array([4.0, 0.5, 15.0, 8.0, 1.0, 60.0])
    names = ["record_id", "temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm", "fault"]
    train = np.column_stack([rid, offset + x * scale, y])
    new = np.column_stack([rid_new, offset + xn * scale, yn])
    p = rng.permutation(n)
    return names, train[p], new


def main():
    names, x, batch = modes()
    save(OUT / "line_modes.csv", names, x, "%.3f")
    save(REVEAL / "line_modes_batches.csv", ["batch"], batch[:, None], "%d")

    names, x, fault = channels()
    save(OUT / "line_channels.csv", names, x, "%.4f")
    save(REVEAL / "line_channels_fault.csv", ["fault"], fault[:, None], "%d")

    names, train, new = faults()
    fmt = ["%d"] + ["%.3f"] * 6 + ["%d"]
    save(OUT / "line_faults.csv", names, train, fmt)
    save(REVEAL / "line_faults_new_batch.csv", names, new, fmt)
    print("written", OUT)


if __name__ == "__main__":
    main()
