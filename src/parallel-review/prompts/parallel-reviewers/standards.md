# Code organization review

Check the following conventions in the supplied code.

- **Group related operations.** Keep statements that perform one step together. Use a blank line where the purpose changes, such as the transition from loading inputs to evaluating a decision.
- **Keep orchestration in the application.** Trace a CLI or event handler from parsed inputs to the result. It should call a configured application operation directly, or construct the use-case object from those inputs and call its substantive `run()`. Flag a handler that calls a factory to get a workflow and then invokes that workflow. Bind dependencies outside the handler while preserving help and argument parsing without credentials.
- **Separate responsibilities.** In a CLI, keep argument parsing separate from output formatting. In the greeting example, this includes formatting the greeting.
- **Trace decisions across ports.** Locate each domain rule, including instructions stored as text and outcome-to-action tables. Check that core owns the rule, application code coordinates its use, and the concrete adapter receives the decided action. Transport-specific lookup of an external identifier for a supplied target belongs in the adapter.
- **Trace each provider binding.** Identify the consumer-owned port declaration, the call through it and the concrete operation bound in composition. Compare their names and signatures. The concrete module and symbol should identify the provider and its operation. Flag consumer-specific resource selection, parsing, validation or errors in an adapter that could serve several consumers.
- **Check prerequisite capabilities.** When acquisition is a requested step, verify that the application invokes a named port for the value it needs before using that value. Substituting a fake that returns the needed value is sufficient. Preserve this abstraction when reviewing its binding: composition may bind a configured resource identifier and interpret a provider result to satisfy the consumer's contract. Do not replace a satisfied consumer port with a lower-level storage API or move deployment selectors into the use case merely to expose calls inside its binding.
- **Name decisions precisely.** Function and variable names should say what is assessed, compared or returned.
- **Keep imports side-effect free.** Run the CLI through its entry point.

## Reporting findings

For each finding, cite the relevant lines and explain which operations are hard to distinguish or follow. Skip hypothetical refactors.
