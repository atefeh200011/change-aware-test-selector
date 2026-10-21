import argparse
import subprocess
import sys
from pathlib import Path
from .core import load_mapping, select
from .git_changes import SelectionError, changes
from .report import write_report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Select tests using Git changes and explicit mappings")
    parser.add_argument("--base", required=True, help="Git commit/ref compared with current working tree")
    parser.add_argument("--run", action="store_true", help="execute selected tests with pytest")
    parser.add_argument("--report-dir", default="reports/latest")
    args = parser.parse_args(argv)
    try:
        root = Path.cwd()
        report = select(root, changes(root, args.base), load_mapping(root))
        report["base"] = args.base
        write_report(report, args.report_dir)
        print(f"Selection: {report['mode']}; targets: {', '.join(report['selected_tests']) or '(none needed)'}", flush=True)
        for reason in report["full_suite_fallback"]:
            print(f"Full suite: {reason}", flush=True)
        if args.run and report["mode"] != "none":
            return subprocess.run([sys.executable, "-m", "pytest", "-q", "--", *report["selected_tests"]], cwd=root).returncode
        return 0
    except (SelectionError, OSError) as exc:
        print(f"Selection failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
