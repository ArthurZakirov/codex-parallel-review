# Review placement before editing {targets}

Inspect the tree with `rg --files` or `find`, then read comparable modules. Trace the proposed workflow from invocation to result. For new boundaries, consult the placement matrix at `{guide}`.

Check the proposed tree against these ownership rules before registering paths.

- **Application orchestration.** The application sequences core operations and calls to ports. Trace which inputs it acquires, which decision it asks core to make, and which resulting action it sends to a port.
- **Proposed paths.** For each new single-purpose module, name its intended primary public function or class in the placement entry. Derive the filename from that symbol. A provider-named client module should expose that client. For a standalone adapter function use the action name, retaining provider context where it identifies the implementation.
- **Invocation.** Sketch the handler's call site. After parsing, invoke one application operation and present its result. A handler may construct a use-case object with named inputs and call its `run()` method, or call a configured function directly. The method or function owns the actual sequence. Bind concrete adapters in composition. If the handler first calls a factory and then invokes the returned callable, revise the design so it receives or imports the configured operation instead. Keep credentials and service access lazy so help and parsing work independently.
- **Input acquisition.** Distinguish data supplied in the invocation from a reference identifying data to retrieve. When retrieval is a step of the use case, have the application invoke an input-source port. Place file, stream and remote reads in concrete adapters.
- **Replaceable caller.** Trace a second caller using a different source. It should invoke the same application operation without repeating any retrieval, processing or update steps.
- **External systems.** Give independently replaceable systems their own adapter modules. Translate application requests into the provider's wire format and supply transport credentials there.
- **Port contracts.** Before choosing adapter paths, write the consumer's required capability, inputs and result in the consumer's vocabulary. Declare that named contract with the application and use it at the call site. A callable type or protocol can express it without a forwarding class.
- **Provider operations.** For each concrete implementation, name both the module and its primary function or class for the provider and the reusable operation it actually performs. Check its parameters, return value, errors and validation: could a second use case perform the same provider operation without adopting the first consumer's terminology or data conventions? Keep selection of the resource and interpretation of its value on the consumer side. Bind configured resource identifiers and implementation to the named port in composition.
- **Core policy.** Place decision criteria and mappings from outcomes to intended actions in core. For each outbound port, sketch the arguments: supply the already-decided action or target value. Its adapter should implement the external operation without interpreting the project's business outcome.
- **Prompt resources.** When instructions encode a domain decision, store them in a dedicated Markdown resource in core alongside the policy they express. Load the resource independently of the current directory.
- **Request assembly.** Core defines the semantic request, including trusted instructions and user data. The application passes that request to the port. Provider-specific serialization belongs in the adapter.
- **Directories.** Review every ownership group in the proposed tree. When the feature has both domain policy and a use case, group pure decisions and transformations under core, and use-case sequencing under application, alongside the adapters. Follow established project names. Give each package concrete work to own.
- **Delegation.** Bind dependencies to the actual application operation at startup. Trace its caller and remove any proposed function or class whose sole job is to build or forward to another callable. Preserve entry points required by an external contract.

For each target submit a JSON object with string fields `path`, `responsibility`, `rationale` and either `evidence` (a comparable existing file) or `design` (flow, owner and dependency direction). Submit the following as its own shell tool call, with your JSON array in place of `[...]`.

```sh
{plan_start}[...]{plan_end}
```

Retry the revised patch using `apply_patch`.
