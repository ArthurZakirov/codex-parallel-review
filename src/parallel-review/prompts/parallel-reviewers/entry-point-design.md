# Entry-point design

Apply these rules when reviewing how callers enter the application.

- **Keep orchestration in the application.** Trace a CLI or event handler from parsed inputs to the result. It should call a configured application operation directly, or construct the use-case object from those inputs and call its substantive `run()`. Flag a handler that calls a factory to get a workflow and then invokes that workflow. Bind dependencies outside the handler while preserving help and argument parsing without credentials.
- **Separate responsibilities.** In a CLI, keep argument parsing separate from output formatting.
- **Keep imports side-effect free.** Run the CLI through its entry point.
