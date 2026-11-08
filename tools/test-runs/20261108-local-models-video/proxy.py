"""Logging pass-through proxy: saves each request body OpenCode sends, forwards it unchanged to Ollama."""
import http.server, json, sys, time, urllib.request
from pathlib import Path
OUT = Path(sys.argv[1]); UP = 'http://127.0.0.1:11434'
n = 0
class H(http.server.BaseHTTPRequestHandler):
    def _fwd(self, body=None):
        global n
        if body is not None:
            n += 1
            (OUT / f'{n:03d}{self.path.replace("/", "_")}.json').write_bytes(body)
        req = urllib.request.Request(UP + self.path, data=body, method=self.command,
                                     headers={k: v for k, v in self.headers.items() if k.lower() not in ('host', 'content-length')})
        with urllib.request.urlopen(req, timeout=600) as r:
            self.send_response(r.status)
            for k, v in r.headers.items():
                if k.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                    self.send_header(k, v)
            self.send_header('Connection', 'close'); self.end_headers()
            while chunk := r.read(4096):
                self.wfile.write(chunk); self.wfile.flush()
    def do_GET(self): self._fwd()
    def do_POST(self): self._fwd(self.rfile.read(int(self.headers.get('Content-Length', 0))))
    def log_message(self, fmt, *a): print(time.strftime('%T'), self.command, self.path, flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1', 11435), H).serve_forever()
