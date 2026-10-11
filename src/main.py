import argparse
import base64
import time
import xml.etree.ElementTree as element_tree


VFS_NAME = "my_vfs"
ONE_ARGUMENT = 1
TWO_ARGUMENTS = 2
DEFAULT_VFS = """
<vfs>
    <directory name="/" />
</vfs>
"""


def parse_cli_args(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument("--vfs")
    parser.add_argument("--script")

    return parser.parse_args(args)


def parse_input(user_input):
    parts = user_input.split()

    if not parts:
        return "", []

    command = parts[0]
    args = parts[1:]

    return command, args


def load_vfs(vfs_path=None):
    if vfs_path is None:
        return element_tree.fromstring(DEFAULT_VFS)

    tree = element_tree.parse(vfs_path)
    return tree.getroot()


def read_vfs_file(file_element):
    content = file_element.text or ""

    if file_element.get("encoding") == "base64":
        return base64.b64decode(content.strip())

    return content


def build_directory(directory_element):
    directory = {
        "type": "directory",
        "children": {},
    }

    for child in directory_element:
        name = child.get("name")

        if child.tag == "directory":
            directory["children"][name] = build_directory(child)
        elif child.tag == "file":
            directory["children"][name] = {
                "type": "file",
                "content": read_vfs_file(child),
            }

    return directory


def build_vfs(vfs_root):
    root_directory = vfs_root.find("directory")

    if root_directory is None:
        raise ValueError("Root directory not found")

    return build_directory(root_directory)


def create_shell_state(vfs):
    return {
        "vfs": vfs,
        "cwd": [],
        "started_at": time.monotonic(),
    }


def command_uptime(args, state):
    if args:
        print("uptime: too many arguments")
        return

    elapsed = int(time.monotonic() - state["started_at"])

    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"{hours:02d}:{minutes:02d}:{seconds:02d}")


def get_directory(state, path_parts):
    directory = state["vfs"]

    for part in path_parts:
        child = directory["children"].get(part)

        if child is None or child["type"] != "directory":
            return None

        directory = child

    return directory


def get_node(state, path_parts):
    node = state["vfs"]

    for part in path_parts:
        if node["type"] != "directory":
            return None

        node = node["children"].get(part)

        if node is None:
            return None

    return node


def resolve_path(current_path, target):
    if target.startswith("/"):
        path_parts = []
    else:
        path_parts = current_path.copy()

    for part in target.split("/"):
        if not part or part == ".":
            continue

        if part == "..":
            if path_parts:
                path_parts.pop()
        else:
            path_parts.append(part)

    return path_parts


def get_parent_and_name(state, target):
    path_parts = resolve_path(state["cwd"], target)

    if not path_parts:
        return None, None

    name = path_parts[-1]
    parent = get_directory(state, path_parts[:-1])

    return parent, name

    
def run_startup_script(script_path, state=None):
    with open(script_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            print(f"{VFS_NAME}> {line}")

            command, args = parse_input(line)
            should_continue = execute_command(command, args, state)

            if not should_continue:
                return False

    return True


def command_ls(args, state):
    if len(args) > ONE_ARGUMENT:
        print("ls: too many arguments")
        return

    if args:
        path_parts = resolve_path(state["cwd"], args[0])
    else:
        path_parts = state["cwd"]

    directory = get_directory(state, path_parts)

    if directory is None:
        print("ls: no such directory")
        return

    names = sorted(directory["children"].keys())
    print(" ".join(names))


def command_cd(args, state):
    if len(args) != ONE_ARGUMENT:
        print("cd: expected one argument")
        return

    target = args[0]
    new_path = resolve_path(state["cwd"], target)
    directory = get_directory(state, new_path)

    if directory is None:
        print(f"cd: no such directory: {target}")
        return

    state["cwd"] = new_path


def command_pwd(args, state):
    if args:
        print("pwd: too many arguments")
        return

    if not state["cwd"]:
        print("/")
        return

    print("/" + "/".join(state["cwd"]))


def command_wc(args, state):
    if len(args) != ONE_ARGUMENT:
        print("wc: expected one argument")
        return

    target = args[0]
    path_parts = resolve_path(state["cwd"], target)

    if not path_parts:
        print("wc: file not found")
        return

    file_name = path_parts[-1]
    directory = get_directory(state, path_parts[:-1])

    if directory is None:
        print("wc: file not found")
        return

    file_node = directory["children"].get(file_name)

    if file_node is None or file_node["type"] != "file":
        print("wc: file not found")
        return

    content = file_node["content"]

    if isinstance(content, bytes):
        byte_count = len(content)
        line_count = content.count(b"\n")
        word_count = len(content.split())
    else:
        byte_count = len(content.encode("utf-8"))
        line_count = len(content.splitlines())
        word_count = len(content.split())

    print(line_count, word_count, byte_count, target)


def get_source(state, source):
    parent, name = get_parent_and_name(state, source)

    if parent is None:
        return None, None, None

    node = parent["children"].get(name)

    if node is None:
        return None, None, None

    return parent, name, node


def get_destination(state, destination, source_name):
    path_parts = resolve_path(state["cwd"], destination)
    node = get_node(state, path_parts)

    if node is not None and node["type"] == "directory":
        return node, source_name

    return get_parent_and_name(state, destination)


def contains_node(root, target):
    if root is target:
        return True

    if root["type"] != "directory":
        return False

    for child in root["children"].values():
        if contains_node(child, target):
            return True

    return False


def command_mv(args, state):
    if len(args) != TWO_ARGUMENTS:
        print("mv: expected two arguments")
        return

    source, destination = args

    source_parent, source_name, source_node = get_source(
        state,
        source
    )

    if source_node is None:
        print(f"mv: no such file or directory: {source}")
        return

    destination_parent, destination_name = get_destination(
        state,
        destination,
        source_name
    )

    if destination_parent is None:
        print(f"mv: invalid destination: {destination}")
        return

    if (
        source_node["type"] == "directory"
        and contains_node(source_node, destination_parent)
    ):
        print("mv: cannot move directory into itself")
        return

    if destination_name in destination_parent["children"]:
        print(f"mv: destination already exists: {destination}")
        return

    destination_parent["children"][destination_name] = source_node
    del source_parent["children"][source_name]


def execute_command(command, args, state=None):
    if command == "ls":
        command_ls(args, state)
    elif command == "cd":
        command_cd(args, state)
    elif command == "pwd":
        command_pwd(args, state)
    elif command == "wc":
        command_wc(args, state)
    elif command == "uptime":
        command_uptime(args, state)
    elif command == "mv":
        command_mv(args, state)
    elif command == "exit":
        return False
    else:
        print(f"Unknown command: {command}")
    return True


def repl(state):
    while True:
        user_input = input(f"{VFS_NAME}> ")

        command, args = parse_input(user_input)

        if not command:
            continue

        should_continue = execute_command(command, args, state)

        if not should_continue:
            break


if __name__ == "__main__":
    args = parse_cli_args()

    print("VFS:", args.vfs)
    print("Script:", args.script)

    vfs_root = load_vfs(args.vfs)
    print("VFS loaded:", vfs_root.tag)

    vfs = build_vfs(vfs_root)
    state = create_shell_state(vfs)

    if not args.script or run_startup_script(args.script, state):
        repl(state)

