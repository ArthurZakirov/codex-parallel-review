# Code organization review

Check the following conventions in the supplied code.

- **Group related operations.** Keep statements that perform one step together. Use a blank line where the purpose changes, such as the transition from loading inputs to evaluating a decision.
- **Keep orchestration in the application.** Trace a CLI or event handler from parsed inputs to the result. It should call a configured application operation directly, or construct the use-case object from those inputs and call its substantive `run()`. Flag a handler that calls a factory to get a workflow and then invokes that workflow. Bind dependencies outside the handler while preserving help and argument parsing without credentials.
- **Separate responsibilities.** In a CLI, keep argument parsing separate from output formatting. In the greeting example, this includes formatting the greeting.
- **Trace decisions across ports.** Locate each domain rule, including instructions stored as text and outcome-to-action tables. Check that core owns the rule, application code coordinates its use, and the concrete adapter receives the decided action. Transport-specific lookup of an external identifier for a supplied target belongs in the adapter.
- **Name decisions precisely.** Function and variable names should say what is assessed, compared or returned.
- **Keep imports side-effect free.** Run the CLI through its entry point.

## Reporting findings

For each finding, cite the relevant lines and explain which operations are hard to distinguish or follow. Skip hypothetical refactors.
