"""Tests for controller/analysis.py. The fixture CSV is hand-made test input, not a real capture."""
from pathlib import Path

import pytest

from controller.analysis import compare, summarize_csv

FIXTURE = Path(__file__).parent / "fixtures" / "sample.csv"


# ---------------------------------------------------------------- summarize_csv

def test_summary_of_fixture():
    summary = summarize_csv(FIXTURE)

    assert summary["frames"] == 240  # 300 frames minus 60 warm-up (footer rows ignored)
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


def test_too_few_frames_raises(tmp_path):
    short = tmp_path / "short.csv"
    short.write_text("FrameTime\n" + "14.0\n" * 65)  # only 5 left after warm-up
    with pytest.raises(ValueError):
        summarize_csv(short)


# ---------------------------------------------------------------- bottleneck

def test_fixture_is_gpu_bound():
    bottleneck = summarize_csv(FIXTURE)["bottleneck"]

    assert bottleneck["bound"] == "gpu"
    assert set(bottleneck["median_ms"]) == {"game", "render", "gpu"}
    assert bottleneck["frames_limited_pct"]["gpu"] > 50
    assert round(sum(bottleneck["frames_limited_pct"].values())) == 100


def test_cpu_bound_game_thread(tmp_path):
    cpu = tmp_path / "cpu.csv"
    cpu.write_text("FrameTime,GameThreadTime,RenderThreadTime,GPUTime\n" + "20.0,19.0,8.0,10.0\n" * 80)  # 20 left after warm-up
    bottleneck = summarize_csv(cpu)["bottleneck"]

    assert bottleneck["bound"] == "game"
    assert bottleneck["frames_limited_pct"]["game"] == 100.0


def test_near_tie_is_mixed(tmp_path):
    tie = tmp_path / "tie.csv"
    tie.write_text("FrameTime,GameThreadTime,RenderThreadTime,GPUTime\n" + "16.0,5.0,15.0,15.5\n" * 80)  # 20 left after warm-up
    assert summarize_csv(tie)["bottleneck"]["bound"] == "mixed"


def test_no_thread_columns_gives_no_bottleneck(tmp_path):
    plain = tmp_path / "plain.csv"
    plain.write_text("FrameTime\n" + "14.0\n" * 80)  # 20 left after warm-up
    summary = summarize_csv(plain)

    assert summary["bottleneck"] is None
    assert len(summary["timeline"]["frame"]) == 20


def test_timeline_is_thinned_but_keeps_the_spike():
    summary = summarize_csv(FIXTURE)
    timeline = summary["timeline"]

    assert len(timeline["frame"]) <= 200
    assert len(timeline["gpu"]) == len(timeline["frame"])
    assert max(timeline["frame"]) == summary["max_ms"]  # the hitch isn't averaged away


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
