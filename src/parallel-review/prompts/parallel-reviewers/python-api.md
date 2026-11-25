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

## Function inputs and results

Flag a hidden record shape when the evidence shows either pattern:

- A function accepts a generic dictionary but relies on particular keys. Its signature should identify the required and optional fields and their types.
- A function returns a positional tuple, or accepts a collection of tuples, whose positions represent distinct fields that callers must remember. Give those fields meaningful names and types.

Prefer an existing record type. If a new type is needed, choose it according to the caller's contract.

- Use a dataclass for a domain record.
- Use a `TypedDict` when callers need dictionary access.
- Use a `NamedTuple` when callers need tuple compatibility.

A `TypedDict` describes the expected shape to a type checker. When runtime guarantees are needed, validate untrusted JSON at the input boundary.

Keep ordinary collections when their existing types express the contract, such as a mapping from arbitrary IDs to counts.

## Conventions across peers

- Check comparable elements such as columns, CLI commands, method signatures, test assertions, and file structures. Flag a change that introduces an unexplained exception to the established pattern.
- Apply the same check to related modules. If peer client modules consistently expose classes, a new module exposing only loose functions needs a reason for that difference.

## Imports

Prefer absolute imports. Existing packages that consistently use relative imports may keep that convention.
