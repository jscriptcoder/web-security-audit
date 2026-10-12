"""Strip Juice Shop's built-in answer key from a working copy. Usage: scrub_juice.py <copy> <answer_key_dir>"""
import json, re, shutil, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
key_dir = Path(sys.argv[2]).resolve()
key_dir.mkdir(parents=True, exist_ok=True)

# 1. Keep the answer key outside the tree.
for rel in ["data/static/challenges.yml", "rsn/cache.json", "threat-model.json"]:
    src = root / rel
    if src.exists():
        shutil.copy2(src, key_dir / src.name)

# 2. Collect challenge keys before deleting the registry.
keys = sorted(set(re.findall(r"^\s*-\s*name:.*$|^\s*key:\s*(\w+)\s*$", (root / "data/static/challenges.yml").read_text(encoding="utf-8"), re.M)))
keys = sorted(k for k in keys if k)
code_keys = set()
for path in root.rglob("*"):
    if path.is_file() and path.suffix in {".ts", ".js", ".html", ".yml", ".json"} and ".git" not in path.parts and "node_modules" not in path.parts:
        code_keys.update(re.findall(r"\b([a-z][A-Za-z0-9]*Challenge)\b", path.read_text(encoding="utf-8", errors="replace")))
all_keys = sorted(set(keys) | code_keys)
mapping = {k: f"challenge{idx:03d}" for idx, k in enumerate(all_keys, start=1)}
(key_dir / "rename-map.json").write_text(json.dumps(mapping, indent=1), encoding="utf-8")

# 3. Delete solution material, tests, agent guidance and history.
removed = ["data/static/challenges.yml", "data/static/i18n", "data/static/codefixes", "frontend/src/hacking-instructor",
           "test", "rsn", "SOLUTIONS.md", "HALL_OF_FAME.md", "REFERENCES.md", "threat-model.json", "AGENTS.md",
           ".ai", ".claude", ".codeium", ".continue", ".cursor", ".junie", ".github", "screenshots", ".git",
           "cypress.config.ts", "docker-compose.test.yml"]
gone = []
for rel in removed:
    p = root / rel
    if p.is_dir():
        shutil.rmtree(p, onerror=lambda f, path, exc: (Path(path).chmod(0o700), f(path)))
        gone.append(rel)
    elif p.is_file():
        p.unlink(); gone.append(rel)

# 4. Scrub marker comments and rename challenge keys in every text file.
marker_line = re.compile(r"\s*(//|#|<!--)\s*vuln-code-snippet.*?(-->)?\s*$")
key_re = re.compile(r"\b(" + "|".join(map(re.escape, sorted(all_keys, key=len, reverse=True))) + r")\b")
scrubbed_lines = renamed = 0
for path in root.rglob("*"):
    if not path.is_file() or "node_modules" in path.parts:
        continue
    if path.suffix not in {".ts", ".js", ".html", ".yml", ".yaml", ".json", ".md", ".scss", ".css", ".txt"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    lines = []
    for line in text.splitlines(keepends=True):
        if "vuln-code-snippet" in line:
            scrubbed_lines += 1
            stripped = marker_line.sub("", line.rstrip("\r\n"))
            if not stripped.strip():
                continue
            line = stripped + ("\r\n" if line.endswith("\r\n") else "\n")
        lines.append(line)
    new = "".join(lines)
    new, n = key_re.subn(lambda m: mapping[m.group(1)], new)
    renamed += n
    if new != text:
        path.write_text(new, encoding="utf-8")

print(json.dumps({"removed": gone, "challenge_keys": len(all_keys), "renamed_occurrences": renamed, "marker_lines": scrubbed_lines}, indent=1))
