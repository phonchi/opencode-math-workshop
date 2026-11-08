"""Replay each logged OpenCode request to Ollama (non-streaming, 1 output token) and record prompt token counts."""
import json, sys, urllib.request
from pathlib import Path
rows = []
for f in sorted(Path(sys.argv[1] if len(sys.argv)>1 else 'requests').glob('*.json')):
    body = json.loads(f.read_text())
    tools = body.get('tools') or []
    sys_chars = sum(len(m['content']) if isinstance(m.get('content'), str) else len(json.dumps(m.get('content'), ensure_ascii=False))
                    for m in body['messages'] if m['role'] == 'system')
    replay = dict(body, stream=False, max_tokens=1)
    replay.pop('stream_options', None)
    req = urllib.request.Request('http://127.0.0.1:11434/v1/chat/completions', data=json.dumps(replay).encode(),
                                 headers={'Content-Type': 'application/json'})
    usage = json.load(urllib.request.urlopen(req, timeout=600)).get('usage', {})
    # same request without tool definitions, to separate their cost
    no_tools = {k: v for k, v in replay.items() if k not in ('tools', 'tool_choice')}
    req2 = urllib.request.Request('http://127.0.0.1:11434/v1/chat/completions', data=json.dumps(no_tools).encode(),
                                  headers={'Content-Type': 'application/json'})
    usage2 = json.load(urllib.request.urlopen(req2, timeout=600)).get('usage', {})
    rows.append({'file': f.name, 'model': body.get('model'), 'messages': [m['role'] for m in body['messages']],
                 'n_tools': len(tools), 'tool_names': [t['function']['name'] for t in tools],
                 'system_chars': sys_chars, 'request_bytes': f.stat().st_size,
                 'prompt_tokens': usage.get('prompt_tokens'), 'prompt_tokens_without_tools': usage2.get('prompt_tokens')})
json.dump(rows, open(sys.argv[2] if len(sys.argv)>2 else 'measure.json', 'w'), ensure_ascii=False, indent=2)
for r in rows:
    print({k: r[k] for k in ('file', 'messages', 'n_tools', 'system_chars', 'request_bytes', 'prompt_tokens', 'prompt_tokens_without_tools')})
