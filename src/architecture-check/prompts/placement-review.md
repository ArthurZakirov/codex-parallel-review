# Review placement before editing {targets}

Inspect the tree with `rg --files` or `find`, then read comparable modules. Trace the proposed workflow from invocation to result. For new boundaries, consult the placement matrix at `{guide}`.

Check the proposed tree against these ownership rules before registering paths.

- **Module ownership.** Keep invocation, application decisions and startup wiring in separately owned modules.
- **Proposed paths.** For a module centered on one operation or client, derive the filename from that operation or client. Use the owning package to supply context.
- **Replaceable caller.** Another caller should be able to invoke the workflow with substitute dependencies.
- **External systems.** Give independently replaceable systems their own adapter modules. Keep protocol translation in those modules.
- **Decision criteria.** Place the rules for deciding an outcome with the application that defines them.
- **Prompt resources.** Store reusable model instructions in a dedicated Markdown resource under the owning package. Load it independently of the current directory. The application assembles the complete ordered request, including which text is trusted instruction and which is user data. Pass that request as one value across the port. The adapter translates it into the provider's wire format and supplies transport credentials.
- **Directories.** Group related modules into named packages by capability or architectural role. Inspect the parent and siblings of each proposed path. In a new project, create the directories that express those groups.

For each target submit a JSON object with string fields `path`, `responsibility`, `rationale` and either `evidence` (a comparable existing file) or `design` (flow, owner and dependency direction). Run this exact shell form with your JSON array in place of `[...]`.

```sh
{plan_start}[...]{plan_end}
```

Retry the revised patch using `apply_patch`.
