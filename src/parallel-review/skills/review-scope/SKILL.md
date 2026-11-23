---
name: review-scope
description: Run Parallel Review retrospectively on user-selected files, recursive folders, or a whole repository, then verify and apply findings in the invoking chat.
---

## Run the review

1. **Resolve the selection.** Interpret paths in the user's intended workspace. For “this repository,” use its Git worktree root. Ask for the target if unspecified.
2. **Launch the reviewers.** Run [scripts/review.py](scripts/review.py) with Python 3, resolving the script relative to this installed skill. Pass the selection as arguments:
   - `--focus` takes the optional scope guidance as one string.
   - `--` precedes the selected paths, each passed as a separate argument.
3. **Read the report.** Wait for the runner to print the path to `review.md`. The reviewers need Codex login and network access. If the sandbox blocks access, use the host’s standard approval flow for the invocation.
4. **Verify the findings.** Compare each finding with the current file and requested focus. Apply confirmed fixes in the invoking chat. For a findings-only request, hand over the report.
5. **Verify the result.** Re-read changed passages from disk and check the diff. Give the user the report location, fixes applied, and reasons for skipping any findings.
