#!/usr/bin/env python3
"""印出一輪互動實跑的摘要：狀態、工具、回答、程式與執行輸出。"""
import json,sys,re
from pathlib import Path
r=Path(sys.argv[1]); full=len(sys.argv)>2
d=json.load(open(r/'result.json',encoding='utf-8'))
print('#####',r,d.get('model'),[(t['status'],t['secs'],t['perms']) for t in d['turns']])
s=json.load(open(r/'session.json',encoding='utf-8'))
for m in s['messages']:
    if m['info']['role']!='assistant': continue
    for p in m['parts']:
        if p.get('type')=='tool':
            st=p.get('state',{}); i=st.get('input',{}) ; 
            if p['tool']=='bash':
                print('$',str(i.get('command'))[:160]); print(str(st.get('output',''))[:1800 if full else 900])
            else: print('['+p['tool']+']',str(i.get('filePath') or i.get('query') or '')[:100])
        elif p.get('type')=='text' and p['text'].strip():
            print('>>',p['text'][:1500])
print('files',[str(f.relative_to(r/'project')) for f in (r/'project').rglob('*') if f.is_file() and f.suffix in('.py','.md') and f.name!='AGENTS.md'])
