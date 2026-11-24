# Use exact identifiers and concrete operations

Apply these steps whenever prose refers to a specific technical object.

1. **Identify the object.** Use the task and its source to establish which object the statement concerns. For example, determine whether a user needs to recognize a product or invoke its executable. If the source leaves the object ambiguous, state what is unresolved.
2. **Write its identifier.** Once the object is known, apply these rules:
   - **Name selection.** Use the product name for a product, the command for an executable, or the filename or unambiguous path for a file.
   - **Spelling.** Copy the identifier from the source, preserving case, spacing and punctuation. If its exact spelling is unavailable, say so.
   - **Presentation.** Use inline code for literal identifiers and link located symbols. Add a plain-language explanation when helpful.

The examples below show how to replace an ambiguous reference or description with a precise one. Verify each name, expression and value against the source you are describing.

| Ambiguous wording | Precise wording |
| --- | --- |
| “The order status column now has validation.” | “The `orderStatus` column now has validation.” |
| “The managed template was regenerated.” | “The renderer regenerated `home/dot_codex/AGENTS.md.tmpl`.” |
| “Start the terminal client.” | “Run `codex`.” |
| "the underscore keep intervals before rebuild function" | `_keep_intervals_before_rebuild` |
| "The left-edge partition owns the earlier days." | "Rows where `state_date < rebuild_start` are passed to `_keep_intervals_before_rebuild`." |
| "The older dates are kept." | "Rows where `state_date < rebuild_start` are kept; rows where `state_date >= rebuild_start` are rebuilt." |
| "The old left edge is wrong." | "With `valid_from='2026-10-01'` and `rebuild_start='2026-10-10'`, the output starts at `2026-10-01`; the expected start is `2026-10-10`." |
