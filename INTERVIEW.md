# Interview guide

## Explain the design in a minute

“I built a Python prototype that compares a Git ref with the working tree and
uses an explicit JSON source-to-test map to select pytest files. Git change
detection is automatic; dependency knowledge is manual. Unknown changes trigger
the full suite. I evaluated selected tests against a manual reference and a full
run in isolated Git copies, including one injected pricing regression. The
selected tests caught that fault, but stale mapping edges remain a risk.”

## Follow the code

1. `git_changes.changes`: resolve the ref to a commit before invoking diff;
   parse NULs so spaces/newlines do not split filenames. No rename inference is
   needed because both old and new paths are retained as delete/add changes.
2. `core.load_mapping`: validate JSON shape and local test-file targets.
   `core.select`: union mapped and changed tests, accumulating uncertainty reasons.
   Any fallback changes the executable target to the full `tests` directory.
3. `cli.main`: distinguish none/selected/full from errors, persist the report,
   then invoke pytest with the same interpreter and return its actual exit code.
4. `report.write_report`: render the same JSON data in an escaped local HTML
   relationship table. Visualization exposes what the maintained map claims.
5. `evaluation/run.py`: create baseline copies, modify files, run three strategies
   and read JUnit XML for actual case counts rather than counting target files.

## Questions and trade-offs

- **Is this dynamic dependency analysis?** No. The selection responds dynamically
  to changes, but source-to-test dependencies are explicit manual configuration.
- **Why a JSON map?** Easy to inspect, explain and version. It provides a small
  working baseline before attempting coverage-based or import-based techniques.
- **What happens when a source is deleted or renamed?** Deletions still consult
  the old mapping; additions consult the new one. Unknown paths fall back.
- **What if the map is wrong?** Existing but incomplete edges can miss tests.
  Review the map, keep full-suite CI, and evaluate more realistic faults.
- **Does matching the reference prove correctness?** No. Both can encode the same
  mistaken assumptions. Full-suite comparison and injected faults add evidence
  but cannot prove complete regression detection.
- **Did it make tests faster?** Counts and timings are measured, but this tiny
  suite is dominated by startup and nested subprocess tests. One sample does not
  establish general speed improvement. Show the raw evaluation report.
- **Why run the full suite in CI anyway?** It checks the prototype's selections
  while confidence is being built; this first version demonstrates a strategy,
  not a validated replacement for safety-critical verification.
- **What would come next?** More fault scenarios, mapping maintenance checks,
  repeated timing measurements, then per-test coverage mappings as a separate
  version. No automatic analysis is claimed in this implementation.

## Exercises before an interview

Add a pricing dependency to shipping and update both code and mapping. Observe
how an omitted edge would miss shipping tests. Try a doc-only edit, a new module,
a renamed file and an invalid base. Explain the difference between CLI exit 2
and pytest's other failure codes. Re-run the controlled fault and identify which
assertions fail. Be explicit about the assistance used and your own understanding.
