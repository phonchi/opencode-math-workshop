#!/bin/bash
# 第二批補跑：每小時探測，通過後先跑 Beam（E2 對照、E3），再跑 big-pickle（Lab 3、E1）。
cd "$(dirname "$0")"
OC=~/.cache/oc-lab-redesign/home/.opencode/bin/opencode
probe(){ m=$1; d=$(mktemp -d "$PWD/.probe.XXXX"); for k in home data config state cache p; do mkdir -p $d/$k; done
  ( cd $d/p; HOME=$d/home XDG_DATA_HOME=$d/data XDG_CONFIG_HOME=$d/config XDG_STATE_HOME=$d/state XDG_CACHE_HOME=$d/cache timeout -s KILL 40 $OC run --print-logs --model opencode/$m "Reply exactly OK" </dev/null >$d/out 2>$d/err ) 2>/dev/null; r=1; grep -q 'Free usage limit' $d/err || { sed 's/\x1b\[[0-9;]*m//g' $d/out | grep -q 'OK' && r=0; }; rm -rf $d; return $r; }
until probe beam-free; do echo "probe beam-free blocked $(date '+%m/%d %H:%M')"; sleep 3600; done; echo "probe beam-free ok $(date '+%m/%d %H:%M')"
python3 interactive_run.py cases-exp2-beam.json phase5-beam-free --model opencode/beam-free --runs 3 --jobs 1 --timeout 420 > phase5-beam-free.log 2>&1
echo BEAM_DONE $(date '+%m/%d %H:%M')
until probe big-pickle; do echo "probe big-pickle blocked $(date '+%m/%d %H:%M')"; sleep 3600; done; echo "probe big-pickle ok $(date '+%m/%d %H:%M')"
python3 interactive_run.py cases-exp2-pickle.json phase5-big-pickle --model opencode/big-pickle --runs 3 --jobs 1 --timeout 600 > phase5-big-pickle.log 2>&1
echo BATCHES_DONE $(date '+%m/%d %H:%M')
