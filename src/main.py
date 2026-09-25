import argparse 

VFS_NAME = "my_vfs"

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

def run_startup_script(script_path):
    with open(script_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            print(f"{VFS_NAME}> {line}")

            command, args = parse_input(line)
            should_continue = execute_command(command, args)

            if not should_continue:
                return False

    return True

def command_ls(args):
    print("ls", args)

def command_cd(args):
    print("cd", args)

def execute_command(command, args):
    if command == "ls":
        command_ls(args)
    elif command == "cd":
        command_cd(args)
    elif command == "exit":
        return False
    else:
        print(f"Unknown command: {command}")
    
    return True

def repl():
    while True:
        user_input = input(f"{VFS_NAME}> ")

        command, args = parse_input(user_input)

        if not command:
            continue

        should_continue = execute_command(command, args)

        if not should_continue:
            break

if __name__ == "__main__":
    args = parse_cli_args()

    print("VFS:", args.vfs)
    print("Script:", args.script)

    if args.script:
        run_startup_script(args.script)

    repl()
