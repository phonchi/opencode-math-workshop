#!/usr/bin/env python3
"""Lab 3 模糊 prompt 的逐次摘要：實際程式中的正則化、切分、數值檢查、最後回覆。"""
import json,re,sys
from pathlib import Path
for r in map(Path,sys.argv[1:]):
    d=json.load(open(r/'result.json'));s=json.load(open(r/'session.json'))
    tools=[p['tool'] for m in s['messages'] for p in m['parts'] if p.get('type')=='tool']
    print('#####',r,[(t['status'],t['secs'],t['perms']) for t in d['turns']],'tools',len(tools))
    last=[p['text'] for m in s['messages'] if m['info']['role']=='assistant' for p in m['parts'] if p.get('type')=='text' and p['text'].strip()]
    print('FINAL:',last[-1][:1500] if last else None)
    for f in (r/'project').rglob('*'):
        if f.is_file() and '.venv' not in f.parts and f.suffix in('.py','.md') and f.name!='AGENTS.md':
            t=f.read_text(errors='ignore');print('--',f.relative_to(r/'project'),len(t))
            for pat in ['LogisticRegression\\(.*','penalty.*','\\bC=.*','train_test_split.*','check_grad|approx_fprime|finite|中央差分|central|numerical.grad','/ *16','不存在|可分|發散']:
                hits=[l.strip()[:110] for l in t.splitlines() if re.search(pat,l)][:3]
                if hits: print('  ',pat,'=>',hits)
