"""Gate native patches and record the working agent's placement decisions."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import sys


GUIDE = Path(__file__).resolve().parents[1] / "routing.md"
HEADER = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", re.M)
PLAN_START = "cat <<'CODEX_PLACEMENT_PLAN'\n"
PLAN_END = "\nCODEX_PLACEMENT_PLAN"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        print(json.dumps(handle(payload)))
    except (KeyError, TypeError, ValueError, RuntimeError, OSError, sqlite3.Error) as error:
        print(json.dumps(deny(f"Could not check patch placement: {error}")))


def handle(event: dict) -> dict:
    if event["tool_name"] == "apply_patch":
        return check_patch_placement(event)
    command = event["tool_input"].get("command", "").rstrip()
    if command.startswith(PLAN_START):
        if not command.endswith(PLAN_END):
            raise ValueError("End the placement submission with CODEX_PLACEMENT_PLAN.")
        entries = json.loads(command[len(PLAN_START):-len(PLAN_END)])
        submit(placement_database(event, Path(event["cwd"]).resolve()), entries)
    return {}


def check_patch_placement(event: dict) -> dict:
    root = Path(event["cwd"]).resolve()
    names = HEADER.findall(event["tool_input"]["command"])
    targets = {relative_path(root, name) for name in names
               if Path(name).suffix.lower() not in {".md", ".markdown", ".mdx"}}

    if not targets:
        return {}
    database = placement_database(event, root)
    missing = sorted(targets - recorded_paths(database, root))
    if not missing:
        return {}
    template = (GUIDE.parent / "prompts/placement-review.md").read_text(encoding="utf-8")
    return deny(template.format(targets=json.dumps(missing), guide=GUIDE,
                                plan_start=PLAN_START, plan_end=PLAN_END).strip())


def placement_database(event: dict, root: Path) -> Path:
    identity = json.dumps([event["session_id"], event["turn_id"], str(root)])
    state = Path(os.environ["PLUGIN_DATA"]) / sha256(identity.encode()).hexdigest()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    return state / "placement.db"


def submit(database: Path, entries: object) -> None:
    if not isinstance(entries, list) or not entries:
        raise ValueError("Submit a nonempty array of placement entries.")
    with sqlite3.connect(database.resolve().as_uri() + "?mode=rw", uri=True) as db:
        root = Path(db.execute("SELECT root FROM workspace").fetchone()[0])
        for entry in entries:
            path = validate_entry(root, entry)
            db.execute("INSERT OR REPLACE INTO plans VALUES (?, ?)", (path, json.dumps(entry)))


def recorded_paths(database: Path, root: Path) -> set[str]:
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS workspace (root TEXT PRIMARY KEY)")
        db.execute("INSERT OR IGNORE INTO workspace VALUES (?)", (str(root),))
        db.execute("CREATE TABLE IF NOT EXISTS plans (path TEXT PRIMARY KEY, entry TEXT)")
        return {row[0] for row in db.execute("SELECT path FROM plans")}


def validate_entry(root: Path, entry: object) -> str:
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
    return path


def relative_path(root: Path, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonempty file path.")
    return str((root / value).resolve().relative_to(root))


def deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": reason}}


if __name__ == "__main__":
    main()
