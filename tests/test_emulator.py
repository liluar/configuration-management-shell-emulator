import unittest

from contextlib import redirect_stdout
from io import StringIO
from src.main import execute_command, parse_input

class TestEmulator(unittest.TestCase):
    def test_parse_ls(self):
        command, args = parse_input("ls")

        self.assertEqual(command, "ls")
        self.assertEqual(args, [])

    def test_parse_cd_with_argument(self):
        command, args = parse_input("cd home")

        self.assertEqual(command, "cd")
        self.assertEqual(args, ["home"])

    def test_exit(self):
        result = execute_command("exit", [])

        self.assertFalse(result)

    def test_ls(self):
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("ls", ["home"])

        self.assertTrue(result)
        self.assertEqual(output.getvalue().strip(), "ls ['home']")

    def test_cd(self):
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("cd", ["home"])

        self.assertTrue(result)
        self.assertEqual(output.getvalue().strip(), "cd ['home']")

    def test_unknown_command(self):
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("hello", [])

        self.assertTrue(result)
        self.assertEqual(
            output.getvalue().strip(),
            "Unknown command: hello"
        )