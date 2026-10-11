import unittest

from contextlib import redirect_stdout
from io import StringIO
from src.main import (
    build_vfs,
    create_shell_state,
    execute_command,
    get_directory,
    load_vfs,
    parse_cli_args,
    parse_input,
    read_vfs_file,
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
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("ls", [], state)

        self.assertTrue(result)
        self.assertEqual(output.getvalue().strip(), "home")

    def test_cd(self):
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)

        result = execute_command("cd", ["home"], state)

        self.assertTrue(result)
        self.assertEqual(state["cwd"], ["home"])

    def test_pwd_after_cd(self):
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)

        execute_command("cd", ["home"], state)

        output = StringIO()

        with redirect_stdout(output):
            execute_command("pwd", [], state)

        self.assertEqual(output.getvalue().strip(), "/home")

    def test_wc(self):
        root = load_vfs("vfs/files.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("wc", ["readme.txt"], state)

        self.assertTrue(result)
        self.assertEqual(
            output.getvalue().strip(),
            "1 1 5 readme.txt"
        )

    def test_uptime(self):
        root = load_vfs("vfs/minimal.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("uptime", [], state)

        self.assertTrue(result)

        uptime = output.getvalue().strip()

        self.assertRegex(
            uptime,
            r"^\d{2}:\d{2}:\d{2}$"
        )

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
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)
        output = StringIO()

        with redirect_stdout(output):
            result = run_startup_script(
                "scripts/startup.txt",
                state
            )

        text = output.getvalue()

        self.assertTrue(result)
        self.assertIn("my_vfs> ls", text)
        self.assertIn("home", text)
        self.assertIn("my_vfs> cd home", text)
        self.assertIn("Unknown command: hello", text)
        self.assertEqual(state["cwd"], ["home"])
        self.assertNotIn("#", text)

    def test_load_minimal_vfs(self):
        root = load_vfs("vfs/minimal.xml")

        self.assertEqual(root.tag, "vfs")

    def test_load_files_vfs(self):
        root = load_vfs("vfs/files.xml")

        root_directory = root.find("directory")
        files = root_directory.findall("file")

        self.assertEqual(len(files), 3)
        
    def test_load_nested_vfs(self):
        root = load_vfs("vfs/nested.xml")

        root_directory = root.find("directory")
        home = root_directory.find("directory[@name='home']")
        user = home.find("directory[@name='user']")
        documents = user.find("directory[@name='documents']")
        notes = documents.find("file[@name='notes.txt']")

        self.assertIsNotNone(home)
        self.assertIsNotNone(user)
        self.assertIsNotNone(documents)
        self.assertIsNotNone(notes)

    def test_default_vfs(self):
        root = load_vfs()

        self.assertEqual(root.tag, "vfs")

        root_directory = root.find("directory")

        self.assertIsNotNone(root_directory)
        self.assertEqual(root_directory.get("name"), "/")
    
    def test_base64_file(self):
        root = load_vfs("vfs/binary.xml")

        root_directory = root.find("directory")
        file_element = root_directory.find("file")
        content = read_vfs_file(file_element)

        self.assertEqual(content, bytes([0, 1, 2, 3, 4]))

    def test_pwd(self):
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command("pwd", [], state)

        self.assertTrue(result)
        self.assertEqual(output.getvalue().strip(), "/")


    def test_mv_rename_file(self):
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)

        execute_command(
            "cd",
            ["/home/user/documents"],
            state
        )
        result = execute_command(
            "mv",
            ["notes.txt", "text.txt"],
            state
        )

        directory = get_directory(
            state,
            ["home", "user", "documents"]
        )

        self.assertTrue(result)
        self.assertNotIn("notes.txt", directory["children"])
        self.assertIn("text.txt", directory["children"])


    def test_mv_move_file(self):
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)

        result = execute_command(
            "mv",
            [
                "/home/user/documents/notes.txt",
                "/home/user",
            ],
            state
        )

        documents = get_directory(
            state,
            ["home", "user", "documents"]
        )
        user = get_directory(
            state,
            ["home", "user"]
        )

        self.assertTrue(result)
        self.assertNotIn("notes.txt", documents["children"])
        self.assertIn("notes.txt", user["children"])


    def test_mv_missing_source(self):
        root = load_vfs("vfs/nested.xml")
        vfs = build_vfs(root)
        state = create_shell_state(vfs)
        output = StringIO()

        with redirect_stdout(output):
            result = execute_command(
                "mv",
                ["missing.txt", "new.txt"],
                state
            )

        self.assertTrue(result)
        self.assertEqual(
            output.getvalue().strip(),
            "mv: no such file or directory: missing.txt"
        )