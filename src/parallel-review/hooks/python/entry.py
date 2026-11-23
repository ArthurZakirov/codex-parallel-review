"""Launch the packaged handler or this thread's explicitly selected development source."""
import io
import json
import os
from pathlib import Path
import runpy
import sys
from uuid import UUID


def main() -> None:
    payload = sys.stdin.read()
    event = json.loads(payload)
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    try:
        thread = UUID(event["session_id"])
    except ValueError:
        thread = None
    selection = home / "parallel-review-dev" / str(thread)
    directory = Path(__file__).resolve().parent
    if thread and selection.is_symlink():
        directory = selection / "src/parallel-review/hooks/python"
        if not (directory / "dispatch.py").is_file():
            sys.exit("Parallel Review development checkout is missing. Run ./develop in the active checkout.")
        # Same-size edits made within one second can otherwise reuse stale bytecode.
        sys.pycache_prefix = os.devnull
        sys.dont_write_bytecode = True
        selection.with_suffix(".last-event").write_text(
            f"{event['hook_event_name']} {directory.resolve()}\n"
        )

    sys.stdin = io.StringIO(payload)
    sys.path.insert(0, str(directory))
    runpy.run_path(str(directory / "dispatch.py"), run_name="__main__")


if __name__ == "__main__":
    main()
