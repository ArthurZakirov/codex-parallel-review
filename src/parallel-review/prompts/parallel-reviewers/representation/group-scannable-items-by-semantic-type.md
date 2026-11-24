# Group scannable items by semantic type

Follow these **grouping rules**:

- **Expose separate peers.** Give independently checkable requirements, behaviors or outcomes their own list items. Check comma-separated clauses for hidden peers. Keep each condition with its consequence and each action with its qualifications.
- **Separate different semantic types.** When adjacent items serve different purposes, give each type its own accurately named group, whether the types are changes, steps, reasons, alternatives, evidence, constraints, examples, decisions, or anything else. These are **examples, not a closed list**; derive the categories from the content.
- **Keep connected material together.** Do not create a new group merely because two sentences differ in wording. Split when readers need to recognize a change in semantic role, not simply to increase the number of headings.

##### Comparison example — updater behavior

The following examples show the same updater behavior with different information structures.

###### Negative example — Hard to scan

```markdown
The updater preserves staged versus unstaged changes, untracked and
ignored files, symlinks, executable modes, conflicted indexes, and
previous commits. Submodule copies receive independent Git metadata.
Interrupted-operation metadata is saved as evidence; archived
operations are not automatically resumed in recovery copies.
```

###### Positive example — Easier to scan

```markdown
The updater preserves:

- staged versus unstaged changes
- untracked and ignored files
- symlinks
- executable modes
- conflicted indexes
- previous commits

The following rules apply:

- Submodule copies receive independent Git metadata.
- Interrupted-operation metadata is saved as evidence.
- Archived operations are not automatically resumed in recovery copies.
```

**Illustration scope:** This particular example separates preserved items from operational rules. In another document, the distinct groups might be alternatives and trade-offs, completed work and open questions, or other types determined by the content—not by this example.
