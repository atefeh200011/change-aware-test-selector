"""Read Git's NUL-delimited output without shell parsing."""
import os
import subprocess
from pathlib import Path


class SelectionError(Exception):
    pass


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise SelectionError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def changes(root, base):
    root = Path(root).resolve()
    actual = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if actual != root:
        raise SelectionError("Run from the repository root")
    commit = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").strip().decode()
    # --no-renames represents renames as deletion + addition: both paths matter.
    fields = git(root, "diff", "--name-status", "-z", "--no-renames", commit, "--").split(b"\0")
    result = []
    for i in range(0, len(fields) - 1, 2):
        result.append({"status": os.fsdecode(fields[i]), "path": os.fsdecode(fields[i + 1])})
    for path in git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        if path:
            result.append({"status": "?", "path": os.fsdecode(path)})
    return sorted(result, key=lambda x: (x["path"], x["status"]))
