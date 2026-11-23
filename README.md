# Parallel Review for Codex

**Catch the obvious mistake before you get the “you’re right” reply.** When Codex finishes an edit, independent reviewers check the patch and send findings back to the working agent. You see the result after it has had a chance to fix them.

## Install

With Python 3.10+ and a signed-in, plugin-capable Codex CLI, run:

```sh
git clone https://github.com/ArthurZakirov/codex-parallel-review.git
cd codex-parallel-review
./install
```

Start a fresh Codex chat and trust the installed hooks when prompted.

## How review works

**Code edits.** Native patches go to experience, standards and correctness reviewers.

**Markdown edits.** Around native patches and shell commands, the hook compares Markdown files in the working directory. For Git workspaces it includes tracked and non-ignored untracked files. A new document goes to both reviewers in full. For an existing document, each receives a diff and the enclosing sections. The submission supplies the writing request when available.

| Reviewer | Review question |
| --- | --- |
| Reader | Can the intended reader find the answer, and does each section deliver what its heading promises? |
| Representation | Can the reader follow, look up or compare the information, and reach its supporting sources? |

**Compare the draft and the fixes.** Ask Codex to commit its initial changes before finishing the turn. When the review finds an issue, the worker receives a [handoff prompt](src/parallel-review/prompts/handoff.md) directing it to create a separate commit for confirmed fixes. Select that follow-up commit in your Git history to inspect its diff against the draft.

**Review budget.** By default, each user turn gets one review pass. All applicable reviewers run together. The worker applies confirmed fixes and can finish immediately. Its next user request starts a fresh budget. To change the limit, set `max_review_passes` in `$CODEX_HOME/parallel-review.json` (normally `~/.codex/parallel-review.json`). For example:

```json
{"max_review_passes": 2}
```

With `2`, review-guided edits can trigger one verification pass. Use `0` for no passes or `"unlimited"` to keep reviewing while the worker makes new eligible edits. A stop without new edits costs nothing. A failed reviewer launch consumes the attempted pass. Reports remain separate so the worker can identify which pass requested a fix.

**Capture limits.** Workspace comparisons observe changes during a tool call. Concurrent external edits in the same directory can be included. Background writes after a command returns, MCP writes, ignored untracked files in Git, and writes outside the observed directory can be missed. The hook skips snapshotting the home directory and filesystem root. Native code patches still use their patch evidence.

**Markdown guidance.** Both reviewers receive their own bundled rules with tools disabled. When the local information-representation-design skill is available, the hook includes its structure rules for Reader and its presentation and reference rules for Representation. To supplement both roles, set `PARALLEL_REVIEW_MARKDOWN_GUIDE` to an absolute path containing additional rules.

## Tests

1. Install the test dependencies with `python3 -m pip install -r tests/requirements.txt`.
2. Choose the suite you want to run.

   - **Unit tests** — `python3 -m pytest`
   - **Live integration tests** — `python3 -m pytest tests/integration`
   - **Installed-plugin tests** — `PARALLEL_REVIEW_TEST_AUTH_HOME="$HOME/.codex" python3 -m pytest tests/system`. This suite requires a file-backed Codex login.
