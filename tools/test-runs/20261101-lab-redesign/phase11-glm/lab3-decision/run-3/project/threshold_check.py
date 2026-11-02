import pandas as pd
from sklearn.linear_model import LogisticRegression

train = pd.read_csv("data/line_faults.csv")
test = pd.read_csv("data/line_faults_new_batch.csv")
feats = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]

model = LogisticRegression(max_iter=5000)
model.fit(train[feats], train["fault"])
p = model.predict_proba(test[feats])[:, 1]

n = len(test)
budget = 40
print(f"新批資料 {n} 筆，實際故障 {int(test['fault'].sum())} 筆；複查預算 40 件\n")
print(f"{'門檻':>6} {'警報':>6} {'抓到':>6} {'漏掉':>6} {'誤報':>6} {'超預算':>6}")
for t in [0.5, 0.3, 0.2, 0.1, 0.05]:
    alarm = p >= t
    caught = int((alarm & (test["fault"] == 1)).sum())
    missed = int(test["fault"].sum()) - caught
    fp = int((alarm & (test["fault"] == 0)).sum())
    print(f"{t:>6} {int(alarm.sum()):>6} {caught:>6} {missed:>6} {fp:>6} {str(int(alarm.sum()) > budget):>6}")
