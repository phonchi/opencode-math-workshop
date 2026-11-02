#!/bin/bash
# Gemini 每日額度重置後補跑 phase11 尚未完成的案例（已完成者會跳過）。
cd "$(dirname "$0")"
. ~/.gemini-workshop-key
until [ "$(curl -s -m 40 -o /dev/null -w '%{http_code}' -H "x-goog-api-key: $GEMINI_API_KEY" -H 'Content-Type: application/json' -d '{"contents":[{"parts":[{"text":"ok"}]}]}' https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent)" = 200 ]; do echo "blocked $(date '+%m/%d %H:%M')"; sleep 1800; done
echo "ok $(date '+%m/%d %H:%M')"
GOOGLE_GENERATIVE_AI_API_KEY="$GEMINI_API_KEY" python3 interactive_run.py cases-phase11.json phase11-gemini --model google/gemini-3.5-flash-lite --runs 3 --jobs 1 --timeout 600 > phase11-gemini-resume.log 2>&1
echo GEMINI_DONE $(date '+%m/%d %H:%M')
