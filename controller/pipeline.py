"""pipeline.py - the ONE optimization loop. The command line and the window both call it.

Loop: measure -> AI proposes -> validate -> benchmark in Unreal -> compare -> keep or discard -> repeat.
Start reading at: optimize().
"""
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
        raise FileNotFoundError("config.local.json not found. Copy config.example.json and fill in your Unreal paths.")
    return load_json(CONFIG)


def optimize(rounds, config, client=None, progress=print, measure=None, reports_folder=None, goal=""):
    """Measure, let the AI propose, test, keep what helps, repeat.

    rounds   = how many AI experiments to try (the developer picks this).
    goal     = optional direction from the developer, passed to the AI every round.
    progress = called with a short status line after each step, so the UI can show it.
    measure  = optional; tests pass a fake so Unreal isn't needed. It gets
               (experiment, current_best) and returns a summary from summarize_csv().
    Returns the starting numbers, the best settings found, and what happened each round.
    Nothing in the Unreal project is changed: the developer applies the result by hand.
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
        "total": compare(start_summary, best_summary),
        "rounds": history,
        "stopped_early": stopped_early,
        "goal": goal.strip(),
    }
    result["summary_report"] = str(save_report(build_summary(result), folder, "summary.md"))
    progress(f"Done. Summary: {result['summary_report']}")
    return result
