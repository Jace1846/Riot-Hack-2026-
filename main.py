"""main.py - FrameOptimizer's front door. Reads the command you typed and runs the pipeline.

Start reading at: main().
"""
import json
import sys
from pathlib import Path

from controller.agent import propose_experiment
from controller.analysis import compare, summarize_csv
from controller.benchmark import load_json, run_benchmark, validate_experiment
from controller.report import build_report, save_report

ROOT = Path(__file__).parent
EXPERIMENTS = ROOT / "experiments"
REPORTS = ROOT / "reports"

USAGE = """Usage:
  py main.py
      Open the FrameOptimizer window (benchmark, charts, and AI in one place).
  py main.py propose <baseline.csv>
      Ask the AI to propose one experiment. Writes experiments/<name>.json for you to review.
  py main.py run <experiment.json>
      Benchmark the baseline and the experiment in Unreal, then write a report.
  py main.py report <before.csv> <after.csv> <experiment.json>
      Write a report from two CSVs you already have (no Unreal needed)."""


def main(args):
    """args = the words typed after 'py main.py'. Returns 0 on success, 1 on bad usage."""
    if len(args) == 0:
        # Imported here, not at the top: ui/server.py imports from this file, so a top-level
        # import would be circular.
        from ui.server import start
        start()
    elif len(args) == 2 and args[0] == "propose":
        propose_command(args[1])
    elif len(args) == 2 and args[0] == "run":
        run_command(args[1])
    elif len(args) == 4 and args[0] == "report":
        report_command(args[1], args[2], args[3])
    else:
        print(USAGE)
        return 1
    return 0


def propose_command(baseline_csv):
    """AI suggests: read the baseline CSV, ask Claude for one experiment, save it for human review."""
    allowlist, baseline = _load_rules()
    summary = summarize_csv(baseline_csv)
    tried = load_tried_experiments()

    print("Asking the AI for an experiment...")
    experiment = propose_experiment(summary, allowlist, baseline, tried)
    path = save_experiment(experiment)

    print(f"Proposal: {experiment['settings']}")
    print(f"Reason:   {experiment['reason']}")
    print(f"Saved to: {path}")
    print(f"Review it, then run:  py main.py run {path.relative_to(ROOT)}")


def load_tried_experiments():
    """Every experiment JSON already in experiments/ (so the AI doesn't repeat them)."""
    return [load_json(p) for p in sorted(EXPERIMENTS.glob("*.json")) if p.name not in ("allowlist.json", "baseline.json")]


def save_experiment(experiment):
    """Write experiments/<name>.json, never overwriting an existing file. Returns the path."""
    path = EXPERIMENTS / f"{experiment['name']}.json"
    number = 2
    while path.exists():
        path = EXPERIMENTS / f"{experiment['name']}_{number}.json"
        number += 1
    experiment["name"] = path.stem
    path.write_text(json.dumps(experiment, indent=2) + "\n")
    return path


def run_command(experiment_path):
    """Benchmark baseline, then experiment, back to back so conditions match."""
    config_path = ROOT / "config.local.json"
    if not config_path.exists():
        raise FileNotFoundError("config.local.json not found. Copy config.example.json and fill in your paths.")

    config = load_json(config_path)
    allowlist, baseline = _load_rules()
    experiment = load_json(experiment_path)

    print("Running baseline in Unreal...")
    before_csv = run_benchmark(baseline, baseline, allowlist, config)
    print(f"Running {experiment['name']} in Unreal...")
    after_csv = run_benchmark(experiment, baseline, allowlist, config)

    _analyze_and_report(experiment, baseline, allowlist, before_csv, after_csv)


def report_command(before_csv, after_csv, experiment_path):
    """Skip Unreal: build a report from two existing CSVs."""
    allowlist, baseline = _load_rules()
    experiment = load_json(experiment_path)

    problems = validate_experiment(experiment, allowlist)
    if problems:
        raise ValueError("Experiment rejected: " + " ".join(problems))

    _analyze_and_report(experiment, baseline, allowlist, before_csv, after_csv)


def optimize(rounds, config, client=None, progress=print, measure=None, reports_folder=REPORTS):
    """One-click optimize: measure, let the AI propose, test, keep what helps, repeat.

    rounds   = how many AI experiments to try (the developer picks this).
    progress = called with a short status line after each step, so the UI can show it.
    measure  = optional; tests pass a fake so Unreal isn't needed. It gets
               (experiment, current_best) and returns a summary from summarize_csv().
    Returns the starting numbers, the best settings found, and what happened each round.
    """
    if not isinstance(rounds, int) or not 1 <= rounds <= 10:
        raise ValueError("Rounds must be a whole number from 1 to 10.")

    allowlist, baseline = _load_rules()
    if measure is None:
        def measure(experiment, current_best):
            return summarize_csv(run_benchmark(experiment, current_best, allowlist, config))

    progress("Measuring the baseline in Unreal...")
    best = baseline
    best_summary = start_summary = measure(baseline, baseline)
    tried = []  # experiments from this run, so the AI doesn't repeat itself
    history = []

    for number in range(1, rounds + 1):
        progress(f"Round {number}/{rounds}: asking the AI for a change...")
        experiment = propose_experiment(best_summary, allowlist, best, tried, client=client)
        tried.append(experiment)
        changes = ", ".join(f"{s}={v}" for s, v in experiment["settings"].items())

        progress(f"Round {number}/{rounds}: testing {changes} in Unreal...")
        after = measure(experiment, best)
        comparison = compare(best_summary, after)

        text = build_report(experiment, best, best_summary, after, comparison, allowlist)
        report = save_report(text, Path(reports_folder) / f"round{number}_{experiment['name']}")

        # Keep only measured improvements; the next round builds on top of them.
        kept = comparison["verdict"] == "improved"
        if kept:
            best = {"name": "best", "settings": {**best["settings"], **experiment["settings"]}}
            best_summary = after

        progress(f"Round {number}/{rounds}: {changes} → {comparison['verdict']} "
                 f"(median {comparison['median_change_pct']:+.1f}%), {'kept' if kept else 'discarded'}")
        history.append({"round": number, "experiment": experiment, "comparison": comparison,
                         "kept": kept, "report": str(report)})

    return {
        "start": start_summary,
        "best": best_summary,
        "best_settings": best["settings"],
        "total": compare(start_summary, best_summary),
        "rounds": history,
    }


# ---------------------------------------------------------------- Helpers

def _load_rules():
    """Load the allowlist and baseline every command needs."""
    return load_json(EXPERIMENTS / "allowlist.json"), load_json(EXPERIMENTS / "baseline.json")


def _analyze_and_report(experiment, baseline, allowlist, before_csv, after_csv):
    """Summarize both CSVs, compare them, save the report, and print a one-line result."""
    before = summarize_csv(before_csv)
    after = summarize_csv(after_csv)
    comparison = compare(before, after)

    text = build_report(experiment, baseline, before, after, comparison, allowlist)
    path = save_report(text, REPORTS / experiment["name"])

    print(
        f"{experiment['name']}: {comparison['verdict']} "
        f"(median {comparison['median_change_pct']:+.1f}%, p95 {comparison['p95_change_pct']:+.1f}%)"
    )
    print(f"Report: {path}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"Error: {error}")
        sys.exit(1)
