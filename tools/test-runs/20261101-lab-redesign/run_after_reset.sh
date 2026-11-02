#!/bin/bash
# 等額度恢復後逐次補跑。先探測，還被擋就每 15 分鐘再試（探測本身只有一句話）。
cd "$(dirname "$0")"
OC=~/.cache/oc-lab-redesign/home/.opencode/bin/opencode
probe(){ m=$1; d=$(mktemp -d "$PWD/.probe.XXXX"); for k in home data config state cache p; do mkdir -p $d/$k; done
  ( cd $d/p; HOME=$d/home XDG_DATA_HOME=$d/data XDG_CONFIG_HOME=$d/config XDG_STATE_HOME=$d/state XDG_CACHE_HOME=$d/cache timeout -s KILL 40 $OC run --print-logs --model opencode/$m "Reply exactly OK" </dev/null >$d/out 2>$d/err ); r=1; grep -q 'Free usage limit' $d/err || { sed 's/\x1b\[[0-9;]*m//g' $d/out | grep -q 'OK' && r=0; }; rm -rf $d; return $r; }
until [ "$(date +%H%M)" -ge "$1" ] && [ "$(date +%H)" -lt 20 ]; do sleep 60; done
for m in beam-free big-pickle; do until probe $m; do echo "probe $m blocked $(date +%H:%M)"; sleep 900; done; echo "probe $m ok $(date +%H:%M)"; done
python3 interactive_run.py cases-exp-beam.json phase4-beam-free --model opencode/beam-free --runs 3 --jobs 1 --timeout 420 > phase4-beam-free.log 2>&1 &
python3 interactive_run.py cases-exp-pickle.json phase4-big-pickle --model opencode/big-pickle --runs 3 --jobs 1 --timeout 600 > phase4-big-pickle.log 2>&1 &
wait; echo BATCHES_DONE
