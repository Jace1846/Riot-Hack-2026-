# FrameForge

An AI-assisted frame-rate optimizer for Unreal Engine 5, built for **DevHacks 2026**, Riot Games Track 2: Agentic Development.

> **Status:** in progress (hackathon build, Nov 14–15, 2026)

## What it does

Tuning a game's settings for lower-end PCs usually means hours of manual profiling. FrameForge automates that loop:

1. **Benchmark:** runs a fixed Unreal scene and records frame times with Unreal's CSV profiler.
2. **Propose:** an AI agent reads the measurements and picks the next experiment from an approved list of rendering settings.
3. **Validate:** the controller rejects any setting or value that isn't on the allowlist.
4. **Measure:** the scene runs again with the candidate settings.
5. **Verify:** deterministic Python code, not the agent, compares median and p95 frame time against the baseline.
6. **Apply:** the best verified result becomes a reviewable config change, and the baseline is preserved.

**Core rule:** the agent suggests; measurements decide.

## Project layout

```
controller/    Python CLI: validator, runner, parser, verifier, agent
experiments/   Baseline and candidate configurations (JSON)
reports/       Benchmark results and raw profiler CSVs
tests/         pytest tests
unreal/        Unreal scene and setup notes
```

## Requirements

- Windows PC with Unreal Engine 5 (for benchmarks)
- Python 3.12
- An LLM API key (optional; manual mode works without one)

## Usage

_Coming soon._

## Honesty notes

- All reported numbers come from real profiler captures unless they're explicitly labeled **synthetic/test data**.
- Lower graphics settings can reduce visual quality. Any trade-offs are listed in each report.