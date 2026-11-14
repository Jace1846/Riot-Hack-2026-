import pytest

from controller.benchmark import (
    PROJECT_ROOT,
    load_allowlist,
    load_json,
    to_exec_cmds,
    validate_experiment,
)

EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


@pytest.fixture
def allowlist():
    return load_allowlist()


def make(changes, exp_id="test_exp"):
    return {"id": exp_id, "description": "test", "changes": changes}


def test_allowlist_has_seven_settings(allowlist):
    assert len(allowlist) == 7
    assert allowlist["r.ScreenPercentage"]["min"] == 50


def test_baseline_file_is_valid(allowlist):
    assert validate_experiment(load_json(EXPERIMENTS_DIR / "baseline.json"), allowlist) == []


def test_shadow_02_file_is_valid(allowlist):
    assert validate_experiment(load_json(EXPERIMENTS_DIR / "shadow_02.json"), allowlist) == []


def test_unknown_setting_rejected(allowlist):
    errors = validate_experiment(make({"r.SomethingElse": 1}), allowlist)
    assert any("not in the allowlist" in e for e in errors)


def test_value_out_of_range_rejected(allowlist):
    assert validate_experiment(make({"sg.ShadowQuality": 5}), allowlist)
    assert validate_experiment(make({"r.ScreenPercentage": 49}), allowlist)


def test_range_edges_allowed(allowlist):
    assert validate_experiment(make({"sg.ShadowQuality": 0}), allowlist) == []
    assert validate_experiment(make({"sg.ShadowQuality": 4}), allowlist) == []
    assert validate_experiment(make({"r.ScreenPercentage": 50}), allowlist) == []


@pytest.mark.parametrize("bad_value", ["2", 2.5, True, None])
def test_non_integer_values_rejected(allowlist, bad_value):
    assert validate_experiment(make({"sg.ShadowQuality": bad_value}), allowlist)


def test_command_injection_in_value_rejected(allowlist):
    errors = validate_experiment(make({"sg.ShadowQuality": "2,quit"}), allowlist)
    assert errors


@pytest.mark.parametrize("bad_id", ["", "../evil", "has space", "a" * 65, 7])
def test_bad_ids_rejected(allowlist, bad_id):
    assert validate_experiment(make({"sg.ShadowQuality": 2}, exp_id=bad_id), allowlist)


def test_empty_changes_rejected(allowlist):
    assert validate_experiment(make({}), allowlist)


def test_extra_top_level_key_rejected(allowlist):
    exp = make({"sg.ShadowQuality": 2})
    exp["command"] = "rm -rf"
    assert validate_experiment(exp, allowlist)


def test_non_object_rejected(allowlist):
    assert validate_experiment(["sg.ShadowQuality", 2], allowlist)


def test_to_exec_cmds_format(allowlist):
    exp = make({"sg.ShadowQuality": 2, "r.ScreenPercentage": 75})
    assert to_exec_cmds(exp, allowlist) == "sg.ShadowQuality 2,r.ScreenPercentage 75"


def test_to_exec_cmds_refuses_invalid(allowlist):
    with pytest.raises(ValueError):
        to_exec_cmds(make({"sg.ShadowQuality": 9}), allowlist)
