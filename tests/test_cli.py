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
