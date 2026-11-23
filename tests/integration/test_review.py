"""Run the review hook with real local Codex reviewers."""
import json
import os
from pathlib import Path
import subprocess
import sys

from pytest_bdd import given, scenarios, then, when

scenarios("review.feature")
ROOT = Path(__file__).resolve().parents[2]


@given("a completed request in a sample workspace", target_fixture="workspace")
def sample_workspace(tmp_path):
    (tmp_path / "service.py").write_bytes((ROOT / "tests/fixtures/dispatch_api/service.py").read_bytes())
    return tmp_path


def send(workspace, event, **fields):
    env = dict(os.environ, PLUGIN_DATA=str(workspace / "review-state"))
    payload = dict(hook_event_name=event, session_id="review-test", turn_id="turn", cwd=str(workspace), **fields)
    result = subprocess.check_output(
        [sys.executable, ROOT / "src/parallel-review/hooks/dispatch.py"],
        input=json.dumps(payload), text=True, env=env, cwd=workspace, timeout=280,
    )
    return json.loads(result)


@when("the review plugin receives a mixed patch and a stop event", target_fixture="handoff")
def review(workspace):
    send(workspace, "PostToolUse", tool_name="apply_patch", tool_use_id="one",
         tool_response="Exit code: 0\n", tool_input={"command": "*** Begin Patch\n*** Add File: sample.py\n+print(1)\n*** Add File: NOTES.md\n+# Notes\n*** End Patch"})
    return send(workspace, "Stop", stop_hook_active=False)


@then("it returns a report with findings from each review perspective")
def verify_report(workspace, handoff):
    report, = (workspace / "review-state").rglob("review.md")
    assert handoff["decision"] == "block" and str(report) in handoff["reason"]
    sections = report.read_text().split("\n## ")[1:]
    assert {"Experience", "Standards", "Correctness", "Reader", "Representation"} <= {s.splitlines()[0] for s in sections}
    assert all(s.partition("\n")[2].strip() for s in sections)


@then("a follow-up stop does not request another review")
def verify_followup(workspace):
    send(workspace, "PostToolUse", tool_name="apply_patch", tool_use_id="repair",
         tool_response="Exit code: 0\n", tool_input={"command": "*** Begin Patch\n*** Add File: fix.py\n+print(2)\n*** End Patch"})
    assert send(workspace, "Stop", stop_hook_active=True) == {}


@when("the user edits a paragraph containing setup and two alternative commands")
def review_dense_instructions(workspace, monkeypatch):
    # Exercise the shipped prompt independently of the user's optional Markdown guide.
    guide = workspace / "empty-guide.md"
    guide.touch()
    monkeypatch.setenv("PARALLEL_REVIEW_MARKDOWN_GUIDE", str(guide))
    paragraph = ("First initialize the client with `relay init`. Then choose a delivery mode. "
                 "For a local delivery run `relay local` or for remote delivery run `relay remote`. "
                 "Remote delivery requires a signed certificate.")
    patch = f"*** Begin Patch\n*** Add File: DELIVERY.md\n+# Delivery\n+\n+{paragraph}\n*** End Patch"
    send(workspace, "PostToolUse", tool_name="apply_patch", tool_use_id="delivery",
         tool_response="Exit code: 0", tool_input={"command": patch})
    send(workspace, "Stop", stop_hook_active=False)


@then("the Markdown reviewer proposes ordered steps with grouped alternatives and preserves the prerequisite")
def verify_grouped_instructions(workspace):
    import re

    report, = (workspace / "review-state").rglob("review.md")
    text = report.read_text()
    replacement = text.partition("## Representation")[2]
    assert "relay init" in replacement
    for command in ("relay local", "relay remote"):
        assert re.search(r"(?m)^\s*(?:[-*+]|\|).*`" + command + r"`", replacement), replacement
    assert "certificate" in replacement.lower()
