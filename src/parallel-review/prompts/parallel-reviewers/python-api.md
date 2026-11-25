# Python names and public interfaces

## Names

- Name functions and methods for actions. Prefer `translate_row` to `translator` and `build_error_message` to `error_message_builder`. Omit redundant suffixes such as `_func`.
- Name an operation for what its layer does. A query builder that filters by area can expose `filter_by_area` without naming the user or service that calls it.
- Give CLI entry points descriptive names such as `deploy_bundle` or `generate_eval_dataset`. Call that function directly from the script guard.

```python
if __name__ == "__main__":
    deploy_bundle()
```

## Interfaces and ownership

- Annotate function and method parameters and return values. The implicit `self` or `cls` can remain unannotated.
- Prefer standard-library types when they express the same contract as a custom type. For example, use `collections.abc.Callable[[str], int]` for a callback that accepts a string and returns an integer.
- Keep the public API small. Once `resolve_id` handles external callers' needs, keep its lookup helpers private when the evidence confirms they have no external callers.
- Match a module's structure to its name. A module named `dependency_fetcher` suggests a `DependencyFetcher` class that groups the fetching operations. Authentication helpers specific to one client belong on that client.

## Conventions across peers

- Check comparable elements such as columns, CLI commands, method signatures, test assertions, and file structures. Flag a change that introduces an unexplained exception to the established pattern.
- Apply the same check to related modules. If peer client modules consistently expose classes, a new module exposing only loose functions needs a reason for that difference.
- Prefer absolute imports. Existing packages that consistently use relative imports may keep that convention.
