"""Strip WebGoat's built-in answer key from a working copy.

Usage: python -I scrub_webgoat.py <copy> <answer-key-dir>

WebGoat is a lesson catalogue: its package names announce each vulnerability class and the
lesson text, hints, translations, solution pages, integration tests and source comments
describe the exact attack. This script keeps the code and the lesson HTML forms (the attack
surface) and removes the material that names the answer:

- top-level agent guidance, release notes, CI configuration, dependency-check suppressions
- src/it and src/test (every integration test is a worked solution)
- lesson documentation (AsciiDoc), lesson i18n (hints and success messages), lessonSolutions
- the two solution notes under src/main/resources/lessons
- every comment and every @AssignmentHints annotation in lesson Java sources
- HTML comments in lesson pages

Everything removed except .git and docs is copied to the answer-key directory first.
What stays, and cannot be removed without rewriting the application: package and class names,
the success()/failed() calls that mark each solved condition, and the i18n keys they reference.
"""

import json
import re
import shutil
import stat
import sys
from pathlib import Path
from typing import Dict, List, Union

REMOVE = [
    ".git",
    ".github",
    "docs",
    "AGENTS.md",
    "WEBGOAT_IN_THE_AGE_OF_AI.md",
    "RELEASE_NOTES.md",
    "CREATE_RELEASE.md",
    "release-explained.md",
    "config/dependency-check",
    "src/it",
    "src/test",
    "src/main/resources/lessons/sol.MD",
    "src/main/resources/lessons/sol.txt",
]
REMOVE_GLOBS = [
    "src/main/resources/lessons/*/documentation",
    "src/main/resources/lessons/*/i18n",
    "src/main/resources/lessons/*/lessonSolutions",
]
UNSAVED = {".git", "docs"}
STRIP_JAVA_UNDER = ["src/main/java/org/owasp/webgoat/lessons", "src/main/java/org/dummy"]
LESSON_RESOURCES = "src/main/resources/lessons"

SENTINEL = "\x00"
HINTS_IMPORT = re.compile(r"^import org\.owasp\.webgoat\.container\.assignments\.AssignmentHints;[ \t]*\r?\n", re.M)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def _skip_quoted(text: str, i: int, quote: str) -> int:
    """Return the index just past the literal that opens at text[i]."""
    j = i + 1
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == quote:
            return j + 1
        j += 1
    return len(text)


def _skip_text_block(text: str, i: int) -> int:
    end = text.find('"""', i + 3)
    return len(text) if end == -1 else end + 3


def _annotation_end(text: str, i: int) -> int:
    """Return the index just past the balanced parentheses of the annotation at text[i]."""
    j = text.find("(", i)
    if j == -1:
        return len(text)
    depth = 0
    while j < len(text):
        c = text[j]
        if c == '"':
            j = _skip_quoted(text, j, '"')
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return len(text)


def _mark_removals(text: str) -> str:
    """Replace comments and @AssignmentHints annotations with a sentinel; keep literals intact."""
    out: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if text.startswith('"""', i):
            j = _skip_text_block(text, i)
            out.append(text[i:j])
            i = j
        elif c in "\"'":
            j = _skip_quoted(text, i, c)
            out.append(text[i:j])
            i = j
        elif text.startswith("//", i):
            j = i
            while j < n and text[j] not in "\r\n":
                j += 1
            out.append(SENTINEL)
            i = j
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            out.append(SENTINEL)
            i = n if end == -1 else end + 2
        elif text.startswith("@AssignmentHints", i):
            out.append(SENTINEL)
            i = _annotation_end(text, i)
        else:
            out.append(c)
            i += 1
    return "".join(out)


def strip_java(text: str) -> str:
    """Remove every comment and @AssignmentHints annotation from Java source, preserving line endings."""
    marked = _mark_removals(HINTS_IMPORT.sub("", text))
    lines: List[str] = []
    for line in marked.splitlines(keepends=True):
        if SENTINEL not in line:
            lines.append(line)
            continue
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        body = body.replace(SENTINEL, "").rstrip(" \t")
        if body:
            lines.append(body + ending)
    return "".join(lines)


def _read(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _force_remove(func, path, _exc_info) -> None:
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def _rewrite(paths: List[Path], transform) -> int:
    changed = 0
    for path in paths:
        try:
            before = _read(path)
        except UnicodeDecodeError:
            continue
        after = transform(before)
        if after != before:
            _write(path, after)
            changed += 1
    return changed


def scrub(root: Union[str, Path], key_dir: Union[str, Path]) -> Dict[str, object]:
    root = Path(root).resolve()
    key_dir = Path(key_dir).resolve()
    key_dir.mkdir(parents=True, exist_ok=True)

    targets = [root / rel for rel in REMOVE]
    for pattern in REMOVE_GLOBS:
        targets.extend(sorted(root.glob(pattern)))

    removed: List[str] = []
    for path in targets:
        if not path.exists():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.split("/")[0] not in UNSAVED:
            dest = key_dir / rel
            if path.is_dir():
                shutil.copytree(path, dest, dirs_exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
        if path.is_dir():
            shutil.rmtree(path, onerror=_force_remove)
        else:
            path.unlink()
        removed.append(rel)

    java_files: List[Path] = []
    for base in STRIP_JAVA_UNDER:
        java_files.extend(sorted((root / base).rglob("*.java")))
    html_files = sorted((root / LESSON_RESOURCES).rglob("*.html"))

    summary: Dict[str, object] = {
        "removed": removed,
        "java_files_changed": _rewrite(java_files, strip_java),
        "html_files_changed": _rewrite(html_files, lambda text: HTML_COMMENT.sub("", text)),
    }
    (key_dir / "scrub-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    summary = scrub(argv[1], argv[2])
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
