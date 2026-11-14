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
main.py        Entry point: py main.py <command>
controller/    All the Python logic (see code map below)
experiments/   allowlist.json, baseline.json, one JSON per experiment
reports/       One folder per session: raw CSVs, results.json, report.md
tests/         pytest tests (one test file per controller file); fixtures/ = fake CSVs
unreal/        Unreal scene and setup notes
```

### Code map (in the order the loop runs)

| Step | File | What it does | Start reading at |
|---|---|---|---|
| front door | `main.py` → `controller/cli.py` | Reads the command you typed | `main()` |
| 1. Propose | `controller/agent.py` | AI suggests one experiment *(not written yet)* | |
| 2. Validate | `controller/experiments.py` | Rejects anything not on the allowlist | `validate_experiment()` |
| 3. Measure | `controller/runner.py` | Launches Unreal, collects the CSV *(dry-run tested; real run untested until desktop)* | `run_benchmark()` |
| 3. Measure | `controller/parser.py` | Turns a CSV into a summary (median ms, p95, FPS, GPU passes) | `parse_csv()` |
| 4. Verify | `controller/verifier.py` | Decides improved / worse / no clear change | `compare()` |
| 5. Report | `controller/report.py` | Writes results.json + report.md | `build_results()` |

Every controller file starts with the same header: what it does, its loop step, and which function to read first. Main functions are at the top; helpers are below a `Helpers` divider.

## Requirements

- Windows PC with Unreal Engine 5 (for benchmarks)
- Python 3.12
- An LLM API key (optional; manual mode works without one)

## Usage

_Coming soon._

## Honesty notes

- All reported numbers come from real profiler captures unless they're explicitly labeled **synthetic/test data**.
- Lower graphics settings can reduce visual quality. Any trade-offs are listed in each report.