# 參考程式雙位置實跑 — 2026-11-11

- `*.repo.txt`：在教材 repo 內 `cd starter && uv run --offline python ../reference/<檔>.py`（WSL，資料讀 `assets/data/`）。
- `*.windows.txt`：原生 Windows Git Bash 的學生專案（資料與揭曉檔都在 `data/`），`uv run python reference/<檔>.py`。
- 揭曉檔還沒下載時，`lab1_cluster.py` 會停在「找不到 shops_daily_store.csv，請先把它下載到 data/」。
- 兩邊只差在 1e-10 以下的浮點雜訊（BLAS 不同），PASS/FAIL 判定與三位小數的數字一致。
