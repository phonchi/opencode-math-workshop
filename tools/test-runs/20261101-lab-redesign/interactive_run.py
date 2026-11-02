#!/usr/bin/env python3
"""在獨立 tmux 內以互動 TUI 跑 OpenCode，流程與學生相同：貼 prompt、逐次回應權限要求。
用法：interactive_run.py <cases.json> <輸出資料夾> [--only 案例] [--runs N] [--jobs N]
不操作任何 GUI；每次都是新專案與新 session，資料與使用者的 OpenCode 隔離。"""
import argparse, concurrent.futures as cf, json, os, re, shutil, subprocess as sp, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
ISO = Path.home() / '.cache/oc-lab-redesign'
OC = ISO / 'home/.opencode/bin/opencode'
QUOTA = 'Free usage exceeded'
STOP = threading.Event()
MODEL = None
DENY = re.compile(r'rm\s+-rf|sudo|git\s+push|curl\s|wget\s|ssh\s')
AGENTS = """# AI-Math 工作坊　專案規則

## 語言
一律使用台灣繁體中文回答。程式碼、變數名稱、套件名稱保留英文。

## 執行環境
本專案用 uv 管理環境。執行 Python 一律用：`uv run python <檔案>`
不要用 `python`、`python3`、`pip install`。要加套件用 `uv add <套件>`。

## 圖檔
所有圖存到 `figs/`，用 `savefig()`，不要用 `plt.show()`（無視窗環境無效）。

## 筆記
筆記寫在 `notes/` 底下的 .md 檔，數學式用 $...$ 與 $$...$$。

## 不要做的事
- 不要 git commit 或 git push，除非我明講。
- 不要刪除 `figs/` 或 `notes/` 裡既有的檔案。
"""
def env(base):
    e = dict(os.environ)
    for k, d in dict(HOME='home', XDG_DATA_HOME='data', XDG_CONFIG_HOME='config', XDG_STATE_HOME='state', XDG_CACHE_HOME='cache').items():
        p = base / d; p.mkdir(parents=True, exist_ok=True); e[k] = str(p)
    real = Path.home()
    e['UV_CACHE_DIR'] = str(real / '.cache/uv'); e['UV_PYTHON_INSTALL_DIR'] = str(real / '.local/share/uv/python')
    e['TERM'] = 'xterm-256color'
    return e
def tm(*a, **k):
    return sp.run(['tmux', '-L', 'oclab', *a], capture_output=True, text=True, **k)
def screen(s, hist=False):
    return tm('capture-pane', '-p', '-J', *(['-S', '-6000'] if hist else []), '-t', s).stdout
def paste(s, text):
    b = 'b' + s; tm('set-buffer', '-b', b, '--', text); tm('paste-buffer', '-p', '-b', b, '-t', s); tm('delete-buffer', '-b', b)
def run_turn(s, text, log, timeout):
    paste(s, text); time.sleep(1.5); tm('send-keys', '-t', s, 'Enter')
    t0 = time.time(); last = ''; stable = 0; seen_busy = False; perms = 0
    while time.time() - t0 < timeout:
        time.sleep(2); sc = screen(s)
        if QUOTA in sc: return dict(status='quota', secs=round(time.time() - t0), perms=perms)
        if 'Allow once' in sc:
            bad = DENY.search(sc); perms += 1
            log.append({'t': round(time.time() - t0), 'permission': 'reject' if bad else 'allow_once', 'screen': sc[-1500:]})
            if bad: tm('send-keys', '-t', s, 'Right'); time.sleep(.3); tm('send-keys', '-t', s, 'Right'); time.sleep(.3)
            tm('send-keys', '-t', s, 'Enter'); time.sleep(2); stable = 0; seen_busy = True; continue
        busy = 'esc interrupt' in sc or 'esc again' in sc
        seen_busy = seen_busy or busy
        stable = stable + 1 if (sc == last and not busy) else 0
        last = sc
        if seen_busy and not busy and stable >= 5: return dict(status='idle', secs=round(time.time() - t0), perms=perms)
        if not seen_busy and stable >= 30: return dict(status='never_busy', secs=round(time.time() - t0), perms=perms)
    return dict(status='timeout', secs=round(time.time() - t0), perms=perms)
def one(case, n, out, timeout):
    name = f"{case['id']}-{n}"; d = out / case['id'] / f'run-{n}'
    if (d / 'result.json').exists(): return name, 'skip'
    if STOP.is_set(): return name, 'skip-quota'
    shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    base = ISO / 'runs' / out.name / name; shutil.rmtree(base, ignore_errors=True); base.mkdir(parents=True)
    proj = base / 'project'; proj.mkdir(); e = env(base)
    for f in ['pyproject.toml', 'uv.lock', 'opencode.json']: shutil.copy(ROOT / 'starter' / f, proj / f)
    (proj / 'AGENTS.md').write_text(AGENTS + case.get('agents_extra', ''), encoding='utf-8'); (proj / 'notes').mkdir(); (proj / 'figs').mkdir()
    sp.run(['uv', 'sync', '--quiet'], cwd=proj, env=e, capture_output=True)
    envargs = [x for k in ['HOME','XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_STATE_HOME','XDG_CACHE_HOME','UV_CACHE_DIR','UV_PYTHON_INSTALL_DIR','TERM'] for x in ('-e', f'{k}={e[k]}')]
    s = 'lab' + out.name.replace('.', '_') + '-' + name.replace('.', '_')
    tm('kill-session', '-t', s)
    tm('new-session', '-d', '-s', s, '-x', '120', '-y', '40', '-c', str(proj), *envargs, str(OC), *(['--model', MODEL] if MODEL else []))
    time.sleep(10); log = []; res = []
    try:
        for i, turn in enumerate(case['turns']):
            text = turn['text'] if isinstance(turn, dict) else turn
            if isinstance(turn, dict) and turn.get('tab'):
                tm('send-keys', '-t', s, 'Tab'); time.sleep(1.5)
            r = run_turn(s, text, log, timeout); r['turn'] = i
            r['agent_shown'] = 'Plan' if re.search(r'Plan\s+·', screen(s)) else 'Build' if re.search(r'Build\s+·', screen(s)) else '?'
            res.append(r)
            if r['status'] == 'quota': STOP.set(); break
            (d / f'screen-turn{i}.txt').write_text(screen(s, True), encoding='utf-8')
    finally:
        tm('kill-session', '-t', s)
    ls = sp.run([str(OC), 'session', 'list', '--format', 'json'], cwd=proj, env=e, capture_output=True, text=True).stdout
    sid = None
    try: sid = json.loads(ls)[0]['id']
    except Exception: pass
    if sid:
        with open(d / 'session.raw', 'wb') as fh: sp.run([str(OC), 'export', sid], cwd=proj, env=e, stdout=fh, stderr=sp.DEVNULL)
        x = (d / 'session.raw').read_text(encoding='utf-8'); (d / 'session.raw').unlink()
        (d / 'session.json').write_text(x[x.find('{'):], encoding='utf-8')
    (d / 'permissions.json').write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding='utf-8')
    (d / 'project').mkdir()
    for f in proj.rglob('*'):
        if f.is_file() and '.venv' not in f.parts and f.name != 'uv.lock' and f.stat().st_size < 200000:
            t = d / 'project' / f.relative_to(proj); t.parent.mkdir(parents=True, exist_ok=True); shutil.copy(f, t)
    (d / 'result.json').write_text(json.dumps(dict(case=case['id'], run=n, session=sid, turns=res, version=sp.run([str(OC), '--version'], capture_output=True, text=True).stdout.strip(), mode='interactive-tui', model=MODEL or 'config-default', prompts=case['turns'], when=time.strftime('%Y-%m-%d %H:%M:%S')), ensure_ascii=False, indent=1), encoding='utf-8')
    shutil.rmtree(base, ignore_errors=True)
    return name, [r['status'] for r in res]
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cases'); ap.add_argument('out'); ap.add_argument('--only'); ap.add_argument('--model'); ap.add_argument('--runs', type=int, default=5); ap.add_argument('--jobs', type=int, default=3); ap.add_argument('--timeout', type=int, default=420)
    a = ap.parse_args(); MODEL = a.model; out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    cases = [c for c in json.load(open(a.cases, encoding='utf-8')) if not a.only or c['id'] == a.only]
    jobs = [(c, n) for c in cases for n in range(1, a.runs + 1)]
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for f in cf.as_completed([ex.submit(one, c, n, out, a.timeout) for c, n in jobs]):
            print(f.result(), flush=True)
