#!/bin/bash
# 用課前準備的步驟走一次：starter 設定、/connect、opencode run、備案切換。key 一律遮蔽。
cd "$(dirname "$0")"; ROOT=$(cd ../../../..; pwd)
. ~/.gemini-workshop-key; G="$GEMINI_API_KEY"; unset GEMINI_API_KEY
. ~/.nvidia-workshop-key; N="$NVIDIA_API_KEY"; unset NVIDIA_API_KEY
OC=~/.cache/oc-lab-redesign/home/.opencode/bin/opencode; T="tmux -L occonn"
mask(){ sed -e "s/$G/<KEY>/g" -e "s/$N/<KEY>/g"; }
fresh(){ B=$HOME/.cache/oc-lab-redesign/flow-$1; rm -rf $B; mkdir -p $B/{home,data,config,state,cache,p/notes,p/figs}; cp $ROOT/starter/{opencode.json,AGENTS.md,pyproject.toml,uv.lock} $B/p/; (cd $B/p; UV_CACHE_DIR=$HOME/.cache/uv UV_PYTHON_INSTALL_DIR=$HOME/.local/share/uv/python uv sync --quiet); }
envs(){ echo HOME=$B/home XDG_DATA_HOME=$B/data XDG_CONFIG_HOME=$B/config XDG_STATE_HOME=$B/state XDG_CACHE_HOME=$B/cache UV_CACHE_DIR=$HOME/.cache/uv UV_PYTHON_INSTALL_DIR=$HOME/.local/share/uv/python TERM=xterm-256color; }
start(){ S=$1; a=(); for e in $(envs); do a+=(-e "$e"); done; $T kill-session -t $S 2>/dev/null; $T new-session -d -s $S -x 120 -y 40 -c $B/p "${a[@]}" $OC; sleep 10; }
show(){ echo "--- $1"; $T capture-pane -p -J -t $S | mask | grep -v '^\s*$' | cut -c1-112 | tail -${2:-8}; }
connect(){ $T send-keys -t $S '/connect'; sleep 1.5; $T send-keys -t $S Enter; sleep 3; $T send-keys -t $S "$1"; sleep 1.5; show "搜尋 $1" 6; $T send-keys -t $S Enter; sleep 3; show "選 $1 後" 6; $T set-buffer -b kb -- "$2"; $T paste-buffer -p -b kb -t $S; $T delete-buffer -b kb; sleep 1.5; $T send-keys -t $S Enter; sleep 5; show "貼 key 後" 10; }
ask(){ t0=$(date +%s); $T send-keys -t $S "$1"; sleep 1; $T send-keys -t $S Enter; sleep 3; while $T capture-pane -p -t $S | grep -q 'esc interrupt\|esc again'; do sleep 3; [ $(( $(date +%s)-t0 )) -gt 240 ] && { echo TIMEOUT; break; }; done; echo "耗時 $(( $(date +%s)-t0 )) 秒"; show "回覆" 12; }
logs(){ grep -h 'message=stream' $B/data/opencode/log/*.log | grep -o 'providerID=[^ ]* modelID=[^ ]*\|small=[a-z]*' | paste - - | sort | uniq -c; grep -hE 'level=ERROR' $B/data/opencode/log/*.log | cut -c1-200 | mask | tail -3; }
pick(){ $T send-keys -t $S "$1"; sleep 1.5; $T send-keys -t $S Enter; sleep 3; show "選模型後" 8; if $T capture-pane -p -t $S | grep -qE 'Select variant|Default'; then $T send-keys -t $S Enter; sleep 2; show "variant 按 Enter 後" 5; fi; }
echo "===== A. 預設畫面與 Gemini 備案"; fresh a; start fa; show "開機（應為 Big Pickle）" 5; connect Google "$G"; pick 'Flash Lite'
ask '請用繁體中文回覆：1+1 等於多少？只回答數字'
$T kill-session -t $S; start fa; show "重開 OpenCode 後的模型" 5; $T kill-session -t $S
echo '--- run --model Gemini'; (cd $B/p; env $(envs) timeout 150 $OC run --model google/gemini-3.5-flash-lite "用一句話說明什麼是主成分分析" 2>&1 | mask | sed 's/\x1b\[[0-9;]*m//g' | tail -3 | cut -c1-200)
echo '--- log'; logs
echo "===== B. NVIDIA 備案"; fresh b; start fb; connect NVIDIA "$N"; pick 'GLM-5.3-Flash'
ask '不要執行任何程式，直接回答：sklearn 的 digits 資料集，64 個像素中有哪幾個在全部 1797 張圖裡都是 0？'
$T kill-session -t $S; echo '--- log'; logs
rm -rf $HOME/.cache/oc-lab-redesign/flow-a $HOME/.cache/oc-lab-redesign/flow-b; echo FLOW_DONE
