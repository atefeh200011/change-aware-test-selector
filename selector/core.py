import json
from pathlib import Path, PurePosixPath
from .git_changes import SelectionError


def safe_path(value):
    return (isinstance(value, str) and bool(value) and "\\" not in value
            and not value.startswith("-") and ":" not in value
            and not PurePosixPath(value).is_absolute()
            and all(part not in ("..", ".") for part in value.split("/")))


def load_mapping(root, filename="selection.json"):
    try:
        data = json.loads((Path(root) / filename).read_text(encoding="utf-8"))
        mapping = data["mapping"]
        if not isinstance(mapping, dict):
            raise ValueError("mapping must be an object")
        for source, tests in mapping.items():
            if not safe_path(source) or not isinstance(tests, list) or not tests:
                raise ValueError("each source needs a safe path and nonempty test list")
            for test in tests:
                if (not safe_path(test) or not test.startswith("tests/")
                        or not test.endswith(".py")):
                    raise ValueError("test targets must be Python files under tests/")
        return mapping
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SelectionError(f"Invalid mapping: {exc}") from exc


def select(root, changed, mapping):
    selected, reasons, fallback = set(), [], []
    for item in changed:
        path, status = item["path"], item["status"]
        if status not in {"A", "M", "D", "T", "?"}:
            fallback.append(f"uncertain Git status: {status} {path}")
        if (Path(path).name in {"conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "setup.py", "tox.ini", "selection.json"}
                or Path(path).name.startswith("requirements") or path.endswith(".lock")):
            fallback.append(f"shared configuration or dependency file: {path}")
        elif path.startswith("docs/") or path in {"README.md", "INTERVIEW.md", "CV.md", "LICENSE"}:
            reasons.append(f"documentation only: {path}")
        elif path.startswith("tests/") and Path(path).name.startswith("test_") and path.endswith(".py"):
            if status == "D" or not (Path(root) / path).is_file():
                fallback.append(f"deleted or missing test: {path}")
            else:
                selected.add(path)
                reasons.append(f"changed test: {path}")
        elif path in mapping:
            selected.update(mapping[path])
            reasons.append(f"mapped source: {path}")
        else:
            fallback.append(f"unmapped or shared configuration change: {path}")
    # Validate every target, including mappings not exercised by this change.
    for targets in mapping.values():
        for target in targets:
            if not (Path(root) / target).is_file():
                fallback.append(f"mapping target missing: {target}")
    return {"changed_files": changed, "selected_tests": ["tests"] if fallback else sorted(selected),
            "mode": "full" if fallback else "selected" if selected else "none",
            "reasons": reasons, "full_suite_fallback": sorted(set(fallback)),
            "mapping": mapping}
