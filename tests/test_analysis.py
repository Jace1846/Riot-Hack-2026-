import pytest

from controller.benchmark import PROJECT_ROOT
from controller.analysis import compare, parse_csv, percentile, spread

SAMPLE = PROJECT_ROOT / "tests" / "fixtures" / "sample_synthetic.csv"


@pytest.fixture
def summary():
    return parse_csv(SAMPLE)


def test_counts_only_data_rows(summary):
    # 10 frames; the repeated header and [metadata] rows are not counted.
    assert summary["frame_count"] == 10


def test_median_and_fps(summary):
    assert summary["median_frame_ms"] == pytest.approx(20.15)
    assert summary["fps_estimate"] == pytest.approx(1000 / 20.15)


def test_p95_catches_the_hitch(summary):
    assert summary["p95_frame_ms"] == pytest.approx(25.6)


def test_gpu_bound(summary):
    assert summary["median_gpu_ms"] == pytest.approx(19.85)
    assert summary["bottleneck"] == "GPU-bound"


def test_gpu_passes(summary):
    assert summary["gpu_passes_ms"]["ShadowDepths"] == pytest.approx(7.0)
    assert set(summary["gpu_passes_ms"]) == {"BasePass", "ShadowDepths", "Lumen", "PostProcessing"}


def test_metadata_kept_and_labeled_synthetic(summary):
    assert summary["metadata"]["platform"] == "Windows"
    assert "SYNTHETIC" in summary["metadata"]["source"]


def test_columns_found_by_name_not_position(tmp_path):
    # Same data, columns in a different order.
    f = tmp_path / "reordered_synthetic.csv"
    f.write_text("GPUTime,EVENTS,FrameTime\n9.0,,10.0\n9.0,,12.0\n9.0,,14.0\n")
    result = parse_csv(f)
    assert result["median_frame_ms"] == pytest.approx(12.0)


def test_cpu_bound_when_gpu_is_idle(tmp_path):
    f = tmp_path / "cpu_bound_synthetic.csv"
    f.write_text("FrameTime,GPUTime\n20.0,8.0\n20.0,8.0\n")
    assert parse_csv(f)["bottleneck"] == "CPU-bound"


def test_missing_frame_column_is_an_error(tmp_path):
    f = tmp_path / "broken_synthetic.csv"
    f.write_text("GPUTime\n9.0\n")
    with pytest.raises(ValueError):
        parse_csv(f)


def test_percentile_simple():
    assert percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 95) == 10
    assert percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 50) == 5


# ---------------------------------------------------------------------------
# compare (the verifier)
# ---------------------------------------------------------------------------

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
