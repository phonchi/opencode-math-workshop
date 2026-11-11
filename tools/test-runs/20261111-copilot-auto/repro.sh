#!/usr/bin/env bash
# 重現 lab2-hand 的 patch 卡住：私人伺服器（--standalone）＋ debug log，專案在 Temp 以外
cd /c/Users/User/copilot-lab-test && uv sync -q
OUT=/c/Users/User/AppData/Local/Temp/copilot-runs/repro; mkdir -p $OUT
L2H="用 numpy 的 eigh 手刻 PCA，存成 lab2_pca.py：
讀 data/orders.csv，每欄先除以標準差、不要減平均（中心化留給 PCA 自己做），取前 4 個主成分，
用 sklearn 的 PCA(n_components=4, svd_solver='full') 當對照組。
再寫幾項檢查驗證手刻的結果，每項印出實際數值、門檻和 PASS/FAIL，用 uv run python 跑一次。
列出你替我做的每個決定（前處理、準則、門檻、丟掉的欄位）。"
echo "start $(date +%T)" > $OUT/status
opencode run --standalone --print-logs --log-level debug --auto -m "${MODEL:-github-copilot/gpt-6.1-terra}" "$L2H" > $OUT/stdout.log 2> $OUT/debug.log </dev/null
echo "end $(date +%T) rc=$?" >> $OUT/status
