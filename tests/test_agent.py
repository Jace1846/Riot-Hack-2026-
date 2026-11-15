"""Tests for controller/agent.py. No real API calls: a fake client stands in for Claude,
so these tests are free, need no API key, and give the same result every time."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from controller.agent import _safe_name, build_prompt, build_schema, propose_experiment
from controller.analysis import summarize_csv
from controller.benchmark import load_json

ROOT = Path(__file__).parent.parent
ALLOWLIST = load_json(ROOT / "experiments" / "allowlist.json")
BASELINE = load_json(ROOT / "experiments" / "baseline.json")
SUMMARY = summarize_csv(ROOT / "tests" / "fixtures" / "sample.csv")
TRIED = [load_json(ROOT / "tests" / "fixtures" / "experiment.json")]


class FakeClient:
    """Pretends to be anthropic.Anthropic(). Returns pre-written answers, one per call."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts = []  # what we "sent", so tests can inspect it
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.prompts.append(kwargs["messages"][0]["content"])
        text = json.dumps(self.answers.pop(0))
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])


GOOD = {"name": "AA Quality 3", "reason": "test", "settings": [{"setting": "r.PostProcessAAQuality", "value": 3}]}
BAD = {"name": "too_far", "reason": "test", "settings": [{"setting": "r.ScreenPercentage", "value": 10}]}


def test_prompt_contains_measurements_rules_and_history():
    prompt = build_prompt(SUMMARY, ALLOWLIST, BASELINE, TRIED)
    assert "Median frame time: 14.09 ms" in prompt
    assert "GPU/ShadowDepths: 3.31" in prompt
    assert "r.Shadow.MaxResolution: allowed values [2048, 1024, 512]" in prompt
    assert "shadow_02: r.Shadow.MaxResolution=1024" in prompt


def test_prompt_includes_the_bottleneck():
    prompt = build_prompt(SUMMARY, ALLOWLIST, BASELINE, TRIED)
    assert "CPU vs GPU bottleneck" in prompt
    assert "Verdict: GPU" in prompt


def test_prompt_works_without_bottleneck_data():
    no_threads = {key: value for key, value in SUMMARY.items() if key != "bottleneck"}
    assert "CPU vs GPU bottleneck" not in build_prompt(no_threads, ALLOWLIST, BASELINE, TRIED)


def test_developer_direction_reaches_the_prompt():
    client = FakeClient(GOOD)
    propose_experiment(SUMMARY, ALLOWLIST, BASELINE, TRIED, client=client, goal="Keep the shadows sharp.")
    assert "## Developer's direction\nKeep the shadows sharp." in client.prompts[0]


def test_no_direction_section_when_goal_is_empty():
    assert "Developer's direction" not in build_prompt(SUMMARY, ALLOWLIST, BASELINE, TRIED, goal="   ")


def test_schema_only_allows_approved_setting_names():
    schema = build_schema(ALLOWLIST)
    enum = schema["properties"]["settings"]["items"]["properties"]["setting"]["enum"]
    assert enum == list(ALLOWLIST)


def test_good_proposal_is_returned_as_experiment():
    client = FakeClient(GOOD)
    experiment = propose_experiment(SUMMARY, ALLOWLIST, BASELINE, TRIED, client=client)
    assert experiment == {"name": "aa_quality_3", "reason": "test", "settings": {"r.PostProcessAAQuality": 3}}
    assert len(client.prompts) == 1


def test_rejected_proposal_gets_one_retry_with_the_problems():
    client = FakeClient(BAD, GOOD)
    experiment = propose_experiment(SUMMARY, ALLOWLIST, BASELINE, TRIED, client=client)
    assert experiment["settings"] == {"r.PostProcessAAQuality": 3}
    assert "r.ScreenPercentage = 10 is not allowed" in client.prompts[1]


def test_rejected_twice_raises():
    with pytest.raises(ValueError):
        propose_experiment(SUMMARY, ALLOWLIST, BASELINE, TRIED, client=FakeClient(BAD, BAD))


def test_safe_name():
    assert _safe_name("Shadow Res 1024!") == "shadow_res_1024"
    assert _safe_name("../../etc") == "etc"
    assert _safe_name("!!!") == "experiment"
