"""Behavior tests for sink_inventory.py. Run: python3 -m unittest discover scripts"""

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import sink_inventory as si

REFERENCES = Path(__file__).resolve().parent.parent / "references"


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class DetectStacks(unittest.TestCase):
    def test_backend_manifests_map_to_their_stack(self) -> None:
        cases = {
            "go.mod": "go",
            "pom.xml": "java-kotlin",
            "build.gradle.kts": "java-kotlin",
            "pyproject.toml": "python",
            "requirements.txt": "python",
            "composer.json": "php",
            "Gemfile": "ruby",
            "Api.csproj": "dotnet",
        }
        for manifest, stack in cases.items():
            with tempfile.TemporaryDirectory() as tmp:
                write(Path(tmp), manifest, "")
                self.assertEqual(si.detect_stacks(Path(tmp)), [stack], manifest)

    def test_package_json_with_server_dependency_is_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "package.json", json.dumps({"dependencies": {"express": "4"}}))
            self.assertEqual(si.detect_stacks(Path(tmp)), ["javascript-node"])

    def test_package_json_with_only_spa_dependencies_is_frontend_not_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "package.json", json.dumps({"dependencies": {"react": "19", "vite": "5"}}))
            self.assertEqual(si.detect_stacks(Path(tmp)), ["frontend"])

    def test_meta_framework_is_both_frontend_and_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "package.json", json.dumps({"dependencies": {"next": "15", "react": "19"}}))
            self.assertEqual(si.detect_stacks(Path(tmp)), ["frontend", "javascript-node"])

    def test_nested_manifests_in_a_monorepo_are_found_and_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "api/build.gradle.kts", "")
            write(Path(tmp), "web/package.json", json.dumps({"dependencies": {"react": "18"}}))
            write(Path(tmp), "web/node_modules/dep/package.json", json.dumps({"dependencies": {"express": "4"}}))
            self.assertEqual(si.detect_stacks(Path(tmp)), ["frontend", "java-kotlin"])


class LoadSearches(unittest.TestCase):
    def test_parses_category_and_regex_lines_from_the_starting_searches_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp) / "stack.md"
            ref.write_text(
                "# Stack\n\n## Topic leads\n\n```text\nnot this: block\n```\n\n"
                "## Starting searches\n\n```text\nEntry points: app\\.get|router\\.\nInterpreters: exec\\(\n```\n",
                encoding="utf-8",
            )
            self.assertEqual(
                si.load_searches(ref),
                [("Entry points", r"app\.get|router\."), ("Interpreters", r"exec\(")],
            )

    def test_every_bundled_reference_with_searches_has_only_compilable_patterns(self) -> None:
        files = list((REFERENCES / "stacks").glob("*.md")) + [
            REFERENCES / "frontend-frameworks.md",
            REFERENCES / "frontend-runtime.md",
        ]
        checked = 0
        for ref in files:
            if ref.name == "README.md":
                continue
            searches = si.load_searches(ref)
            self.assertTrue(searches, f"{ref.name} has no Starting searches block")
            for category, pattern in searches:
                re.compile(pattern)
                checked += 1
        self.assertGreater(checked, 20)

    def test_every_detectable_stack_resolves_to_existing_reference_files(self) -> None:
        for stack, files in si.STACK_REFERENCES.items():
            for rel in files:
                self.assertTrue((REFERENCES.parent / rel).is_file(), f"{stack}: {rel}")


class Scan(unittest.TestCase):
    def test_reports_category_file_line_and_excerpt_for_a_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "src/run.js", "const x = 1;\nchild_process.exec(cmd);\n")
            leads = si.scan(root, [("Interpreters", r"child_process|exec\(")], stack="javascript-node")
            self.assertEqual(len(leads), 1)
            lead = leads[0]
            self.assertEqual((lead.stack, lead.category, lead.path, lead.line), ("javascript-node", "Interpreters", "src/run.js", 2))
            self.assertEqual(lead.excerpt, "child_process.exec(cmd);")

    def test_one_line_matching_two_patterns_in_the_same_category_is_reported_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "a.js", "child_process.exec(cmd);\n")
            leads = si.scan(root, [("Interpreters", r"child_process|exec\(")], stack="js")
            self.assertEqual(len(leads), 1)

    def test_vendor_build_and_vcs_directories_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ["node_modules/x/a.js", "dist/a.js", ".git/a.js", "target/a.kt", "vendor/a.php", ".next/a.js"]:
                write(root, rel, "exec(cmd)\n")
            write(root, "src/a.js", "exec(cmd)\n")
            leads = si.scan(root, [("Interpreters", r"exec\(")], stack="js")
            self.assertEqual([lead.path for lead in leads], ["src/a.js"])

    def test_other_agent_skills_in_the_repository_are_still_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, ".claude/skills/web-security-audit/SKILL.md", "---\nname: web-security-audit\n---\n")
            write(root, ".claude/skills/web-security-audit/evals/a.js", "exec(cmd)\n")
            write(root, ".claude/skills/deploy/SKILL.md", "---\nname: deploy\n---\n")
            write(root, ".claude/skills/deploy/run.js", "exec(cmd)\n")
            leads = si.scan(root, [("Interpreters", r"exec\(")], stack="js")
            self.assertEqual([lead.path for lead in leads], [".claude/skills/deploy/run.js"])

    def test_binary_files_are_skipped_and_long_excerpts_are_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "blob.bin").write_bytes(b"exec(\x00\x01\x02")
            write(root, "bundle.js", "exec(" + "a" * 500 + ")\n")
            leads = si.scan(root, [("Interpreters", r"exec\(")], stack="js")
            self.assertEqual([lead.path for lead in leads], ["bundle.js"])
            self.assertLessEqual(len(leads[0].excerpt), si.EXCERPT_LIMIT + 1)
            self.assertTrue(leads[0].excerpt.endswith("…"))

    def test_an_invalid_pattern_is_reported_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "a.js", "exec(cmd)\n")
            leads = si.scan(root, [("Broken", r"exec(("), ("Interpreters", r"exec\(")], stack="js")
            self.assertEqual([lead.category for lead in leads], ["Interpreters"])


class Cli(unittest.TestCase):
    def run_cli(self, *args: str) -> str:
        out = io.StringIO()
        with redirect_stdout(out):
            code = si.main(list(args))
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_json_output_lists_detected_stacks_and_leads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "go.mod", "module example\n")
            write(root, "main.go", 'package main\nfunc h() { exec.Command("sh", "-c", c) }\n')
            data = json.loads(self.run_cli(str(root), "--json"))
            self.assertEqual(data["stacks"], ["go"])
            paths = {(lead["path"], lead["line"]) for lead in data["leads"]}
            self.assertIn(("main.go", 2), paths)

    def test_markdown_output_groups_leads_under_stack_and_category_headings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "Gemfile", "")
            write(root, "app/x.rb", "Marshal.load(data)\n")
            text = self.run_cli(str(root))
            self.assertIn("Stacks: ruby", text)
            self.assertIn("## ruby: Interpreters", text)
            self.assertIn("| app/x.rb:1 |", text)

    def test_forced_stack_overrides_detection_and_unknown_stack_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "x.py", "pickle.loads(b)\n")
            data = json.loads(self.run_cli(str(root), "--stack", "python", "--json"))
            self.assertEqual(data["stacks"], ["python"])
            self.assertEqual(data["leads"][0]["path"], "x.py")
            self.assertNotEqual(si.main([str(root), "--stack", "cobol"]), 0)

    def test_installed_copies_of_this_skill_are_neither_detected_nor_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "go.mod", "module example\n")
            write(root, "main.go", 'package main\nfunc h() { exec.Command("sh", "-c", c) }\n')
            for skills_dir in [".claude/skills", ".agents/skills"]:
                copy = f"{skills_dir}/web-security-audit"
                write(root, f"{copy}/SKILL.md", "---\nname: web-security-audit\ndescription: x\n---\n")
                write(root, f"{copy}/evals/fixtures/shop/package.json", json.dumps({"dependencies": {"express": "4"}}))
                write(root, f"{copy}/evals/fixtures/shop/server.go", 'func h() { exec.Command("sh", "-c", c) }\n')
            data = json.loads(self.run_cli(str(root), "--json"))
            self.assertEqual(data["stacks"], ["go"])
            self.assertEqual({lead["path"] for lead in data["leads"]}, {"main.go"})

    def test_no_detected_stack_still_runs_the_frontend_and_node_searches_with_a_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "page.js", "el.innerHTML = data;\n")
            data = json.loads(self.run_cli(str(root), "--json"))
            self.assertEqual(data["stacks"], [])
            self.assertTrue(data["note"])
            self.assertIn("page.js", {lead["path"] for lead in data["leads"]})


if __name__ == "__main__":
    unittest.main()
