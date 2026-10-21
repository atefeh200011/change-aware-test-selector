import subprocess
import pytest


@pytest.fixture
def repo(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    git("init", "-q")
    git("config", "user.email", "synthetic@example.invalid")
    git("config", "user.name", "Synthetic fixture")
    (tmp_path / "source.py").write_text("value = 1\n")
    git("add", ".")
    git("commit", "-qm", "baseline")
    return tmp_path, git
