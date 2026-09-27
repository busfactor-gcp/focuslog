import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from focuslog.cli import main


class FocuslogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name) / "tasks.json"

    def run_cli(self, *args):
        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = main(["--data", str(self.data), *args])
        return code, output.getvalue(), errors.getvalue()

    def tasks(self):
        return json.loads(self.data.read_text())["tasks"]

    def test_add_and_list(self):
        self.assertEqual(self.run_cli("add", "Write outline")[0], 0)
        self.assertEqual(self.run_cli("add", "Book room")[0], 0)
        self.assertEqual([task["id"] for task in self.tasks()], [1, 2])
        self.assertIn("Write outline", self.run_cli("list")[1])


if __name__ == "__main__":
    unittest.main()


class WorkflowTests(FocuslogTests):
    def test_edit_export_import_and_clear(self):
        self.run_cli("add", "First", "--tag", "work", "--due", "2026-10-01")
        self.run_cli("add", "Second", "--priority", "high")
        self.assertEqual(self.run_cli("edit", "1", "--title", "Revised")[0], 0)
        self.assertIn("Revised", self.run_cli("search", "revised")[1])
        self.run_cli("done", "1")
        csv_path = Path(self.temp.name) / "tasks.csv"
        self.assertEqual(self.run_cli("export", str(csv_path))[0], 0)
        self.assertIn("Revised", csv_path.read_text())
        self.assertEqual(self.run_cli("import", str(csv_path))[0], 0)
        self.assertEqual(len(self.tasks()), 4)
        self.assertEqual(self.run_cli("clear-completed")[0], 0)
        self.assertEqual([task["title"] for task in self.tasks()], ["Second", "Second"])

    def test_invalid_import_is_atomic(self):
        self.run_cli("add", "Existing")
        csv_path = Path(self.temp.name) / "bad.csv"
        csv_path.write_text("title,done,priority,tags,due\nBad,maybe,high,,\n")
        code, _, error = self.run_cli("import", str(csv_path))
        self.assertEqual(code, 2)
        self.assertIn("done must be true or false", error)
        self.assertEqual([task["title"] for task in self.tasks()], ["Existing"])
