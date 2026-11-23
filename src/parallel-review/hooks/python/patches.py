"""Extract review evidence from a successful native Codex patch without reading the workspace."""
from pathlib import PurePath
import re

from file_types import kind

HEADER = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
MOVE = re.compile(r"^\*\*\* Move to: (.+)$", re.MULTILINE)


def review_inputs(event: dict) -> dict[str, list[str]]:
    if event.get("tool_name") != "apply_patch":
        return {}
    response = event.get("tool_response")
    if not isinstance(response, str) or response.splitlines()[:1] != ["Exit code: 0"]:
        return {}

    patch = event["tool_input"]["command"].partition("\n*** End Patch")[0]
    headers = list(HEADER.finditer(patch))
    groups: dict[str, list[str]] = {}
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(patch)
        section = patch[header.start():end].rstrip("\n")
        move = MOVE.search(section)
        path = PurePath(move[1] if move else header[1])
        category = kind(path)
        if category:
            groups.setdefault(category, []).append(section)
    return groups
