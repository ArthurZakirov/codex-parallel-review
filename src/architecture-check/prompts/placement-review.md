# Review placement before editing {targets}

Inspect the tree with `rg --files` or `find`, then read comparable modules. Trace the proposed workflow from invocation to result. For new boundaries, consult the placement matrix at `{guide}`.

Check the proposed tree against these ownership rules before registering paths.

- **Module ownership.** Keep invocation, application decisions and startup wiring in separately owned modules.
- **Proposed paths.** For a module centered on one operation or client, derive the filename from that operation or client. Use the owning package to supply context.
- **Invocation.** Have each entry point translate its arguments or event into one application call and present the result. Put dependency assembly in startup wiring.
- **Input acquisition.** Distinguish data supplied in the invocation from a reference identifying data to retrieve. When retrieval is a step of the use case, have the application invoke an input-source port. Place file, stream and remote reads in concrete adapters.
- **Replaceable caller.** Trace a second caller using a different source. It should invoke the same application operation without repeating any retrieval, processing or update steps.
- **External systems.** Give independently replaceable systems their own adapter modules. Translate application requests into the provider's wire format and supply transport credentials there.
- **Decision criteria.** Place the rules for deciding an outcome with the application that defines them.
- **Prompt resources.** Store reusable model instructions in a dedicated Markdown resource under the owning package. Load it independently of the current directory.
- **Request assembly.** Assemble the complete ordered request in the application, distinguishing trusted instructions from user data. Pass that request as one value across the port.
- **Directories.** Group related modules into named packages by capability or architectural role. Inspect the parent and siblings of each proposed path. In a new project, create the directories that express those groups.

For each target submit a JSON object with string fields `path`, `responsibility`, `rationale` and either `evidence` (a comparable existing file) or `design` (flow, owner and dependency direction). Run this exact shell form with your JSON array in place of `[...]`.

```sh
{plan_start}[...]{plan_end}
```

Retry the revised patch using `apply_patch`.
