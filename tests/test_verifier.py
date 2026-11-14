import pytest

from controller.verifier import compare, spread

BASELINE = [20.1, 20.3, 20.0]


def test_clear_improvement():
    result = compare(BASELINE, [17.9, 18.2, 18.0])
    assert result["verdict"] == "improved"
    assert result["improvement_ms"] == pytest.approx(2.1)
    assert result["noise_ms"] == pytest.approx(0.3)


def test_small_change_is_not_claimed_as_better():
    assert compare(BASELINE, [19.9, 20.2, 20.0])["verdict"] == "no clear change"


def test_clearly_worse():
    assert compare(BASELINE, [23.0, 23.2, 23.1])["verdict"] == "worse"


def test_noisy_runs_block_the_claim():
    # Candidate median is 2 ms faster, but its runs vary by 5 ms.
    assert compare(BASELINE, [15.0, 18.1, 20.0])["verdict"] == "no clear change"


def test_needs_three_runs_each():
    assert compare([20.1, 20.3], [17.9, 18.2, 18.0])["verdict"] == "not enough runs"
    assert compare(BASELINE, [17.9])["verdict"] == "not enough runs"


def test_improvement_percent():
    result = compare([20.0, 20.0, 20.0], [15.0, 15.0, 15.0])
    assert result["verdict"] == "improved"
    assert result["improvement_pct"] == pytest.approx(25.0)


def test_raw_runs_are_kept_as_evidence():
    result = compare(BASELINE, [17.9, 18.2, 18.0])
    assert result["baseline_runs_ms"] == BASELINE
    assert result["candidate_runs_ms"] == [17.9, 18.2, 18.0]


def test_spread():
    assert spread([20.1, 20.3, 20.0]) == pytest.approx(0.3)
