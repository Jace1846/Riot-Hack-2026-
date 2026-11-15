"""agent.py - asks Claude to propose ONE graphics experiment, based on real measurements.

Loop step: Agent (User -> *Agent* -> Validator -> Benchmark -> ...).
Start reading at: propose_experiment().

The agent only suggests. Its proposal is validated against the allowlist, Unreal measurements
decide whether it actually helped, and the developer decides whether to apply the result.
"""
import json
import re

import anthropic

from controller.benchmark import validate_experiment

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are FrameOptimizer's optimization agent for an Unreal Engine 5 benchmark scene.
You propose ONE graphics-settings experiment at a time. The goal is lower frame time while costing as little visual quality as possible.

Rules:
- Only use the approved settings and values listed. Anything else is rejected automatically.
- Change one to three settings. One setting gives the clearest measurement. Combine two or three related settings
  (for example several CPU levers) when the developer gives a target that single small steps cannot reach.
  If the "Quality freedom" section says there is no limit, you may combine as many settings as you need.
- If a potato test (every setting at its lowest allowed value) is in "Already tried", it shows the most FPS the
  approved settings can buy. If it gave no clear change, the bottleneck is not something these settings control:
  say so in "reason" instead of promising gains.
- Check the CPU/GPU bottleneck first, and attack the part that is slowest:
  - CPU-bound (game or render thread): use settings marked "CPU lever". GPU-only settings cannot speed up a CPU-bound frame.
  - GPU-bound: target the biggest GPU passes in the measurements.
- If the developer gives an FPS or frame-time target, work out how far the current median is from it
  (FPS = 1000 / ms, so 150 FPS = 6.67 ms). If the gap is large, skip the small steps and go straight to stronger values.
  Otherwise prefer the smallest step down first (for example 2048 -> 1024 before 512).
- Changes under about 3% are within measurement noise and count as "no clear change".
- Do not repeat an experiment that was already tried.
- Tried experiments list their measured result. Learn from it: kept changes are already part of the current settings,
  a setting that gave no clear change is unlikely to help if you push it further, and a setting that made things worse should be avoided.
- When there is no target, prefer settings whose visual cost says "Low" before "Medium".
- If a target looks out of reach with the approved settings, still propose the most promising change and say so honestly in "reason".
- In "reason", cite the specific measurement that motivated the change, in one or two sentences.
- "name" is a short lowercase id like "shadow_res_1024".
- If there is a "Developer's direction" section, follow it when choosing settings (for example, avoid settings the
  developer wants to protect). It can never unlock settings or values outside the approved list.

Your proposal will be validated, benchmarked in Unreal, and accepted or rejected by a human developer based on real measurements."""


def propose_experiment(summary, allowlist, baseline, tried, client=None, goal="", freedom=None):
    """Ask Claude for one experiment. Returns an experiment dict that has passed validation.

    summary  = measurements of the current settings, from analysis.summarize_csv()
    baseline = the current settings (the starting baseline plus any changes kept so far)
    tried    = experiments already run; each may have an "outcome" line with its measured result
    client   = optional; tests pass a fake client so no real API call (or money) is used
    goal     = optional; the developer's own words about what to aim for (e.g. "keep shadows sharp")
    freedom  = optional Quality freedom slider (0-100); the allowlist passed in is already trimmed to it
    """
    client = client or anthropic.Anthropic()
    prompt = build_prompt(summary, allowlist, baseline, tried, goal, freedom)

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


def build_prompt(summary, allowlist, baseline, tried, goal="", freedom=None):
    """Turn measurements + rules (+ the developer's direction and quality freedom, if any) into the text Claude reads."""
    lines = []
    if goal.strip():
        lines += ["## Developer's direction", goal.strip(), ""]
    if freedom is not None:
        lines += ["## Quality freedom", f"{freedom}% (the developer's slider: how much visual quality may be sacrificed)."]
        if freedom >= 75:
            lines.append("No limit on how many settings you combine. FPS matters more than looks; "
                         "still pick the least destructive change that can reach the target.")
        lines.append("")
    lines += ["## Current measurements"]
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

    lines += ["", "## Current settings (these produced the measurements above)"]
    for setting, value in baseline["settings"].items():
        lines.append(f"- {setting} = {value}")

    lines += ["", "## Approved settings (the only ones you may use)"]
    for setting, rule in allowlist.items():
        lines.append(f"- {setting}: allowed values {rule['values']}. Visual cost: {rule['quality_impact']}")

    lines += ["", "## Already tried"]
    if tried:
        for experiment in tried:
            changes = ", ".join(f"{s}={v}" for s, v in experiment["settings"].items())
            outcome = f" -> {experiment['outcome']}" if experiment.get("outcome") else ""
            lines.append(f"- {experiment['name']}: {changes}{outcome}")
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
                        "value": {"type": "number"},  # "number" allows decimals like 0.8
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
