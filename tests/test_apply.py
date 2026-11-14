"""Tests for controller/apply.py. Each test uses a throwaway ini in pytest's temp folder,
never a real Unreal project."""
import pytest

from controller.apply import apply_settings, undo_apply

ALLOWLIST = {
    "r.MotionBlurQuality": {"values": [4, 2, 0], "quality_impact": "low"},
    "r.ViewDistanceScale": {"values": [1.0, 0.8, 0.6], "quality_impact": "low"},
}

ORIGINAL = (
    "[/Script/Engine.RendererSettings]\n"
    "+Foo=1\n"
    "+Foo=2\n"
    "\n"
    "[SystemSettings]\n"
    "; my comment\n"
    "r.MotionBlurQuality=4\n"
    "\n"
    "[/Script/Other]\n"
    "Bar=3\n"
)


@pytest.fixture
def ini(tmp_path):
    path = tmp_path / "DefaultEngine.ini"
    path.write_text(ORIGINAL)
    return path


def test_replaces_existing_and_adds_new_settings(ini):
    apply_settings(ini, {"r.MotionBlurQuality": 0, "r.ViewDistanceScale": 0.8}, ALLOWLIST)
    text = ini.read_text()
    assert "r.MotionBlurQuality=0" in text
    assert "r.MotionBlurQuality=4" not in text
    assert text.count("r.MotionBlurQuality") == 1
    # New setting lands inside [SystemSettings], before the next section.
    assert text.index("r.ViewDistanceScale=0.8") < text.index("[/Script/Other]")


def test_leaves_other_lines_untouched(ini):
    apply_settings(ini, {"r.MotionBlurQuality": 0}, ALLOWLIST)
    text = ini.read_text()
    for line in ["+Foo=1", "+Foo=2", "; my comment", "Bar=3", "[/Script/Other]"]:
        assert line in text


def test_adds_section_when_missing(tmp_path):
    path = tmp_path / "DefaultEngine.ini"
    path.write_text("[/Script/Other]\nBar=3\n")
    apply_settings(path, {"r.MotionBlurQuality": 2}, ALLOWLIST)
    assert path.read_text().endswith("[SystemSettings]\nr.MotionBlurQuality=2\n")


def test_backup_and_undo_restore_the_original(ini):
    backup = apply_settings(ini, {"r.MotionBlurQuality": 0}, ALLOWLIST)
    assert backup.read_text() == ORIGINAL
    undo_apply(ini)
    assert ini.read_text() == ORIGINAL
    assert not backup.exists()


def test_rejects_unapproved_values_without_touching_the_file(ini):
    with pytest.raises(ValueError):
        apply_settings(ini, {"r.MotionBlurQuality": 99}, ALLOWLIST)
    assert ini.read_text() == ORIGINAL
    assert not list(ini.parent.glob("*.bak"))


def test_undo_without_backup_raises(ini):
    with pytest.raises(FileNotFoundError):
        undo_apply(ini)
