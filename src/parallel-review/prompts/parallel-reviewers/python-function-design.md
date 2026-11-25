# Python function design

## Function bodies

- Keep each function focused on one responsibility. Roughly 7–10 lines is a reading aid. A coherent longer function can stay together.
- Separate distinct steps with blank lines. When a step deserves a name, extract it into a private helper such as `_read_rows`.
- Keep each function at one level of abstraction. An orchestrator names the steps in the workflow. A low-level helper performs the filesystem or parsing operations for one step.

## Module constants

Extract fixed settings and meaningful repeated literals from function bodies into named module-level constants.

## Closed sets of values

When branches compare raw strings that represent a known set of states, modes, or actions, look for an existing domain type first. Choose the representation according to how the values are used:

- Use an `Enum` for named members that code compares, such as `Decision.APPROVE`. Use a string-valued enum when a CLI, API, or stored record also requires specific string values. Preserve those external values.
- Use `Literal["approve", "reject"]` when callers already pass strings and a type annotation is sufficient. A `Literal` annotation alone does not validate incoming data at runtime.

Limit findings to sets the evidence shows are closed. Free-form messages and arbitrary user input can remain strings.

## Example

`REPORT_FILENAME` names the fixed input file. `build_report` describes the workflow, while the helpers handle CSV parsing and row selection.

```python
import csv
from pathlib import Path

REPORT_FILENAME = "report.csv"


def build_report(directory: Path) -> list[str]:
    rows = _read_rows(directory / REPORT_FILENAME)
    return _select_names(rows)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def _select_names(rows: list[dict[str, str]]) -> list[str]:
    return [row["name"] for row in rows if row.get("name")]
```
