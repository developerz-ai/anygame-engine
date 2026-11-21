import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_docs import check, github_slug


class CheckDocsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def codes(self):
        return [error["code"] for error in check(self.root)]

    def test_clean_docs_pass(self):
        self.write("docs/idea/README.md", "[A](a.md#-hello-world)\n")
        self.write("docs/idea/a.md", "## 🧠 Hello, world\n\n| x | y |\n|---|---|\n| 1 | 2 |\n")
        self.assertEqual(self.codes(), [])

    def test_broken_link(self):
        self.write("a.md", "[x](missing.md)\n")
        self.assertEqual(self.codes(), ["broken-link"])

    def test_link_outside_repo_is_broken(self):
        self.write("a.md", "[x](../../outside.md)\n")
        self.assertEqual(self.codes(), ["broken-link"])

    def test_broken_anchor(self):
        self.write("a.md", "# Title\n\n[x](#nope)\n")
        self.assertEqual(self.codes(), ["broken-anchor"])

    def test_links_in_code_are_ignored(self):
        self.write("a.md", "`[x](no.md)`\n\n```md\n[y](no.md)\n```\n")
        self.assertEqual(self.codes(), [])

    def test_unindexed_doc(self):
        self.write("docs/build/README.md", "# Build\n")
        self.write("docs/build/phase.md", "# Phase\n")
        self.assertEqual(self.codes(), ["unindexed-doc"])

    def test_table_with_wrong_cell_count(self):
        self.write("a.md", "| x | y |\n|---|---|\n| 1 | 2 | 3 |\n")
        self.assertEqual(self.codes(), ["table-columns"])

    def test_escaped_pipe_is_one_cell(self):
        self.write("a.md", "| x | y |\n|---|---|\n| a\\|b | 2 |\n")
        self.assertEqual(self.codes(), [])

    def test_unclosed_fence(self):
        self.write("a.md", "```cpp\nint x;\n")
        self.assertEqual(self.codes(), ["unclosed-fence"])

    def test_secret_value_is_never_reported(self):
        token = "ghp_" + "a" * 36
        self.write("notes.txt", f"token={token}\n")
        errors = check(self.root)
        self.assertEqual([e["code"] for e in errors], ["secret"])
        self.assertNotIn(token, str(errors))

    def test_slug_matches_github(self):
        self.assertEqual(github_slug("🔥 Profilers: which one?"), "-profilers-which-one")


if __name__ == "__main__":
    unittest.main()
