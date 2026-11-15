"""Tests for controller.pipeline.optimize(). SYNTHETIC: a fake Unreal (made-up frame times) and a fake AI,
so these only check the loop's logic - keep what improves, discard the rest. Not real measurements."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from controller.analysis import summarize_csv
from controller.benchmark import build_command, validate_experiment
from controller.pipeline import limit_allowlist, load_rules, make_config, optimize, potato_experiment, run_options

ROOT = Path(__file__).parent.parent
SAMPLE = summarize_csv(ROOT / "tests" / "fixtures" / "sample.csv")


class FakeClient:
    """Stands in for Claude: returns pre-written proposals, one per call."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        text = json.dumps(self.answers.pop(0))
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])


def proposal(name, setting, value):
    return {"name": name, "reason": "test", "settings": [{"setting": setting, "value": value}]}


def fake_unreal(experiment, current_best):
    """Made-up frame times: lower AA is 20% faster, fog off is 1% slower (noise), else unchanged."""
    settings = {**current_best["settings"], **experiment["settings"]}
    factor = 1.0
    if settings["r.PostProcessAAQuality"] == 3:
        factor *= 0.8
    if settings["r.VolumetricFog"] == 0:
        factor *= 1.01
    return {**SAMPLE, "median_ms": round(SAMPLE["median_ms"] * factor, 2),
            "p95_ms": round(SAMPLE["p95_ms"] * factor, 2)}


def test_keeps_improvements_and_discards_the_rest(tmp_path):
    client = FakeClient(proposal("aa_3", "r.PostProcessAAQuality", 3),
                        proposal("fog_off", "r.VolumetricFog", 0))
    lines = []
    result = optimize(2, config={}, client=client, progress=lines.append,
                      measure=fake_unreal, reports_folder=tmp_path)

    assert [r["kept"] for r in result["rounds"]] == [True, False]
    assert result["best_settings"]["r.PostProcessAAQuality"] == 3   # kept
    assert result["best_settings"]["r.VolumetricFog"] == 1          # discarded, stays at baseline
    assert result["total"]["verdict"] == "improved"
    assert all(Path(r["report"]).exists() for r in result["rounds"])
    assert any("kept" in line for line in lines)


def test_rejects_bad_round_counts():
    for bad in (0, 11, "3"):
        with pytest.raises(ValueError):
            optimize(bad, config={}, measure=fake_unreal)


def test_ai_sees_the_measured_outcome_of_earlier_rounds(tmp_path):
    client = FakeClient(proposal("fog_off", "r.VolumetricFog", 0),
                        proposal("aa_3", "r.PostProcessAAQuality", 3))
    client.prompts = []
    create = client._create
    client.beta.messages.create = lambda **kw: (client.prompts.append(kw["messages"][0]["content"]), create(**kw))[1]

    optimize(2, config={}, client=client, progress=lambda line: None, measure=fake_unreal, reports_folder=tmp_path)

    assert "fog_off: r.VolumetricFog=0 -> no clear change (median +1.0%), discarded" in client.prompts[1]


def test_run_writes_a_summary_with_the_settings_to_apply(tmp_path):
    client = FakeClient(proposal("aa_3", "r.PostProcessAAQuality", 3))
    result = optimize(1, config={}, client=client, progress=lambda line: None,
                      measure=fake_unreal, reports_folder=tmp_path)

    summary = Path(result["summary_report"]).read_text(encoding="utf-8")
    assert "## Overall: improved" in summary
    assert "`r.PostProcessAAQuality`: 4 → 3" in summary
    assert "has not changed your Unreal project" in summary


def test_failed_round_stops_the_run_but_keeps_finished_rounds(tmp_path):
    def unreal_dies_on_fog(experiment, current_best):
        if experiment["settings"].get("r.VolumetricFog") == 0:
            raise RuntimeError("Benchmark failed: no new CSV appeared")
        return fake_unreal(experiment, current_best)

    client = FakeClient(proposal("aa_3", "r.PostProcessAAQuality", 3),
                        proposal("fog_off", "r.VolumetricFog", 0))
    result = optimize(3, config={}, client=client, progress=lambda line: None,
                      measure=unreal_dies_on_fog, reports_folder=tmp_path)

    assert len(result["rounds"]) == 1 and result["rounds"][0]["kept"]
    assert "Stopped in round 2" in result["stopped_early"]
    assert result["best_settings"]["r.PostProcessAAQuality"] == 3


# ---------------------------------------------------------------- Quality freedom slider + potato test

def test_slider_trims_values_best_first():
    allowlist = {"r.ScreenPercentage": {"values": [100, 85, 70, 50], "quality_impact": "x"},
                 "r.VolumetricFog": {"values": [1, 0], "quality_impact": "x"}}
    assert limit_allowlist(allowlist, 0)["r.ScreenPercentage"]["values"] == [100]
    assert limit_allowlist(allowlist, 50)["r.ScreenPercentage"]["values"] == [100, 85, 70]
    assert limit_allowlist(allowlist, 100)["r.ScreenPercentage"]["values"] == [100, 85, 70, 50]
    assert limit_allowlist(allowlist, 25)["r.VolumetricFog"]["values"] == [1]     # an on/off switch needs 50%+
    assert limit_allowlist(allowlist, 50)["r.VolumetricFog"]["values"] == [1, 0]


def test_potato_uses_the_lowest_allowed_values():
    allowlist = {"r.ScreenPercentage": {"values": [100, 85, 70, 50], "quality_impact": "x"},
                 "r.VolumetricFog": {"values": [1, 0], "quality_impact": "x"}}
    baseline = {"settings": {"r.ScreenPercentage": 100, "r.VolumetricFog": 1}}
    assert potato_experiment(allowlist, baseline)["settings"] == {"r.ScreenPercentage": 50, "r.VolumetricFog": 0}
    assert potato_experiment(limit_allowlist(allowlist, 0), baseline) is None   # 0%: nothing may change


def test_validator_rejects_values_past_the_slider():
    allowlist, _ = load_rules()
    limited = limit_allowlist(allowlist, 50)
    assert validate_experiment({"name": "x", "settings": {"r.ScreenPercentage": 70}}, limited) == []
    assert validate_experiment({"name": "x", "settings": {"r.ScreenPercentage": 50}}, limited) != []


def test_potato_round_runs_first_and_is_never_kept(tmp_path):
    client = FakeClient(proposal("aa_3", "r.PostProcessAAQuality", 3))
    result = optimize(1, config={}, client=client, progress=lambda line: None,
                      measure=fake_unreal, reports_folder=tmp_path, freedom=100)

    potato, ai_round = result["rounds"]
    assert potato["potato"] and potato["round"] == 0 and not potato["kept"]
    assert potato["experiment"]["settings"]["r.ScreenPercentage"] == 50      # lowest value at 100%
    assert result["best_settings"]["r.ScreenPercentage"] == 100              # potato settings were not kept
    assert ai_round["kept"]


def test_rounds_record_real_before_and_after_numbers(tmp_path):
    client = FakeClient(proposal("fog_off", "r.VolumetricFog", 0))
    result = optimize(1, config={}, client=client, progress=lambda line: None,
                      measure=fake_unreal, reports_folder=tmp_path)

    r = result["rounds"][0]
    assert r["before"]["median_ms"] == SAMPLE["median_ms"]
    assert r["after"]["median_ms"] == round(SAMPLE["median_ms"] * 1.01, 2)  # measured even though discarded
    assert set(r["after"]) == {"median_ms", "p95_ms", "median_fps"}


def test_test_length_reaches_the_unreal_command():
    allowlist, baseline = load_rules()
    base = {"unreal_exe": "C:/Fake/UnrealEditor.exe", "project": "C:/Fake/Game.uproject", "map": "/Game/Map",
            "resolution": [1920, 1080], "frames": 1200, "timeout_seconds": 300}

    assert "csvprofile frames=3000" in build_command(baseline, baseline, run_options(base, frames=3000))
    assert "csvprofile frames=1200" in build_command(baseline, baseline, run_options(base))
    assert run_options(base, frames=3600)["timeout_seconds"] >= 3600 // 20 + 120   # longer test, longer timeout


def test_bad_test_length_is_refused():
    for bad in (599, 3601, "1200"):
        with pytest.raises(ValueError):
            run_options({}, frames=bad)


def test_bad_freedom_is_refused():
    for bad in (-1, 101, "50"):
        with pytest.raises(ValueError):
            optimize(1, config={}, measure=fake_unreal, freedom=bad)


# ---------------------------------------------------------------- make_config (project setup)
# Builds a fake Unreal install and a fake project in a temp folder. No real Unreal needed.

def fake_project(tmp_path, version="5.5", default_map="/Game/Maps/Benchmark.Benchmark"):
    exe = tmp_path / "Epic Games" / f"UE_{version}" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    project = tmp_path / "MyGame" / "MyGame.uproject"
    (project.parent / "Config").mkdir(parents=True)
    project.write_text(json.dumps({"EngineAssociation": version}))
    (project.parent / "Config" / "DefaultEngine.ini").write_text(
        f"[/Script/EngineSettings.GameMapsSettings]\nGameDefaultMap={default_map}\n")
    return project, exe


def test_config_is_built_from_just_the_uproject(tmp_path):
    project, exe = fake_project(tmp_path)
    config = make_config(f'"{project}"', epic_folder=tmp_path / "Epic Games")  # quotes, like "Copy as path"
    assert config["unreal_exe"] == exe.as_posix()
    assert config["project"] == project.as_posix()
    assert config["map"] == "/Game/Maps/Benchmark"
    assert config["resolution"] == [1920, 1080] and config["frames"] == 1200


def test_typed_map_and_exe_override_the_detected_ones(tmp_path):
    project, exe = fake_project(tmp_path, version="5.4")
    config = make_config(str(project), unreal_exe=str(exe), map_name="/Game/Other", epic_folder=tmp_path / "nowhere")
    assert config["unreal_exe"] == exe.as_posix() and config["map"] == "/Game/Other"


def test_missing_unreal_version_gives_clear_error(tmp_path):
    project, _ = fake_project(tmp_path)
    with pytest.raises(FileNotFoundError, match="Unreal 5.5"):
        make_config(str(project), epic_folder=tmp_path / "nowhere")


def test_non_uproject_paths_are_refused(tmp_path):
    with pytest.raises(ValueError):
        make_config(str(tmp_path / "MyGame.txt"))
    with pytest.raises(FileNotFoundError):
        make_config(str(tmp_path / "Missing.uproject"))
