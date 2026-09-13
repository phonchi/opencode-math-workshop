"""Record workshop checks in an isolated WSL project without altering global settings."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools/test-runs/20260912-workshop-refresh/wsl"
PROJECT = OUT / "project"
RUNTIME = OUT / "runtime"


def main():
    PROJECT.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(exist_ok=True)
    for name in ["pyproject.toml", "uv.lock", "opencode.json", "AGENTS.md"]:
        shutil.copy2(ROOT / "starter" / name, PROJECT / name)
    for name in ["figs", "notes"]:
        (PROJECT / name).mkdir(exist_ok=True)
    env = {key: val for key, val in os.environ.items() if not key.endswith(("API_KEY", "ACCESS_TOKEN", "AUTH_TOKEN"))}
    env.update({"XDG_CONFIG_HOME": str(RUNTIME / "config"), "XDG_DATA_HOME": str(RUNTIME / "data"), "XDG_CACHE_HOME": str(RUNTIME / "cache"), "XDG_STATE_HOME": str(RUNTIME / "state"), "OPENCODE_CONFIG_DIR": str(RUNTIME / "opencode"), "OPENCODE_DISABLE_CLAUDE_CODE": "true", "OPENCODE_DISABLE_AUTOUPDATE": "true", "OPENCODE_DISABLE_LSP_DOWNLOAD": "true", "OPENCODE_CONFIG_CONTENT": json.dumps({"enabled_providers": ["opencode"], "share": "disabled"}), "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "PYTHONUTF8": "1", "MPLCONFIGDIR": str(RUNTIME / "matplotlib")})
    retry = "--agents-only" in sys.argv
    attempt = OUT / ("agent-retry" if retry else "setup")
    attempt.mkdir(exist_ok=True)
    outcomes = []
    with (attempt / "run.log").open("w", encoding="utf-8") as master:
        def run(label, command, timeout=600):
            if command[:2] == ["opencode", "run"]:
                command = command[:2] + ["--dir", str(PROJECT)] + command[2:]
            print(f"START {label}", flush=True)
            master.write(f"\n## {label}\n{json.dumps(command, ensure_ascii=False)}\n")
            master.flush()
            started = time.monotonic()
            try:
                proc = subprocess.run(command, cwd=PROJECT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", timeout=timeout)
                output, code = proc.stdout, proc.returncode
            except subprocess.TimeoutExpired as exc:
                raw = exc.stdout or b""
                output = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
                code = 124
            (attempt / f"{label}.log").write_text(output, encoding="utf-8")
            master.write(output + f"\nEXIT={code}\n")
            master.flush()
            outcomes.append({"name": label, "command": command, "exit": code, "seconds": round(time.monotonic() - started, 3)})
            (attempt / "commands.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"END {label}: {code}", flush=True)
            return code, output
        for label, command in [("opencode-version", ["opencode", "--version"]), ("uv-version", ["uv", "--version"]), ("uv-sync", ["uv", "sync", "--locked"]), ("python-imports", ["uv", "run", "python", "-c", "import numpy,scipy,sklearn,matplotlib,networkx; print('環境 OK')"]), ("math-verification", ["uv", "run", "python", str(ROOT / "tools/verify_math.py"), "--out", str(OUT / "math")])]:
            if retry:
                continue
            code, _ = run(label, command)
            if code:
                raise SystemExit(f"Failed: {label}")
        code, auth = run("auth-list", ["opencode", "auth", "list"])
        if code or "0 credentials" not in auth:
            raise SystemExit("Isolated authentication check was not empty")
        run("models", ["opencode", "models", "opencode"])
        code, answer = run("agent-response", ["opencode", "run", "--model", "opencode/big-pickle", "用一句話說明什麼是主成分分析"], 180)
        if code or len(answer.strip()) < 20 or "Error:" in answer:
            raise SystemExit("Free model response failed")
        code, refused = run("ask-rejects", ["opencode", "run", "--model", "opencode/big-pickle", "建立 permission_probe.py，內容是 print(1)。不要只貼出程式，請用寫檔工具。"], 180)
        if (PROJECT / "permission_probe.py").exists() or "auto-reject" not in refused:
            raise SystemExit("Expected noninteractive ask refusal was not observed")
        code, response = run("agent-hello", ["opencode", "run", "--auto", "--model", "opencode/big-pickle", "建立一個 hello.py，內容是印出 1 到 10 的平方，然後執行它"], 240)
        if code or not (PROJECT / "hello.py").exists():
            raise SystemExit("Agent did not create hello.py")
        code, output = run("hello-independent", ["uv", "run", "python", "hello.py"])
        import re
        lines = output.strip().splitlines()
        if len(lines) == 10 and all("=" in line for line in lines):
            numbers = [int(line.rsplit("=", 1)[1].strip()) for line in lines]
        else:
            numbers = [int(n) for n in re.findall(r"\b\d+\b", output)]
        if code or numbers != [n*n for n in range(1, 11)]:
            raise SystemExit("Incorrect square output")
        (OUT / "setup-pass.json").write_text(json.dumps({"status": "PASS", "model": "opencode/big-pickle", "credentials": 0, "scope": "isolated setup, references, ask refusal, actual agent write and execution"}, indent=2), encoding="utf-8")
        print("PASS: WSL setup, mathematics and free-model tool round trip", flush=True)


if __name__ == "__main__":
    main()
