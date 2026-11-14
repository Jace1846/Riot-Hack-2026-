"""analysis.py - turns Unreal CSV profiler captures into numbers, and compares two runs.

Loop step: Analysis (Benchmark -> Unreal -> *Analysis* -> Report).
Start reading at: summarize_csv(), then compare().
"""
import csv
import math
import statistics

# The three parts of the engine that work in parallel on every frame.
# The frame can only finish when the slowest one finishes - that one is the bottleneck.
THREAD_COLUMNS = {"game": "GameThreadTime", "render": "RenderThreadTime", "gpu": "GPUTime"}
THREAD_LABELS = {"game": "Game thread (CPU)", "render": "Render thread (CPU)", "gpu": "GPU"}

TIMELINE_POINTS = 200  # how many points the UI chart gets, so it stays fast


def summarize_csv(path, skip_warmup=20):
    """Read one Unreal CSV capture and return a summary dictionary (all times in ms)."""
    frame_times = []
    gpu_pass_times = {}  # e.g. {"GPU/ShadowDepths": [3.3, 3.1, ...]}
    thread_times = {}  # e.g. {"gpu": [18.1, 17.0, ...]} - only for columns the CSV has

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "FrameTime" not in reader.fieldnames:
            raise ValueError(f"{path} has no FrameTime column - is it an Unreal CSV profile?")

        gpu_columns = [name for name in reader.fieldnames if name.startswith("GPU/")]
        threads = {key: column for key, column in THREAD_COLUMNS.items() if column in reader.fieldnames}

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
            for key, column in threads.items():
                thread_times.setdefault(key, []).append(float(row[column]))

    # Throw away the slow warm-up frames at the start of the capture.
    frame_times = frame_times[skip_warmup:]
    thread_times = {key: times[skip_warmup:] for key, times in thread_times.items()}
    if len(frame_times) < 10:
        raise ValueError(f"{path} has only {len(frame_times)} frames after warm-up - benchmark too short or failed?")

    sorted_times = sorted(frame_times)
    median_ms = statistics.median(sorted_times)

    return {
        "frames": len(frame_times),
        "median_ms": round(median_ms, 2),
        "p95_ms": round(_percentile(sorted_times, 95), 2),
        "max_ms": round(sorted_times[-1], 2),
        "median_fps": round(1000 / median_ms, 1),
        "gpu_passes": {
            name: round(statistics.median(times[skip_warmup:]), 2)
            for name, times in gpu_pass_times.items()
        },
        "bottleneck": find_bottleneck(median_ms, thread_times),
        "timeline": _timeline(frame_times, thread_times),
    }


def find_bottleneck(median_frame_ms, thread_times):
    """Work out whether the CPU (game/render thread) or the GPU is limiting the frame rate.

    thread_times = {"game": [...], "render": [...], "gpu": [...]} (any of them may be missing).
    Returns None if the CSV has none of the thread columns.
    """
    if not thread_times:
        return None

    medians = {key: round(statistics.median(times), 2) for key, times in thread_times.items()}

    # For every frame, which part took longest? Count how often each one "won".
    limited_counts = {key: 0 for key in thread_times}
    frame_count = len(next(iter(thread_times.values())))
    for i in range(frame_count):
        slowest = max(thread_times, key=lambda key: thread_times[key][i])
        limited_counts[slowest] += 1

    # The overall bottleneck is the part with the biggest median time.
    # If the runner-up is within 10% of it, both are holding the frame back: call it "mixed".
    ranked = sorted(medians, key=medians.get, reverse=True)
    top = ranked[0]
    mixed = len(ranked) > 1 and medians[ranked[1]] >= medians[top] * 0.9

    return {
        "bound": "mixed" if mixed else top,
        "label": f"Mixed: {THREAD_LABELS[top]} and {THREAD_LABELS[ranked[1]]}" if mixed else THREAD_LABELS[top],
        "share_of_frame_pct": round(medians[top] / median_frame_ms * 100),
        "median_ms": medians,
        "frames_limited_pct": {key: round(count / frame_count * 100, 1) for key, count in limited_counts.items()},
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

def _timeline(frame_times, thread_times):
    """Per-frame times for the UI chart, thinned out to at most TIMELINE_POINTS points.

    Keeps the slowest frame of each bucket so spikes (hitches) don't disappear from the chart.
    """
    step = max(1, math.ceil(len(frame_times) / TIMELINE_POINTS))
    picks = []
    for start in range(0, len(frame_times), step):
        bucket = range(start, min(start + step, len(frame_times)))
        picks.append(max(bucket, key=lambda i: frame_times[i]))

    timeline = {"frame_index": picks, "frame": [frame_times[i] for i in picks]}
    for key, times in thread_times.items():
        timeline[key] = [times[i] for i in picks]
    return timeline


def _percentile(sorted_values, pct):
    """Nearest-rank percentile: the value that pct% of frames are at or below."""
    index = math.ceil(pct / 100 * len(sorted_values)) - 1
    return sorted_values[max(index, 0)]


def _pct_change(old, new):
    """Percent change from old to new. 14.0 -> 13.0 gives about -7.1."""
    return (new - old) / old * 100
