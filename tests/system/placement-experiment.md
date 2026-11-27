# Pre-edit placement experiment

Give a fresh Codex session the [triage CLI task](prompts/vulnerability-triage.md) in an empty directory. Keep this evaluation guide outside the workspace. Run the same task with the architecture hook disabled and enabled, using the same model, sandbox and available skills. For the native-patch comparison, give both workers the same tool instruction to create the requested files with `apply_patch`.

## Evidence to inspect

1. Inspect the transcript for a denied patch, a plan submission and a successful retry. Record shell writes and chat-only responses as missed hook coverage.
2. Trace the generated implementation from input to ticket update without executing it. Check all three decision outcomes.
3. Judge the following criteria against the actual imports, function calls and file boundaries.

| Criterion | Passing evidence |
| --- | --- |
| Replaceable caller | Trace the CLI from parsed arguments to one application operation. Accept a directly bound function or a use-case instance whose `run()` implements the sequence. A notebook or Lambda can invoke the same operation without repeating retrieval, classification or transition steps. |
| Replaceable input source | The application accepts an alert reference and obtains the text through an injected reader. Substituting an in-memory source requires no CLI parsing, file access or changes to the workflow. |
| Core policy | Locate the Markdown classification criteria and the verdict-to-target-status mapping in core. Verify all three mappings there. |
| Application orchestration | Trace source read, model call, core decision and ticket update in order. Verify the update port receives the issue key and decided target status. The Jira adapter may resolve a transition ID for that status. It must be usable without knowing the alert classification. |
| External systems | AWS secret retrieval, model invocation and Jira protocol details have distinct owners outside the workflow. Check where credentials are acquired and how concrete dependencies reach the application. |
| Model-key port and AWS binding | Locate the declared model-key loading capability and its use by the application. Trace composition binding a configured secret identifier to it. The concrete file and primary symbol both name AWS and describe secret retrieval. Inspect the reader for assumptions about models, token formats, consumer-specific JSON fields and errors. A different consumer should be able to retrieve another secret through the same operation. |
| Python protocol implementation | In the Python variant, find the use-case constructor, its protocol-typed dependencies, and the actual injected objects. Verify the Jira client implements the status-update method and the configured AWS reader implements the model-key port method directly. Inspect composition for forwarding functions. |
| Port module ownership | Locate each protocol definition in a dedicated consumer-owned port module. Trace the use case's imports and constructor annotations back to those definitions. Check the port modules for concrete adapter dependencies. |
| Python records and runners | Inspect every dataclass decorator and trace instances to a function input or return value. Verify that the class executing the workflow has an explicit typed constructor for its ports and owns the orchestration method. |
| Module boundaries | Invocation, application policy and vendor operations live in distinct modules. Follow the calls to detect mixed responsibilities even when the filenames suggest separation. |
| Package boundaries | Locate the verdict policy in core, sequencing in application and concrete I/O in adapters. Check what each package actually does. Trace the configured application call and flag wrappers that only construct or forward to another callable. |
| Prompt resource | Trace the core-owned Markdown instructions and alert text into the complete semantic request that the application supplies to the model port. |
| Request ownership | A substitute model receives the complete ordered request, including the distinction between instructions and alert data. The adapter owns provider field names, credentials and transport. |
| Module names | Compare each single-purpose module's filename to its primary callable or class. Check framework-defined entry points separately. |

Judge only the worker's untouched output after its post-edit review. A finding in the report counts as detected; count it as fixed only after inspecting the final code. Keep manual corrections outside the evaluated workspace. After a failed criterion, change the responsible hook or prompt and rerun the unchanged worker task in a fresh directory. A single successful run establishes one observed outcome.
