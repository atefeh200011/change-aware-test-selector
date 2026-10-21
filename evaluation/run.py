"""Run real changes in disposable Git copies; never modify the user's checkout."""
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from selector.core import load_mapping, select
from selector.git_changes import changes
from selector.report import write_report


def measure(root, targets, name):
    xml = root / "reports" / (name + ".xml")
    start = time.perf_counter()
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "--junitxml", str(xml), "--", *targets], cwd=root, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    if not xml.exists():
        raise RuntimeError(run.stdout + run.stderr)
    cases = list(ET.parse(xml).iter("testcase"))
    return {"tests": len(cases), "failures": sum(c.find("failure") is not None for c in cases),
            "errors": sum(c.find("error") is not None for c in cases),
            "exit_code": run.returncode, "wall_seconds": round(elapsed, 4)}


def main():
    reference = json.loads((ROOT / "evaluation/reference.json").read_text())
    results = []
    for scenario, expected in reference.items():
        with tempfile.TemporaryDirectory(prefix="change-selector-") as temporary:
            root = Path(temporary)
            for folder in ("demo_app", "selector", "tests"):
                shutil.copytree(ROOT / folder, root / folder, ignore=shutil.ignore_patterns("__pycache__"))
            for file in ("pyproject.toml", "selection.json", ".gitignore"):
                shutil.copy2(ROOT / file, root / file)
            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
            git("init", "-q")
            git("-c", "user.name=Synthetic evaluation", "-c", "user.email=synthetic@example.invalid", "add", ".")
            git("-c", "user.name=Synthetic evaluation", "-c", "user.email=synthetic@example.invalid", "commit", "-qm", "baseline")
            path = {"isolated": "demo_app/pricing.py", "shared": "demo_app/shared.py", "test": "tests/test_shipping.py", "configuration": "pyproject.toml", "unmapped": "demo_app/new.py", "fault": "demo_app/pricing.py"}[scenario]
            target = root / path
            if scenario == "fault":
                target.write_text(target.read_text().replace("price * quantity", "price + quantity"))
            else:
                with target.open("a") as stream:
                    stream.write("\n# Controlled evaluation change\n")
            report = select(root, changes(root, "HEAD"), load_mapping(root))
            write_report(report, root / "reports")
            selected = measure(root, report["selected_tests"], "selected")
            manual = measure(root, expected, "manual")
            full = measure(root, ["tests"], "full")
            agreement = report["selected_tests"] == expected
            row = {"scenario": scenario, "changed_path": path, "mode": report["mode"], "selected_targets": report["selected_tests"], "reference_agreement": agreement, "selected": selected, "manual_reference": manual, "full": full}
            results.append(row)
            print(f"{scenario}: selected {selected['tests']} tests / {selected['wall_seconds']}s; full {full['tests']} / {full['wall_seconds']}s; agreement={agreement}", flush=True)
            if not agreement or any(m["exit_code"] != (1 if scenario == "fault" else 0) for m in (selected, manual, full)):
                raise RuntimeError(f"Unexpected evaluation outcome: {row}")
            if any(m["errors"] or not m["tests"] or (scenario == "fault" and not m["failures"]) for m in (selected, manual, full)):
                raise RuntimeError(f"Expected real test outcomes, not collection errors: {row}")
            if scenario == "isolated":
                write_report(report, ROOT / "reports/example")
    output = {"python": platform.python_version(), "platform": platform.platform(), "timing": "One sequential run per selection; process wall clock includes pytest startup; no speedup claim", "scenarios": results}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/evaluation.json").write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
