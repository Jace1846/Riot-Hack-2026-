"""
verifier.py: decide, from measurements only, whether a candidate beat the baseline.

Loop step:      4. Verify  (after 3+ runs of baseline and candidate)
Start reading:  compare()
Used by:        report.py

The agent never decides this. Each config is run 3+ times; we compare the
median of those runs and only say "improved" if the gain is bigger than the
run-to-run noise (spread).
"""

import statistics

MIN_RUNS = 3


def spread(values):
    """How much the runs disagree with each other: slowest minus fastest."""
    return max(values) - min(values)


def compare(baseline_ms, candidate_ms, min_runs=MIN_RUNS):
    """Compare two lists of per-run frame times (ms, lower is better).

    Example: compare([20.1, 20.3, 20.0], [17.9, 18.2, 18.0])
    Returns a dict with a "verdict" plus every number used to reach it.
    """
    if len(baseline_ms) < min_runs or len(candidate_ms) < min_runs:
        return {
            "verdict": "not enough runs",
            "reason": f"need at least {min_runs} runs each, "
                      f"got {len(baseline_ms)} baseline and {len(candidate_ms)} candidate",
        }

    base_median = statistics.median(baseline_ms)
    cand_median = statistics.median(candidate_ms)
    improvement = base_median - cand_median  # positive = candidate is faster
    noise = max(spread(baseline_ms), spread(candidate_ms))

    if improvement > noise:
        verdict = "improved"
    elif -improvement > noise:
        verdict = "worse"
    else:
        verdict = "no clear change"

    return {
        "verdict": verdict,
        "baseline_median_ms": base_median,
        "candidate_median_ms": cand_median,
        "improvement_ms": improvement,
        "improvement_pct": 100 * improvement / base_median,
        "noise_ms": noise,
        "baseline_runs_ms": list(baseline_ms),
        "candidate_runs_ms": list(candidate_ms),
        "reason": f"median changed by {improvement:+.2f} ms, noise is {noise:.2f} ms",
    }
