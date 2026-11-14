import json
from datetime import datetime

import pytest

from controller import report
from controller.report import build_results, new_run_dir, write_report


# ---------------------------------------------------------------------------
# Small fake inputs (synthetic): each run only needs its median frame time
# ---------------------------------------------------------------------------

def runs(*ms_values):
    return [{"median_frame_ms": ms} for ms in ms_values]


def experiment(exp_id, ms_values, setting="sg.ShadowQuality", value=2):
    return {"experiment": {"id": exp_id, "changes": {setting: value}}, "runs": runs(*ms_values)}


BASELINE = experiment("baseline", [20.1, 20.3, 20.0], value=3)


# ---------------------------------------------------------------------------
# build_results
# ---------------------------------------------------------------------------

def test_best_is_the_biggest_verified_improvement():
    results = build_results("test", "synthetic", BASELINE, [
        experiment("small_win", [19.0, 19.1, 19.0]),
        experiment("big_win", [15.0, 15.1, 15.0]),
        experiment("no_change", [20.0, 20.2, 20.1]),
    ])
    assert results["best"] == "big_win"


def test_no_best_when_nothing_improved():
    results = build_results("test", "synthetic", BASELINE, [
        experiment("no_change", [20.0, 20.2, 20.1]),
    ])
    assert results["best"] is None


def test_data_source_must_be_labeled():
    with pytest.raises(ValueError):
        build_results("test", "probably real", BASELINE, [])


def test_results_keep_the_raw_runs():
    results = build_results("test", "synthetic", BASELINE, [experiment("x", [18.0, 18.1, 18.0])])
    assert results["baseline"]["runs"] == BASELINE["runs"]
    assert results["experiments"][0]["runs"] == runs(18.0, 18.1, 18.0)


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------

def test_writes_json_and_markdown(tmp_path):
    results = build_results("test", "synthetic", BASELINE, [experiment("shadow_02", [17.9, 18.2, 18.0])])
    json_path, md_path = write_report(tmp_path, results)

    assert json.loads(json_path.read_text(encoding="utf-8")) == results

    md = md_path.read_text(encoding="utf-8")
    assert "SYNTHETIC" in md
    assert "Best verified experiment: **shadow_02**" in md
    assert "Visual equivalence was not checked" in md


def test_markdown_handles_not_enough_runs(tmp_path):
    results = build_results("test", "synthetic", BASELINE, [experiment("two_runs", [18.0, 18.1])])
    _, md_path = write_report(tmp_path, results)
    assert "| - | - | - | - | not enough runs |" in md_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# new_run_dir
# ---------------------------------------------------------------------------

def test_new_run_dir_never_overwrites(tmp_path, monkeypatch):
    # Freeze the clock so both calls pick the same folder name.
    class FrozenClock:
        @staticmethod
        def now():
            return datetime(2026, 11, 14, 15, 30, 0)

    monkeypatch.setattr(report, "datetime", FrozenClock)

    first = new_run_dir("demo", reports_dir=tmp_path)
    assert first.name == "20261114-153000_demo"
    with pytest.raises(FileExistsError):
        new_run_dir("demo", reports_dir=tmp_path)
