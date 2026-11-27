# Pre-edit placement experiment

Give a fresh Codex session the [triage CLI task](prompts/vulnerability-triage.md) in an empty directory. Keep this evaluation guide outside the workspace. Run the same task with the architecture hook disabled and enabled, using the same model, sandbox and available skills. For the native-patch comparison, give both workers the same tool instruction to create the requested files with `apply_patch`.

## Evidence to inspect

1. Inspect the transcript for a denied patch, a plan submission and a successful retry. Record shell writes and chat-only responses as missed hook coverage.
2. Trace the generated implementation from input to ticket update without executing it. Check all three decision outcomes.
3. Judge the following criteria against the actual imports, function calls and file boundaries.

| Criterion | Passing evidence |
| --- | --- |
| Replaceable caller | Trace the CLI from parsed arguments to one configured application call. A notebook or Lambda can invoke the same operation without repeating retrieval, classification or transition steps. |
| Replaceable input source | The application accepts an alert reference and obtains the text through an injected reader. Substituting an in-memory source requires no CLI parsing, file access or changes to the workflow. |
| Application policy | The application owns the classification instructions and decision-to-status mapping. It invokes model and ticket-update capabilities supplied by its caller. Substitutes can exercise the workflow without network or credentials. |
| External systems | AWS secret retrieval, model invocation and Jira protocol details have distinct owners outside the workflow. Check where credentials are acquired and how concrete dependencies reach the application. |
| Module boundaries | Invocation, application policy and vendor operations live in distinct modules. Follow the calls to detect mixed responsibilities even when the filenames suggest separation. |
| Package boundaries | The actual tree groups related modules into purpose-named directories. Verify which files share a parent and why. A single package containing every implementation file still counts as flat. |
| Prompt resource | The reusable classification instructions live in a dedicated Markdown file. Trace how the application loads that file and passes the text to the model adapter. |
| Request ownership | A substitute model receives the complete ordered request, including the distinction between instructions and alert data. The adapter owns provider field names, credentials and transport. |
| Module names | Compare each single-purpose module's filename to its primary callable or class. Check framework-defined entry points separately. |

A single successful run establishes one observed outcome. Keep the worker task fixed when revising the general hook prompt so the next comparison tests the hook change.
