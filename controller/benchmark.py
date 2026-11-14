"""benchmark.py - checks experiments against the allowlist, then runs them in Unreal.

Loop step: Validator -> Benchmark (Agent -> *Validator* -> *Benchmark* -> Unreal).
Start reading at: validate_experiment(), then run_benchmark().
"""
import json
import subprocess
import time
from pathlib import Path

# Added to every run so frame rate is never capped by the monitor or Unreal.
UNCAP_FPS = ["r.VSync 0", "t.MaxFPS 0"]


def validate_experiment(experiment, allowlist):
    """Return a list of problems with the experiment. An empty list means it is approved."""
    problems = []

    if not experiment.get("name"):
        problems.append("Experiment has no name.")

    settings = experiment.get("settings")
    if not settings:
        problems.append("Experiment has no settings to change.")
        return problems

    for setting, value in settings.items():
        if setting not in allowlist:
            problems.append(f"{setting} is not an approved setting.")
        elif value not in allowlist[setting]["values"]:
            allowed = allowlist[setting]["values"]
            problems.append(f"{setting} = {value} is not allowed. Allowed values: {allowed}.")

    return problems


def run_benchmark(experiment, baseline, allowlist, config, dry_run=False):
    """Run one experiment in Unreal and return the path of the CSV it wrote.

    With dry_run=True, nothing is launched; the command string is returned instead.
    """
    problems = validate_experiment(experiment, allowlist)
    if problems:
        raise ValueError("Experiment rejected: " + " ".join(problems))

    command = build_command(experiment, baseline, config)
    if dry_run:
        return command

    if not Path(config["unreal_exe"]).exists():
        raise FileNotFoundError(f"Unreal not found at {config['unreal_exe']} - check config.local.json")

    started = time.time()
    try:
        subprocess.run(command, timeout=config["timeout_seconds"])
    except subprocess.TimeoutExpired:
        # Unreal may not quit by itself after profiling. subprocess has already closed it;
        # if the capture finished, the CSV is still there and we pick it up below.
        print(f"Note: Unreal was closed after {config['timeout_seconds']}s timeout.")

    csv_folder = capture_folder(config)
    csv_path = find_newest_csv(csv_folder, started)
    if csv_path is None:
        raise RuntimeError(f"Benchmark failed: no new CSV appeared in {csv_folder}")
    return csv_path


def build_command(experiment, baseline, config):
    """Build the Unreal command line: baseline settings, then the experiment's changes on top."""
    settings = {**baseline["settings"], **experiment["settings"]}

    console_commands = [f"{name} {value}" for name, value in settings.items()]
    console_commands += UNCAP_FPS
    console_commands.append(f"csvprofile frames={config['frames']}")

    width, height = config["resolution"]
    # Built as one string (not a list) so the quotes reach Unreal exactly as written.
    return (
        f'"{config["unreal_exe"]}" "{config["project"]}" {config["map"]} '
        f"-game -windowed -ResX={width} -ResY={height} "
        f'-ExecCmds="{",".join(console_commands)}"'
    )


def load_json(path):
    """Read a JSON file (allowlist, baseline, experiment, or config) into a Python dictionary."""
    with open(path) as f:
        return json.load(f)


def capture_folder(config):
    """The folder where Unreal's csvprofile command saves its CSV files for this project."""
    return Path(config["project"]).parent / "Saved" / "Profiling" / "CSV"


def find_newest_csv(folder, started_after=0):
    """Return the newest CSV in folder created after started_after (a time.time() value), or None."""
    folder = Path(folder)
    if not folder.exists():
        return None
    new_csvs = [p for p in folder.rglob("*.csv") if p.stat().st_mtime > started_after]
    if not new_csvs:
        return None
    return max(new_csvs, key=lambda p: p.stat().st_mtime)
