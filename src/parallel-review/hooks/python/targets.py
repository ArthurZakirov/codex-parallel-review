"""Resolve literal shell destinations without executing shell input."""
from collections.abc import Iterator
from pathlib import Path
import os
import re
import shlex

from file_types import kind


def shell_targets(command: str, cwd: Path) -> tuple[set[Path], set[Path]]:
    roots, files = {cwd}, set()
    current = cwd
    for words in _commands(command):
        for index, word in enumerate(words):
            if word in ("cd", "pushd"):
                args = words[index + 1:]
                if args[:1] == ["--"]:
                    args = args[1:]
                if args:
                    target = _literal(args[0], current)
                    if target is not None:
                        current = target
                        roots.add(current)
                break
            target = _literal(word, current)
            if target is not None and kind(target):
                files.add(target)
    return roots, files


def _literal(word: str, cwd: Path) -> Path | None:
    if not word or word.startswith("-"):
        return None
    word = os.path.expandvars(word)
    if any(char in word for char in "$`*?\n"):
        return None
    try:
        return Path(os.path.abspath(cwd / Path(word).expanduser()))
    except (RuntimeError, OSError, ValueError):
        return None


def _commands(command: str) -> Iterator[list[str]]:
    delimiter = None
    for line in command.splitlines():
        if delimiter:
            if line.lstrip("\t") == delimiter:
                delimiter = None
            continue
        heredoc = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line)
        if heredoc:
            delimiter = heredoc[1]
        lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|()<>")
        lexer.whitespace_split = True
        words = []
        try:
            for word in lexer:
                if word in (";", "&&", "||", "|", "&", "(", ")"):
                    yield words
                    words = []
                else:
                    words.append(word)
        except ValueError:
            continue
        yield words
