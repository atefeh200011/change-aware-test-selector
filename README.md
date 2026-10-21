# Change-Aware Test Selector

A small Python portfolio project inspired by dynamic test selection. It detects
Git changes automatically and selects pytest **files using manually maintained
JSON mappings**. It does not discover dependencies. All application data and
faults are synthetic; no employer code or services are used.

## Setup and commands

Requires Python 3.10+ and Git. Run from this repository's root. PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[test]"
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m selector.cli --base HEAD
.venv/Scripts/python -m selector.cli --base HEAD --run
.venv/Scripts/python evaluation/run.py
Start-Process reports/example/selection.html
```

On Linux/macOS, replace `.venv/Scripts/python` with `.venv/bin/python`.
The installed `change-tests --base HEAD` command is also available inside the
activated environment. Use any available commit, branch or tag for `--base`,
for example `--base main` or `--base HEAD~1`. This is a direct comparison with
that commit, **not** a merge-base comparison. A freshly cloned clean checkout
compared with HEAD needs no tests. An invalid ref exits 2.

To demonstrate a local mapped change, append a comment to
`demo_app/pricing.py`, then run the CLI with `--base HEAD --run`. It selects
`tests/test_pricing.py` (five parameterized test cases). Remove the comment
afterward. The evaluation command makes these changes in temporary copies,
including a deliberate regression; it leaves your checkout untouched.

## Architecture and policy

`selector/git_changes.py` calls Git with argument lists and parses NUL-delimited
paths. `git diff <resolved-base> --` compares the base tree to the current
tracked working tree: committed changes since base, staged changes and unstaged
changes are reflected in the final file contents. A staged edit subsequently
undone in the working tree is not a net change. `git ls-files --others
--exclude-standard` adds non-ignored untracked files. Ignored files are excluded:
do not ignore inputs capable of changing test behavior. Git submodules, generated
inputs, environment changes and external dependencies are outside this model.

Renames use `--no-renames`: deletion of the old path plus addition of the new
path ensures both names are considered. Added/modified/deleted mapped sources
select their mapped tests. New unmapped paths cause full-suite execution.
Deleted tests, missing mapping targets, unresolved statuses, unmapped sources,
test helpers, selector changes, CI changes and unknown files cause a full-suite
fallback. Known test configuration and dependency filenames always cause a
fallback, even if someone maps them. Shared application code such as
`demo_app/shared.py` explicitly maps to both application test files.

`selector/core.py` validates mapping paths and unions test files. Changed
`tests/**/test_*.py` files are included; other test-tree changes fall back.
Documentation paths, including `docs/**`, README.md and LICENSE, are considered
documentation only. Keep executable inputs out of those locations. Documentation
mixed with code changes does not suppress code selection. No changes or only
documentation changes give mode `none`, meaning no tests needed under this
policy. This is distinct from an error: malformed/missing mapping, Git errors
and report-writing errors exit 2 and print `Selection failed`.

`selector/cli.py` writes the selection report before optionally executing
`[sys.executable, '-m', 'pytest', '-q', '--', ...targets]`. No shell command
construction is used. Full fallback targets `tests`; selected mode targets
specific files. Pytest's status (including test failure, collection failure and
no-tests-collected) is returned unchanged. Selection-only mode never runs pytest.
Reports describe selection, not proof of test success; use pytest's exit status.
After an error, an older report may still exist: never use it instead of checking
the command exit code. Generated reports belong in the Git-ignored `reports/`
directory to avoid becoming uncertain changes on the next run.

## Reports and relationship visualization

The CLI writes `reports/latest/selection.json` and `selection.html`. HTML is
standalone, uses a source → test relationship table, escapes displayed values,
and makes no external requests. The evaluation writes a mapped-change example
to `reports/example/`. An abbreviated report is:

```json
{
  "changed_files": [{"status": "M", "path": "demo_app/pricing.py"}],
  "selected_tests": ["tests/test_pricing.py"],
  "mode": "selected",
  "reasons": ["mapped source: demo_app/pricing.py"],
  "full_suite_fallback": []
}
```

The actual report also includes the mapping, and CLI reports include the base
ref. Modes are `selected`, `full`, and `none`; errors are process failures,
never successful empty selections.

## Repeatable evaluation

Run `python evaluation/run.py`. It creates six disposable Git repositories from
the current project, commits a baseline, applies one change, and executes the
selected targets, the independently maintained `evaluation/reference.json`
targets, and the full suite. Scenarios cover an isolated source, a shared module,
a test, configuration, an unmapped source and a controlled pricing fault. The
first five changes are comments/new empty modules to isolate selection behavior;
they do not establish sensitivity to realistic behavioral changes.

The fault changes `price * quantity` to `price + quantity`. Evaluation succeeds
only if selected, reference and full runs fail for that scenario and pass for
the others. XML-derived actual test-case counts, failures, errors, exit codes,
and process wall times are saved in `reports/evaluation.json`. It checks exact
reference target agreement separately. See [evaluation results](docs/EVALUATION.md) for
the measured local run. Timings include interpreter and pytest startup and are
one sequential sample per execution; there is no defensible speedup claim.
The full suite includes the selector's own integration tests with nested Git and
pytest subprocesses, whereas mapped selections run only application tests. This
asymmetric synthetic workload is not representative of an industrial test suite.
Reference agreement tests policy expectations, not dependency completeness or
regression-detection correctness. The one fault is evidence about that fault only.

## Verification and CI

The full tests exercise calculation boundaries, conservative selection, invalid
configuration, HTML escaping, actual temporary Git histories, rename/deletion,
untracked/ignored paths and CLI propagation of a real failing pytest run.
GitHub Actions installs the project, always runs the full suite, demonstrates
event-base selection, runs the controlled evaluation and uploads reports.
`fetch-depth: 0` provides history. PRs use the PR base SHA; pushes use the prior
SHA. If unavailable (for example a first push), CI explicitly uses the oldest
available root commit, and the full suite still runs. On an unchanged initial
commit that selection may be empty; the controlled evaluation still demonstrates
nonempty selections.

The repository is publicly available on GitHub. The CI verification workflow has
completed successfully and uploaded selection reports.
[Verified run #1](https://github.com/atefeh200011/change-aware-test-selector/actions/runs/39594210872)
shows successful completion of the full-suite verification, controlled selection
and fault demonstration, and artifact upload steps. The run produced the
`selection-reports` artifact. Runtime and runner-update annotations did not fail
this run. Detailed hosted logs require sign-in; the test counts and timings in
the evaluation document are from the recorded local run.

## Limitations

**Stale or incomplete mappings can miss dependencies.** The fallback protects
unknown paths, not missing edges for a known mapped source. A new dependency on
pricing from shipping would require adding the shipping tests to pricing's
mapping. Review mapping updates alongside code changes and retain the full suite
as a verification backstop. Documentation classification and ignored-file rules
are assumptions. Mapping a file to an existing but irrelevant test is not
detectable here. Selection is at file granularity; there is no coverage mapping,
import analysis, machine learning or automatic dependency inference. The sample
application and one fault are small and cannot justify industrial-scale claims.
Changes during selection/execution can race; run against a stable checkout.

The source repository is public; no application deployment is claimed.
