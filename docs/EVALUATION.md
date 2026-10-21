# Measured local evaluation

Run on 21 October 2026 with Python 3.14.6, pytest 9.1.1, Windows-10-10.0.19045-SP0.

Command: `.venv/Scripts/python evaluation/run.py`.

| Scenario | Selected cases / seconds | Reference cases / seconds | Full cases / seconds | Outcome |
|---|---:|---:|---:|---|
| isolated | 5 / 1.5758 | 5 / 1.5135 | 40 / 22.6548 | All pass |
| shared | 10 / 2.6685 | 10 / 2.3584 | 40 / 24.0894 | All pass |
| test | 5 / 2.9421 | 5 / 2.0633 | 40 / 24.532 | All pass |
| configuration | 40 / 23.7899 | 40 / 25.723 | 40 / 28.8405 | All pass |
| unmapped | 40 / 27.0504 | 40 / 25.6721 | 40 / 25.4104 | All pass |
| fault | 5 / 3.5252 | 5 / 2.9672 | 40 / 26.2423 | 3 assertion failures in each strategy (expected) |

All six selections matched the manually maintained reference targets. Configuration and unmapped-source changes ran the full suite. The fault replaced pricing multiplication with addition; selected, reference and full execution each reported three assertion failures, no collection errors, and exit status 1.

The independent final verification run passed **40 tests in 16.65 seconds**. A temporary real CLI pricing edit selected five tests, which passed. A restored clean tree selected none; an invalid base exited 2. The installed CLI entry point was also checked.

These are single sequential process wall-clock samples including startup, not repeated benchmarks. The full suite contains 10 application cases and 30 selector cases, including nested subprocess integration tests; mapped selections run only application cases. This artificial workload and timing noise do not establish a production speed improvement. Reference agreement does not establish completeness, and catching one injected fault does not establish general regression-detection accuracy.

Raw preserved snapshot: [evaluation-results.json](evaluation-results.json). Re-running the evaluator updates `reports/evaluation.json`, not this dated snapshot.

Hosted verification was subsequently confirmed in [GitHub Actions run #1](https://github.com/atefeh200011/change-aware-test-selector/actions/runs/39594210872). Its `verify` job shows successful full-suite verification, controlled selection and fault demonstration, and artifact upload steps; the summary lists the `selection-reports` artifact. These hosted step results do not replace the local measurements above. The repository is public; no application deployment or production speedup is claimed.
