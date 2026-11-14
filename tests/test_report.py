"""Tests for controller/report.py. The fixture CSV is hand-made test input, not a real capture."""
from pathlib import Path

from controller.analysis import compare, summarize_csv
from controller.benchmark import load_json
from controller.report import build_report, save_report

ROOT = Path(__file__).parent.parent
ALLOWLIST = load_json(ROOT / "experiments" / "allowlist.json")
BASELINE = load_json(ROOT / "experiments" / "baseline.json")
SHADOW = load_json(ROOT / "tests" / "fixtures" / "experiment.json")

BEFORE = summarize_csv(ROOT / "tests" / "fixtures" / "sample.csv")
# A made-up "after" run: every time 10% faster. Only for testing the report layout.
AFTER = {
    **BEFORE,
    "median_ms": round(BEFORE["median_ms"] * 0.9, 2),
    "p95_ms": round(BEFORE["p95_ms"] * 0.9, 2),
    "max_ms": round(BEFORE["max_ms"] * 0.9, 2),
    "median_fps": round(BEFORE["median_fps"] / 0.9, 1),
}


def make_report(before=BEFORE, after=AFTER):
    return build_report(SHADOW, BASELINE, before, after, compare(before, after), ALLOWLIST)


def test_report_contains_the_key_sections():
    report = make_report()
    assert "r.Shadow.MaxResolution`: 2048 → 1024" in report
    assert SHADOW["reason"] in report
    assert "## Verdict: improved" in report
    assert "Blurrier, more pixelated shadow edges" in report  # trade-off from allowlist
    assert "GPU/ShadowDepths" in report


def test_report_has_bottleneck_section():
    report = make_report()
    assert "### CPU vs GPU bottleneck" in report
    assert "Before: **GPU**. After: **GPU**." in report
    assert "moved" not in report  # same bottleneck before and after


def test_report_notes_when_bottleneck_moves_to_cpu():
    cpu_after = {**AFTER, "bottleneck": {**BEFORE["bottleneck"], "bound": "render", "label": "Render thread (CPU)"}}
    report = make_report(after=cpu_after)
    assert "moved from GPU to Render thread (CPU)" in report
    assert "will help less" in report


def test_report_skips_bottleneck_when_missing():
    old_before = {key: value for key, value in BEFORE.items() if key != "bottleneck"}
    assert "CPU vs GPU bottleneck" not in make_report(before=old_before)


def test_save_report_writes_file(tmp_path):
    path = save_report(make_report(), tmp_path / "shadow_02")
    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("# FrameOptimizer report: shadow_02")
