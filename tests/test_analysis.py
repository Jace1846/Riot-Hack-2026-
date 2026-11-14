"""Tests for controller/analysis.py. All data here is SYNTHETIC, not real Unreal measurements."""
from pathlib import Path

import pytest

from controller.analysis import compare, summarize_csv

FIXTURE = Path(__file__).parent / "fixtures" / "sample_synthetic.csv"


# ---------------------------------------------------------------- summarize_csv

def test_summary_of_synthetic_fixture():
    summary = summarize_csv(FIXTURE)

    assert summary["synthetic"] is True  # footer says [synthetic],true
    assert summary["frames"] == 280  # 300 frames minus 20 warm-up (footer rows ignored)
    assert 13.5 < summary["median_ms"] < 14.5
    assert summary["p95_ms"] >= summary["median_ms"]
    assert summary["max_ms"] > 30  # a planted hitch survives
    assert summary["median_fps"] == round(1000 / summary["median_ms"], 1)
    assert "GPU/ShadowDepths" in summary["gpu_passes"]


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        summarize_csv("does_not_exist.csv")


def test_csv_without_frametime_raises(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("Foo,Bar\n1,2\n")
    with pytest.raises(ValueError):
        summarize_csv(bad)


def test_file_without_synthetic_label_is_not_flagged(tmp_path):
    plain = tmp_path / "plain.csv"
    plain.write_text("FrameTime\n" + "14.0\n" * 40)
    assert summarize_csv(plain)["synthetic"] is False


def test_too_few_frames_raises(tmp_path):
    short = tmp_path / "short.csv"
    short.write_text("FrameTime\n" + "14.0\n" * 25)  # only 5 left after warm-up
    with pytest.raises(ValueError):
        summarize_csv(short)


# ---------------------------------------------------------------- compare

BASELINE = {"median_ms": 14.0, "p95_ms": 15.0}


def test_compare_improved():
    result = compare(BASELINE, {"median_ms": 13.0, "p95_ms": 14.0})
    assert result["verdict"] == "improved"
    assert result["median_change_pct"] == -7.1


def test_compare_worse():
    assert compare(BASELINE, {"median_ms": 15.0, "p95_ms": 16.0})["verdict"] == "worse"


def test_compare_small_change_is_noise():
    assert compare(BASELINE, {"median_ms": 13.86, "p95_ms": 14.9})["verdict"] == "no clear change"


def test_compare_faster_but_more_stutter_is_not_improved():
    result = compare(BASELINE, {"median_ms": 13.0, "p95_ms": 17.0})
    assert result["verdict"] != "improved"
