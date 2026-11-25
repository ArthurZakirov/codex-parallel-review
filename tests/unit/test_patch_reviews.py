from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[2] / "src/parallel-review/hooks/python"


@pytest.fixture
def hook(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(HOOKS))
    monkeypatch.setenv("PLUGIN_DATA", str(tmp_path / "state"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    import dispatch
    calls = []

    def review(groups):
        calls.append(groups)
        return "report"

    monkeypatch.setattr(dispatch, "parallel_review", review)

    def send(kind, turn="first", **fields):
        return dispatch.handle(dict(hook_event_name=kind, session_id="worker", turn_id=turn, **fields))

    return send, calls


def patch(name, text, call, *, success=True):
    return dict(tool_name="apply_patch", tool_use_id=call,
                tool_input={"command": f"*** Begin Patch\n*** Add File: {name}\n+{text}\n*** End Patch"},
                tool_response=f"Exit code: {0 if success else 1}\n")


def test_reviews_only_accepted_edits_once_and_for_their_own_turn(hook):
    send, calls = hook
    send("PostToolUse", **patch("failed.py", "failed", "f", success=False))
    send("PostToolUse", **patch("image.png", "unsupported", "u"))
    assert send("Stop") == {} and not calls

    first = patch("a.py", "print(1)", "a")
    send("PostToolUse", **first)
    send("PostToolUse", **first)
    send("PostToolUse", **patch("b.py", "print(2)", "b"))
    assert send("Stop", turn="other") == {}
    assert send("Stop")["decision"] == "block"
    assert calls == [{"python": ["*** Add File: a.py\n+print(1)", "*** Add File: b.py\n+print(2)"]}]
    assert send("Stop", stop_hook_active=True) == {}

    send("PostToolUse", **patch("NOTES.md", "# Notes", "c"))
    assert send("Stop", stop_hook_active=True) == {}
    assert len(calls) == 1
    send("PostToolUse", turn="next", **patch("new.py", "x=1", "d"))
    assert send("Stop", turn="next")["decision"] == "block"
    assert len(calls) == 2


def test_mixed_patch_routes_by_destination_including_move(hook):
    send, calls = hook
    event = patch("unused", "", "mixed")
    event["tool_input"]["command"] = (
        "*** Begin Patch\n*** Update File: old.txt\n*** Move to: Guide.MD\n@@\n-old\n+new\n"
        "*** Delete File: unused.py\n*** End Patch")
    send("PostToolUse", **event)
    send("Stop")
    groups, = calls
    assert groups["python"] == ["*** Delete File: unused.py"]
    assert groups["markdown"] == ["*** Update File: old.txt\n*** Move to: Guide.MD\n@@\n-old\n+new"]


def test_model_inputs_are_limited_to_assigned_edits_and_guidance(tmp_path, monkeypatch):
    from types import SimpleNamespace

    monkeypatch.syspath_prepend(str(HOOKS))
    import reviews
    guide = tmp_path / "guide.md"
    guide.write_text("MARKDOWN_GUIDANCE_CANARY")
    monkeypatch.setenv("PARALLEL_REVIEW_MARKDOWN_GUIDE", str(guide))
    prompts = []

    def capture(command, *, input, cwd, **options):
        assert not list(Path(cwd).iterdir())
        assert "--ignore-user-config" in command
        prompts.append(input)
        return SimpleNamespace(returncode=0, stdout="No findings.")

    monkeypatch.setattr(reviews.subprocess, "run", capture)
    report = reviews.parallel_review({"code": ["PYTHON_CANARY"], "markdown": ["MARKDOWN_CANARY"]})

    boundary = (reviews.PROMPTS / "shared/review-scope.md").read_text().strip()
    assert boundary not in report
    c1 = (reviews.PROMPTS / "parallel-reviewers/representation/use-exact-identifiers-and-concrete-operations.md").read_text()
    assert sum(c1 in prompt for prompt in prompts) == 1
    assert c1.rstrip().endswith("|") and "Apply these **code-explanation rules**" not in c1
    assert len(prompts) == 5
    for prompt in prompts:
        assert boundary in prompt
        assert ("PYTHON_CANARY" in prompt) != ("MARKDOWN_CANARY" in prompt)
        assert ("MARKDOWN_CANARY" in prompt) == ("MARKDOWN_GUIDANCE_CANARY" in prompt)


@pytest.mark.parametrize(("setting", "expected"), [(0, 0), (2, 2), (3, 3), ("unlimited", 5)])
def test_configured_budget_counts_batches_with_new_edits(hook, tmp_path, setting, expected):
    import json

    (tmp_path / "parallel-review.json").write_text(json.dumps({"max_review_passes": setting}))
    send, calls = hook
    for index in range(5):
        send("PostToolUse", **patch("a.py", f"x={index}", str(index)))
        response = send("Stop", stop_hook_active=index > 0)
        assert bool(response) == (index < expected)
        assert send("Stop", stop_hook_active=True) == {}
    assert len(calls) == expected


def test_failed_reviewer_does_not_repeatedly_spend_the_turn_budget(hook, monkeypatch):
    import dispatch

    send, _ = hook
    def unavailable(groups):
        raise RuntimeError("reviewer unavailable")

    monkeypatch.setattr(dispatch, "parallel_review", unavailable)
    send("PostToolUse", **patch("sample.py", "x=1", "first"))
    with pytest.raises(RuntimeError, match="reviewer unavailable"):
        send("Stop")
    send("PostToolUse", **patch("sample.py", "x=2", "retry"))
    assert send("Stop") == {}


def test_shell_edit_in_dirty_document_includes_only_changed_section(hook, tmp_path):
    import subprocess

    send, calls = hook
    root = tmp_path / "project"
    root.mkdir()
    (root / "workflow.md").write_text("# Earlier\nUnrelated dirty text.\n## Commands\nShared setup.\n")
    event = dict(cwd=str(root), tool_name="exec_command", tool_use_id="cat")
    send("PreToolUse", **event)
    subprocess.run(["sh", "-c", "cat >> workflow.md <<'EOF'\nRun cmd.\nEOF"], cwd=root, check=True)
    send("PostToolUse", **event)
    send("Stop")
    text, = calls[0]["markdown"]
    assert "## Commands\nShared setup.\nRun cmd." in text
    assert "+Run cmd." in text
    assert "Unrelated dirty text" not in text


def test_shell_from_home_changes_dirty_markdown_and_new_code_elsewhere(hook, tmp_path, monkeypatch):
    import shlex
    import subprocess

    send, calls = hook
    home = tmp_path / "home"
    target = tmp_path / "other project"
    home.mkdir()
    target.mkdir()
    monkeypatch.setenv("HOME", str(home))
    (target / "workflow.md").write_text("existing dirty line\n")
    cmd = f"cd {shlex.quote(str(target))} && echo next >> workflow.md && echo done > step.py"
    event = dict(cwd=str(home), tool_name="Bash", tool_use_id="outside", tool_input={"command": cmd})
    send("PreToolUse", **event)
    subprocess.run(["sh", "-c", cmd], cwd=home, check=True)
    send("PostToolUse", **event)
    send("Stop")
    groups, = calls
    assert "+next" in groups["markdown"][0]
    assert "+existing dirty line" not in groups["markdown"][0]
    assert "+done" in groups["python"][0]


def test_absolute_shell_destination_without_changing_directory(hook, tmp_path):
    import subprocess

    send, calls = hook
    start = tmp_path / "start"
    start.mkdir()
    path = tmp_path / "outside.md"
    cmd = f"echo evidence > '{path}'"
    event = dict(cwd=str(start), tool_name="Bash", tool_use_id="absolute", tool_input={"command": cmd})
    send("PreToolUse", **event)
    subprocess.run(["sh", "-c", cmd], cwd=start, check=True)
    send("PostToolUse", **event)
    send("Stop")
    assert calls[0]["markdown"] == [f"New document {path}:\nevidence\n"]


def test_native_patch_survives_empty_snapshot(hook, tmp_path):
    send, calls = hook
    event = dict(patch(str(tmp_path.parent / "external.md"), "new text", "patch"), cwd=str(tmp_path))
    send("PreToolUse", **event)
    send("PostToolUse", **event)
    send("Stop")
    assert "+new text" in calls[0]["markdown"][0]


def test_generator_from_subdirectory_commits_a_sibling_file(hook, tmp_path):
    import subprocess

    send, calls = hook
    repo = tmp_path / "checkout"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / ".gitignore").write_text("ignored.md\n")
    (repo / "older.md").write_text("Pre-existing user change.\n")
    (scripts / "generate").write_text(
        "echo generated > ../output.md\necho ignored > ../ignored.md\n"
        "git add ../output.md && git -c user.name=test -c user.email=t@example.org commit -qm generate\n"
    )
    event = dict(cwd=str(tmp_path), tool_name="exec_command", tool_use_id="generate",
                 tool_input={"cmd": "sh generate", "workdir": str(scripts)})
    send("PreToolUse", **event)
    subprocess.run(["sh", "generate"], cwd=scripts, check=True)
    send("PostToolUse", **event)
    send("Stop")
    assert calls == [{"markdown": [f"New document {repo}/output.md:\ngenerated\n"]}]
