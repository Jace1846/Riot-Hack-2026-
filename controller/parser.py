"""Read one Unreal CSV profiler file and summarize it.

Unreal writes one row per frame, one column per stat (100+ columns).
At the end it may repeat the header row and add a metadata row like:
    [HasHeaderRowAtEnd],1,[platform],Windows,[config],Development
"""

import csv
import math
import statistics

# Column names. Check these against the first REAL capture before trusting them.
FRAME_COL = "FrameTime"
GPU_COL = "GPUTime"
GPU_PASS_PREFIX = "GPU/"

# If the GPU is busy for at least this share of the frame, call it GPU-bound.
GPU_BOUND_RATIO = 0.9


def parse_csv(path):
    """Return a summary dict for one capture file."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = rows[0]
    data_rows = []
    metadata = {}

    for row in rows[1:]:
        if not row:
            continue
        if row[0].startswith("["):  # metadata row: stop reading data
            metadata = read_metadata(row)
            break
        if row == header:  # repeated header row: data is over
            continue
        data_rows.append(row)

    columns = {name: numbers_in_column(header, data_rows, name) for name in header}

    frame_times = columns.get(FRAME_COL, [])
    if not frame_times:
        raise ValueError(f"{path}: no '{FRAME_COL}' values found")
    gpu_times = columns.get(GPU_COL, [])

    median_frame = statistics.median(frame_times)
    median_gpu = statistics.median(gpu_times) if gpu_times else None

    gpu_passes = {
        name[len(GPU_PASS_PREFIX):]: statistics.median(values)
        for name, values in columns.items()
        if name.startswith(GPU_PASS_PREFIX) and values
    }

    return {
        "file": str(path),
        "frame_count": len(frame_times),
        "median_frame_ms": median_frame,
        "p95_frame_ms": percentile(frame_times, 95),
        "fps_estimate": 1000 / median_frame,
        "median_gpu_ms": median_gpu,
        "bottleneck": guess_bottleneck(median_frame, median_gpu),
        "gpu_passes_ms": gpu_passes,
        "metadata": metadata,
    }


def numbers_in_column(header, data_rows, name):
    """Return the numeric values in one column (looked up by name), skipping blanks."""
    index = header.index(name)
    values = []
    for row in data_rows:
        if index >= len(row):
            continue
        try:
            values.append(float(row[index]))
        except ValueError:  # blank or text cell
            continue
    return values


def percentile(values, pct):
    """Nearest-rank percentile, e.g. pct=95 -> the value 95% of frames are at or below."""
    ordered = sorted(values)
    rank = math.ceil(pct / 100 * len(ordered))
    return ordered[max(rank - 1, 0)]


def guess_bottleneck(median_frame, median_gpu):
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
