"""apply.py - writes approved settings into the Unreal project's config file, with a backup and undo.

Loop step: the very end. Only runs when the developer clicks "Apply to project".
Start reading at: apply_settings(), then undo_apply().

Unreal .ini files allow duplicate keys and lines starting with + or -, which Python's
configparser would mangle. So we edit line by line and leave every other line untouched.
"""
import shutil
from datetime import datetime
from pathlib import Path

SECTION = "[SystemSettings]"  # settings here load at startup and override the scalability presets


def engine_ini(config):
    """Path of the project's DefaultEngine.ini, next to the .uproject file."""
    return Path(config["project"]).parent / "Config" / "DefaultEngine.ini"


def apply_settings(ini_path, settings, allowlist):
    """Back up the ini, then write each setting into [SystemSettings]. Returns the backup's path.

    settings = {"r.MotionBlurQuality": 0, ...}. Every one is checked against the allowlist first.
    """
    for setting, value in settings.items():
        if setting not in allowlist or value not in allowlist[setting]["values"]:
            raise ValueError(f"{setting} = {value} is not an approved setting, so it was not applied.")
    if not settings:
        raise ValueError("There are no settings to apply.")

    ini_path = Path(ini_path)
    if not ini_path.exists():
        raise FileNotFoundError(f"Config file not found: {ini_path}")

    backup = _backup_path(ini_path)
    shutil.copy2(ini_path, backup)

    with open(ini_path, encoding="utf-8-sig", newline="") as f:
        text = f.read()
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()

    for setting, value in settings.items():
        lines = _set_line(lines, setting, value)

    with open(ini_path, "w", encoding="utf-8", newline="") as f:
        f.write(newline.join(lines) + newline)
    return backup


def undo_apply(ini_path):
    """Put the newest backup back in place (and remove it). Returns the backup that was restored."""
    ini_path = Path(ini_path)
    backups = sorted(ini_path.parent.glob(f"{ini_path.name}.frameoptimizer-*.bak"))
    if not backups:
        raise FileNotFoundError("No FrameOptimizer backup found, so there is nothing to undo.")
    newest = backups[-1]
    shutil.copy2(newest, ini_path)
    newest.unlink()
    return newest


# ---------------------------------------------------------------- Helpers

def _set_line(lines, setting, value):
    """Return lines with 'setting=value' inside [SystemSettings]: replaced if present, added if not."""
    new_line = f"{setting}={value}"

    start = next((i for i, line in enumerate(lines) if line.strip().lower() == SECTION.lower()), None)
    if start is None:  # no section yet: add it at the end of the file
        return lines + ([""] if lines and lines[-1].strip() else []) + [SECTION, new_line]

    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip().startswith("[")), len(lines))

    result = lines[:start + 1]
    replaced = False
    for line in lines[start + 1:end]:
        if _key(line) == setting.lower():
            if not replaced:  # replace the first one, drop any duplicates
                result.append(new_line)
                replaced = True
            continue
        result.append(line)
    if not replaced:
        # Add after the section's last non-blank line, so blank spacing before the next section stays.
        insert_at = len(result)
        while insert_at > start + 1 and not result[insert_at - 1].strip():
            insert_at -= 1
        result.insert(insert_at, new_line)
    return result + lines[end:]


def _key(line):
    """The setting name on an ini line, lowercase ('r.Foo=1' -> 'r.foo'). Comments give ''."""
    line = line.strip()
    if not line or line.startswith(";") or "=" not in line:
        return ""
    return line.split("=", 1)[0].strip().lower()


def _backup_path(ini_path):
    """DefaultEngine.ini.frameoptimizer-20261114_213045.bak (with _2, _3... if that name is taken)."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ini_path.with_name(f"{ini_path.name}.frameoptimizer-{stamp}.bak")
    number = 2
    while backup.exists():
        backup = ini_path.with_name(f"{ini_path.name}.frameoptimizer-{stamp}_{number}.bak")
        number += 1
    return backup
