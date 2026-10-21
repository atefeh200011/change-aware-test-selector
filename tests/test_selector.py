import json
import pytest
from selector.core import select, load_mapping
from selector.git_changes import changes, SelectionError
from selector.report import write_report


def changed(path, status="M"):
    return [{"path": path, "status": status}]


@pytest.fixture
def mapped(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_a.py").touch()
    return tmp_path, {"src/a.py": ["tests/test_a.py"]}


def test_mapped_source(mapped):
    root, mapping = mapped
    report = select(root, changed("src/a.py"), mapping)
    assert report["mode"] == "selected"
    assert report["selected_tests"] == ["tests/test_a.py"]


@pytest.mark.parametrize("path", ["pyproject.toml", "requirements.txt", "tests/conftest.py", "src/new.py", "selector/core.py", ".github/workflows/ci.yml"])
def test_uncertain_changes_fall_back(mapped, path):
    root, mapping = mapped
    assert select(root, changed(path), mapping)["mode"] == "full"


def test_changed_and_deleted_test(mapped):
    root, mapping = mapped
    assert select(root, changed("tests/test_a.py"), mapping)["mode"] == "selected"
    assert select(root, changed("tests/test_a.py", "D"), mapping)["mode"] == "full"


def test_docs_and_no_changes(mapped):
    root, mapping = mapped
    assert select(root, changed("docs/design.md"), mapping)["mode"] == "none"
    assert select(root, [], mapping)["mode"] == "none"


def test_missing_target(mapped):
    root, mapping = mapped
    (root / "tests/test_a.py").unlink()
    assert select(root, [], mapping)["mode"] == "full"


def test_shared_configuration_cannot_be_mapped_away(mapped):
    root, mapping = mapped
    mapping["tests/conftest.py"] = ["tests/test_a.py"]
    assert select(root, changed("tests/conftest.py"), mapping)["mode"] == "full"


def test_union_docs_and_deleted_mapped_source(mapped):
    root, mapping = mapped
    report = select(root, changed("src/a.py", "D") + changed("tests/test_a.py") + changed("README.md"), mapping)
    assert report["mode"] == "selected"
    assert report["selected_tests"] == ["tests/test_a.py"]


def test_unsupported_status_falls_back(mapped):
    root, mapping = mapped
    assert select(root, changed("src/a.py", "U"), mapping)["mode"] == "full"


@pytest.mark.parametrize("data", [{}, {"mapping": []}, {"mapping": {"src/a.py": []}}, {"mapping": {"src/a.py": ["../bad.py"]}}, {"mapping": {"src/a.py": ["-x"]}}])
def test_bad_mapping(tmp_path, data):
    (tmp_path / "selection.json").write_text(json.dumps(data))
    with pytest.raises(SelectionError):
        load_mapping(tmp_path)


def test_html_escaping(tmp_path):
    report = select(tmp_path, changed("docs/<script>.md"), {"<img>": ["<script>"]})
    write_report(report, tmp_path)
    html = (tmp_path / "selection.html").read_text()
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_git_staged_unstaged_untracked_and_ignored(repo):
    root, git = repo
    (root / "source.py").write_text("value = 2\n")
    git("add", "source.py")
    (root / "source.py").write_text("value = 3\n")
    (root / "new file.py").touch()
    (root / ".gitignore").write_text("ignored.py\n")
    (root / "ignored.py").touch()
    result = changes(root, "HEAD")
    assert {x["path"] for x in result} == {"source.py", "new file.py", ".gitignore"}
    assert {x["status"] for x in result} == {"M", "?"}


def test_git_rename_and_delete(repo):
    root, git = repo
    git("mv", "source.py", "renamed.py")
    assert changes(root, "HEAD") == [{"status": "A", "path": "renamed.py"}, {"status": "D", "path": "source.py"}]
    (root / "renamed.py").unlink()
    assert {x["path"] for x in changes(root, "HEAD")} == {"source.py"}


def test_invalid_base_and_non_repository(repo, tmp_path_factory):
    root, git = repo
    with pytest.raises(SelectionError):
        changes(root, "nonexistent")
    with pytest.raises(SelectionError):
        changes(tmp_path_factory.mktemp("outside"), "HEAD")


def test_committed_change_since_base(repo):
    root, git = repo
    (root / "source.py").write_text("value = 2\n")
    git("add", ".")
    git("commit", "-qm", "change")
    assert changes(root, "HEAD~1") == changed("source.py")


def test_added_and_deleted_tracked_paths_with_spaces(repo):
    root, git = repo
    (root / "added file.py").touch()
    git("add", "added file.py")
    (root / "source.py").unlink()
    assert changes(root, "HEAD") == [{"path": "added file.py", "status": "A"}, {"path": "source.py", "status": "D"}]


def test_net_worktree_contents_define_changes(repo):
    root, git = repo
    original = (root / "source.py").read_text()
    (root / "source.py").write_text("value = 2\n")
    git("add", "source.py")
    (root / "source.py").write_text(original)
    assert changes(root, "HEAD") == []
