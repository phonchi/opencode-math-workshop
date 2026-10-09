"""Check preserved teaching content against the recorded pre-change baseline."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(); self.headings=[]; self.checks=[]; self.pre=[]; self.outputs=[]
        self.depth=0; self.text=[]; self.output_depth=None; self.stack=[]; self.output_text=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='h2':self.headings.append(attrs.get('id'))
        if tag=='input' and attrs.get('type')=='checkbox':self.checks.append(attrs.get('id'))
        if tag=='pre':self.depth+=1;self.text=[]
        if tag=='div':
            self.stack.append(tag)
            if attrs.get('class')=='o':self.output_depth=len(self.stack);self.output_text=[]
    def handle_data(self, text):
        if self.depth:self.text.append(text)
        if self.output_depth is not None:self.output_text.append(text)
    def handle_endtag(self, tag):
        if tag=='pre':self.pre.append(''.join(self.text));self.depth-=1
        if tag=='div':
            if self.output_depth==len(self.stack):self.outputs.append(''.join(self.output_text));self.output_depth=None
            if self.stack:self.stack.pop()

def formulas(text):
    return re.findall(r'\$\$.*?\$\$|(?<!\$)\$(?!\$)[^\n$]*\$',text,re.S)

def old(path):
    return subprocess.check_output(['git','show',baseline['head']+':'+path],cwd=ROOT,text=True)

baseline=json.loads((HERE/'baseline.json').read_text())
checks=[]
for slug, before in baseline['pages'].items():
    current=(ROOT/(slug+'.html')).read_text(); scan=Scan();scan.feed(current)
    assert set(before['headings'])<=set(scan.headings),(slug,'missing heading anchor')
    assert before['checkboxes']==scan.checks,(slug,'changed checklist IDs')
    assert before['pre']==scan.pre,(slug,'changed commands or preformatted outputs')
    source=(ROOT/before['source']).read_text()
    assert before['formulas']==formulas(source),(slug,'changed source formulas')
    prior=Scan();prior.feed(old(before['source']))
    present=Scan();present.feed(source)
    assert prior.outputs==present.outputs,(slug,'changed displayed numerical outputs')
    checks.append({'page':slug,'headings':len(before['headings']),'checkboxes':len(scan.checks),
                   'preformatted_blocks':len(scan.pre),'formulas':len(before['formulas']),
                   'displayed_output_rows':len(prior.outputs),'status':'passed'})
for path in ['tools/pca-explorer.html']:
    assert formulas(old(path))==formulas((ROOT/path).read_text()),(path,'changed formulas')
for path in ['tools/site-navigation.js','reference/lab1_cluster.py','reference/lab2_pca.py','reference/lab3_logistic.py','starter/AGENTS.md']:
    assert old(path)==(ROOT/path).read_text(),(path,'unexpected changes')
# The new example distinguishes centering from rescaling without new software.
values=[2,4,6];mean=sum(values)/len(values);centered=[v-mean for v in values]
assert mean==4 and centered==[-2,0,2] and sum(centered)==0
assert sum(v*v for v in centered)/len(centered)!=1
result={'status':'passed','baseline_head':baseline['head'],'pages':checks,
        'unchanged_navigation_behavior_and_reference_programs':True,
        'new_centering_example':{'values':values,'mean':mean,'centered':centered,'population_variance':8/3,'sample_variance':4}}
(HERE/'preservation-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: original formulas, commands, numerical outputs, heading anchors, checkbox IDs and navigation behavior preserved across 13 pages.')
