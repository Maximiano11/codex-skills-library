#!/usr/bin/env python3
"""Read-only compatibility probe; never starts a model turn or changes configuration."""
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def probe(binary, cwd):
    version = subprocess.check_output([binary, "--version"], text=True, timeout=10).strip()
    features = subprocess.run([binary, "features", "list"], capture_output=True, text=True, timeout=10)
    confirmed = [line for line in features.stdout.splitlines() if line.split() and line.split()[0] in {"hooks", "multi_agent", "plugin_hooks"}]
    proc = subprocess.Popen([binary, "app-server", "--listen", "stdio://"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
    messages = queue.Queue()
    def reader():
        for line in proc.stdout:
            messages.put(line)
    thread = threading.Thread(target=reader, daemon=True);thread.start()
    def send(value):
        proc.stdin.write(json.dumps(value)+"\n");proc.stdin.flush()
    def receive(rid):
        deadline=time.monotonic()+25
        while time.monotonic()<deadline:
            try: line=messages.get(timeout=1)
            except queue.Empty:
                if proc.poll() is not None: raise RuntimeError("app-server exited")
                continue
            data=json.loads(line)
            if data.get("id")==rid:
                if "error" in data: raise RuntimeError("app-server returned a protocol error")
                return data["result"]
        raise TimeoutError("No app-server response within 25 seconds")
    try:
        send({"id":1,"method":"initialize","params":{"clientInfo":{"name":"engineering_os_probe","version":"1.0.0"}}})
        receive(1);send({"method":"initialized"})
        send({"id":2,"method":"skills/list","params":{"cwds":[str(Path(cwd).resolve())],"forceReload":True}})
        data=receive(2)
        names={"engineering-os","prompt-engineer","software-architect","implementation-standards","product-ux","database-engineer","security-auditor","quality-engineer","code-reviewer","performance-engineer","technical-documentation","release-manager","production-reliability"}
        found=[];errors=[]
        for entry in data.get("data",[]):
            found.extend({"name":s["name"],"scope":s.get("scope"),"enabled":s.get("enabled"),"path":s.get("path")} for s in entry.get("skills",[]) if s.get("name") in names)
            errors.extend(e for e in entry.get("errors",[]) if any(n in json.dumps(e) for n in names))
        return {"binary":binary,"version":version,"feature_lines":confirmed,"cwd":str(cwd),
                "skills":found,"related_errors":errors,"model_turns_started":0,
                "limits":["Discovery proves presence, not selection or compliance on every future request."]}
    finally:
        proc.terminate()
        try: proc.wait(timeout=3)
        except subprocess.TimeoutExpired: proc.kill();proc.wait()


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--codex");parser.add_argument("--cwd",default=str(Path.home()));parser.add_argument("--out")
    args=parser.parse_args()
    binary=args.codex or os.environ.get("CODEX_CLI_PATH") or shutil.which("codex")
    if not binary: parser.error("Pass --codex or make Codex available on PATH")
    data=probe(binary,args.cwd)
    text=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        with Path(args.out).open("x") as f: f.write(text)
    print(text)
