"""Copy complete bounded Windows evidence back to the workshop; omit environments/caches."""
from pathlib import Path
import hashlib,json,shutil
src=Path('/mnt/c/Users/User/Documents/ai-math-refresh-20260912')
out=Path(__file__).resolve().parent
shutil.copytree(src/'evidence',out/'evidence',dirs_exist_ok=True)
for project in src.glob('agent-*'):
 if project.is_dir():shutil.copytree(project,out/'agent-projects'/project.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.venv','__pycache__','node_modules'))
summary={}
for f in (out/'evidence').glob('*agent.log'):
 b=f.read_bytes();text=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8-sig',errors='replace')
 (out/'evidence'/f.name.replace('.log','.utf8.log')).write_text(text,encoding='utf-8')
 events=[]
 for line in text.splitlines():
  try:events.append(json.loads(line))
  except json.JSONDecodeError:pass
 summary[f.name]={'sessions':sorted({e.get('sessionID') for e in events if e.get('sessionID')}),'tool_calls':[{'tool':e['part']['tool'],'status':e['part']['state']['status'],'input':e['part']['state'].get('input'),'exit':e['part']['state'].get('metadata',{}).get('exit')} for e in events if e.get('type')=='tool_use'],'reported_cost':sum(e['part'].get('cost',0) for e in events if e.get('type')=='step_finish'),'last_event':events[-1]['type'] if events else None}
(out/'agent-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
logs=[f for f in (out/'evidence').rglob('*.log') if not f.name.endswith('.utf8.log')]
with (out/'run.log').open('w',encoding='utf-8') as merged:
 for f in sorted(logs):
  b=f.read_bytes();text=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8-sig',errors='replace')
  merged.write('\n### '+str(f.relative_to(out))+'\n'+text+'\n')
files={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and f.name!='sha256.json'}
(out/'sha256.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print('Collected Windows projects, logs and hashes:',out)
