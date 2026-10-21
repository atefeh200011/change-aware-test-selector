# Factual CV bullet drafts

- Built a Python CLI that detects Git working-tree changes, selects pytest files
  using explicit JSON dependency mappings, and conservatively falls back to the
  full suite for uncertain changes; added JSON and escaped local HTML reports.
- Verified the prototype with 40 passing pytest cases covering selection policy,
  temporary Git histories, mapping validation, and CLI failure-status propagation;
  authored a GitHub Actions workflow retaining full-suite verification.
- Implemented six repeatable synthetic evaluation scenarios comparing selected,
  manual-reference and full-suite execution with measured test counts and wall
  times, including an injected pricing regression detected by selected tests.

These describe this local prototype. The workflow has not been run on GitHub,
the project has not been deployed, and no production speedup is claimed. The
implementation was developed with Codex assistance; use these bullets only when
you can explain and modify the code yourself.
