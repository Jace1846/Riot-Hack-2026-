"""main.py - FrameForge's front door. Reads the command you typed and runs the pipeline.

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
  py main.py propose <baseline.csv>
      Ask the AI to propose one experiment. Writes experiments/<name>.json for you to review.
  py main.py run <experiment.json>
      Benchmark the baseline and the experiment in Unreal, then write a report.
  py main.py report <before.csv> <after.csv> <experiment.json>
      Write a report from two CSVs you already have (no Unreal needed)."""


def main(args):
    """args = the words typed after 'py main.py'. Returns 0 on success, 1 on bad usage."""
    if len(args) == 2 and args[0] == "propose":
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
    tried = [load_json(p) for p in sorted(EXPERIMENTS.glob("*.json")) if p.name not in ("allowlist.json", "baseline.json")]

    print("Asking the AI for an experiment...")
    experiment = propose_experiment(summary, allowlist, baseline, tried)

    # Never overwrite an existing experiment file.
    path = EXPERIMENTS / f"{experiment['name']}.json"
    number = 2
    while path.exists():
        path = EXPERIMENTS / f"{experiment['name']}_{number}.json"
        number += 1
    experiment["name"] = path.stem
    path.write_text(json.dumps(experiment, indent=2) + "\n")

    if summary["synthetic"]:
        print("  [Based on SYNTHETIC DATA]")
    print(f"Proposal: {experiment['settings']}")
    print(f"Reason:   {experiment['reason']}")
    print(f"Saved to: {path}")
    print(f"Review it, then run:  py main.py run {path.relative_to(ROOT)}")


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

    label = "  [SYNTHETIC DATA]" if before["synthetic"] or after["synthetic"] else ""
    print(
        f"{experiment['name']}: {comparison['verdict']} "
        f"(median {comparison['median_change_pct']:+.1f}%, p95 {comparison['p95_change_pct']:+.1f}%){label}"
    )
    print(f"Report: {path}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"Error: {error}")
        sys.exit(1)
