import json
import os
from pathlib import Path
import subprocess

from pytest_bdd import given, scenarios, then, when

scenarios("review.feature")
ROOT = Path(__file__).resolve().parents[2]


@given("a Codex workspace with only Parallel Review installed", target_fixture="chat")
def review_chat(tmp_path):
    home = tmp_path / "codex"
    home.mkdir()
    auth = Path(os.environ["PARALLEL_REVIEW_TEST_AUTH_HOME"]) / "auth.json"
    (home / "auth.json").symlink_to(auth)
    workspace = tmp_path / "project"
    workspace.mkdir()
    (workspace / "service.py").write_bytes((ROOT / "tests/fixtures/dispatch_api/service.py").read_bytes())
    subprocess.run(["git", "init", "-q", "-b", "main", "--separate-git-dir", str(tmp_path / "history")], check=True, cwd=workspace)
    env = dict(os.environ, CODEX_HOME=str(home), HOME=str(tmp_path))
    env.update(GIT_AUTHOR_NAME="Demo worker", GIT_COMMITTER_NAME="Demo worker",
               GIT_AUTHOR_EMAIL="demo@example.invalid", GIT_COMMITTER_EMAIL="demo@example.invalid")
    for args in (["marketplace", "add", str(ROOT)], ["add", "parallel-review@codex-parallel-review"]):
        subprocess.run(["codex", "plugin", *args], env=env, cwd=workspace, check=True)
    return home, workspace, env


@when("the user makes a documentation edit", target_fixture="events")
def request_handoff(chat):
    prompt = ("Use native apply_patch to create NOTES.md with the heading # Delivery and this initial draft "
              "as a single paragraph: First initialize the client with `relay init`. Then choose a delivery mode. "
              "For local delivery run `relay local` or for remote delivery run `relay remote`. "
              "Remote delivery requires a signed certificate. Commit the initial document before ending your turn.")
    return _run_turn(chat, prompt)


@when("the user asks a discussion question", target_fixture="discussion")
def discuss(chat):
    return _run_turn(chat, "What is a file extension? Answer in one sentence without editing files.")


@then("the turn completes without recording edits or producing a report")
def verify_discussion(chat, discussion):
    home, _, _ = chat
    assert discussion[-1]["type"] == "turn.completed"
    assert not list(home.rglob("edits.db"))
    assert not list(home.rglob("review.md"))


def _run_turn(chat, prompt):
    _, workspace, env = chat
    output = subprocess.check_output(
        ["codex", "--no-daemon", "exec", "--json", "--trust", "--dangerously-bypass-hook-trust",
         "--add-dir", str(workspace.parent / "history"), "--skip-git-repo-check", "-s", "workspace-write", "-m", "gpt-6-luna",
         "-c", 'model_reasoning_effort="low"', prompt],
        env=env, cwd=workspace, text=True, timeout=320,
    )
    return [json.loads(line) for line in output.splitlines()]


@then("the draft and its review-guided edit are separate commits after one review pass")
def verify_handoff(chat, events):
    home, workspace, _ = chat
    def revision(rev: str) -> str:
        return subprocess.check_output(["git", "show", rev + ":NOTES.md"], cwd=workspace, text=True)

    initial, reviewed = revision("HEAD^"), revision("HEAD")
    assert "First initialize" in initial and "1." not in initial
    assert "1." in reviewed and "relay remote" in reviewed and "certificate" in reviewed.lower()
    assert (workspace / "NOTES.md").read_text() == reviewed
    assert subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=workspace).strip() == b"2"
    assert not list(home.rglob("review-2.md"))
    report, = home.rglob("review.md")
    assert report.stat().st_size > 0
    assert events[-1]["type"] == "turn.completed"
    assert [s.splitlines()[0] for s in report.read_text().split("\n## ")[1:]] == ["Markdown"]
