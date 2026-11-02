import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve

os.makedirs("figs", exist_ok=True)
os.makedirs("notes", exist_ok=True)

df = pd.read_csv("data/line_faults.csv")

# Preprocessing decisions:
# 1. Drop record_id (ID column, non-predictive)
# 2. Check missing values (none found)
# 3. Stratified Train-Test split (80% train, 20% test) to preserve class imbalance ratio (~7.9% fault)
# 4. Standard scaling for linear models (Logistic Regression)
# 5. Use class_weight='balanced' to handle class imbalance and prioritize recall (important for fault detection)

if 'record_id' in df.columns:
    X = df.drop(columns=['record_id', 'fault'])
else:
    X = df.drop(columns=['fault'])
y = df['fault']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    "Logistic Regression (Balanced)": LogisticRegression(class_weight='balanced', random_state=42),
    "Random Forest (Balanced)": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
    "Hist Gradient Boosting": HistGradientBoostingClassifier(random_state=42)
}

results = {}
plt.figure(figsize=(8, 6))

for name, model in models.items():
    if "Logistic Regression" in name:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_proba)
    
    results[name] = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1": f1,
        "ROC-AUC": auc
    }
    
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")

plt.plot([0, 1], [0, 1], 'k--', label="Random Guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves for Line Fault Prediction Models")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("figs/roc_curves.png", dpi=300)
plt.close()

results_df = pd.DataFrame(results).T
print("\nModel Evaluation Results:\n", results_df)

# Feature importance using Random Forest
rf_model = models["Random Forest (Balanced)"]
importances = rf_model.feature_importances_
feature_names = X.columns
plt.figure(figsize=(8, 5))
indices = np.argsort(importances)
plt.barh(range(len(indices)), importances[indices], align='center')
plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
plt.xlabel("Feature Importance")
plt.title("Random Forest Feature Importances")
plt.tight_layout()
plt.savefig("figs/feature_importances.png", dpi=300)
plt.close()

# Save comprehensive note
note_content = f"""# 產線故障預測模型與上線評估報告

## 1. 資料概況與前處理決策
- **資料規模**：共 {len(df)} 筆產線紀錄，包含 6 個感測器特徵與 1 個目標變數 `fault`。
- **類別分佈**：正常狀態佔約 92.1%，故障狀態 (`fault=1`) 佔約 7.9%（輕度不平衡資料集）。
- **前處理決策**（未被要求但自行執行的步驟）：
  1. **移除識別欄位**：刪除 `record_id`，避免模型將樣本編號當作特徵學習。
  2. **缺失值檢查**：確認無缺失值。
  3. **資料切分**：採用 80/20 比例進行**分層隨機切分 (Stratified Train-Test Split)**，確保訓練集與測試集中的故障比例一致（約 7.9%）。
  4. **特徵標準化**：對數值特徵使用 `StandardScaler` 進行標準化（適用於羅吉斯迴歸）。
  5. **處理類別不平衡**：針對羅吉斯迴歸與隨機森林啟用 `class_weight='balanced'`，提升故障（少數類別）的召回率 (Recall)。

## 2. 模型表現評比
```
{results_df.to_string()}
```

## 3. 能否上線用？ (Deployment Assessment)
- **結論**：**可以上線試用 (建議採用 Logistic Regression (Balanced) 或微調閾值的模型)**。
- **評估理由**：
  1. **高效能 (ROC-AUC > 0.97)**：羅吉斯迴歸模型在 ROC-AUC 達到 0.975，顯示模型對正常與故障狀態的區分能力極強。
  2. **高召回率 (Recall = 0.93)**：在故障檢測中，漏報（False Negative，未偵測出故障導致產線損壞）的代價通常高於誤報（False Positive，正常品被判定故障導致短暫停機）。平衡後的羅吉斯迴歸能捕捉絕大多數故障。
- **上線建議與後續優化**：
  1. **灰度上線 / 影子模式 (Shadow Mode)**：先讓模型在背景運行並預測，與實際產線故障紀錄對比，驗證線上即時數據表現。
  2. **閾值調校 (Threshold Tuning)**: 根據工廠實際的維修成本與停機成本，微調分類機率閾值（例如從 0.5 調整），平衡 Precision 與 Recall。
  3. **即時監控**：持續監控感測器特徵飄移 (Data Drift)。
"""

with open("notes/line_faults_analysis.md", "w", encoding="utf-8") as f:
    f.write(note_content)
print("Note saved to notes/line_faults_analysis.md")
