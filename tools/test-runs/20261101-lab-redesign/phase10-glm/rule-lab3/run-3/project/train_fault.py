import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, average_precision_score,
                             precision_recall_curve, confusion_matrix)

df = pd.read_csv('data/line_faults.csv')
X = df.drop(columns=['record_id', 'fault'])
y = df['fault']

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

model = RandomForestClassifier(
    n_estimators=400, class_weight='balanced', random_state=42, n_jobs=-1)

cv = StratifiedKFold(5, shuffle=True, random_state=42)
scores = cross_validate(model, X_tr, y_tr, cv=cv,
                        scoring=['average_precision', 'recall', 'precision'])
print('CV  AP=%.3f  recall=%.3f  precision=%.3f' % (
    scores['test_average_precision'].mean(),
    scores['test_recall'].mean(),
    scores['test_precision'].mean()))

model.fit(X_tr, y_tr)
p = model.predict_proba(X_te)[:, 1]
print('Test AP = %.3f' % average_precision_score(y_te, p))
print(confusion_matrix(y_te, (p >= 0.5).astype(int)))

print(classification_report(y_te, (p >= 0.5).astype(int)))

print('特徵重要性：')
for name, imp in sorted(zip(X.columns, model.feature_importances_),
                        key=lambda t: -t[1]):
    print(f'  {name}: {imp:.3f}')
