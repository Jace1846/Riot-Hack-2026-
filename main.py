"""main.py - FrameOptimizer's front door. Reads the command you typed and starts the right thing.

The optimization loop itself lives in controller/pipeline.py.
Start reading at: main().
"""
import sys

from controller.analysis import compare, summarize_csv
from controller.benchmark import load_json, validate_experiment
from controller.pipeline import REPORTS, load_config, load_rules, optimize
from controller.report import build_report, save_report

USAGE = """Usage:
  py main.py
      Open the FrameOptimizer window (benchmark, charts, and the optimize loop in one place).
  py main.py optimize [rounds]
      Run the full loop in Unreal: measure, AI proposes, test, keep what helps. Default 3 rounds.
      Needs the ANTHROPIC_API_KEY environment variable, and your Unreal project set once in the window.
  py main.py report <before.csv> <after.csv> <experiment.json>
      Write a report from two CSVs you already have (no Unreal or AI needed)."""


def main(args):
    """args = the words typed after 'py main.py'. Returns 0 on success, 1 on bad usage."""
    if len(args) == 0:
        from ui.server import start  # imported here so the other commands don't load the web server
        start()
    elif args[0] == "optimize" and len(args) <= 2 and all(a.isdigit() for a in args[1:]):
        optimize_command(int(args[1]) if len(args) == 2 else 3)
    elif len(args) == 4 and args[0] == "report":
        report_command(args[1], args[2], args[3])
    else:
        print(USAGE)
        return 1
    return 0


def optimize_command(rounds):
    """Run the loop, printing progress as it goes, then show where the result is."""
    result = optimize(rounds, load_config())
    total = result["total"]
    print(f"Overall: {total['verdict']} (median {total['median_change_pct']:+.1f}%, p95 {total['p95_change_pct']:+.1f}%)")
    print("Review the summary, then apply the settings you approve in Unreal yourself.")


def report_command(before_csv, after_csv, experiment_path):
    """Skip Unreal: build one before/after report from two existing CSVs."""
    allowlist, baseline = load_rules()
    experiment = load_json(experiment_path)

    problems = validate_experiment(experiment, allowlist)
    if problems:
        raise ValueError("Experiment rejected: " + " ".join(problems))

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
