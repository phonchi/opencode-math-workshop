"""Run the local-models chapter's final agent task with several Ollama models through OpenCode.

For each model: build a 32k-context variant with a Modelfile (as the chapter teaches), copy the
workshop starter project, register the model as an Ollama provider, run the chapter's task text
with `opencode run` under a clean HOME (no instructor-specific global config), then check the
result independently: does local_hello.py exist, does `uv run python local_hello.py` print the
ten squares, and what did the agent claim.

Deviation from the chapter: `opencode run` is non-interactive and nobody can answer an "ask"
prompt, so the test copies use least-privilege rules instead of "ask": bash may run only
`uv run python local_hello.py`, edits stay inside the throwaway project copy, and web access
and other directories are denied.

Usage: python3 run_final_task.py [runs_per_model]
"""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MODELS = {  # local name -> base model pulled from the Ollama library
    'qwen3.5-9b-32k': 'qwen3.5:9b',
    'gemma4-e4b-32k': 'gemma4:e4b',
    'qwen3.5-4b-32k': 'qwen3.5:4b',
}
CTX = 32768
TASK = ('請讀 AGENTS.md，再建立 local_hello.py，內容是印出 1 到 10 的平方。\n'
        '用 uv run python local_hello.py 實際執行。\n'
        '完成後回報你寫入的檔案與執行指令；沒有成功的部分請明說。')
SQUARES = ['1', '4', '9', '16', '25', '36', '49', '64', '81', '100']


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def clean_env(home):
    env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'),
               XDG_DATA_HOME=str(home / '.local/share'), XDG_CACHE_HOME=str(home / '.cache'),
               XDG_STATE_HOME=str(home / '.local/state'))
    # uv keeps its own cache so the starter environment is not re-downloaded per run
    env['UV_CACHE_DIR'] = str(Path(os.environ['HOME']) / '.cache/uv')
    return env


def prepare_model(name, base, log):
    modelfile = HERE / 'modelfiles' / name
    modelfile.parent.mkdir(exist_ok=True)
    modelfile.write_text(f'FROM {base}\nPARAMETER num_ctx {CTX}\n')
    r = sh(['ollama', 'create', name, '-f', str(modelfile)])
    log(f'ollama create {name}: rc={r.returncode} {r.stderr.strip()[-200:]}')
    show = sh(['ollama', 'show', base]).stdout
    params = sh(['ollama', 'show', '--parameters', name]).stdout
    return {'base': base, 'show': show, 'parameters': params}


def prepare_project(name, run_dir):
    project = run_dir / 'project'
    shutil.copytree(REPO / 'starter', project, ignore=shutil.ignore_patterns('.venv'))
    cfg = json.loads((project / 'opencode.json').read_text())
    cfg['provider']['ollama'] = {
        'npm': '@ai-sdk/openai-compatible', 'name': 'Ollama (local)',
        'options': {'baseURL': 'http://localhost:11434/v1'},
        'models': {name: {'name': name, 'tool_call': True, 'limit': {'context': CTX, 'output': 8192}}}}
    # Least privilege for an unattended run: only the one command the task needs may run; no web,
    # no access outside this throwaway copy. Everything else is denied instead of asked.
    cfg['permission'] = {
        'bash': {'*': 'deny', 'uv run python local_hello.py': 'allow'},
        'edit': 'allow',
        'webfetch': 'deny',
        'external_directory': 'deny',
    }
    (project / 'opencode.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
    return project


def check(project):
    target = project / 'local_hello.py'
    out = {'file_exists': target.is_file(), 'file_text': target.read_text() if target.is_file() else None}
    if target.is_file():
        r = sh(['uv', 'run', 'python', 'local_hello.py'], cwd=project, timeout=600)
        out['run_rc'] = r.returncode
        out['run_stdout'] = r.stdout[-2000:]
        # Accept one number per line ("1 的平方是 1" -> last number) or all numbers in one row.
        per_line = [re.findall(r'\d+', line) for line in r.stdout.splitlines()]
        last_each = [nums[-1] for nums in per_line if nums]
        all_nums = [n for nums in per_line for n in nums]
        out['squares_ok'] = last_each == SQUARES or all_nums == SQUARES
    else:
        out['squares_ok'] = False
    return out


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    logf = (HERE / 'run.log').open('a')

    def log(msg):
        line = time.strftime('%Y-%m-%dT%H:%M:%S ') + msg
        print(line, flush=True)
        logf.write(line + '\n')
        logf.flush()

    log(f'start: {sh(["ollama", "--version"]).stdout.strip()} | opencode {sh(["opencode", "--version"]).stdout.strip()}')
    # One clean HOME shared by all runs: only OpenCode's own caches, no personal config. A fresh
    # HOME per run failed in ~1.5 s with "Unexpected server error" while OpenCode installed its
    # provider package, so the HOME is reused and warmed up once.
    home = HERE / 'opencode-home'
    home.mkdir(exist_ok=True)
    results = []
    for name, base in MODELS.items():
        info = prepare_model(name, base, log)
        (HERE / 'models').mkdir(exist_ok=True)
        (HERE / 'models' / f'{name}.txt').write_text(info['show'] + '\n--- parameters ---\n' + info['parameters'])
        for i in range(1, runs + 1):
            run_dir = HERE / 'runs' / f'{name}-run{i}'
            if run_dir.exists():
                shutil.rmtree(run_dir)
            run_dir.mkdir(parents=True)
            project = prepare_project(name, run_dir)
            t0 = time.time()
            try:
                env = clean_env(home)
                env['PWD'] = str(project)  # OpenCode 1.18.30 locates the project from $PWD, not the real cwd
                r = sh(['opencode', 'run', TASK, '-m', f'ollama/{name}'], cwd=project, env=env, timeout=900,
                       stdin=subprocess.DEVNULL)
                rc, transcript = r.returncode, r.stdout + '\n--- stderr ---\n' + r.stderr
            except subprocess.TimeoutExpired as e:
                rc, transcript = 'timeout', (e.stdout or b'').decode(errors='ignore') if isinstance(e.stdout, bytes) else (e.stdout or '')
            elapsed = round(time.time() - t0, 1)
            (run_dir / 'transcript.txt').write_text(transcript)
            ps = sh(['ollama', 'ps']).stdout
            result = {'model': name, 'base': base, 'run': i, 'opencode_rc': rc, 'seconds': elapsed,
                      'ollama_ps': ps, **check(project)}
            (run_dir / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
            log(f'{name} run{i}: rc={rc} {elapsed}s file={result["file_exists"]} squares_ok={result["squares_ok"]}')
            results.append(result)
            shutil.rmtree(project / '.venv', ignore_errors=True)
        sh(['ollama', 'stop', name])
    (HERE / 'summary.json').write_text(json.dumps(
        [{k: r[k] for k in ('model', 'run', 'opencode_rc', 'seconds', 'file_exists', 'squares_ok')} for r in results],
        ensure_ascii=False, indent=2))
    log('done')


if __name__ == '__main__':
    main()
