"""Compare reviewable working files across a single tool invocation."""
from collections.abc import Iterator
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from patches import HEADER
from targets import kind, shell_targets


def snapshot(root: Path, include_code: bool = False) -> dict[str, str]:
    if not root.is_dir() or (root == Path.home() or root in Path.home().parents):
        return {}
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
                            capture_output=True)
    if listed.returncode == 0:
        paths = (Path(os.fsdecode(name)) for name in listed.stdout.split(b"\0") if name)
    else:
        paths = (p.relative_to(root) for p in root.iterdir())

    result = {}
    for path in paths:
        if kind(path) not in ({"markdown", "code"} if include_code else {"markdown"}):
            continue
        file = root / path
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root):
            continue
        try:
            result[str(file)] = file.read_text()
        except (FileNotFoundError, UnicodeDecodeError, PermissionError):
            continue
    return result


def _checkout_or_directory(path: Path) -> Path:
    result = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                            capture_output=True)
    return Path(os.fsdecode(result.stdout).rstrip("\n")) if result.returncode == 0 else path


def capture(event: dict, directory: Path) -> dict[str, list[str]]:
    if "cwd" not in event or not event.get("tool_use_id"):
        return {}
    root = Path(event["cwd"]).resolve()
    key = hashlib.sha256(event["tool_use_id"].encode()).hexdigest()
    before = directory / (key + ".before")
    if event["hook_event_name"] == "PreToolUse":
        inputs = event.get("tool_input", {})
        command = inputs.get("command") or inputs.get("cmd", "")
        shell = event.get("tool_name") != "apply_patch"
        if shell:
            working = (root / inputs.get("workdir", ".")).resolve()
            roots, files = shell_targets(command, working)
            roots = {_checkout_or_directory(path) for path in roots}
        else:
            roots = set()
            files = {root / match[1] for match in HEADER.finditer(command)
                     if kind(Path(match[1])) == "markdown"}
        baseline = _snapshot_targets(roots, files, shell)
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        before.write_text(json.dumps([list(map(str, roots)), list(map(str, files)), shell, baseline]))
        return {}
    if not before.exists():
        return {}
    roots, files, shell, previous = json.loads(before.read_text())
    before.unlink()
    current = _snapshot_targets(map(Path, roots), map(Path, files), shell)
    groups = {}
    for path in previous.keys() | current.keys():
        old, new = previous.get(path), current.get(path)
        if old == new:
            continue
        category = kind(Path(path))
        evidence = _evidence(path, old, new or "") if category == "markdown" else (
            "\n".join(difflib.unified_diff((old or "").splitlines(), (new or "").splitlines(),
                                          fromfile=path, tofile=path, lineterm="")))
        if evidence:
            groups.setdefault(category, []).append(evidence)
    return groups


def _snapshot_targets(roots: Iterator[Path] | set[Path], files: Iterator[Path] | set[Path], include_code: bool) -> dict[str, str]:
    contents = {}
    for root in roots:
        contents.update(snapshot(root, include_code))
    for file in files:
        if str(file) in contents or file.is_symlink() or not file.is_file():
            continue
        try:
            if subprocess.run(["git", "-C", str(file.parent), "check-ignore", "-q", "--", file.name],
                              capture_output=True).returncode == 0:
                continue
            contents[str(file)] = file.read_text()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            continue
    return contents


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
