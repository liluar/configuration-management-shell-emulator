import unittest

from contextlib import redirect_stdout
from io import StringIO
from src.main import (
    execute_command,
    parse_cli_args,
    parse_input,
    run_startup_script,
)

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

    def test_parse_vfs_argument(self):
        args = parse_cli_args(["--vfs", "example_vfs.xml"])

        self.assertEqual(args.vfs, "example_vfs.xml")
        self.assertIsNone(args.script)

    def test_parse_script_argument(self):
        args = parse_cli_args(["--script", "scripts/startup.txt"])

        self.assertIsNone(args.vfs)
        self.assertEqual(args.script, "scripts/startup.txt")

    def test_parse_all_arguments(self):
        args = parse_cli_args([
            "--vfs",
            "example_vfs.xml",
            "--script",
            "scripts/startup.txt"
        ])

        self.assertEqual(args.vfs, "example_vfs.xml")
        self.assertEqual(args.script, "scripts/startup.txt")

    def test_startup_script(self):
        output = StringIO()

        with redirect_stdout(output):
            result = run_startup_script("scripts/startup.txt")

        text = output.getvalue()

        self.assertTrue(result)
        self.assertIn("my_vfs> ls", text)
        self.assertIn("ls []", text)
        self.assertIn("my_vfs> cd home", text)
        self.assertIn("cd ['home']", text)
        self.assertIn("Unknown command: hello", text)
        self.assertNotIn("#", text)