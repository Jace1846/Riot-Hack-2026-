"""ui/server.py - tiny local web server for the FrameForge React page.

Run:   py ui/server.py      then open http://127.0.0.1:8000

Only listens on 127.0.0.1 (this computer). The API key you paste in the page is used for
one request and never saved to disk. Uses only Python's standard library - no Flask etc.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))  # so "controller" and "main" can be imported when run from ui/

import anthropic  # noqa: E402

from controller.agent import propose_experiment  # noqa: E402
from controller.analysis import summarize_csv  # noqa: E402
from main import _load_rules, load_tried_experiments, save_experiment  # noqa: E402

PAGE = Path(__file__).parent / "index.html"
HOST, PORT = "127.0.0.1", 8000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/experiments":
            self._send_json(200, {"experiments": load_tried_experiments()})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/propose":
            return self._send_json(404, {"error": "Not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            api_key = body.get("api_key", "").strip()
            csv_path = body.get("csv_path", "").strip()
            if not api_key:
                raise ValueError("Paste your Anthropic API key first.")
            if not csv_path:
                raise ValueError("Enter the path to a baseline CSV.")

            allowlist, baseline = _load_rules()
            summary = summarize_csv(ROOT / csv_path)
            client = anthropic.Anthropic(api_key=api_key)
            experiment = propose_experiment(summary, allowlist, baseline, load_tried_experiments(), client=client)
            path = save_experiment(experiment)

            self._send_json(200, {
                "experiment": experiment,
                "saved_to": str(path.relative_to(ROOT)),
                "synthetic": summary["synthetic"],
                "summary": summary,
            })
        except (FileNotFoundError, ValueError, RuntimeError) as error:
            self._send_json(400, {"error": str(error)})

    def _send_json(self, status, data):
        self._send(status, json.dumps(data).encode(), "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Only log the method and path, never request bodies (which contain the API key).
        print(f"{self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


if __name__ == "__main__":
    print(f"FrameForge UI running at http://{HOST}:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
