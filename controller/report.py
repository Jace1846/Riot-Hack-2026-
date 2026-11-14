"""
report.py: save the results of one session to a new reports/<run_id>/ folder.

Loop step:      5. Report  (after the verifier has judged each experiment)
Start reading:  new_run_dir() -> build_results() -> write_report()
Uses:           analysis.py (compare)

Writes two files:
    results.json   all the data; the single source of truth
    report.md      the same results as a readable page
"""

import json
from datetime import datetime
from pathlib import Path

from controller.analysis import compare
from controller.benchmark import PROJECT_ROOT

REPORTS_DIR = PROJECT_ROOT / "reports"
SCHEMA_VERSION = 1                       # bump if the results.json layout changes
DATA_SOURCES = ("actual", "synthetic")   # every report must say which one it is


# ---------------------------------------------------------------------------
# Main functions, in the order you call them
# ---------------------------------------------------------------------------

def new_run_dir(label, reports_dir=REPORTS_DIR):
    """Create a new folder like reports/20261114-153000_shadow_test/.

    Raises an error if it already exists, so old results are never overwritten.
    """
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(reports_dir) / f"{stamp}_{label}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def build_results(run_id, data_source, baseline, experiments):
    """Combine all measurements into one dict (this becomes results.json).

    baseline:     {"experiment": {...}, "runs": [parse_csv summaries]}
    experiments:  [{"experiment": {...}, "hypothesis": "...", "runs": [...]}, ...]
    """
    if data_source not in DATA_SOURCES:
        raise ValueError(f"data_source must be one of {DATA_SOURCES}, got {data_source!r}")

    baseline_ms = frame_times(baseline["runs"])

    rows = []
    for item in experiments:
        candidate_ms = frame_times(item["runs"])
        rows.append({
            "id": item["experiment"]["id"],
            "changes": item["experiment"]["changes"],
            "hypothesis": item.get("hypothesis"),
            "runs": item["runs"],
            "comparison": compare(baseline_ms, candidate_ms),
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created": datetime.now().isoformat(timespec="seconds"),
        "data_source": data_source,
        "baseline": {
            "id": baseline["experiment"]["id"],
            "changes": baseline["experiment"]["changes"],
            "runs": baseline["runs"],
        },
        "experiments": rows,
        "best": pick_best(rows),
    }


def write_report(run_dir, results):
    """Write results.json and report.md into run_dir. Returns both file paths."""
    run_dir = Path(run_dir)
    json_path = run_dir / "results.json"
    md_path = run_dir / "report.md"

    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(results), encoding="utf-8")
    return json_path, md_path


# ---------------------------------------------------------------------------
# Helpers for build_results
# ---------------------------------------------------------------------------

def frame_times(runs):
    """One number per run: that run's median frame time."""
    return [run["median_frame_ms"] for run in runs]


def pick_best(rows):
    """The id of the "improved" experiment with the biggest gain, or None."""
    improved = [row for row in rows if row["comparison"]["verdict"] == "improved"]
    if not improved:
        return None
    biggest = max(improved, key=lambda row: row["comparison"]["improvement_ms"])
    return biggest["id"]


# ---------------------------------------------------------------------------
# Helpers for report.md
# ---------------------------------------------------------------------------

def to_markdown(results):
    """Build the text of report.md."""
    baseline_runs = ", ".join(f"{ms:.2f}" for ms in frame_times(results["baseline"]["runs"]))

    lines = [
        f"# FrameForge report: {results['run_id']}",
        "",
        f"- Created: {results['created']}",
        f"- Data source: **{results['data_source'].upper()}**",
        f"- Baseline `{results['baseline']['id']}` runs (median frame ms): {baseline_runs}",
        "",
        "## Experiments",
        "",
        "| Experiment | Changes | Median ms | FPS | Change | Noise ms | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in results["experiments"]:
        lines.append(table_row(row))

    lines += ["", "## Result", ""]
    if results["best"]:
        lines.append(f"Best verified experiment: **{results['best']}**")
    else:
        lines.append("No experiment beat the baseline by more than the run-to-run noise.")

    lines += [
        "",
        "Positive change = faster than baseline. 'improved' means the gain is larger "
        "than the run-to-run noise (>= 3 runs each, medians compared).",
        "Visual equivalence was not checked in this report.",
        "",
    ]
    return "\n".join(lines)


def table_row(row):
    """One line of the experiments table."""
    c = row["comparison"]
    changes = ", ".join(f"{name}={value}" for name, value in row["changes"].items())

    if c["verdict"] == "not enough runs":
        return f"| {row['id']} | {changes} | - | - | - | - | {c['verdict']} |"

    ms = c["candidate_median_ms"]
    fps = 1000 / ms
    return (
        f"| {row['id']} | {changes} | {ms:.2f} | {fps:.1f} "
        f"| {c['improvement_pct']:+.1f}% | {c['noise_ms']:.2f} | {c['verdict']} |"
    )
