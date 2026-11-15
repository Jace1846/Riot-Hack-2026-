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
    lines = [f"# FrameOptimizer report: {experiment['name']}", ""]

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


def build_summary(result):
    """Markdown summary of a whole optimize() run: start vs best, every round, and the settings to apply."""
    start, best = result["start"], result["best"]
    lines = ["# FrameOptimizer run summary", ""]
    if result.get("goal"):
        lines += [f"**Developer's direction:** {result['goal']}", ""]
    lines += [
        f"## Overall: {result['total']['verdict']}",
        "",
        "| Metric | Start | Best | Change |",
        "|---|---|---|---|",
        _row("Median frame time (ms)", start["median_ms"], best["median_ms"]),
        _row("p95 frame time (ms)", start["p95_ms"], best["p95_ms"]),
        _row("Median FPS", start["median_fps"], best["median_fps"]),
        "",
        "## Rounds",
        "",
        "| Round | Change | FPS | Median | p95 | Verdict | Kept |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in result["rounds"]:
        changes = ", ".join(f"`{s}`={v}" for s, v in r["experiment"]["settings"].items())
        c = r["comparison"]
        fps = f"{r['before']['median_fps']} → {r['after']['median_fps']}" if r.get("before") else ""
        label = "0 (potato test)" if r.get("potato") else r["round"]
        kept = "no (ceiling test)" if r.get("potato") else ("yes" if r["kept"] else "no")
        lines.append(f"| {label} | {changes} | {fps} | {c['median_change_pct']:+.1f}% | {c['p95_change_pct']:+.1f}% "
                     f"| {c['verdict']} | {kept} |")
    if result.get("stopped_early"):
        lines += ["", f"**{result['stopped_early']}**"]

    lines += ["", "## Settings to apply", ""]
    if result["changes"]:
        for setting, value in result["changes"].items():
            lines.append(f"- `{setting}`: {result['start_settings'].get(setting)} → {value}")
        lines += ["", "FrameOptimizer has not changed your Unreal project. Check the visual trade-off in each "
                      "round's report, then click Apply to project in the window if you approve."]
    else:
        lines.append("No tested change gave a clear measured improvement. Keep the starting settings.")

    lines += ["", "---", "*The AI suggests. Measurements decide. The developer approves.*", ""]
    return "\n".join(lines)


def save_report(text, folder, filename="report.md"):
    """Write the report into folder (created if needed) and return its path."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
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
    """One table row: label | before | after | % change. A 0 "before" has no % change (can't divide by 0)."""
    if not before:
        return f"| {label} | {before} | {after} | n/a |"
    change = (after - before) / before * 100
    return f"| {label} | {before} | {after} | {change:+.1f}% |"
