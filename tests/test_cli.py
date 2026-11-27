import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from vacancy_analytics.cli import main


class DemoTests(unittest.TestCase):
    def test_demo_preserves_existing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vacancies.db"
            args = ["--db", str(path), "demo", "-n", "8"]
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(args), 0)
                before = path.read_bytes()
                self.assertEqual(main(args), 1)
            self.assertEqual(path.read_bytes(), before)
