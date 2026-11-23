"""Exercise two turns in one app-server process with one trusted installation."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]


def test_next_turn_uses_edited_checkout(tmp_path):
    home = tmp_path / "codex"
    home.mkdir()
    (home / "auth.json").symlink_to(Path(os.environ["PARALLEL_REVIEW_TEST_AUTH_HOME"]) / "auth.json")
    env = dict(os.environ, CODEX_HOME=str(home))
    for args in (["marketplace", "add", str(ROOT)], ["add", "parallel-review@codex-parallel-review"]):
        subprocess.run(["codex", "plugin", *args], env=env, check=True, cwd=tmp_path)
    checkout = tmp_path / "development"
    shutil.copytree(ROOT / "src", checkout / "src")
    shutil.copy2(ROOT / "develop", checkout / "develop")
    guide = checkout / "src/parallel-review/prompts/main-agent/editing.md"
    proc = subprocess.Popen(["codex", "--no-daemon", "app-server"], env=env, cwd=tmp_path,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def receive(predicate):
        for line in proc.stdout:
            message = json.loads(line)
            if predicate(message):
                return message
        raise RuntimeError("App server closed unexpectedly")

    def rpc(method, params):
        request = str(uuid4())
        proc.stdin.write(json.dumps(dict(id=request, method=method, params=params)) + "\n")
        proc.stdin.flush()
        reply = receive(lambda m: m.get("id") == request)
        assert "error" not in reply, reply
        return reply["result"]

    try:
        rpc("initialize", {"clientInfo": {"name": "live-test", "version": "1"},
                           "capabilities": {"experimentalApi": True}})
        inventory = rpc("hooks/list", {"cwds": [str(tmp_path)]})["data"][0]["hooks"]
        trust = {h["key"]: {"trusted_hash": h["currentHash"]} for h in inventory
                 if h["key"].startswith("parallel-review@codex-parallel-review:")}
        assert len(trust) == 4
        rpc("config/batchWrite", {"edits": [{"keyPath": "hooks.state", "value": trust,
                                             "mergeStrategy": "upsert"}], "reloadUserConfig": True})
        thread = rpc("thread/start", {"cwd": str(tmp_path), "model": "gpt-6.1-terra",
                                      "approvalPolicy": "never", "sandbox": "read-only"})["thread"]["id"]
        subprocess.run([checkout / "develop", "--thread", thread], env=env, check=True)
        for index in range(2):
            marker = uuid4().hex
            guide.write_text(f"Your test receipt for this turn is {marker}.")
            if index:
                handler = checkout / "src/parallel-review/hooks/python/dispatch.py"
                source = handler.read_text()
                assert "guide.read_text()" in source
                handler.write_text(source.replace("guide.read_text()", '"Python updated. " + guide.read_text()'))
            turn = rpc("turn/start", {"threadId": thread, "input": [{"type": "text", "text":
                "Repeat the test receipt from the hook, including its Python updated prefix if present."}]})
            done = receive(lambda m: m.get("method") == "turn/completed")
            assert done["params"]["turn"]["id"] == turn["turn"]["id"]
            record = rpc("thread/read", {"threadId": thread, "includeTurns": True})["thread"]["turns"][-1]
            reply = " ".join(i["text"] for i in record["items"] if i["type"] == "agentMessage")
            assert marker in reply, reply
            if index:
                assert "python updated" in reply.lower(), reply
    finally:
        proc.terminate()
        proc.wait(timeout=10)
