# FrameForge

An AI-assisted frame-rate optimizer for Unreal Engine 5, built for **DevHacks 2026**, Riot Games Track 2: Agentic Development.

> **Status:** hackathon build (Nov 14–15, 2026). Analysis, CPU/GPU bottleneck charts, the AI agent and reports are working and tested.
> The Unreal launch is built; the first full run against a real Unreal project is being tested on the benchmark PC.

## What it does

Tuning a game's settings for lower-end PCs usually means hours of manual profiling. FrameForge automates that loop:

1. **Measure:** launches a fixed Unreal scene and records frame times with Unreal's CSV profiler, or reads a CSV capture you already have.
2. **Diagnose:** finds the bottleneck (game thread, render thread, or GPU) and which GPU passes cost the most.
3. **Propose:** an AI agent reads the measurements and picks one experiment from an approved list of rendering settings.
4. **Validate:** any setting or value that isn't on the allowlist is rejected before Unreal runs.
5. **Benchmark:** the scene runs again with the experiment's settings, under the same scene, camera and resolution.
6. **Verify:** plain Python code, not the AI, compares median and p95 frame time and writes a before/after report.

**Core rule:** the AI suggests. Measurements decide. The developer approves.

Settings are passed to Unreal on the command line for each run only, so nothing in your Unreal project is changed.

## Setup

Requirements: Windows, Python 3.12+, Unreal Engine 5 (for benchmarks), and an Anthropic API key (only for the AI step).

```
git clone https://github.com/Jace1846/FrameForge--Riot-Hack-2026-.git FrameForge
cd FrameForge
py -m pip install -r requirements.txt
copy config.example.json config.local.json
```

Then edit `config.local.json` with the paths on your PC (use forward slashes):

| Field | Meaning |
|---|---|
| `unreal_exe` | Path to `UnrealEditor.exe` |
| `project` | Path to your `.uproject` file |
| `map` | The benchmark map, e.g. `/Game/Maps/Benchmark` |
| `resolution` | `[width, height]`, kept the same for every run |
| `frames` | How many frames to record per run |
| `timeout_seconds` | Unreal is closed after this long if it hasn't quit by itself |

`config.local.json` is ignored by Git, so your paths stay on your machine.

## Usage

### The FrameForge window (recommended)

```
py main.py
```

This opens FrameForge in its own window. Then:

1. **Measure:** choose **Unreal** (click *Benchmark in Unreal*) or **CSV file** (paste the path to a capture).
2. Read the results: frame-time stats, the CPU vs GPU bottleneck verdict, a frame-time chart, and the cost of each GPU pass.
3. **Ask the agent:** paste your API key and click *Propose experiment*. The proposal is validated and saved to `experiments/`.

Your API key is only kept in the page's memory and never written to disk.

### Command line

```
py main.py propose <baseline.csv>                        AI proposes one experiment (needs ANTHROPIC_API_KEY)
py main.py run <experiment.json>                         Benchmark baseline + experiment in Unreal, write a report
py main.py report <before.csv> <after.csv> <exp.json>    Write a report from two existing captures
```

Reports are saved to `reports/<experiment name>/report.md`.

### Tests

```
py -m pytest
```

The tests need neither Unreal nor an API key. The AI is replaced by a fake client.

## Project layout

```
main.py         Entry point: no arguments opens the window; otherwise runs a command
controller/     All the Python logic (see code map below)
ui/             server.py (local web server) + index.html (the FrameForge window)
experiments/    allowlist.json, baseline.json, one JSON per experiment
reports/        One folder per experiment with its report.md
tests/          pytest tests, one file per controller file; fixtures/ holds a hand-made test CSV
unreal/         Unreal scene and setup notes
```

### Code map (in the order the loop runs)

| Step | File | What it does | Start reading at |
|---|---|---|---|
| Front door | `main.py` | Opens the window or runs the command you typed | `main()` |
| Window | `ui/server.py` | Local server for the page; launches benchmarks on request | `Handler` |
| Propose | `controller/agent.py` | Asks Claude for one experiment, retries once if it's rejected | `propose_experiment()` |
| Validate + benchmark | `controller/benchmark.py` | Checks the allowlist, launches Unreal, finds the new CSV | `validate_experiment()`, `run_benchmark()` |
| Analyze | `controller/analysis.py` | CSV → median/p95 frame time, GPU passes, CPU/GPU bottleneck; compares two runs | `summarize_csv()`, `compare()` |
| Report | `controller/report.py` | Writes the before/after Markdown report | `build_report()` |

Every controller file starts with the same header: what it does, its loop step, and which function to read first.

## Honesty notes

- Every number FrameForge shows comes from an Unreal CSV profiler capture that you run or supply. No measurements are invented.
- The test CSV in `tests/fixtures/` is hand-made test input. It is only used by the tests and is never shown as a result.
- The CPU/GPU bottleneck is an estimate from Unreal's measured thread times; very close calls are labeled "mixed".
- Lower graphics settings can reduce visual quality. Each report lists the visual trade-off of every changed setting.
