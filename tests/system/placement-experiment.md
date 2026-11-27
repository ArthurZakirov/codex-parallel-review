# Pre-edit placement experiment

Give a fresh Codex session the [triage CLI task](prompts/vulnerability-triage.md) in an empty directory. Keep this evaluation guide outside the workspace. Run the same task with the architecture hook disabled and enabled, using the same model, sandbox and available skills. For the native-patch comparison, give both workers the same tool instruction to create the requested files with `apply_patch`.

## Evidence to inspect

1. Inspect the transcript for a denied patch, a plan submission and a successful retry. Record shell writes and chat-only responses as missed hook coverage.
2. Trace the generated implementation from input to ticket update without executing it. Check all three decision outcomes.
3. Judge the following criteria against the actual imports, function calls and file boundaries.

| Criterion | Passing evidence |
| --- | --- |
| Replaceable caller | A notebook or Lambda can call the workflow directly with alert data and a ticket key. It does not need command-line parsing or process exit handling. |
| Application policy | The application owns the decision-to-status mapping. It invokes classification and ticket-update capabilities supplied by its caller. A fake classifier and ticket updater can exercise the workflow without network or credentials. |
| External systems | AWS secret retrieval, model invocation and Jira protocol details have distinct owners outside the workflow. Check where credentials are acquired and how concrete dependencies reach the application. |
| Module boundaries | Invocation, application policy and vendor operations live in distinct modules. Follow the calls to detect mixed responsibilities even when the filenames suggest separation. |

A single successful run establishes one observed outcome. Keep the worker task fixed when revising the general hook prompt so the next comparison tests the hook change.
