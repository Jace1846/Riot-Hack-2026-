"""
parser.py: turn one Unreal CSV profiler file into a short summary.

Loop step:      3. Measure  (after Unreal has written a CSV)
Start reading:  parse_csv()
Used by:        report.py (and later runner.py)

An Unreal CSV has one row per frame and one column per stat (100+ columns).
At the end it repeats the header row and adds one metadata row like:
    [HasHeaderRowAtEnd],1,[platform],Windows,[config],Development
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


# ---------------------------------------------------------------------------
# Main function
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


# ---------------------------------------------------------------------------
# Helpers (each one does a single job for parse_csv)
# ---------------------------------------------------------------------------

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
