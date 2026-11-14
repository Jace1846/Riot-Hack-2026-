"""
runner.py: launch Unreal with an experiment's settings and collect the CSV.

Loop step:      3. Measure
Start reading:  run_benchmark()
Uses:           experiments.py (to_exec_cmds validates before building the command)

Python only launches Unreal, waits, and copies the CSV. The timing itself
(warm-up, csvprofile, quit) is done inside Unreal by the Level Blueprint.

Paths come from config.local.json (your real paths, never committed).
If that file doesn't exist, config.example.json is used, which is only
good enough for --dry-run.
"""

import shutil
import subprocess
import time
from pathlib import Path

from controller.experiments import PROJECT_ROOT, load_json, to_exec_cmds

LOCAL_CONFIG = PROJECT_ROOT / "config.local.json"
EXAMPLE_CONFIG = PROJECT_ROOT / "config.example.json"

# Always sent first, on every run. Without these, VSync / the frame cap
# hold every frame at ~16.67 ms and no setting change would show up.
BENCHMARK_CMDS = "r.VSync 0,t.MaxFPS 0"


# ---------------------------------------------------------------------------
# Main functions
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


def load_config():
    """Your real config.local.json if it exists, otherwise the example."""
    path = LOCAL_CONFIG if LOCAL_CONFIG.exists() else EXAMPLE_CONFIG
    return load_json(path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
