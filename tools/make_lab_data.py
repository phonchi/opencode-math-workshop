#!/usr/bin/env python3
"""產生工作坊三關用的設計資料（固定 seed，可重現）。

用法：starter/.venv/bin/python tools/make_lab_data.py
輸出：
  assets/data/shops_daily.csv、orders.csv、loans.csv   學生下載
  assets/data/reveal/*.csv                              揭曉時才提供

三份資料的「隱藏結構」（群、主成分、洩漏）都先在標準常態尺度 z 上產生，
再用 offset + z * scale 換成生活化的單位。標準化對每欄的平移與縮放不變，
所以標準化後的結論只取決於 z；原始尺度的結論才取決於 scale。
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "data"
REVEAL = OUT / "reveal"


def save(path, names, rows, fmt):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, rows, delimiter=",", header=",".join(names), comments="", fmt=fmt)


def shops(seed=20261103, n_cols=6, close_gap=4.0, min_sep=9.0):
    """手搖飲 10 家分店的每日營業紀錄。第 1、10 家（同一捷運站兩個出口）很接近；另有 2 欄全連鎖統一的常數。"""
    rng = np.random.default_rng(seed)
    centers = []
    while len(centers) < 9:
        c = rng.uniform(-14, 14, n_cols)
        if all(np.linalg.norm(c - x) > min_sep for x in centers):
            centers.append(c)
    u = rng.normal(size=n_cols)
    centers.append(centers[0] + close_gap * u / np.linalg.norm(u))
    sizes = rng.integers(55, 95, 10)
    z, store = [], []
    for i, (c, n) in enumerate(zip(centers, sizes)):
        z.append(c + rng.normal(size=(n, n_cols)) * rng.uniform(0.8, 1.2, n_cols))
        store += [i + 1] * n
    z, store = np.vstack(z), np.array(store)
    order = rng.permutation(len(store))
    z, store = z[order], store[order]
    # 營業額以「元」記錄，數字遠大於其他欄；不標準化時距離幾乎只看它。
    names = ["revenue_ntd", "cups_sold", "topping_share", "wait_min", "delivery_share", "rating"]
    offset = np.array([42000.0, 600.0, 0.30, 8.0, 0.35, 4.2])
    scale = np.array([1000.0, 15.0, 0.01, 0.25, 0.012, 0.02])
    x = offset + z * scale
    n = len(store)
    names += ["open_hours", "menu_version"]
    x = np.column_stack([x, np.full(n, 12.0), np.full(n, 3.0)])
    return names, x, store


def orders(seed=20261104, n=800):
    """校園外送訂單。騎士累積里程（公尺）數字很大卻和客訴無關；客訴只反映在兩個讀數很小的欄。"""
    rng = np.random.default_rng(seed)
    complaint = (rng.random(n) < 0.08).astype(int)
    factors = rng.normal(size=(n, 3))
    load = rng.normal(size=(3, 8))
    scale = np.array([20.0, 0.3, 1.5, 1.5, 0.25, 2.0, 60.0, 0.06])
    base = (factors @ load + 0.4 * rng.normal(size=(n, 8))) * scale
    base += np.array([230.0, 2.5, 18.0, 20.0, 2.0, 15.0, 600.0, 4.3])
    small = np.column_stack(
        [
            0.03 + 0.03 * complaint + 0.006 * rng.normal(size=n),
            0.05 + 0.06 * complaint + 0.012 * rng.normal(size=n),
        ]
    )
    odometer = 1500000 + 300000 * rng.normal(size=n)
    x = np.column_stack([base, small, odometer])
    names = [
        "amount_ntd", "distance_km", "prep_min", "ride_min", "handoff_min", "tip_ntd",
        "package_g", "shop_rating", "drop_offset_km", "pause_ratio", "rider_odometer_m",
    ]
    return names, x, complaint


def loans(seed=20261105, n=900, n_new=300):
    """圖書館借閱，少數會逾期；case_no 因「舊紀錄回填時先處理逾期案件」而與標籤相關。"""
    rng = np.random.default_rng(seed)
    w = np.array([1.2, -0.8, 0.6, 0.0, 0.0, 0.4])

    def sample(m):
        x = rng.normal(size=(m, 6))
        y = ((x @ w - 2.6 + 0.8 * rng.normal(size=m)) > 0).astype(int)
        return x, y

    x, y = sample(n)
    order = np.argsort(-y + rng.normal(0, 0.3, size=n))
    cid = np.empty(n, dtype=int)
    cid[order] = np.arange(1, n + 1)
    xn, yn = sample(n_new)
    cid_new = np.arange(n + 1, n + n_new + 1)
    offset = np.array([350.0, 86.0, 18.0, 30.0, 900.0, 12.0])
    scale = np.array([70.0, 3.0, 3.0, 8.0, 200.0, 3.0])
    names = ["case_no", "pages", "past_ontime_pct", "past_avg_days", "commute_min",
             "account_age_days", "book_age_years", "overdue"]
    train = np.column_stack([cid, offset + x * scale, y])
    new = np.column_stack([cid_new, offset + xn * scale, yn])
    p = rng.permutation(n)
    return names, train[p], new


def main():
    names, x, store = shops()
    save(OUT / "shops_daily.csv", names, x, ["%.0f", "%.0f", "%.3f", "%.2f", "%.3f", "%.3f", "%.0f", "%.0f"])
    save(REVEAL / "shops_daily_store.csv", ["store"], store[:, None], "%d")

    names, x, complaint = orders()
    save(OUT / "orders.csv", names, x,
         ["%.0f", "%.2f", "%.1f", "%.1f", "%.2f", "%.1f", "%.0f", "%.2f", "%.4f", "%.4f", "%.0f"])
    save(REVEAL / "orders_complaint.csv", ["complaint"], complaint[:, None], "%d")

    names, train, new = loans()
    fmt = ["%d", "%.0f", "%.1f", "%.1f", "%.1f", "%.0f", "%.1f", "%d"]
    save(OUT / "loans.csv", names, train, fmt)
    save(REVEAL / "loans_new_batch.csv", names, new, fmt)
    print("written", OUT)


if __name__ == "__main__":
    main()
