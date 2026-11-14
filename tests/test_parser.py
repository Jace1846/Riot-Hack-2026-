import pytest

from controller.experiments import PROJECT_ROOT
from controller.parser import parse_csv, percentile

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
