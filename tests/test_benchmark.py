"""Tests for controller/benchmark.py. No Unreal needed: Unreal is never actually launched."""
import os
from pathlib import Path

import pytest

from controller.benchmark import build_command, capture_folder, find_newest_csv, load_json, run_benchmark, validate_experiment

EXPERIMENTS = Path(__file__).parent.parent / "experiments"
ALLOWLIST = load_json(EXPERIMENTS / "allowlist.json")


def test_example_experiment_is_approved():
    assert validate_experiment(load_json(EXPERIMENTS / "shadow_02.json"), ALLOWLIST) == []


def test_baseline_is_approved():
    assert validate_experiment(load_json(EXPERIMENTS / "baseline.json"), ALLOWLIST) == []


def test_unknown_setting_is_rejected():
    problems = validate_experiment({"name": "x", "settings": {"r.Something.Fake": 1}}, ALLOWLIST)
    assert problems == ["r.Something.Fake is not an approved setting."]


def test_disallowed_value_is_rejected():
    problems = validate_experiment({"name": "x", "settings": {"r.ScreenPercentage": 10}}, ALLOWLIST)
    assert len(problems) == 1
    assert "r.ScreenPercentage = 10 is not allowed" in problems[0]


def test_missing_name_and_empty_settings_are_rejected():
    assert validate_experiment({"settings": {"r.VolumetricFog": 0}}, ALLOWLIST) == ["Experiment has no name."]
    assert validate_experiment({"name": "x", "settings": {}}, ALLOWLIST) == ["Experiment has no settings to change."]


def test_all_problems_are_reported_at_once():
    experiment = {"name": "x", "settings": {"r.Something.Fake": 1, "r.ScreenPercentage": 10}}
    assert len(validate_experiment(experiment, ALLOWLIST)) == 2


# ---------------------------------------------------------------- run_benchmark / build_command
# No Unreal needed: these use dry_run, fake paths, and fake CSV files.

BASELINE = load_json(EXPERIMENTS / "baseline.json")
CONFIG = load_json(Path(__file__).parent.parent / "config.example.json")
SHADOW = load_json(EXPERIMENTS / "shadow_02.json")


def test_command_merges_baseline_and_experiment():
    command = build_command(SHADOW, BASELINE, CONFIG)
    assert "r.Shadow.MaxResolution 1024" in command  # experiment's change wins
    assert "r.Shadow.MaxResolution 2048" not in command
    assert "r.ScreenPercentage 100" in command  # untouched baseline settings kept


def test_command_uncaps_fps_and_sets_resolution_and_length():
    command = build_command(SHADOW, BASELINE, CONFIG)
    assert "r.VSync 0" in command and "t.MaxFPS 0" in command
    assert "-ResX=1920 -ResY=1080" in command
    assert "csvprofile frames=600" in command


def test_dry_run_returns_command_without_launching():
    # config.example.json points at a fake Unreal path, so a real launch would fail.
    command = run_benchmark(SHADOW, BASELINE, ALLOWLIST, CONFIG, dry_run=True)
    assert "-ExecCmds=" in command


def test_invalid_experiment_is_refused_before_launch():
    bad = {"name": "x", "settings": {"r.ScreenPercentage": 10}}
    with pytest.raises(ValueError):
        run_benchmark(bad, BASELINE, ALLOWLIST, CONFIG)


def test_missing_unreal_gives_clear_error():
    with pytest.raises(FileNotFoundError):
        run_benchmark(SHADOW, BASELINE, ALLOWLIST, CONFIG)


def test_find_newest_csv_ignores_old_files(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("x")
    new.write_text("x")
    os.utime(old, (1000, 1000))  # pretend old.csv was written long ago
    os.utime(new, (3000, 3000))

    assert find_newest_csv(tmp_path, started_after=2000) == new
    assert find_newest_csv(tmp_path, started_after=4000) is None
    assert find_newest_csv(tmp_path / "missing", started_after=0) is None


def test_capture_folder_is_inside_the_unreal_project():
    folder = capture_folder({"project": "C:/Games/MyGame/MyGame.uproject"})
    assert folder == Path("C:/Games/MyGame/Saved/Profiling/CSV")
