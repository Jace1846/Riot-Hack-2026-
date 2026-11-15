"""pipeline.py - the ONE optimization loop. The command line and the window both call it.

Loop: measure -> AI proposes -> validate -> benchmark in Unreal -> compare -> keep or discard -> repeat.
Start reading at: optimize().
"""
import json
from datetime import datetime
from pathlib import Path

from controller.agent import propose_experiment
from controller.analysis import compare, summarize_csv
from controller.benchmark import load_json, run_benchmark
from controller.report import build_report, build_summary, save_report

ROOT = Path(__file__).parent.parent
EXPERIMENTS = ROOT / "experiments"
REPORTS = ROOT / "reports"
CONFIG = ROOT / "config.local.json"


def load_rules():
    """The allowlist (what may be changed) and the baseline (the starting settings)."""
    return load_json(EXPERIMENTS / "allowlist.json"), load_json(EXPERIMENTS / "baseline.json")


def load_config():
    """Read config.local.json (Unreal paths for this PC). Raises a clear error if it's missing."""
    if not CONFIG.exists():
        raise FileNotFoundError("No Unreal project set yet. Paste your .uproject path in the FrameOptimizer window.")
    return load_json(CONFIG)


# Kept the same for every run, so measurements stay comparable.
# 1200 frames: the first 60 are skipped as warm-up, the rest (10-40 s of play) are measured.
RUN_DEFAULTS = {"resolution": [1920, 1080], "frames": 1200, "timeout_seconds": 300}
EPIC_GAMES = Path("C:/Program Files/Epic Games")  # where the Epic launcher installs Unreal


def make_config(uproject, unreal_exe="", map_name="", epic_folder=EPIC_GAMES):
    """Build the whole config from just the .uproject path. unreal_exe and map_name are optional overrides."""
    project = Path(uproject.strip().strip('"'))  # Windows "Copy as path" wraps the path in quotes
    if project.suffix.lower() != ".uproject":
        raise ValueError("That isn't a .uproject file. Pick the .uproject file inside your Unreal project folder.")
    if not project.exists():
        raise FileNotFoundError(f"File not found: {project}")

    # The .uproject is JSON. "EngineAssociation" says which Unreal version it belongs to, e.g. "5.5".
    version = load_json(project).get("EngineAssociation", "")
    exe = Path(unreal_exe.strip().strip('"')) if unreal_exe.strip() else (
        epic_folder / f"UE_{version}" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe")
    if not exe.exists():
        raise FileNotFoundError(f"Couldn't find Unreal {version} at {exe}. Paste the path to UnrealEditor.exe "
                                "under More options.")

    return {"unreal_exe": exe.as_posix(), "project": project.as_posix(),
            "map": map_name.strip() or default_map(project), **RUN_DEFAULTS}


def default_map(project):
    """The map the project opens by default (GameDefaultMap in DefaultEngine.ini), or "" if none is set.

    The ini stores it as "/Game/Maps/Benchmark.Benchmark"; Unreal's command line wants "/Game/Maps/Benchmark".
    """
    ini = Path(project).parent / "Config" / "DefaultEngine.ini"
    if not ini.exists():
        return ""
    for line in ini.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        key, _, value = line.partition("=")
        if key.strip().lower() == "gamedefaultmap" and value.strip():
            return value.strip().split(".")[0]
    return ""


def save_config(config):
    """Write config.local.json (ignored by Git, so these paths stay on this PC)."""
    CONFIG.write_text(json.dumps(config, indent=2))


def optimize(rounds, config, client=None, progress=print, measure=None, reports_folder=None, goal=""):
    """Measure, let the AI propose, test, keep what helps, repeat.

    rounds   = how many AI experiments to try (the developer picks this).
    goal     = optional direction from the developer, passed to the AI every round.
    progress = called with a short status line after each step, so the UI can show it.
    measure  = optional; tests pass a fake so Unreal isn't needed. It gets
               (experiment, current_best) and returns a summary from summarize_csv().
    Returns the starting numbers, the best settings found, and what happened each round.
    Nothing in the Unreal project is changed here: the developer decides whether to apply "changes".
    """
    if not isinstance(rounds, int) or not 1 <= rounds <= 10:
        raise ValueError("Rounds must be a whole number from 1 to 10.")

    allowlist, baseline = load_rules()
    if measure is None:
        def measure(experiment, current_best):
            return summarize_csv(run_benchmark(experiment, current_best, allowlist, config))
    # Each run gets its own folder, so an older run's reports are never overwritten.
    folder = Path(reports_folder or REPORTS / f"run_{datetime.now():%Y%m%d_%H%M%S}")

    progress("Measuring the baseline in Unreal...")
    best = baseline
    best_summary = start_summary = measure(baseline, baseline)
    tried = []  # this run's experiments AND their measured outcome, so the AI learns from them
    history = []
    stopped_early = None

    for number in range(1, rounds + 1):
        try:
            progress(f"Round {number}/{rounds}: asking the AI for a change...")
            experiment = propose_experiment(best_summary, allowlist, best, tried, client=client, goal=goal)
            changes = ", ".join(f"{s}={v}" for s, v in experiment["settings"].items())

            progress(f"Round {number}/{rounds}: testing {changes} in Unreal...")
            after = measure(experiment, best)
        except (FileNotFoundError, ValueError, RuntimeError) as error:
            # A failed AI call or benchmark ends the run, but the finished rounds are kept.
            stopped_early = f"Stopped in round {number}: {error}"
            progress(stopped_early)
            break

        comparison = compare(best_summary, after)
        text = build_report(experiment, best, best_summary, after, comparison, allowlist)
        report = save_report(text, folder / f"round{number}_{experiment['name']}")

        # Keep only measured improvements; the next round builds on top of them.
        kept = comparison["verdict"] == "improved"
        if kept:
            best = {"name": "best", "settings": {**best["settings"], **experiment["settings"]}}
            best_summary = after

        outcome = (f"{comparison['verdict']} (median {comparison['median_change_pct']:+.1f}%), "
                   f"{'kept' if kept else 'discarded'}")
        tried.append({**experiment, "outcome": outcome})
        progress(f"Round {number}/{rounds}: {changes} → {outcome}")
        history.append({"round": number, "experiment": experiment, "comparison": comparison,
                         "kept": kept, "report": str(report)})

    result = {
        "start": start_summary,
        "best": best_summary,
        "start_settings": baseline["settings"],
        "best_settings": best["settings"],
        # Only the settings that differ from the start: what the report lists and Apply writes.
        "changes": {s: v for s, v in best["settings"].items() if baseline["settings"].get(s) != v},
        "total": compare(start_summary, best_summary),
        "rounds": history,
        "stopped_early": stopped_early,
        "goal": goal.strip(),
    }
    result["summary_report"] = str(save_report(build_summary(result), folder, "summary.md"))
    progress(f"Done. Summary: {result['summary_report']}")
    return result
