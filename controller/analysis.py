"""
analysis.py: turn Unreal CSVs into numbers, then decide if a candidate beat the baseline.

Loop steps:     3. Measure (parse_csv)  ->  4. Verify (compare)
Start reading:  parse_csv(), then compare()
Used by:        report.py, main.py

An Unreal CSV has one row per frame and one column per stat (100+ columns).
At the end it repeats the header row and adds one metadata row like:
    [HasHeaderRowAtEnd],1,[platform],Windows,[config],Development

The agent never decides "better". Each config is run 3+ times; we compare the
median of those runs and only say "improved" if the gain is bigger than the
run-to-run noise (spread).
"""

import csv
import math
import statistics

# Column names we look for. Check these against the first REAL capture.
FRAME_COL = "FrameTime"
GPU_COL = "GPUTime"
GPU_PASS_PREFIX = "GPU/"  # e.g. "GPU/ShadowDepths" = time spent drawing shadows

# If the GPU is busy for at least 90% of the frame, call it GPU-bound.
GPU_BOUND_RATIO = 0.9

MIN_RUNS = 3


# ---------------------------------------------------------------------------
# Part 1: read one CSV
# ---------------------------------------------------------------------------

def parse_csv(path):
    """Read one capture file and return a summary dict."""
    header, data_rows, metadata = split_csv(path)

    frame_times = column_numbers(header, data_rows, FRAME_COL)
    gpu_times = column_numbers(header, data_rows, GPU_COL)
    if not frame_times:
        raise ValueError(f"{path}: no '{FRAME_COL}' values found")

    median_frame = statistics.median(frame_times)
    median_gpu = statistics.median(gpu_times) if gpu_times else None

    return {
        "file": str(path),
        "frame_count": len(frame_times),
        "median_frame_ms": median_frame,
        "p95_frame_ms": percentile(frame_times, 95),
        "fps_estimate": 1000 / median_frame,
        "median_gpu_ms": median_gpu,
        "bottleneck": guess_bottleneck(median_frame, median_gpu),
        "gpu_passes_ms": gpu_pass_medians(header, data_rows),
        "metadata": metadata,
    }


def split_csv(path):
    """Split the file into: header row, frame rows, metadata dict."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = rows[0]
    data_rows = []
    metadata = {}

    for row in rows[1:]:
        if not row:                  # empty line: skip it
            continue
        if row == header:            # repeated header: not a frame
            continue
        if row[0].startswith("["):   # metadata row: the data is over
            metadata = read_metadata(row)
            break
        data_rows.append(row)

    return header, data_rows, metadata


def column_numbers(header, data_rows, name):
    """All numbers in the column called `name`. Blank or text cells are skipped."""
    if name not in header:
        return []
    index = header.index(name)

    numbers = []
    for row in data_rows:
        if index >= len(row):
            continue
        try:
            numbers.append(float(row[index]))
        except ValueError:
            continue
    return numbers


def gpu_pass_medians(header, data_rows):
    """Median time of every "GPU/..." column, e.g. {"ShadowDepths": 7.0, ...}."""
    medians = {}
    for name in header:
        if not name.startswith(GPU_PASS_PREFIX):
            continue
        numbers = column_numbers(header, data_rows, name)
        if numbers:
            short_name = name[len(GPU_PASS_PREFIX):]
            medians[short_name] = statistics.median(numbers)
    return medians


def percentile(values, pct):
    """Nearest-rank percentile. pct=95 gives the value 95% of frames are at or below."""
    ordered = sorted(values)
    rank = math.ceil(pct / 100 * len(ordered))
    return ordered[max(rank - 1, 0)]


def guess_bottleneck(median_frame, median_gpu):
    """GPU-bound if the GPU is busy for most of the frame, otherwise CPU-bound."""
    if median_gpu is None:
        return "unknown"
    if median_gpu >= GPU_BOUND_RATIO * median_frame:
        return "GPU-bound"
    return "CPU-bound"


def read_metadata(row):
    """Turn [platform],Windows,[config],Development into {"platform": "Windows", ...}."""
    metadata = {}
    for i in range(0, len(row) - 1, 2):
        key = row[i]
        if key.startswith("[") and key.endswith("]"):
            metadata[key[1:-1]] = row[i + 1]
    return metadata


# ---------------------------------------------------------------------------
# Part 2: compare baseline vs candidate (the verifier)
# ---------------------------------------------------------------------------

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
