import html
import json
from pathlib import Path


def write_report(report, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, ensure_ascii=True)
    (directory / "selection.json").write_text(payload + "\n", encoding="utf-8")
    rows = "".join("<tr><td>" + html.escape(source) + "</td><td>" +
                   html.escape(", ".join(tests)) + "</td></tr>"
                   for source, tests in sorted(report["mapping"].items()))
    (directory / "selection.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Test selection</title>'
        '<style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:16px}'
        'td,th{border:1px solid #aaa;padding:10px}table{border-collapse:collapse}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
        '<h1>Change-Aware Test Selector</h1><p>Manually maintained source → test relationships</p>'
        '<table><tr><th>Source</th><th>Tests</th></tr>' + rows + '</table>'
        '<h2>Selection and reasons</h2><pre>' + html.escape(payload) + '</pre></html>', encoding="utf-8")
