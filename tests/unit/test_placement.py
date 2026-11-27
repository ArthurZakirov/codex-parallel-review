import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "src/architecture-check/hooks/placement.py"
spec = importlib.util.spec_from_file_location("placement", SCRIPT)
placement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(placement)


def test_mixed_placement_move_and_turn_scope(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGIN_DATA", str(tmp_path / "state"))
    source = tmp_path / "old.py"
    source.touch()
    patch = "*** Update File: old.py\n*** Move to: new.py\n*** Add File: README.md"
    event = dict(cwd=str(tmp_path), session_id="s", turn_id="t", tool_input={"command": patch})
    reason = placement.check_patch_placement(event)["hookSpecificOutput"]["permissionDecisionReason"]
    assert '["new.py", "old.py"]' in reason
    database, = tmp_path.rglob("placement.db")
    existing = dict(path="old.py", responsibility="old owner", rationale="move it", evidence="old.py")
    new = dict(path="new.py", responsibility="new owner", rationale="relocate", design="runner calls port")
    with pytest.raises(ValueError):
        placement.submit(database, [existing, dict(new, evidence="../missing")])
    assert placement.check_patch_placement(event)["hookSpecificOutput"]["permissionDecisionReason"] == reason
    placement.submit(database, [existing, new])
    assert placement.check_patch_placement(event) == {}
    assert placement.check_patch_placement(dict(event, turn_id="next"))["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_markdown_patch_needs_no_state(tmp_path):
    assert placement.check_patch_placement(dict(cwd=str(tmp_path), tool_input={"command": "*** Add File: notes.md"})) == {}
