"""agent.py - asks Claude to propose ONE graphics experiment, based on real measurements.

Loop step: Agent (User -> *Agent* -> Validator -> Benchmark -> ...).
Start reading at: propose_experiment().

The agent only suggests. Its proposal is validated against the allowlist, then a human
reviews the JSON file, and Unreal measurements decide whether it actually helped.
"""
import json
import re

import anthropic

from controller.benchmark import validate_experiment

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are FrameForge's optimization agent for an Unreal Engine 5 benchmark scene.
You propose ONE graphics-settings experiment at a time. The goal is lower frame time while costing as little visual quality as possible.

Rules:
- Only use the approved settings and values listed. Anything else is rejected automatically.
- Change one setting (two at most), so the measurement clearly shows what caused any difference.
- Check the CPU/GPU bottleneck first. The approved settings mainly reduce GPU work, so they help most when the scene is GPU-bound.
  If it is CPU-bound (game or render thread), still propose the most promising setting, but say in "reason" that the gain will likely be small.
- Target the biggest GPU costs in the measurements first.
- Do not repeat an experiment that was already tried.
- Prefer the smallest step down first (for example 2048 -> 1024 before 512).
- In "reason", cite the specific measurement that motivated the change, in one or two sentences.
- "name" is a short lowercase id like "shadow_res_1024".

Your proposal will be validated, benchmarked in Unreal, and accepted or rejected by a human developer based on real measurements."""


def propose_experiment(summary, allowlist, baseline, tried, client=None):
    """Ask Claude for one experiment. Returns an experiment dict that has passed validation.

    summary  = baseline summary from analysis.summarize_csv()
    tried    = list of experiment dicts already run (so the AI doesn't repeat them)
    client   = optional; tests pass a fake client so no real API call (or money) is used
    """
    client = client or anthropic.Anthropic()
    prompt = build_prompt(summary, allowlist, baseline, tried)

    experiment = _ask_claude(client, prompt, allowlist)
    problems = validate_experiment(experiment, allowlist)

    if problems:
        # One retry: show the AI exactly what was wrong.
        retry_prompt = (
            prompt
            + "\n\n## Your previous proposal was rejected\n"
            + json.dumps(experiment)
            + "\nProblems:\n- " + "\n- ".join(problems)
            + "\nPropose a corrected experiment."
        )
        experiment = _ask_claude(client, retry_prompt, allowlist)
        problems = validate_experiment(experiment, allowlist)
        if problems:
            raise ValueError("Agent proposal rejected twice: " + " ".join(problems))

    return experiment


def build_prompt(summary, allowlist, baseline, tried):
    """Turn measurements + rules into the text Claude reads."""
    lines = ["## Baseline measurements"]
    lines += [
        f"Median frame time: {summary['median_ms']} ms ({summary['median_fps']} FPS)",
        f"p95 frame time: {summary['p95_ms']} ms, worst frame: {summary['max_ms']} ms",
        "GPU passes (median ms), biggest first:",
    ]
    for name, ms in sorted(summary["gpu_passes"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"- {name}: {ms}")

    bottleneck = summary.get("bottleneck")
    if bottleneck:
        lines += [
            "",
            "## CPU vs GPU bottleneck (estimated from Unreal's thread times)",
            f"Verdict: {bottleneck['label']} ({bottleneck['share_of_frame_pct']}% of the median frame)",
            "Median ms per part: " + ", ".join(f"{part} {ms}" for part, ms in bottleneck["median_ms"].items()),
            "Slowest part, % of frames: "
            + ", ".join(f"{part} {pct}%" for part, pct in bottleneck["frames_limited_pct"].items()),
        ]

    lines += ["", "## Current baseline settings"]
    for setting, value in baseline["settings"].items():
        lines.append(f"- {setting} = {value}")

    lines += ["", "## Approved settings (the only ones you may use)"]
    for setting, rule in allowlist.items():
        lines.append(f"- {setting}: allowed values {rule['values']}. Visual cost: {rule['quality_impact']}")

    lines += ["", "## Already tried"]
    if tried:
        for experiment in tried:
            changes = ", ".join(f"{s}={v}" for s, v in experiment["settings"].items())
            lines.append(f"- {experiment['name']}: {changes}")
    else:
        lines.append("Nothing yet.")

    return "\n".join(lines)


def build_schema(allowlist):
    """JSON schema Claude's answer must follow. Setting names are limited to the allowlist."""
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "reason": {"type": "string"},
            "settings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "setting": {"type": "string", "enum": list(allowlist)},
                        "value": {"type": "integer"},
                    },
                    "required": ["setting", "value"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["name", "reason", "settings"],
        "additionalProperties": False,
    }


# ---------------------------------------------------------------- Helpers

def _ask_claude(client, prompt, allowlist):
    """One API call. Returns {"name", "reason", "settings": {setting: value}}."""
    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            output_config={
                "effort": "medium",
                "format": {"type": "json_schema", "schema": build_schema(allowlist)},
            },
            # Safety net: if the model declines, the API retries on a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except TypeError as error:
        # The SDK raises TypeError when it finds no API key at all.
        raise RuntimeError("No Anthropic API key found. Set the ANTHROPIC_API_KEY environment variable.") from error
    except anthropic.APIError as error:
        raise RuntimeError(f"AI request failed: {error}") from error

    if response.stop_reason == "refusal":
        raise RuntimeError("The AI declined to make a proposal.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("The AI's answer was cut off before it finished.")

    text = next(block.text for block in response.content if block.type == "text")
    data = json.loads(text)
    return {
        "name": _safe_name(data["name"]),
        "reason": data["reason"],
        "settings": {item["setting"]: item["value"] for item in data["settings"]},
    }


def _safe_name(name):
    """Make the AI's name safe to use as a file/folder name: 'Shadow Res 1024!' -> 'shadow_res_1024'."""
    return re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_") or "experiment"
