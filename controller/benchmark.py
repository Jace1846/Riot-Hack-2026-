"""
benchmark.py: check an experiment against the allowlist, then run it in Unreal.

Loop steps:     2. Validate  ->  3. Measure
Start reading:  validate_experiment(), then run_benchmark()
Used by:        main.py, later agent.py

Guardrail: nothing reaches Unreal unless validate_experiment() returns [].

An experiment file looks like:
    {"id": "shadow_02", "description": "...", "changes": {"sg.ShadowQuality": 2}}

Python only launches Unreal, waits, and copies the CSV. The timing itself
(warm-up, csvprofile, quit) is done inside Unreal by the Level Blueprint.

Paths come from config.local.json (your real paths, never committed).
If that file doesn't exist, config.example.json is used, which is only
good enough for --dry-run.
"""

import json
import re
import shutil
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ALLOWLIST = PROJECT_ROOT / "experiments" / "allowlist.json"
LOCAL_CONFIG = PROJECT_ROOT / "config.local.json"
EXAMPLE_CONFIG = PROJECT_ROOT / "config.example.json"

# The id becomes part of a folder name, so keep it to safe characters.
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
ALLOWED_KEYS = {"id", "description", "changes"}

# Always sent first, on every run. Without these, VSync / the frame cap
# hold every frame at ~16.67 ms and no setting change would show up.
BENCHMARK_CMDS = "r.VSync 0,t.MaxFPS 0"


# ---------------------------------------------------------------------------
# Loading files
# ---------------------------------------------------------------------------

def load_json(path):
    """Read a JSON file and return its contents."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_allowlist(path=DEFAULT_ALLOWLIST):
    """Return {setting_name: {"min": int, "max": int, ...}}."""
    return load_json(path)


def load_config():
    """Your real config.local.json if it exists, otherwise the example."""
    path = LOCAL_CONFIG if LOCAL_CONFIG.exists() else EXAMPLE_CONFIG
    return load_json(path)


# ---------------------------------------------------------------------------
# Checking an experiment (the guardrail)
# ---------------------------------------------------------------------------

def validate_experiment(experiment, allowlist):
    """Return a list of problems. An empty list means the experiment is allowed."""
    if not isinstance(experiment, dict):
        return ["experiment must be a JSON object"]

    errors = []

    extra = set(experiment) - ALLOWED_KEYS
    if extra:
        errors.append(f"unknown top-level keys: {sorted(extra)}")

    exp_id = experiment.get("id")
    if not isinstance(exp_id, str) or not ID_PATTERN.match(exp_id):
        errors.append("id must be 1-64 characters: letters, numbers, _ or -")

    if "description" in experiment and not isinstance(experiment["description"], str):
        errors.append("description must be a string")

    changes = experiment.get("changes")
    if not isinstance(changes, dict) or not changes:
        errors.append("changes must be a non-empty object")
        return errors

    for setting, value in changes.items():
        problem = check_change(setting, value, allowlist)
        if problem:
            errors.append(problem)

    return errors


def check_change(setting, value, allowlist):
    """Check one setting/value pair. Returns an error message, or None if it's fine."""
    rule = allowlist.get(setting)
    if rule is None:
        return f"{setting}: not in the allowlist"

    # bool is a kind of int in Python (True == 1), so reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, int):
        return f"{setting}: value must be a whole number, got {value!r}"

    if not rule["min"] <= value <= rule["max"]:
        return f"{setting}: {value} is outside {rule['min']}-{rule['max']}"

    return None


def to_exec_cmds(experiment, allowlist):
    """Build the -ExecCmds text, e.g. "sg.ShadowQuality 2,r.ScreenPercentage 75".

    Validates first and raises ValueError if the experiment is not allowed.
    """
    errors = validate_experiment(experiment, allowlist)
    if errors:
        raise ValueError("experiment not allowed: " + "; ".join(errors))
    return ",".join(f"{name} {value}" for name, value in experiment["changes"].items())


# ---------------------------------------------------------------------------
# Running Unreal
# ---------------------------------------------------------------------------

def run_benchmark(experiment, allowlist, config, run_dir, run_number, dry_run=True):
    """Run Unreal once for this experiment.

    dry_run=True:  only print the command, launch nothing, return None.
    dry_run=False: launch Unreal, wait, copy the new CSV into run_dir,
                   and return the copied file's path.
    """
    command = build_command(experiment, allowlist, config)

    if dry_run:
        print("DRY RUN - would launch:")
        print("  " + subprocess.list2cmdline(command))
        return None

    started = time.time()
    subprocess.run(command, timeout=config["timeout_seconds"], check=False)
    return collect_csv(config, started, run_dir, experiment["id"], run_number)


def build_command(experiment, allowlist, config):
    """The exact Unreal command, as a list (no shell, so nothing can be injected).

    to_exec_cmds() raises ValueError if the experiment is not on the allowlist.
    """
    settings = to_exec_cmds(experiment, allowlist)
    return [
        config["unreal_editor"],
        config["uproject"],
        "-game",                      # run the game, not the editor UI
        "-windowed",
        f"-ResX={config['res_x']}",
        f"-ResY={config['res_y']}",
        f"-ExecCmds={BENCHMARK_CMDS},{settings}",
    ]


def csv_folder(config):
    """Where Unreal writes captures: <Project>/Saved/Profiling/CSV/."""
    return Path(config["uproject"]).parent / "Saved" / "Profiling" / "CSV"


def collect_csv(config, started, run_dir, exp_id, run_number):
    """Copy the CSV Unreal wrote during this run into run_dir. Never overwrites."""
    folder = csv_folder(config)
    new_files = [f for f in folder.glob("*.csv") if f.stat().st_mtime >= started]
    if not new_files:
        raise RuntimeError(f"Unreal finished but wrote no new CSV in {folder}")

    newest = max(new_files, key=lambda f: f.stat().st_mtime)
    target = Path(run_dir) / f"{exp_id}_run{run_number}_actual.csv"
    if target.exists():
        raise FileExistsError(f"{target} already exists")
    shutil.copy2(newest, target)
    return target
