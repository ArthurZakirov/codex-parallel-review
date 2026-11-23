"""Compare Markdown working copies across a single tool invocation."""
from collections.abc import Iterator
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def snapshot(root: Path) -> dict[str, str]:
    if root in (Path.home(), Path(root.anchor)):
        return {}
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
                            capture_output=True)
    if listed.returncode == 0:
        paths = (Path(os.fsdecode(name)) for name in listed.stdout.split(b"\0") if name)
    else:
        paths = _local_files(root)

    result = {}
    for path in paths:
        if path.suffix.lower() not in {".md", ".mdx", ".markdown"}:
            continue
        file = root / path
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root):
            continue
        try:
            result[str(path)] = file.read_text()
        except (FileNotFoundError, UnicodeDecodeError, PermissionError):
            continue
    return result


def _local_files(root: Path) -> Iterator[Path]:
    for directory, folders, files in os.walk(root):
        folders[:] = [f for f in folders if not f.startswith(".") and f not in {"node_modules", "venv"}]
        for filename in files:
            yield (Path(directory) / filename).relative_to(root)


def capture(event: dict, directory: Path) -> list[str] | None:
    if "cwd" not in event or not event.get("tool_use_id"):
        return None
    root = Path(event["cwd"]).resolve()
    key = hashlib.sha256(event["tool_use_id"].encode()).hexdigest()
    before = directory / (key + ".before")
    if event["hook_event_name"] == "PreToolUse":
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        before.write_text(json.dumps(snapshot(root)))
        return None
    if not before.exists():
        return None
    previous = json.loads(before.read_text())
    before.unlink()
    current = snapshot(root)
    return [_evidence(path, previous.get(path), text) for path, text in current.items()
            if previous.get(path) != text]


def _evidence(path: str, before: str | None, after: str) -> str:
    if before is None:
        return f"New document {path}:\n{after}"
    old, new = before.splitlines(), after.splitlines()
    diff = "\n".join(difflib.unified_diff(old, new, fromfile=path, tofile=path, n=0, lineterm=""))
    boundaries = [0] + [i for i, line in enumerate(new) if i and re.match(r"^#{1,6}\s", line)] + [len(new)]
    edits = [(a, max(a+1, b)) for tag, _, _, a, b in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes() if tag != "equal"]
    sections = ["\n".join(new[start:end]) for start, end in zip(boundaries, boundaries[1:])
                if any(a < end and b > start for a, b in edits)]
    return diff + "\nEnclosing sections (context only):\n" + "\n".join(sections)
