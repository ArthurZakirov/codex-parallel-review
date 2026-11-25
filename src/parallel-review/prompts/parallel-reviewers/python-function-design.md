# Python function bodies

- Keep each function focused on one responsibility. Roughly 7–10 lines is a reading aid. A coherent longer function can stay together.
- Separate distinct steps with blank lines. When a step deserves a name, extract it into a private helper such as `_read_rows`.
- Extract fixed settings and meaningful repeated literals into named module-level constants. For example, define the report filename once alongside the other module constants.
- Keep each function at one level of abstraction. An orchestrator names the steps in the workflow. A low-level helper performs the filesystem or parsing operations for one step.

In this example, `build_report` describes the workflow. The helpers handle CSV parsing and row selection.

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
