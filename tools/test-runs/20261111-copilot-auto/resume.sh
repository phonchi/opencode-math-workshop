#!/usr/bin/env bash
# 在原生 Windows Git Bash 執行：每輪建一個乾淨學生專案，依教材順序跑新版 prompt（opencode run --auto，github-copilot/auto）。
set -u
STARTER=/c/Users/User/AppData/Local/Temp/ai-math-lab-v2
OUT="$1"; RUNS="${2:-1 2}"
BASE=https://phonchi.github.io/opencode-math-workshop/assets/data
L1='data/shops_daily.csv 每一列是某家分店某一天的營業紀錄，匯出時漏了店別。
請用 k-means 分群（先拿掉標準差為 0 的欄位，再標準化；k = 2 到 12，random_state=0、n_init=10）。
不要讀任何店別檔。用三個不看店別的指標比較：silhouette、Calinski-Harabasz、Davies-Bouldin，
並印出每個 k 的各群筆數。程式存成 lab1_cluster.py，圖存到 figs/lab1_k_selection.png。

分別回答：
A. 店型手冊（相近的店可以合併）適合幾群？
B. 客訴回查（不同店不能混在一起）適合幾群？
列出你替我做的每個決定（前處理、準則、門檻、丟掉的欄位）。'
L1C='data/shops_daily_store.csv 是店別紀錄。用它檢查你剛才建議的群數：算 ARI，並列出每一群包含各家店幾天。不要改你剛才的建議。'
L2A='data/orders_complaint.csv 是和 data/orders.csv 同順序的客訴標籤，只能用來檢查。
我的主張：標準化後保留 4 個主成分就夠做客訴預警；如果它的 AUC 比 5 個低超過 0.02，我就撤回。
請比較保留 3、4、5 個主成分時辨識客訴的 AUC：分類器用 logistic 迴歸，用 5 折交叉驗證，
標準化和 PCA 只能用訓練的那幾份資料來算。印出每種的累積變異和 AUC，程式存成 lab2_auc.py。
不要替我改主張。列出你替我做的每個決定（前處理、準則、門檻、丟掉的欄位）。'
L2H="用 numpy 的 eigh 手刻 PCA，存成 lab2_pca.py：
讀 data/orders.csv，每欄先除以標準差、不要減平均（中心化留給 PCA 自己做），取前 4 個主成分，
用 sklearn 的 PCA(n_components=4, svd_solver='full') 當對照組。
再寫幾項檢查驗證手刻的結果，每項印出實際數值、門檻和 PASS/FAIL，用 uv run python 跑一次。
列出你替我做的每個決定（前處理、準則、門檻、丟掉的欄位）。"
L2B='請在 lab2_pca.py 加一個 bug 參數，可選：
none、ratio_topk（比例分母只用前 4 個特徵值的和）、denom_n（變異數分母用 n，不是 n-1）、
no_center（算共變異數矩陣時不中心化）、rows（主成分取錯方向：取矩陣的前 4 列，不是前 4 個特徵向量）。

每一種 bug 都跑一次你原本那組檢查，做成「檢查 × 錯誤」表，
每格印出實際數值與 PASS/FAIL。

規則：不准修 bug、不准新增或修改檢查、不准改門檻，表做好就停下來。'
L3='不要用 case_no 當特徵。用 data/loans.csv 訓練 logistic 迴歸，再用 data/loans_new_batch.csv 檢查。
我優先避免漏掉逾期，每 300 筆最多寄 40 封提醒。
請列出門檻 0.5、0.3、0.2、0.1、0.05 在新一批的提醒數、抓到、漏掉、白提醒，不要替我選。
列出你替我做的每個決定（前處理、準則、門檻、丟掉的欄位）。'
step(){ # name, extra flags, prompt
  local name=$1 flags=$2 prompt=$3 t0=$(date +%s)
  echo "### $name start $(date +%T)" | tee -a "$OUT/progress.log"
  local try rc
  for try in 1 2 3; do  # 新資料夾第一次啟動時 Copilot 模型清單可能還沒載入，Auto 會回 Model unavailable
    opencode run --auto -m github-copilot/auto $flags "$prompt" > "$O/$name.log" 2>&1 </dev/null
    rc=$?
    grep -q "Model unavailable" "$O/$name.log" || break
    echo "### $name retry $try (Model unavailable)" | tee -a "$OUT/progress.log"; sleep 5
  done
  local t1=$(date +%s)
  echo "### $name rc=$rc seconds=$((t1-t0))" | tee -a "$OUT/progress.log"
  if grep -qiE "Free usage exceeded|quota|rate limit" "$O/$name.log"; then echo "### FATAL quota in $name" | tee -a "$OUT/progress.log"; exit 3; fi
}
# 接續：沿用 run1 專案，從 lab2-hand 開始
r=1; P=/c/Users/User/AppData/Local/Temp/ai-math-lab-copilot-run$r; O="$OUT/run-$r"; cd "$P"
step lab2-hand "" "$L2H"
step lab2-bugs "-c" "$L2B"
cp "$STARTER"/data/loans_new_batch.csv data/
step lab3 "" "$L3"
cp -r "$P"/*.py "$P"/figs "$O"/ 2>/dev/null
echo "### all done $(date +%T)" | tee -a "$OUT/progress.log"
