"""report.py - turns before/after measurements into a readable Markdown report.

Loop step: Report (Analysis -> *Report*).
Start reading at: build_report().
"""
from pathlib import Path

RECOMMENDATIONS = {
    "improved": "Measurements support keeping this change. Check the visual trade-off below before approving.",
    "worse": "This change made performance worse. Recommend reverting to the baseline.",
    "no clear change": "No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.",
}


def build_report(experiment, baseline, before, after, comparison, allowlist):
    """Return the report as a Markdown string. before/after are summaries from analysis.summarize_csv()."""
    lines = [f"# FrameForge report: {experiment['name']}", ""]

    # Data source banner - always first, so nobody mistakes test data for real results.
    if before["synthetic"] or after["synthetic"]:
        lines.append("> ⚠ **SYNTHETIC TEST DATA.** These numbers are not real Unreal measurements.")
    else:
        lines.append("> Data source: real Unreal CSV profiler captures.")
    lines.append("")

    lines += ["## What changed", ""]
    for setting, new_value in experiment["settings"].items():
        old_value = baseline["settings"].get(setting, "engine default")
        lines.append(f"- `{setting}`: {old_value} → {new_value}")
    lines += ["", f"**Why the agent proposed it:** {experiment.get('reason', 'No reason given.')}", ""]

    lines += [
        "## Results",
        "",
        f"Frames analyzed: {before['frames']} before, {after['frames']} after.",
        "",
        "| Metric | Before | After | Change |",
        "|---|---|---|---|",
        _row("Median frame time (ms)", before["median_ms"], after["median_ms"]),
        _row("p95 frame time (ms)", before["p95_ms"], after["p95_ms"]),
        _row("Worst frame (ms)", before["max_ms"], after["max_ms"]),
        _row("Median FPS", before["median_fps"], after["median_fps"]),
        "",
    ]

    if before["gpu_passes"]:
        lines += ["### GPU passes (median ms)", "", "| Pass | Before | After | Change |", "|---|---|---|---|"]
        for name, old_ms in before["gpu_passes"].items():
            if name in after["gpu_passes"]:
                lines.append(_row(name, old_ms, after["gpu_passes"][name]))
        lines.append("")

    lines += _bottleneck_section(before.get("bottleneck"), after.get("bottleneck"))

    verdict = comparison["verdict"]
    lines += [
        f"## Verdict: {verdict}",
        "",
        RECOMMENDATIONS[verdict],
        "",
        "## Visual trade-off",
        "",
    ]
    for setting in experiment["settings"]:
        lines.append(f"- `{setting}`: {allowlist[setting]['quality_impact']}")

    lines += ["", "---", "*The AI suggests. Measurements decide. The developer approves.*", ""]
    return "\n".join(lines)


def save_report(text, folder):
    """Write report.md into folder (created if needed) and return its path."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "report.md"
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- Helpers

def _bottleneck_section(before, after):
    """Markdown lines comparing the CPU/GPU bottleneck before and after. Empty if either run lacks the data."""
    if not before or not after:
        return []

    lines = [
        "### CPU vs GPU bottleneck",
        "",
        f"Before: **{before['label']}**. After: **{after['label']}**.",
        "",
        "| Part (median ms) | Before | After | Change |",
        "|---|---|---|---|",
    ]
    for part, old_ms in before["median_ms"].items():
        if part in after["median_ms"]:
            lines.append(_row(part, old_ms, after["median_ms"][part]))
    lines.append("")

    if before["bound"] != after["bound"]:
        note = f"Note: the bottleneck moved from {before['label']} to {after['label']}."
        if after["bound"] != "gpu":
            note += " The GPU is no longer the main limit, so further graphics-setting cuts will help less."
        lines += [note, ""]
    return lines


def _row(label, before, after):
    """One table row: label | before | after | % change."""
    change = (after - before) / before * 100
    return f"| {label} | {before} | {after} | {change:+.1f}% |"
