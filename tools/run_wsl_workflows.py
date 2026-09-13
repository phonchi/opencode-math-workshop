"""Bounded additional WSL checks; preserve all earlier attempts and their failures."""
import argparse,html,json,os,re,shutil,signal,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'tools/test-runs/20260912-workshop-refresh/wsl'
PROJECT=BASE/'project';OUT=BASE/'workflows';RUNTIME=BASE/'runtime'
OUT.mkdir(exist_ok=True)
env={k:v for k,v in os.environ.items() if not k.endswith(('API_KEY','ACCESS_TOKEN','AUTH_TOKEN')) and not k.startswith('OPENCODE_')}
env.update({'XDG_CONFIG_HOME':str(RUNTIME/'config'),'XDG_DATA_HOME':str(RUNTIME/'data'),'XDG_CACHE_HOME':str(RUNTIME/'cache'),'XDG_STATE_HOME':str(RUNTIME/'state'),'OPENCODE_CONFIG_DIR':str(RUNTIME/'opencode'),'OPENCODE_DISABLE_CLAUDE_CODE':'true','OPENCODE_DISABLE_AUTOUPDATE':'true','OPENCODE_DISABLE_LSP_DOWNLOAD':'true','OPENCODE_CONFIG_CONTENT':json.dumps({'enabled_providers':['opencode'],'share':'disabled'}),'OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','PYTHONUTF8':'1','MPLBACKEND':'Agg','MPLCONFIGDIR':str(RUNTIME/'matplotlib')})
def run(name,command,timeout=600):
 path=OUT/(name+'.log')
 if path.exists():raise RuntimeError('Refuse overwrite existing '+str(path))
 print('START',name,flush=True);started=time.monotonic()
 with path.open('w') as f:
  p=subprocess.Popen(command,cwd=PROJECT,env=env,stdout=f,stderr=subprocess.STDOUT,text=True,start_new_session=True)
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   code=124
 result={'name':name,'exit':code,'seconds':round(time.monotonic()-started,2),'command':command}
 (OUT/(name+'.result.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
 with (OUT/'run.log').open('a') as f:f.write('\n## '+name+'\n'+json.dumps(command,ensure_ascii=False)+'\n'+path.read_text()+'\nEXIT='+str(code)+'\n')
 print('END',name,code,flush=True)
 if code:raise SystemExit(code)
 return path.read_text()
def call(name,prompt,session=None):
 (OUT/(name+'.prompt.txt')).write_text(prompt)
 cmd=['opencode','run','--dir',str(PROJECT),'--auto','--model','opencode/big-pickle','--format','json']
 if session:cmd+=['--session',session]
 return run(name,cmd+[prompt])
def main():
 phase=argparse.ArgumentParser();phase.add_argument('phase',choices=['correction','workflow','fresh','ratio-fix']);phase=phase.parse_args().phase
 if phase=='correction':
  source=(ROOT/'tools/body_lab3-notes.html').read_text();blocks=[html.unescape(re.sub('<[^>]+>','',b)) for b in re.findall(r'<pre[^>]*>.*?</pre>',source,re.S)]
  prompt='保留原先 lab3_logreg.py，不要修改或執行它。另建本輪指定 lab3_logistic.py，以下是唯一範圍。\n'+blocks[0]+'\n接著本輪只補以下梯度檢查，其他項目不要做：\n'+blocks[1]+'\n最後保存 notes/logistic.md，包含loss/gradient推導、資料定義、w0與這次實際差分表格和誤差觀察。不要訓練、不切資料、不更換演算法、不生成新資料。寫完筆記就停止。'
  call('lab3-correction',prompt,'ses_f69b011f1ffeMY9SZe6vgAaRA9')
  assert (PROJECT/'lab3_logistic.py').exists() and (PROJECT/'notes/logistic.md').exists()
  run('lab3-independent-execution',['uv','run','python','lab3_logistic.py'])
 elif phase=='workflow':
  source=(ROOT/'content/mcp-skills.md').read_text()
  for b in re.findall(r'```markdown\n(.*?)\n```',source,re.S):
   if b.startswith('---\nname: math-notes'):p=PROJECT/'.opencode/skills/math-notes/SKILL.md'
   elif b.startswith('---\ndescription: 檢查數學'):p=PROJECT/'.opencode/agents/math-reviewer.md'
   else:continue
   p.parent.mkdir(parents=True,exist_ok=True);p.write_text(b+'\n')
  run('debug-skill',['opencode','debug','skill']);run('debug-reviewer',['opencode','debug','agent','math-reviewer'])
  # Freshly captured true outputs, no invented execution records.
  for name in ['lab1_cluster.py','lab2_pca.py']:
   output=run(name.removesuffix('.py')+'-output',['uv','run','python',name])
   (PROJECT/'notes'/(name.removesuffix('.py')+'-output.log')).write_text('Command: uv run python '+name+'\n'+output)
  call('combined-workflow','請只根據目前專案實際檔案與notes中的執行輸出依序完成，沒有的資料標明缺少，不重跑實驗：\n1. 用 skill 工具載入 math-notes，讀lab1_cluster.py與notes/lab1_cluster-output.log，整理notes/lab1-review.md。\n2. 委派 @math-reviewer 唯讀檢查 lab2_pca.py 的手刻PCA與notes/lab2_pca-output.log，不修改不執行。\n3. 委派 @explore 唯讀檢查 lab1_cluster.py、lab2_pca.py、lab3_logistic.py 的隨機性，回報檔名行號及用途；不修改不執行。\n4. 保存notes/progress.md：目標限制、成果相對路徑、實際指令與結果、缺少/未確認部分、下一步。全部完成即停止，不另外實驗。')
  assert (PROJECT/'notes/progress.md').exists()
 elif phase=='ratio-fix':
  shutil.copy2(PROJECT/'lab2_pca.py',OUT/'original-lab2-ratio.py')
  rows=[json.loads(line) for line in (BASE/'lessons/lab2.jsonl').read_text().splitlines() if line.startswith('{')]
  session=next(x['sessionID'] for x in rows if 'sessionID' in x)
  call('lab2-ratio-fix','只修正 lab2_pca.py 中已發現的解釋變異比例錯誤，不修改其他檔案，不更換PCA主演算法。手刻比例分母須為全部64個特徵值總和，sklearn對照直接取pca.explained_variance_ratio_（沿用你程式原有PCA物件名稱），不可兩側都自行重算分母。印出總體變異與前10維累計比例，累計應約0.738，不得恆為1。只改lab2，實際 uv run python lab2_pca.py 執行，完成即停止。',session)
 else:call('fresh-session' ,'請先讀 AGENTS.md 與 notes/progress.md，再查看其中提到的相關檔案。不要修改或執行；說明目前做到哪裡、哪一件事還不能確定、接下來的第一步。只根據實際存在的檔案。')
if __name__=='__main__':main()
