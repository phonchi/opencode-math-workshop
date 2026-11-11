"""統計 Copilot Auto 實跑的模型、請求數與花費（讀 OpenCode session DB 的副本）。

用法：python3 copilot_usage.py DB路徑 目錄子字串 [開始時間ms]
"""
import json
import sqlite3
import sys
import time
from collections import Counter

db = sqlite3.connect(sys.argv[1])
key = sys.argv[2]
since = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rows = db.execute(
    "select id,title,cost,time_created,time_updated from session_v2 "
    "where directory like ? and time_created>=? order by time_created",
    (f"%{key}%", since),
).fetchall()
tot_cost = tot_req = 0
models_all = Counter()
for sid, title, cost, t0, t1 in rows:
    msgs = db.execute(
        "select data from session_message where session_id=? and type='assistant' order by seq", (sid,)
    ).fetchall()
    models = Counter()
    c = 0.0
    tin = tout = tcache = 0
    for (d,) in msgs:
        d = json.loads(d)
        models[d.get("model", {}).get("id")] += 1
        c += d.get("cost") or 0
        tk = d.get("tokens") or {}
        tin += tk.get("input") or 0
        tout += tk.get("output") or 0
        tcache += (tk.get("cache") or {}).get("read") or 0
    tot_cost += c
    tot_req += len(msgs)
    models_all.update(models)
    print(
        f"{time.strftime('%T', time.localtime(t0/1000))} {title[:40]!r:44} req={len(msgs):3d} "
        f"cost=${c:.4f} (session ${cost or 0:.4f}) in={tin} out={tout} cache_read={tcache} models={dict(models)}"
    )
print(f"TOTAL sessions={len(rows)} requests={tot_req} cost=${tot_cost:.4f} = {tot_cost*100:.1f} credits models={dict(models_all)}")
