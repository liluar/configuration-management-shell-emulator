VFS_NAME = "my_vfs"
def parse_input(user_input):
    parts = user_input.split()

    if not parts:
        return "", []

    command = parts[0]
    args = parts[1:]

    return command, args


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
    repl()
