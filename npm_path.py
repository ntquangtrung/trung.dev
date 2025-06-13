import subprocess


def get_npm_path():
    try:
        npm_path = subprocess.check_output(["which", "npm"]).decode("utf-8").strip()
        return npm_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
