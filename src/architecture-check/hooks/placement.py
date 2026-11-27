"""Gate native patches and record the working agent's placement decisions."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import sys


GUIDE = Path(__file__).resolve().parents[1] / "routing.md"
HEADER = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", re.M)


def relative_path(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonempty file path.")
    return str((root / value).resolve().relative_to(root))


def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": reason}}


def check(event):
    root = Path(event["cwd"]).resolve()
    names = HEADER.findall(event["tool_input"]["command"])
    targets = {relative_path(root, name) for name in names
               if Path(name).suffix.lower() not in {".md", ".markdown", ".mdx"}}
    if not targets:
        return {}
    identity = json.dumps([event["session_id"], event["turn_id"], str(root)])
    state = Path(os.environ["PLUGIN_DATA"]) / sha256(identity.encode()).hexdigest()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    database = state / "placement.db"
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS workspace (root TEXT PRIMARY KEY)")
        db.execute("INSERT OR IGNORE INTO workspace VALUES (?)", (str(root),))
        db.execute("CREATE TABLE IF NOT EXISTS plans (path TEXT PRIMARY KEY, entry TEXT)")
        missing = sorted(targets.difference(row[0] for row in db.execute("SELECT path FROM plans")))
    if not missing:
        return {}
    command = shlex.join(["python3", str(Path(__file__).resolve()), "submit", str(database)])
    return deny(f"Review placement before editing {json.dumps(missing)}. Inspect the tree with rg --files "
                "(or find), then read comparable modules. Split the proposed patch by responsibility. "
                "For each target submit a JSON object with path, responsibility, rationale and either "
                "evidence (a comparable existing file) or design (the flow, owner and dependency direction "
                f"for a new boundary). For new boundaries read {GUIDE}. Pipe the JSON array to "
                f"{command} on stdin, then retry the revised patch using apply_patch.")


def submit(database, entries):
    if not isinstance(entries, list) or not entries:
        raise ValueError("Submit a nonempty array of placement entries.")
    with sqlite3.connect(database.resolve().as_uri() + "?mode=rw", uri=True) as db:
        root = Path(db.execute("SELECT root FROM workspace").fetchone()[0])
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("Each placement entry must be an object.")
            path = relative_path(root, entry.get("path"))
            for field in ("responsibility", "rationale"):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    raise ValueError(f"{path} requires {field}.")
            if "evidence" in entry:
                evidence = relative_path(root, entry["evidence"])
                if not (root / evidence).is_file():
                    raise ValueError(f"Missing comparable module: {evidence}")
            elif not isinstance(entry.get("design"), str) or not entry["design"].strip():
                raise ValueError(f"Describe the new boundary using {GUIDE}.")
            db.execute("INSERT OR REPLACE INTO plans VALUES (?, ?)", (path, json.dumps(entry)))


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
        if len(sys.argv) == 1:
            print(json.dumps(check(payload)))
        elif len(sys.argv) == 3 and sys.argv[1] == "submit":
            submit(Path(sys.argv[2]), payload)
            print("Placement plan recorded.")
        else:
            sys.exit("Expected submit DATABASE with a JSON array on stdin.")
    except (KeyError, TypeError, ValueError, RuntimeError, OSError, sqlite3.Error) as error:
        if len(sys.argv) > 1:
            sys.exit(str(error))
        print(json.dumps(deny(f"Could not check patch placement: {error}")))
