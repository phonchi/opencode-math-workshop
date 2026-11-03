#!/bin/bash
# big-pickle 額度恢復後跑 phase11（學生寫卡後的 prompt）。結束後印 PICKLE11_DONE。
# 額度有限，依教材最需要的順序跑；interactive_run 遇到額度上限會跳過其餘次數。
cd "$(dirname "$0")"
OC=~/.cache/oc-lab-redesign/home/.opencode/bin/opencode
probe(){ d=$(mktemp -d "$PWD/.probe.XXXX"); for k in home data config state cache p; do mkdir -p $d/$k; done
  ( cd $d/p; HOME=$d/home XDG_DATA_HOME=$d/data XDG_CONFIG_HOME=$d/config XDG_STATE_HOME=$d/state XDG_CACHE_HOME=$d/cache timeout -s KILL 60 $OC run --print-logs --model opencode/big-pickle "Reply exactly OK" </dev/null >$d/out 2>$d/err ) 2>/dev/null; r=1; grep -q 'Free usage limit' $d/err || { sed 's/\x1b\[[0-9;]*m//g' $d/out | grep -q 'OK' && r=0; }; rm -rf $d; return $r; }
# 11-03 實測 08:07 仍被擋、09:07 恢復，先等到重置後再探測。
until [ "$(date +%m%d%H%M)" -ge 11040910 ]; do sleep 300; done
until probe; do echo "blocked $(date '+%m/%d %H:%M')"; sleep 3600; done; echo "ok $(date '+%m/%d %H:%M')"
run(){ python3 interactive_run.py "$1" phase11-big-pickle --only "$2" --model opencode/big-pickle --runs 3 --jobs 1 --timeout 600 >> phase11-big-pickle.log 2>&1; }
run cases-phase11.json stop-rule
run cases-phase11.json lab3-decision
run cases-phase11b.json lab1-goal-open
run cases-phase11.json lab2-accept
echo PICKLE11_DONE $(date '+%m/%d %H:%M')
