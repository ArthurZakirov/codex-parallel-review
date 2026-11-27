# Review placement before editing {targets}

Inspect the tree with `rg --files` or `find`, then read comparable modules. Trace the proposed workflow from invocation to result. For new boundaries, consult the placement matrix at `{guide}`.

Check the proposed tree against these ownership rules before registering paths.

- **Module ownership.** Keep invocation, application decisions and startup wiring in separately owned modules.
- **Proposed paths.** For each new single-purpose module, name its intended primary public function or class in the placement entry. Derive the filename from that symbol. A provider-named client module should expose that client. For a standalone adapter function use the action name, retaining provider context where it identifies the implementation.
- **Invocation.** Sketch the handler's call site. After parsing, invoke one application operation and present its result. A handler may construct a use-case object with named inputs and call its `run()` method, or call a configured function directly. The method or function owns the actual sequence. Bind concrete adapters in composition. If the handler first calls a factory and then invokes the returned callable, revise the design so it receives or imports the configured operation instead. Keep credentials and service access lazy so help and parsing work independently.
- **Input acquisition.** Distinguish data supplied in the invocation from a reference identifying data to retrieve. When retrieval is a step of the use case, have the application invoke an input-source port. Place file, stream and remote reads in concrete adapters.
- **Replaceable caller.** Trace a second caller using a different source. It should invoke the same application operation without repeating any retrieval, processing or update steps.
- **External systems.** Give independently replaceable systems their own adapter modules. Translate application requests into the provider's wire format and supply transport credentials there.
- **Decision criteria.** Place the rules for deciding an outcome with the application that defines them.
- **Prompt resources.** Store reusable model instructions in a dedicated Markdown resource under the owning package. Load it independently of the current directory.
- **Request assembly.** Assemble the complete ordered request in the application, distinguishing trusted instructions from user data. Pass that request as one value across the port.
- **Directories.** Review every ownership group in the proposed tree. When the feature has both domain policy and a use case, group pure decisions and transformations under core, and use-case sequencing under application, alongside the adapters. Follow established project names. Give each package concrete work to own.
- **Delegation.** Bind dependencies to the actual application operation at startup. Trace its caller and remove any proposed function or class whose sole job is to build or forward to another callable. Preserve entry points required by an external contract.

For each target submit a JSON object with string fields `path`, `responsibility`, `rationale` and either `evidence` (a comparable existing file) or `design` (flow, owner and dependency direction). Submit the following as its own shell tool call, with your JSON array in place of `[...]`.

```sh
{plan_start}[...]{plan_end}
```

Retry the revised patch using `apply_patch`.
