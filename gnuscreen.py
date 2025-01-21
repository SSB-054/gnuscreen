import subprocess
import tempfile

__version__ = "0.1.0"
__author__ = "Suraj Singh Bisht"
__license__ = "MIT"
__description__ = "This module is used to create and manage GNU screen sessions."


def get_screens_list():
    output = []
    res = subprocess.run(
        ["screen", "-ls"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    for i in res.stdout.strip().splitlines():
        if i and "(" in i and ")" in i and i.count("\t") > 1:
            screen_pid, screen_name = i.strip("\t").split("\t")[0].split(".")
            output.append((screen_pid, screen_name))
    return output


def screen_exists(screen_name_or_pid):
    screens = get_screens_list()
    for i in screens:
        if screen_name_or_pid in i:
            return i
    return None


def kill_screen(screen_pid, screen_name):
    if not screen_exists(screen_name):
        return None
    subprocess.run(
        ["screen", "-XS", f"{screen_pid}.{screen_name}", "quit"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    return True


def kill_all_screens():
    screens = get_screens_list()
    for screen_pid, screen_name in screens:
        kill_screen(screen_pid, screen_name)
    return True


def get_screen_pid(screen_name):
    if not screen_exists(screen_name):
        return None
    screens = get_screens_list()
    for i in screens:
        if screen_name in i:
            return i[0]
    return None


def screen_is_running(screen_name):
    if not screen_exists(screen_name):
        return None
    screen_pid = get_screen_pid(screen_name)
    res = subprocess.run(
        ["ps", "-p", screen_pid],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    return screen_pid in res.stdout


def create_screen(screen_name, command: list, kill_if_exists=False, log_file=None):
    if screen_exists(screen_name):
        if kill_if_exists:
            kill_screen(screen_name)
        else:
            return None

    if not isinstance(command, list):
        command = [command]

    commands = ["screen"]
    # screen -L -Logfile Log_file_name
    if log_file:
        commands += ["-L", "-Logfile", log_file]
    commands += ["-dmS", screen_name]
    commands += command
    res = subprocess.run(
        commands, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    screen_pid = get_screen_pid(screen_name)
    return screen_pid, screen_name

def create_if_not_exists(screen_name, command: list, kill_if_exists=False, log_file=None):
    if not screen_exists(screen_name):
        return create_screen(screen_name, command, kill_if_exists, log_file)
    return None

def test():
    kill_all_screens()
    screen_pid, _ = create_if_not_exists("test", "top", )
    assert screen_exists("test")
    assert screen_is_running("test")
    assert get_screen_pid("test") == screen_pid
    with tempfile.NamedTemporaryFile() as f:
        log_file = f.name
        create_screen("test", ["echo"], log_file=log_file)
        assert screen_exists("test")
        assert screen_is_running("test")
        assert get_screen_pid("test")


if __name__ == "__main__":
    import sys

    sys.path.append("..")
    test()
