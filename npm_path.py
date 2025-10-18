import subprocess


def get_npm_path():
    try:
        return subprocess.check_output(["which", "npm"]).decode("utf-8").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
