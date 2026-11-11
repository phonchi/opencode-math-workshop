# -*- coding: utf-8 -*-
"""lab3_loans_reminder.py — 逾期預測與提醒門檻比較。

流程：
1. 用 data/loans.csv（900 筆）訓練 logistic 迴歸，data/loans_new_batch.csv（300 筆）只拿來驗收。
2. 特徵：pages、past_ontime_pct、past_avg_days、commute_min、account_age_days、book_age_years。
   case_no 是流水號，不當特徵；overdue 是標籤。
3. Pipeline = StandardScaler -> LogisticRegression（L2、C=1.0、無 class_weight）。
   scaler 只用訓練資料 fit。另外在訓練資料做 5 折分層 CV 算折外 AUC，只當體檢，
   最終模型仍是全部 900 筆訓練的那顆。
4. 新批次算出逾期機率後，對門檻 0.5 / 0.3 / 0.2 / 0.1 / 0.05（p >= 門檻算陽性）統計：
   - 超過門檻筆數（還沒考慮寄信上限）
   - 提醒數（受「每 300 筆最多 40 封」限制：超過 40 就只寄機率最高的 40 筆，
     同分時依原列順序（case_no 遞增）當 tie-break）
   - 抓到（寄中逾期）、漏掉（逾期但沒寄到）、白提醒（寄了但其實沒逾期）
5. 只印數字，不替使用者挑門檻。
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TRAIN_CSV = "data/loans.csv"
NEW_CSV = "data/loans_new_batch.csv"
DROP_COLS = ["case_no"]          # 流水號，不當特徵
LABEL = "overdue"
THRESHOLDS = [0.5, 0.3, 0.2, 0.1, 0.05]
MAX_REMINDERS = 40               # 每 300 筆最多寄 40 封
N_SPLITS = 5
RANDOM_STATE = 0
MAX_ITER = 1000


def main():
    train = pd.read_csv(TRAIN_CSV)
    new = pd.read_csv(NEW_CSV)

    feats = [c for c in train.columns if c not in DROP_COLS + [LABEL]]
    assert feats == [c for c in new.columns if c not in DROP_COLS + [LABEL]], "兩份欄位不一致"

    X_tr, y_tr = train[feats], train[LABEL]
    X_new, y_new = new[feats], new[LABEL]

    print(f"訓練：{X_tr.shape[0]} 筆 x {len(feats)} 特徵；逾期 {int(y_tr.sum())} 筆（{y_tr.mean():.1%}）")
    print(f"新批：{X_new.shape[0]} 筆；逾期 {int(y_new.sum())} 筆（{y_new.mean():.1%}）")
    print(f"特徵：{feats}")
    print(f"寄信上限：每 {len(X_new)} 筆最多 {MAX_REMINDERS} 封\n")

    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=MAX_ITER)),
        ]
    )

    # --- 體檢：訓練資料 5 折分層 CV，折外 AUC ---
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    oof = np.zeros(len(y_tr))
    for tr_idx, te_idx in cv.split(X_tr, y_tr):
        pipe.fit(X_tr.iloc[tr_idx], y_tr.iloc[tr_idx])
        oof[te_idx] = pipe.predict_proba(X_tr.iloc[te_idx])[:, 1]
    print(f"訓練資料 5 折折外 AUC：{roc_auc_score(y_tr, oof):.4f}")

    # --- 最終模型：全部 900 筆訓練 ---
    pipe.fit(X_tr, y_tr)
    p_new = pipe.predict_proba(X_new)[:, 1]
    print(f"新批 AUC：{roc_auc_score(y_new, p_new):.4f}\n")

    # 排序依機率降冪；同分用原列順序（case_no 遞增）tie-break，結果可重現
    order = np.lexsort((np.arange(len(p_new)), -p_new))

    overdue_total = int(y_new.sum())
    header = (
        f"{'門檻':>5} | {'>門檻筆數':>9} | {'提醒數(上限40)':>13} | "
        f"{'抓到':>4} | {'漏掉':>4} | {'白提醒':>5} | {'抓到/逾期':>9}"
    )
    print(header)
    print("-" * len(header))
    for t in THRESHOLDS:
        above = p_new >= t
        n_above = int(above.sum())
        # 受上限約束的實際寄出名單：門檻內的筆數若超過 40，只寄機率最高的 40 筆
        n_sent = min(n_above, MAX_REMINDERS)
        sent_idx = order[:n_sent] if n_above > MAX_REMINDERS else np.where(above)[0]
        caught = int(y_new.to_numpy()[sent_idx].sum())
        missed = overdue_total - caught
        false_alarm = n_sent - caught
        print(
            f"{t:>5.2f} | {n_above:>9} | {n_sent:>13} | "
            f"{caught:>4} | {missed:>4} | {false_alarm:>5} | {caught / overdue_total:>8.1%}"
        )


if __name__ == "__main__":
    main()
