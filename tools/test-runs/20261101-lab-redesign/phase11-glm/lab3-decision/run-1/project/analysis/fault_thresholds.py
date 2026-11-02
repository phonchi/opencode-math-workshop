import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

FEATURES = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]

train = pd.read_csv("data/line_faults.csv")
new = pd.read_csv("data/line_faults_new_batch.csv")

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
model.fit(train[FEATURES], train["fault"])

proba = model.predict_proba(new[FEATURES])[:, 1]
y = new["fault"].values

print(f"新批次筆數: {len(new)}, 實際故障數: {y.sum()}, 正常數: {(1 - y).sum()}")
print(f"每 300 筆上限 40 件 → 警報率上限 {40 / 300:.1%}\n")
print(f"{'門檻':>6} {'警報':>6} {'抓到':>6} {'漏掉':>6} {'誤報':>6} {'警報率':>8} {'召回':>8}")
for t in [0.5, 0.3, 0.2, 0.1, 0.05]:
    alarm = proba >= t
    tp = int((alarm & (y == 1)).sum())
    fn = int((~alarm & (y == 1)).sum())
    fp = int((alarm & (y == 0)).sum())
    print(f"{t:>6} {int(alarm.sum()):>6} {tp:>6} {fn:>6} {fp:>6} {alarm.mean():>8.1%} {tp / (tp + fn):>8.1%}")
