# Review placement before editing {targets}

Inspect the tree with `rg --files` or `find`, then read comparable modules. Trace the proposed workflow from invocation to result. For new boundaries, consult the placement matrix at `{guide}`.

Check the proposed tree against these ownership rules before registering paths.

- **Entry points and workflow.** Keep invocation, application decisions and startup wiring in separately owned modules. Another caller should be able to invoke the workflow with substitute dependencies.
- **External systems.** Give independently replaceable systems their own adapter modules. Keep protocol translation there and decision criteria with the application.
- **Prompt resources.** When the application sends reusable natural-language instructions to a model, store the instructions in a dedicated Markdown resource under the owning package. Load that resource independently of the caller's current directory. Pass its text through the application boundary to the adapter.
- **Directories.** Group related modules into named packages by capability or architectural role. Inspect the parent and siblings of each proposed path. In a new project, create the directories that express those groups.

For each target submit a JSON object with string fields `path`, `responsibility`, `rationale` and either `evidence` (a comparable existing file) or `design` (flow, owner and dependency direction). Run this exact shell form with your JSON array in place of `[...]`.

```sh
{plan_start}[...]{plan_end}
```

Retry the revised patch using `apply_patch`.
