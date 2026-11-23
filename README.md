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

**Parallel Review.** A successful native `apply_patch` call records its patch excerpts under the Codex session and turn IDs. At stop, code goes to experience, standards and correctness reviewers. Markdown goes to the Markdown reviewer. A mixed patch triggers both groups. Each reviewer receives only its assigned excerpts in a temporary workspace. The worker receives one report path and applies confirmed fixes. A repeated stop with no new edits returns immediately. [Supported file types](src/parallel-review/hooks/patches.py) · [Review guidance](src/parallel-review/prompts)

**Review budget.** By default, each user turn gets one review pass. All applicable reviewers run together. The worker applies confirmed fixes and can finish immediately. Its next user request starts a fresh budget. To change the limit, set `max_review_passes` in `$CODEX_HOME/parallel-review.json` (normally `~/.codex/parallel-review.json`). For example:

```json
{"max_review_passes": 2}
```

With `2`, review-guided edits can trigger one verification pass. Use `0` for no passes or `"unlimited"` to keep reviewing while the worker makes new eligible edits. A stop without new edits costs nothing. A failed reviewer launch consumes the attempted pass. Reports remain separate so the worker can identify which pass requested a fix.

**Scope limits.** Discussion, failed patches and pre-existing changes do not trigger reviews. Shell or MCP writes and unrecognized file types are outside this trigger. Use native patches for edits you want reviewed. Reports assess patch evidence; runnable end-to-end UI checks belong in a separate workflow. When installed, the Markdown reviewer also receives the text of `~/.agents/skills/format-markdown/SKILL.md`. To select a different rubric, set `PARALLEL_REVIEW_MARKDOWN_GUIDE` to an absolute Markdown file visible to the hook. Only the Markdown reviewer receives its text.

## Tests

Install dependencies with `python3 -m pip install -r tests/requirements.txt`. Run `python3 -m pytest` for unit tests or `python3 -m pytest tests/integration` for live integration tests. Installed-plugin tests use `PARALLEL_REVIEW_TEST_AUTH_HOME="$HOME/.codex" python3 -m pytest tests/system` and require a file-backed Codex login.
