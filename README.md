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

## Optional pre-edit architecture check

Run `./install architecture-check` and trust its hook in a fresh local Codex chat. The first native patch targeting an uncovered non-Markdown path pauses before writing. Codex inspects the repository, records the intended responsibility for each path and retries. Existing modules serve as placement evidence. For new boundaries, the [routing matrix and defect ETL example](src/architecture-check/routing.md) guide the design. Mixed patches can use both routes.

Plans apply to one session, turn and working directory. The hook checks paths and required plan fields. Codex judges whether the placement fits. A covered path can be edited again during the turn. Shell writes, generators and edits through other tools are outside this hook's coverage. Use native patches for edits that need placement review.

The [placement experiment](tests/system/placement-experiment.md) includes a repeatable worker task and a separate evaluation guide. To inspect the decision, compare the blocked patch in the session transcript with the files in the successful retry.

## How review works

**Code edits.** Native and observed shell edits receive experience and correctness reviews plus five independent design reviews.

| Reviewer | What it checks |
| --- | --- |
| [Function readability](src/parallel-review/prompts/parallel-reviewers/function-readability.md) | Grouping related statements and naming decisions |
| [Entry-point design](src/parallel-review/prompts/parallel-reviewers/entry-point-design.md) | Parsing, application invocation, presentation and import-time behavior |
| [Port contracts and bindings](src/parallel-review/prompts/parallel-reviewers/port-contracts-and-bindings.md) | Consumer-defined capabilities, provider operations and direct adapter injection |
| [Package and policy ownership](src/parallel-review/prompts/parallel-reviewers/package-and-policy-ownership.md) | Placement of domain decisions and root-level source files |
| [Error ownership and translation](src/parallel-review/prompts/parallel-reviewers/error-ownership.md) | Failure contracts, dependency direction and translation at caller boundaries |

**Markdown edits.** For shell commands, the hook compares files before and after execution in the tool working directory and literal `cd` destinations. Inside a Git checkout it uses tracked and non-ignored untracked files across the checkout. It also checks explicit file paths in the command. Native patches supply their own edit paths. A new document goes to both reviewers in full. For an existing document, each receives a diff and the enclosing sections. The submission supplies the writing request when available.

| Reviewer | Review question |
| --- | --- |
| Reader | Does each group answer the reader’s question with a clear hierarchy? |
| Representation | Can the reader scan peer items and identify the exact command, file, or operation? |

**Compare the draft and the fixes.** Ask Codex to commit its initial changes before finishing the turn. When the review finds an issue, the worker receives a [handoff prompt](src/parallel-review/prompts/main-agent/handoff.md) directing it to create a separate commit for confirmed fixes. Select that follow-up commit in your Git history to inspect its diff against the draft.

**Review budget.** By default, each user turn gets one review pass. All applicable reviewers run together. The worker applies confirmed fixes and can finish immediately. Its next user request starts a fresh budget. To change the limit, set `max_review_passes` in `$CODEX_HOME/parallel-review.json` (normally `~/.codex/parallel-review.json`). For example:

```json
{"max_review_passes": 2}
```

With `2`, review-guided edits can trigger one verification pass. Use `0` for no passes or `"unlimited"` to keep reviewing while the worker makes new eligible edits. A stop without new edits costs nothing. A failed reviewer launch consumes the attempted pass. Reports remain separate so the worker can identify which pass requested a fix.

**Capture limits.** Workspace comparisons observe changes during a tool call. Concurrent external edits in the same directory can be included. A script that computes a destination in another checkout internally can escape observation. Pass its output path explicitly or run it from the destination checkout. Outside Git, directory snapshots cover immediate files. Background writes after the hook returns and writes through MCP can also escape observation. The hook skips snapshotting the home directory and filesystem root. Native code patches still use their patch evidence.

**Markdown guidance.** Reader receives [Define the parent contract](src/parallel-review/prompts/parallel-reviewers/reader/define-the-parent-contract.md). Representation receives [Group scannable items by semantic type](src/parallel-review/prompts/parallel-reviewers/representation/group-scannable-items-by-semantic-type.md) and [Use exact identifiers and concrete operations](src/parallel-review/prompts/parallel-reviewers/representation/use-exact-identifiers-and-concrete-operations.md). These excerpts are bundled with the plugin. To supplement both roles, set `PARALLEL_REVIEW_MARKDOWN_GUIDE` to an absolute file path.

## Review existing files from chat

Invoke `$review-scope` and name the files, folders, or repository to inspect. For example:

> $review-scope Review README.md and everything under docs/. Focus on instructions that bury command choices in prose. Apply the confirmed fixes.

The skill sends complete files to the applicable review roles, saves their findings in a temporary `review.md`, and hands the report to the current chat. Folder selection includes supported code and Markdown recursively, including ignored files. Git metadata and symbolic links are skipped. Select a narrower folder when generated dependencies would add unnecessary reviews.

## Tests

1. Install the test dependencies with `python3 -m pip install -r tests/requirements.txt`.
2. Choose the suite you want to run.

   - **Unit tests** — `python3 -m pytest`
   - **Live integration tests** — `python3 -m pytest tests/integration`
   - **Installed-plugin tests** — `PARALLEL_REVIEW_TEST_AUTH_HOME="$HOME/.codex" python3 -m pytest tests/system`. This suite requires a file-backed Codex login.
