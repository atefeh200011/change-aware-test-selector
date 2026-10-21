import json
import subprocess
import sys
from pathlib import Path
from selector import cli


def test_error_is_not_empty_success(repo, monkeypatch, capsys):
    root, _ = repo
    monkeypatch.chdir(root)
    assert cli.main(["--base", "invalid"]) == 2
    assert "Selection failed" in capsys.readouterr().err


def test_preserves_real_pytest_failure(repo, monkeypatch):
    root, git = repo
    (root / "tests").mkdir()
    (root / "tests/test_failure.py").write_text("def test_failure():\n    assert False\n")
    (root / "selection.json").write_text(json.dumps({"mapping": {"source.py": ["tests/test_failure.py"]}}))
    git("add", ".")
    git("commit", "-qm", "test fixture")
    (root / "source.py").write_text("value = 4\n")
    monkeypatch.chdir(root)
    assert cli.main(["--base", "HEAD", "--run"]) == 1
    assert json.loads((root / "reports/latest/selection.json").read_text())["mode"] == "selected"


def test_no_tests_needed_does_not_invoke_pytest(repo, monkeypatch):
    root, git = repo
    (root / "selection.json").write_text('{"mapping": {}}')
    git("add", ".")
    git("commit", "-qm", "config")
    monkeypatch.chdir(root)
    assert cli.main(["--base", "HEAD", "--run"]) == 0
    assert json.loads((root / "reports/latest/selection.json").read_text())["mode"] == "none"


def test_missing_mapping_is_error(repo, monkeypatch, capsys):
    root, _ = repo
    monkeypatch.chdir(root)
    assert cli.main(["--base", "HEAD"]) == 2
    assert "Invalid mapping" in capsys.readouterr().err


def test_pytest_no_collection_status_preserved(repo, monkeypatch):
    root, git = repo
    (root / "tests").mkdir()
    (root / "tests/test_empty.py").write_text("# no tests\n")
    (root / "selection.json").write_text('{"mapping": {"source.py": ["tests/test_empty.py"]}}')
    git("add", ".")
    git("commit", "-qm", "empty test")
    (root / "source.py").write_text("value = 5\n")
    monkeypatch.chdir(root)
    assert cli.main(["--base", "HEAD", "--run"]) == 5
