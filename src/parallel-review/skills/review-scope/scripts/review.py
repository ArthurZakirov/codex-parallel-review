"""Collect explicit full-file evidence and run the plugin's shared review roles."""
import argparse
import os
from pathlib import Path
import sys
from tempfile import mkdtemp

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / "hooks/python"))
from reviews import review_batches
from file_types import kind

BATCH_CHARS = 48_000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--focus", default="")
    args = parser.parse_args()

    files = selected_files(args.paths)
    if not files:
        parser.error("No supported code or Markdown files in the selected paths.")

    boundary = (PLUGIN / "prompts/shared/selected-scope.md").read_text().strip()
    if args.focus:
        boundary += "\n\nUser's review focus:\n" + args.focus
    report = review_batches(evidence_batches(files), boundary)
    inventory = "\n".join(f"- `{file}`" for file in files)

    destination = Path(mkdtemp(prefix="parallel-review-")) / "review.md"
    destination.write_text(report + "\n## Reviewed files\n\n" + inventory + "\n")
    print(destination)


def selected_files(paths: list[Path]) -> list[Path]:
    files = set()

    for path in paths:
        if path.is_symlink() or not path.exists():
            raise ValueError(f"Expected an existing file or directory: {path}")
        if path.is_file():
            if not kind(path):
                raise ValueError(f"No reviewer for {path}")
            files.add(path.resolve())
            continue
        for directory, folders, names in os.walk(path, onerror=_raise_error):
            folders[:] = [name for name in folders if name != ".git"]
            for name in names:
                entry = Path(directory) / name
                if kind(entry) and not entry.is_symlink() and entry.is_file():
                    files.add(entry.resolve())
    return sorted(files)


def _raise_error(error: OSError) -> None:
    raise error


def evidence_batches(files: list[Path]) -> list[dict[str, list[str]]]:
    batches = []
    groups = {}
    size = 0
    for path in files:
        source = path.read_text(encoding="utf-8")
        numbered = "\n".join(f"{number} | {line}" for number, line in enumerate(source.splitlines(), 1))
        content = f"Full file {path} (line number | literal source):\n{numbered}"
        if groups and size + len(content) > BATCH_CHARS:
            batches.append(groups)
            groups = {}
            size = 0
        groups.setdefault(kind(path), []).append(content)
        size += len(content)
    if groups:
        batches.append(groups)
    return batches


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        sys.exit(str(exc))
