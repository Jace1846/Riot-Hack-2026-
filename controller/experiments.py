"""Load experiments and check them against the allowlist.

Guardrail: nothing reaches Unreal unless validate_experiment() returns [].
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ALLOWLIST = PROJECT_ROOT / "experiments" / "allowlist.json"

# The id becomes part of a folder name, so keep it to safe characters.
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
ALLOWED_KEYS = {"id", "description", "changes"}


def load_json(path):
    """Read a JSON file and return its contents."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_allowlist(path=DEFAULT_ALLOWLIST):
    """Return {setting_name: {"min": int, "max": int, ...}}."""
    return load_json(path)


def validate_experiment(experiment, allowlist):
    """Return a list of problems. An empty list means the experiment is allowed."""
    if not isinstance(experiment, dict):
        return ["experiment must be a JSON object"]

    errors = []

    extra = set(experiment) - ALLOWED_KEYS
    if extra:
        errors.append(f"unknown top-level keys: {sorted(extra)}")

    exp_id = experiment.get("id")
    if not isinstance(exp_id, str) or not ID_PATTERN.match(exp_id):
        errors.append("id must be 1-64 characters: letters, numbers, _ or -")

    if "description" in experiment and not isinstance(experiment["description"], str):
        errors.append("description must be a string")

    changes = experiment.get("changes")
    if not isinstance(changes, dict) or not changes:
        errors.append("changes must be a non-empty object")
        return errors

    for setting, value in changes.items():
        rule = allowlist.get(setting)
        if rule is None:
            errors.append(f"{setting}: not in the allowlist")
            continue
        # bool is a subclass of int in Python, so reject it explicitly.
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{setting}: value must be a whole number, got {value!r}")
            continue
        if not rule["min"] <= value <= rule["max"]:
            errors.append(f"{setting}: {value} is outside {rule['min']}-{rule['max']}")

    return errors


def to_exec_cmds(experiment, allowlist):
    """Build the -ExecCmds string, e.g. "sg.ShadowQuality 2,r.ScreenPercentage 75".

    Validates first and raises ValueError if the experiment is not allowed.
    """
    errors = validate_experiment(experiment, allowlist)
    if errors:
        raise ValueError("experiment not allowed: " + "; ".join(errors))
    return ",".join(f"{name} {value}" for name, value in experiment["changes"].items())
