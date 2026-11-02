#!/bin/bash
# big-pickle 額度恢復後補跑 phase10（每小時探測）。結束後印 PICKLE_DONE。
cd "$(dirname "$0")"
OC=~/.cache/oc-lab-redesign/home/.opencode/bin/opencode
probe(){ d=$(mktemp -d "$PWD/.probe.XXXX"); for k in home data config state cache p; do mkdir -p $d/$k; done
  ( cd $d/p; HOME=$d/home XDG_DATA_HOME=$d/data XDG_CONFIG_HOME=$d/config XDG_STATE_HOME=$d/state XDG_CACHE_HOME=$d/cache timeout -s KILL 60 $OC run --print-logs --model opencode/big-pickle "Reply exactly OK" </dev/null >$d/out 2>$d/err ) 2>/dev/null; r=1; grep -q 'Free usage limit' $d/err || { sed 's/\x1b\[[0-9;]*m//g' $d/out | grep -q 'OK' && r=0; }; rm -rf $d; return $r; }
until probe; do echo "blocked $(date '+%m/%d %H:%M')"; sleep 3600; done; echo "ok $(date '+%m/%d %H:%M')"
python3 interactive_run.py cases-new.json phase10-big-pickle --model opencode/big-pickle --runs 3 --jobs 1 --timeout 600 > phase10-big-pickle.log 2>&1
echo PICKLE_DONE $(date '+%m/%d %H:%M')
