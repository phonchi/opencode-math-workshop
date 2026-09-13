"""Exercise authored prompts with a free model; keep exact prompts and JSON events."""
import html
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools/test-runs/20260912-workshop-refresh/wsl"
PROJECT = OUT / "project"
EVIDENCE = OUT / "lessons"
RUNTIME = OUT / "runtime"


def code_blocks(slug):
    source = (ROOT / f"tools/body_{slug}.html").read_text()
    return [html.unescape(re.sub(r"<[^>]+>", "", part)) for part in re.findall(r'<pre class="cmd"><code>(.*?)</code></pre>', source, re.S)]


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    env = {key: val for key, val in os.environ.items() if not key.endswith(("API_KEY", "ACCESS_TOKEN", "AUTH_TOKEN"))}
    env.update({"XDG_CONFIG_HOME": str(RUNTIME / "config"), "XDG_DATA_HOME": str(RUNTIME / "data"), "XDG_CACHE_HOME": str(RUNTIME / "cache"), "XDG_STATE_HOME": str(RUNTIME / "state"), "OPENCODE_CONFIG_DIR": str(RUNTIME / "opencode"), "OPENCODE_DISABLE_CLAUDE_CODE": "true", "OPENCODE_DISABLE_AUTOUPDATE": "true", "OPENCODE_DISABLE_LSP_DOWNLOAD": "true", "OPENCODE_CONFIG_CONTENT": json.dumps({"enabled_providers": ["opencode"], "share": "disabled"}), "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "PYTHONUTF8": "1", "MPLCONFIGDIR": str(RUNTIME / "matplotlib")})
    l1, l2, l3 = (code_blocks(slug) for slug in ["lab1-cluster", "lab2-pca", "lab3-notes"])
    prompts = {
        "lab1": next(p for p in l1 if p.startswith("用 sklearn")),
        "lab2": "\n\n".join([l2[0], "請固定使用 sklearn 的 svd_solver='full'，並比對比例、方向正負號、重建誤差、正交性與特徵值本身。每項印出數值與判斷。"]),
        "lab3": "\n\n".join([l3[0], l3[1], l3[2], next(p for p in l3 if p.startswith("請把今天已完成"))]),
    }
    with (EVIDENCE / "run.log").open("a", encoding="utf-8") as master:
        def record(label, command, timeout=900):
            event_file = EVIDENCE / f"{label}.jsonl"
            command_file = EVIDENCE / f"{label}-command.json"
            command_file.write_text(json.dumps(command, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"START {label}", flush=True)
            master.write(f"\nSTART {label}\n");master.flush()
            start = time.monotonic()
            with event_file.open("w", encoding="utf-8") as log:
                process = subprocess.Popen(command, cwd=PROJECT, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(process.pid, signal.SIGKILL);process.wait()
                    code = 124
            meta = {"exit": code, "seconds": round(time.monotonic()-start, 2), "events": event_file.name}
            master.write(json.dumps(meta)+"\n");master.flush()
            print(f"END {label}: {code}", flush=True)
            return meta

        for name, prompt in prompts.items():
            outcome = EVIDENCE / f"{name}-result.json"
            if outcome.exists() and json.loads(outcome.read_text()).get("status") == "PASS":
                print(f"REUSE {name}: previously passed", flush=True)
                continue
            (EVIDENCE / f"{name}-prompt.txt").write_text(prompt, encoding="utf-8")
            meta = record(name, ["opencode", "run", "--dir", str(PROJECT), "--model", "opencode/big-pickle", "--auto", "--format", "json", prompt])
            expected = {"lab1": "lab1_cluster.py", "lab2": "lab2_pca.py", "lab3": "lab3_logistic.py"}[name]
            if name == "lab3" and not (PROJECT / expected).is_file():
                candidates = sorted(PROJECT.glob("lab3_*.py"))
                if len(candidates) == 1:
                    expected = candidates[0].name
            if meta["exit"] or not (PROJECT / expected).is_file():
                meta["status"] = "FAIL"
                outcome.write_text(json.dumps(meta, indent=2))
                raise SystemExit(f"Agent task did not complete: {name}; inspect exact events")
            executed = record(name+"-independent", ["uv", "run", "python", expected], timeout=180)
            if executed["exit"]:
                meta["status"] = "FAIL"
                outcome.write_text(json.dumps(meta, indent=2))
                raise SystemExit(f"Generated program failed: {name}")
            meta.update({"status": "PASS", "scope": "actual agent file creation and independently successful execution", "file": expected})
            outcome.write_text(json.dumps(meta, indent=2))
        print("PASS: three real WSL agent lessons (numerical output remains reviewable)", flush=True)


if __name__ == "__main__":
    main()
