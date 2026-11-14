"""analysis.py - turns Unreal CSV profiler captures into numbers, and compares two runs.

Loop step: Analysis (Benchmark -> Unreal -> *Analysis* -> Report).
Start reading at: summarize_csv(), then compare().
"""
import csv
import math
import statistics


def summarize_csv(path, skip_warmup=20):
    """Read one Unreal CSV capture and return a summary dictionary (all times in ms)."""
    frame_times = []
    gpu_pass_times = {}  # e.g. {"GPU/ShadowDepths": [3.3, 3.1, ...]}

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "FrameTime" not in reader.fieldnames:
            raise ValueError(f"{path} has no FrameTime column - is it an Unreal CSV profile?")

        gpu_columns = [name for name in reader.fieldnames if name.startswith("GPU/")]

        for row in reader:
            # Unreal ends the file with a repeated header and a metadata line.
            # Those rows don't have a number in FrameTime, so we stop there.
            try:
                frame_time = float(row["FrameTime"])
            except (TypeError, ValueError):
                break

            frame_times.append(frame_time)
            for name in gpu_columns:
                gpu_pass_times.setdefault(name, []).append(float(row[name]))

    # Throw away the slow warm-up frames at the start of the capture.
    frame_times = frame_times[skip_warmup:]
    if len(frame_times) < 10:
        raise ValueError(f"{path} has only {len(frame_times)} frames after warm-up - benchmark too short or failed?")

    sorted_times = sorted(frame_times)
    median_ms = statistics.median(sorted_times)

    # Fake test files label themselves in their footer, so reports can't mistake them for real data.
    with open(path) as f:
        synthetic = "[synthetic],true" in f.read()

    return {
        "synthetic": synthetic,
        "frames": len(frame_times),
        "median_ms": round(median_ms, 2),
        "p95_ms": round(_percentile(sorted_times, 95), 2),
        "max_ms": round(sorted_times[-1], 2),
        "median_fps": round(1000 / median_ms, 1),
        "gpu_passes": {
            name: round(statistics.median(times[skip_warmup:]), 2)
            for name, times in gpu_pass_times.items()
        },
    }


def compare(baseline, candidate, threshold_pct=3.0):
    """Compare two summaries. Negative change = faster (better)."""
    median_change = _pct_change(baseline["median_ms"], candidate["median_ms"])
    p95_change = _pct_change(baseline["p95_ms"], candidate["p95_ms"])

    if median_change <= -threshold_pct and p95_change < threshold_pct:
        verdict = "improved"
    elif median_change >= threshold_pct:
        verdict = "worse"
    else:
        verdict = "no clear change"

    return {
        "median_change_pct": round(median_change, 1),
        "p95_change_pct": round(p95_change, 1),
        "verdict": verdict,
    }


# ---------------------------------------------------------------- Helpers

def _percentile(sorted_values, pct):
    """Nearest-rank percentile: the value that pct% of frames are at or below."""
    index = math.ceil(pct / 100 * len(sorted_values)) - 1
    return sorted_values[max(index, 0)]


def _pct_change(old, new):
    """Percent change from old to new. 14.0 -> 13.0 gives about -7.1."""
    return (new - old) / old * 100
