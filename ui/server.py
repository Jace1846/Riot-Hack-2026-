"""ui/server.py - tiny local web server for the FrameForge React page.

Run:   py main.py   (or py ui/server.py) - opens the FrameForge window automatically.

Only listens on 127.0.0.1 (this computer). The API key you paste in the page is used for
one request and never saved to disk. Uses only Python's standard library - no Flask etc.
"""
import json
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))  # so "controller" and "main" can be imported when run from ui/

import anthropic  # noqa: E402

from controller.agent import propose_experiment  # noqa: E402
from controller.analysis import summarize_csv  # noqa: E402
from controller.benchmark import capture_folder, find_newest_csv, load_json, run_benchmark  # noqa: E402
from main import _load_rules, load_tried_experiments, save_experiment  # noqa: E402

PAGE = Path(__file__).parent / "index.html"
CONFIG = ROOT / "config.local.json"
HOST, PORT = "127.0.0.1", 8000

# Only one Unreal benchmark at a time: two at once would fight over the GPU and ruin both measurements.
BENCHMARK_LOCK = threading.Lock()

# Edge ships with Windows. Its "app mode" opens a clean window with no tabs or address bar.
EDGE_PATHS = [
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/experiments":
            self._send_json(200, {"experiments": load_tried_experiments()})
        elif self.path == "/api/latest-csv":
            self._send_json(200, latest_capture())
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/benchmark":
            return self._benchmark()
        if self.path not in ("/api/analyze", "/api/propose"):
            return self._send_json(404, {"error": "Not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            csv_path = body.get("csv_path", "").strip()
            if not csv_path:
                raise ValueError("Measure first: run a benchmark in Unreal or choose a CSV file.")

            # Analyze: just the measurements. No AI, no API key needed.
            if self.path == "/api/analyze":
                summary = summarize_csv(ROOT / csv_path)
                return self._send_json(200, {"summary": summary})

            api_key = body.get("api_key", "").strip()
            if not api_key:
                raise ValueError("Paste your Anthropic API key first.")

            allowlist, baseline = _load_rules()
            summary = summarize_csv(ROOT / csv_path)
            client = anthropic.Anthropic(api_key=api_key)
            experiment = propose_experiment(summary, allowlist, baseline, load_tried_experiments(), client=client)
            path = save_experiment(experiment)

            self._send_json(200, {
                "experiment": experiment,
                "saved_to": str(path.relative_to(ROOT)),
                "summary": summary,
            })
        except (FileNotFoundError, ValueError, RuntimeError) as error:
            self._send_json(400, {"error": str(error)})

    def _benchmark(self):
        """Launch Unreal with the baseline settings, wait for the CSV, and return its analysis."""
        if not BENCHMARK_LOCK.acquire(blocking=False):
            return self._send_json(409, {"error": "A benchmark is already running. Wait for Unreal to finish."})
        try:
            config = load_config()
            allowlist, baseline = _load_rules()
            print("Running baseline benchmark in Unreal...")
            csv_path = run_benchmark(baseline, baseline, allowlist, config)
            print(f"Captured {csv_path}")
            self._send_json(200, {"csv_path": str(csv_path), "summary": summarize_csv(csv_path)})
        except (FileNotFoundError, ValueError, RuntimeError, KeyError) as error:
            self._send_json(400, {"error": f"Benchmark failed: {error}"})
        finally:
            BENCHMARK_LOCK.release()

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


def load_config():
    """Read config.local.json (Unreal paths for this PC). Raises a clear error if it's missing."""
    if not CONFIG.exists():
        raise FileNotFoundError("config.local.json not found. Copy config.example.json and fill in your Unreal paths.")
    return load_json(CONFIG)


def latest_capture():
    """Find the newest CSV Unreal has already saved, so the page can show it on startup."""
    if not CONFIG.exists():
        return {"csv_path": None, "note": "No config.local.json, so Unreal's capture folder is unknown."}
    newest = find_newest_csv(capture_folder(load_config()))
    if newest is None:
        return {"csv_path": None, "note": "No Unreal captures yet. Click Benchmark in Unreal."}
    return {"csv_path": str(newest)}


def open_window(url):
    """Open FrameForge in its own Edge app window, or in the default browser if Edge isn't found."""
    for edge in EDGE_PATHS:
        if edge.exists():
            subprocess.Popen([str(edge), f"--app={url}"])
            return
    webbrowser.open(url)


def start(open_app=True):
    """Start the server, open the window, and keep serving until Ctrl+C."""
    url = f"http://{HOST}:{PORT}"
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)  # bind first, so the page can load immediately
    except OSError:
        print(f"Port {PORT} is busy - FrameForge is probably already running. Opening its window.")
        if open_app:
            open_window(url)
        return
    print(f"FrameForge running at {url}  (Ctrl+C to stop)")
    if open_app:
        open_window(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("FrameForge stopped.")


if __name__ == "__main__":
    start()
