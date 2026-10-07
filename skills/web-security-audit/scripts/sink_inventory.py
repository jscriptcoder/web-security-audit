#!/usr/bin/env python3
"""First-pass lead inventory for a web security audit.

Detects the stacks in a repository from its manifests, runs the `Starting
searches` patterns of the matching reference files and prints one table of
leads. A lead is a place to read, not a finding.

Usage: sink_inventory.py <path> [--stack NAME ...] [--json]
Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Optional

SKILL_ROOT = Path(__file__).resolve().parent.parent

# Stack name -> reference files (relative to the skill root) whose
# `Starting searches` block supplies the patterns.
STACK_REFERENCES: dict[str, list[str]] = {
    "frontend": ["references/frontend-frameworks.md", "references/frontend-runtime.md"],
    "javascript-node": ["references/stacks/javascript-node.md"],
    "java-kotlin": ["references/stacks/java-kotlin.md"],
    "python": ["references/stacks/python.md"],
    "dotnet": ["references/stacks/dotnet.md"],
    "go": ["references/stacks/go.md"],
    "php": ["references/stacks/php.md"],
    "ruby": ["references/stacks/ruby.md"],
}

MANIFESTS: dict[str, str] = {
    "pom.xml": "java-kotlin",
    "build.gradle": "java-kotlin",
    "build.gradle.kts": "java-kotlin",
    "pyproject.toml": "python",
    "Pipfile": "python",
    "setup.py": "python",
    "go.mod": "go",
    "composer.json": "php",
    "Gemfile": "ruby",
}
MANIFEST_SUFFIXES: dict[str, str] = {".csproj": "dotnet", ".sln": "dotnet"}
REQUIREMENTS = re.compile(r"^requirements[\w.-]*\.txt$")

FRONTEND_DEPENDENCIES = {
    "react", "react-dom", "vue", "@angular/core", "svelte", "solid-js", "lit",
    "next", "nuxt", "@sveltejs/kit", "@remix-run/react", "astro", "jquery",
}
NODE_SERVER_DEPENDENCIES = {
    "express", "fastify", "koa", "@hapi/hapi", "@nestjs/core", "hono", "apollo-server",
    "@apollo/server", "graphql-yoga", "next", "nuxt", "@sveltejs/kit", "@remix-run/node",
    "prisma", "@prisma/client", "mongoose", "sequelize", "knex", "typeorm", "ws", "socket.io",
}

EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "dist", "build", "out",
    ".next", ".nuxt", ".svelte-kit", ".output", "target", "bin", "obj", "vendor",
    "coverage", "__pycache__", ".venv", "venv", ".idea", ".vscode", ".gradle", ".tox",
}
# Installers such as `npx skills add` copy this whole skill, eval fixtures included,
# into the audited repository; its intentionally vulnerable code is not the target's.
SKILL_NAME_LINE = re.compile(r"^name:\s*web-security-audit\s*$", re.MULTILINE)
MAX_FILE_BYTES = 2_000_000
EXCERPT_LIMIT = 160


@dataclass(frozen=True)
class Lead:
    stack: str
    category: str
    path: str
    line: int
    excerpt: str


def _dependencies(package_json: Path) -> set[str]:
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = data.get(key) if isinstance(data, dict) else None
        if isinstance(section, dict):
            names.update(section.keys())
    return names


def _stacks_for_package_json(path: Path) -> list[str]:
    deps = _dependencies(path)
    stacks: list[str] = []
    if deps & FRONTEND_DEPENDENCIES:
        stacks.append("frontend")
    if deps & NODE_SERVER_DEPENDENCIES or not (deps & FRONTEND_DEPENDENCIES):
        stacks.append("javascript-node")
    return stacks


def _is_this_skill(directory: Path) -> bool:
    try:
        return bool(SKILL_NAME_LINE.search((directory / "SKILL.md").read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return False


def _walk(root: Path) -> tuple[list[Path], list[Path]]:
    """Return the files under root and the directories left unread as excluded or as a copy of this skill."""
    files: list[Path] = []
    skipped: list[Path] = []
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda p: p.name)
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name in EXCLUDED_DIRS or _is_this_skill(entry):
                    skipped.append(entry)
                else:
                    pending.append(entry)
            elif entry.is_file():
                files.append(entry)
    return files, skipped


def detect_stacks(root: Path) -> list[str]:
    """Return the sorted, deduplicated stacks whose manifests appear under root."""
    files, _ = _walk(root)
    return _stacks_from_manifests(files)


def _stacks_from_manifests(files: Iterable[Path]) -> list[str]:
    found: set[str] = set()
    for path in files:
        name = path.name
        if name == "package.json":
            found.update(_stacks_for_package_json(path))
        elif name in MANIFESTS:
            found.add(MANIFESTS[name])
        elif path.suffix in MANIFEST_SUFFIXES:
            found.add(MANIFEST_SUFFIXES[path.suffix])
        elif REQUIREMENTS.match(name):
            found.add("python")
    return sorted(found)


def load_searches(reference: Path) -> list[tuple[str, str]]:
    """Parse `Category: regex` lines from the fenced block under `## Starting searches`."""
    text = reference.read_text(encoding="utf-8")
    match = re.search(r"^## Starting searches\s*\n+```[a-z]*\n(.*?)^```", text, re.S | re.M)
    if not match:
        return []
    searches: list[tuple[str, str]] = []
    for line in match.group(1).splitlines():
        if ": " not in line:
            continue
        category, pattern = line.split(": ", 1)
        if category.strip() and pattern.strip():
            searches.append((category.strip(), pattern.strip()))
    return searches


def _compile(searches: Iterable[tuple[str, str]]) -> tuple[list[tuple[str, re.Pattern[str]]], list[str]]:
    compiled: list[tuple[str, re.Pattern[str]]] = []
    errors: list[str] = []
    for category, pattern in searches:
        try:
            compiled.append((category, re.compile(pattern)))
        except re.error as exc:
            errors.append(f"{category}: cannot compile /{pattern}/: {exc}")
    return compiled, errors


def _is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(1024)
    except OSError:
        return True


def _excerpt(line: str) -> str:
    stripped = line.strip()
    return stripped if len(stripped) <= EXCERPT_LIMIT else stripped[:EXCERPT_LIMIT] + "…"


def _text_lines(path: Path) -> Optional[list[str]]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES or _is_binary(path):
            return None
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


Compiled = dict[str, list[tuple[str, re.Pattern[str]]]]


def _scan_files(root: Path, files: Iterable[Path], compiled: Compiled) -> list[Lead]:
    """Read each file once and run every stack's searches over it, one lead per stack and category per line."""
    leads: list[Lead] = []
    for path in files:
        lines = _text_lines(path)
        if lines is None:
            continue
        rel = path.relative_to(root).as_posix()
        for number, line in enumerate(lines, start=1):
            for stack, searches in compiled.items():
                seen: set[str] = set()
                for category, pattern in searches:
                    if category in seen or not pattern.search(line):
                        continue
                    seen.add(category)
                    leads.append(Lead(stack, category, rel, number, _excerpt(line)))
    return leads


def scan(root: Path, searches: Iterable[tuple[str, str]], stack: str, errors: Optional[list[str]] = None) -> list[Lead]:
    """Run each search over the text files under root. Invalid patterns are recorded, not raised."""
    compiled, compile_errors = _compile(searches)
    if errors is not None:
        errors.extend(compile_errors)
    files, _ = _walk(root)
    return _scan_files(root, files, {stack: compiled})


def inventory(root: Path, stacks: list[str], files: Iterable[Path]) -> tuple[list[Lead], list[str]]:
    errors: list[str] = []
    compiled: Compiled = {}
    # Stacks in the given order, then categories in the order their reference declares them.
    rank: dict[tuple[str, str], int] = {}
    for stack in stacks:
        for rel in STACK_REFERENCES[stack]:
            reference = SKILL_ROOT / rel
            if not reference.is_file():
                errors.append(f"{stack}: missing reference {rel}")
                continue
            searches = load_searches(reference)
            for category, _ in searches:
                rank.setdefault((stack, category), len(rank))
            patterns, compile_errors = _compile(searches)
            compiled.setdefault(stack, []).extend(patterns)
            errors.extend(compile_errors)
    leads = _scan_files(root, files, compiled)
    return sorted(leads, key=lambda lead: (rank[(lead.stack, lead.category)], lead.path, lead.line)), errors


def _code_span(text: str) -> str:
    """Fence text with more backticks than its longest backtick run, so template literals and shell backticks stay inside."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    if not longest:
        return f"`{text}`"
    fence = "`" * (longest + 1)
    return f"{fence} {text} {fence}"


def render_markdown(root: Path, stacks: list[str], leads: list[Lead], errors: list[str], note: str, skipped: list[str]) -> str:
    lines = [f"# Sink inventory for {root}", "", f"Stacks: {', '.join(stacks) if stacks else 'none detected'}"]
    if note:
        lines.append(f"Note: {note}")
    if skipped:
        counts = Counter(PurePosixPath(rel).name for rel in skipped)
        lines.append("Skipped directories: " + ", ".join(f"`{name}` ({count})" for name, count in sorted(counts.items())))
    lines += ["", "Leads are places to read, not findings. Judge each against the matching reference.", ""]
    groups: dict[tuple[str, str], list[Lead]] = {}
    for lead in leads:
        groups.setdefault((lead.stack, lead.category), []).append(lead)
    for (stack, category), items in groups.items():
        lines += [f"## {stack}: {category} ({len(items)})", "", "| Location | Excerpt |", "| --- | --- |"]
        for lead in items:
            excerpt = lead.excerpt.replace("|", "\\|")
            lines.append(f"| {lead.path}:{lead.line} | {_code_span(excerpt)} |")
        lines.append("")
    if not leads:
        lines += ["No leads matched. Check the stack detection and the excluded directories.", ""]
    if errors:
        lines += ["## Errors", ""] + [f"- {error}" for error in errors] + [""]
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="repository or directory to inventory")
    parser.add_argument("--stack", action="append", default=[], help=f"force a stack ({', '.join(STACK_REFERENCES)}); repeatable")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    unknown = [stack for stack in args.stack if stack not in STACK_REFERENCES]
    if unknown:
        print(f"unknown stack(s): {', '.join(unknown)}; choose from {', '.join(STACK_REFERENCES)}", file=sys.stderr)
        return 2

    files, skipped_dirs = _walk(root)
    skipped = sorted(path.relative_to(root).as_posix() for path in skipped_dirs)
    stacks = sorted(set(args.stack)) if args.stack else _stacks_from_manifests(files)
    note = ""
    effective = stacks
    if not stacks:
        effective = ["frontend", "javascript-node"]
        note = "no manifest recognized; ran the frontend and Node searches as a fallback. Use --stack to choose."
    leads, errors = inventory(root, effective, files)

    if args.json:
        print(json.dumps({"root": str(root), "stacks": stacks, "searched_stacks": effective, "note": note, "leads": [asdict(lead) for lead in leads], "errors": errors, "skipped": skipped}, indent=2))
    else:
        print(render_markdown(root, stacks, leads, errors, note, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
