"""ui/server.py - tiny local web server for the FrameOptimizer React page.

Run:   py main.py   (or py ui/server.py) - opens the FrameOptimizer window automatically.

Only listens on 127.0.0.1 (this computer). The API key you paste in the page is used for
one request and never saved to disk. Uses only Python's standard library - no Flask etc.
"""
import json
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))  # so "controller" can be imported when run from ui/

import anthropic  # noqa: E402

from controller.analysis import summarize_csv  # noqa: E402
from controller.apply import apply_settings, engine_ini, undo_apply  # noqa: E402
from controller.benchmark import capture_folder, find_newest_csv, run_benchmark  # noqa: E402
from controller.pipeline import CONFIG, load_config, load_rules, make_config, optimize, save_config  # noqa: E402

PAGE = Path(__file__).parent / "index.html"
HOST, PORT = "127.0.0.1", 8000

# Only one Unreal job at a time: two at once would fight over the GPU and ruin both measurements.
UNREAL_LOCK = threading.Lock()

# The optimize loop takes minutes, so it runs in the background and the page asks for this every second.
OPTIMIZE = {"running": False, "lines": [], "result": None, "error": None}

# Edge ships with Windows. Its "app mode" opens a clean window with no tabs or address bar.
EDGE_PATHS = [
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/project":
            self._send_json(200, {"config": load_config() if CONFIG.exists() else None})
        elif self.path == "/api/latest-csv":
            self._send_json(200, latest_capture())
        elif self.path == "/api/optimize/status":
            self._send_json(200, OPTIMIZE)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        routes = {"/api/analyze": self._analyze, "/api/benchmark": self._benchmark, "/api/optimize": self._optimize,
                  "/api/apply": self._apply, "/api/undo-apply": self._undo_apply, "/api/project": self._project}
        if self.path not in routes:
            return self._send_json(404, {"error": "Not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}")
            routes[self.path](body)
        except (FileNotFoundError, ValueError, RuntimeError, KeyError) as error:
            self._send_json(400, {"error": str(error)})  # expected problems, e.g. a missing file
        except Exception as error:  # a bug: still tell the page, or it just shows "Request failed"
            self._send_json(500, {"error": f"Unexpected error: {type(error).__name__}: {error}"})

    def _project(self, body):
        """Set the Unreal project from a pasted .uproject path. Finds Unreal and the map, then saves the config."""
        if UNREAL_LOCK.locked():
            raise ValueError("Wait for the running benchmark to finish before changing the project.")
        config = make_config(str(body.get("uproject", "")), str(body.get("unreal_exe", "")), str(body.get("map", "")))
        save_config(config)
        self._send_json(200, {"config": config})

    def _analyze(self, body):
        """Just the measurements of one CSV. No Unreal, no AI."""
        csv_path = body.get("csv_path", "").strip()
        if not csv_path:
            raise ValueError("Enter the path to a CSV file first.")
        self._send_json(200, {"summary": summarize_csv(ROOT / csv_path)})

    def _benchmark(self, body):
        """Measure only: launch Unreal with the baseline settings and return the capture's analysis."""
        if not UNREAL_LOCK.acquire(blocking=False):
            return self._send_json(409, {"error": "Unreal is already running a benchmark. Wait for it to finish."})
        try:
            allowlist, baseline = load_rules()
            csv_path = run_benchmark(baseline, baseline, allowlist, load_config())
            self._send_json(200, {"csv_path": str(csv_path), "summary": summarize_csv(csv_path)})
        finally:
            UNREAL_LOCK.release()

    def _optimize(self, body):
        """Start the full loop in the background. The page follows it through /api/optimize/status."""
        api_key = str(body.get("api_key", "")).strip()
        if not api_key:
            raise ValueError("Paste your Anthropic API key first.")
        goal = str(body.get("goal", "")).strip()
        if len(goal) > 500:
            raise ValueError("Keep the direction under 500 characters.")
        freedom = body.get("freedom", 50)
        if not isinstance(freedom, int) or not 0 <= freedom <= 100:
            raise ValueError("Quality freedom must be a whole number from 0 to 100.")
        frames = body.get("frames", 1200)
        if not isinstance(frames, int) or not 600 <= frames <= 3600:
            raise ValueError("Test length must be a whole number of frames from 600 to 3600.")
        options = {"freedom": freedom, "frames": frames}
        config = load_config()
        if not UNREAL_LOCK.acquire(blocking=False):
            return self._send_json(409, {"error": "Unreal is already running a benchmark. Wait for it to finish."})
        OPTIMIZE.update(running=True, lines=[], result=None, error=None)
        threading.Thread(target=run_optimize, args=(body.get("rounds"), config, api_key, goal, options), daemon=True).start()
        self._send_json(202, {"started": True})

    def _apply(self, body):
        """Write the last run's winning settings into DefaultEngine.ini (after a backup).

        The settings come from the server's own memory of the last measured run, never from
        the page, so nothing unmeasured can be written.
        """
        result = OPTIMIZE["result"]
        if OPTIMIZE["running"] or result is None:
            raise ValueError("Finish an Optimize run first.")
        allowlist, _ = load_rules()
        ini = engine_ini(load_config())
        backup = apply_settings(ini, result["changes"], allowlist)
        self._send_json(200, {"ini": str(ini), "backup": str(backup), "applied": result["changes"]})

    def _undo_apply(self, body):
        """Restore DefaultEngine.ini from the newest FrameOptimizer backup."""
        ini = engine_ini(load_config())
        undo_apply(ini)
        self._send_json(200, {"ini": str(ini)})

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
        if self.path == "/api/optimize/status":
            return  # the page asks every second; don't flood the terminal
        print(f"{self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


def run_optimize(rounds, config, api_key, goal="", options=None):
    """Background job: run the loop, collecting progress lines and the final result for the page.

    options = {"freedom", "frames"} from the Optimize panel's sliders.
    """
    try:
        client = anthropic.Anthropic(api_key=api_key)
        OPTIMIZE["result"] = optimize(rounds, config, client=client, progress=OPTIMIZE["lines"].append, goal=goal,
                                      **(options or {}))
    except Exception as error:  # any crash must reach the page, or it just shows "testing..." forever
        OPTIMIZE["error"] = f"Optimize failed: {type(error).__name__}: {error}"
    finally:
        OPTIMIZE["running"] = False
        UNREAL_LOCK.release()


def latest_capture():
    """Find the newest CSV Unreal has already saved, so the page can show it on startup."""
    if not CONFIG.exists():
        return {"csv_path": None, "note": "Set your Unreal project above to get started."}
    newest = find_newest_csv(capture_folder(load_config()))
    if newest is None:
        return {"csv_path": None, "note": "No Unreal captures yet. Click Benchmark in Unreal."}
    return {"csv_path": str(newest)}


def open_window(url):
    """Open FrameOptimizer in its own Edge app window, or in the default browser if Edge isn't found."""
    for edge in EDGE_PATHS:
        if edge.exists():
            # A separate Edge profile makes Edge start its own copy, which honors --window-size.
            # (An already-running Edge ignores it, so the window opened big and then shrank.)
            # Kept in AppData, not the project folder, so OneDrive and Git don't pick it up.
            profile = Path(os.environ.get("LOCALAPPDATA", ROOT)) / "FrameOptimizer" / "edge-profile"
            subprocess.Popen([str(edge), f"--app={url}", "--window-size=360,480", f"--user-data-dir={profile}",
                              "--no-first-run", "--no-default-browser-check"])
            return
    webbrowser.open(url)


class Server(ThreadingHTTPServer):
    # Python's default (True) lets a second copy share port 8000 on Windows, and the page's
    # requests then get split between both copies. False makes the second copy fail to start instead.
    allow_reuse_address = False


def start(open_app=True):
    """Start the server, open the window, and keep serving until Ctrl+C."""
    url = f"http://{HOST}:{PORT}"
    try:
        server = Server((HOST, PORT), Handler)  # bind first, so the page can load immediately
    except OSError:
        print(f"Port {PORT} is busy - FrameOptimizer is probably already running. Opening its window.")
        if open_app:
            open_window(url)
        return
    print(f"FrameOptimizer running at {url}  (Ctrl+C to stop)")
    if open_app:
        open_window(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("FrameOptimizer stopped.")


if __name__ == "__main__":
    start()
