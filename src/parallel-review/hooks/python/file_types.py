"""Classify reviewable paths for both automatic and on-demand reviews."""
from pathlib import PurePath

CODE = frozenset(".py .pyi .js .jsx .ts .tsx .mjs .cjs .go .rs .java .kt .kts .swift .c .h .cc .cpp .hpp .cs .rb .php .scala .sh .bash .zsh .sql .css .scss .html .vue .svelte .lua .r .ex .exs .dart".split())
MARKDOWN = {".md", ".markdown", ".mdx"}


def kind(path: PurePath) -> str | None:
    suffix = path.suffix.lower()
    if suffix in {".py", ".pyi"}:
        return "python"
    if suffix in MARKDOWN:
        return "markdown"
    if suffix in CODE or path.name in {"Makefile", "Dockerfile"}:
        return "code"
    return None
