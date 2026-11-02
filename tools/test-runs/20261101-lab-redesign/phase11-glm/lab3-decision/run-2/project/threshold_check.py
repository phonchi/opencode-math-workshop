import pandas as pd
from sklearn.linear_model import LogisticRegression

train = pd.read_csv("data/line_faults.csv")
new = pd.read_csv("data/line_faults_new_batch.csv")
feats = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]

model = LogisticRegression(max_iter=5000)
model.fit(train[feats], train["fault"])

p = model.predict_proba(new[feats])[:, 1]
y = new["fault"].values

print(f"新批資料 {len(new)} 筆，實際故障 {y.sum()} 筆\n")
print(f"{'門檻':>6} {'警報':>5} {'抓到':>5} {'漏掉':>5} {'誤報':>5} {'複查率':>8} {'複查額度':>6}")
for t in [0.5, 0.3, 0.2, 0.1, 0.05]:
    alarm = p >= t
    tp = int((alarm & (y == 1)).sum())
    fp = int((alarm & (y == 0)).sum())
    fn = int((~alarm & (y == 1)).sum())
    rate = alarm.sum() / len(new)
    budget = "符合" if alarm.sum() <= 40 else "超過"
    print(f"{t:>6} {alarm.sum():>5} {tp:>5} {fn:>5} {fp:>5} {rate:>7.1%} {budget:>6}")
