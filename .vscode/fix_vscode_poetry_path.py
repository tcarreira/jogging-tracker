#!/usr/bin/env python3
# run from project root: python .vscode/fix_vscode_poetry_path.py
import json
import os
import subprocess
from pathlib import Path

venv_path = subprocess.check_output("poetry env info --path".split())
venv_path = venv_path.decode("UTF-8")
venv_path = venv_path.replace(os.environ.get("HOME", "~"), "~")

settings = dict()
file_path = ".vscode/settings.json"
Path(".vscode").mkdir(parents=True, exist_ok=True)
Path(file_path).touch()


if os.stat(file_path).st_size > 0:
    with open(file_path, "r") as f:
        settings = json.load(f)

settings["python.pythonPath"] = venv_path

with open(file_path, "w") as f:
    json.dump(settings, f, sort_keys=True, indent=4)


print(json.dumps(settings, sort_keys=True, indent=4))
