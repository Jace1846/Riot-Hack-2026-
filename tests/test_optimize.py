"""Tests for controller.pipeline.optimize(). SYNTHETIC: a fake Unreal (made-up frame times) and a fake AI,
so these only check the loop's logic - keep what improves, discard the rest. Not real measurements."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from controller.analysis import summarize_csv
from controller.pipeline import optimize

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
