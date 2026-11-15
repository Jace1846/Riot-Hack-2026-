# FrameOptimizer

An AI-assisted frame-rate optimizer for Unreal Engine 5, built for **DevHacks 2026**, Riot Games Track 2: Agentic Development.

> **Status:** hackathon build (Nov 14–15, 2026). Analysis, CPU/GPU bottleneck charts, the AI agent and reports are working and tested.
> The Unreal launch is built; the first full run against a real Unreal project is being tested on the benchmark PC.

## What it does

Tuning a game's settings for lower-end PCs usually means hours of manual profiling. FrameOptimizer automates that loop:

1. **Measure:** launches a fixed Unreal scene and records frame times with Unreal's CSV profiler, or reads a CSV capture you already have.
2. **Diagnose:** finds the bottleneck (game thread, render thread, or GPU) and which GPU passes cost the most.
3. **Propose:** an AI agent reads the measurements and picks one experiment from an approved list of rendering settings.
4. **Validate:** any setting or value that isn't on the allowlist is rejected before Unreal runs.
5. **Benchmark:** the scene runs again with the experiment's settings, under the same scene, camera and resolution.
6. **Verify:** plain Python code, not the AI, compares median and p95 frame time and writes a before/after report.
7. **Keep or discard, then repeat:** only a measured improvement is kept. The AI is told the result and proposes the next change on top.

At the end you get a summary: start vs best, every round, and the settings to apply. You decide whether to apply them.

**Core rule:** the AI suggests. Measurements decide. The developer approves.

Settings are passed to Unreal on the command line for each run only, so nothing in your Unreal project is changed.

## Setup

Requirements: Windows, Python 3.12+, Unreal Engine 5 (for benchmarks), and an Anthropic API key (only for the AI step).

```
git clone https://github.com/Jace1846/FrameForge--Riot-Hack-2026-.git FrameOptimizer
cd FrameOptimizer
py -m pip install -r requirements.txt
```

Then run `py main.py` and paste the path to your `.uproject` file into the **Unreal project** box.
FrameOptimizer finds Unreal (from the engine version in the `.uproject`) and the project's default map
by itself. Under **More options** you can pick a different map or point at `UnrealEditor.exe` manually.

It saves this to `config.local.json` (ignored by Git, so your paths stay on your machine). Every run uses
1920x1080 and records 600 frames, so measurements stay comparable.

## Usage

### The FrameOptimizer window (recommended)

```
py main.py
```

This opens FrameOptimizer in its own window. Then:

1. Paste your API key, pick the number of rounds, and click **Optimize**. Unreal opens and closes once per run.
2. Watch the progress lines, then read the result: start vs best, each round's verdict, and the settings to apply.
3. The charts below show the best run: frame-time stats, the CPU vs GPU bottleneck, and the cost of each GPU pass.

**Benchmark** (top right) only measures the baseline, and the **CSV** tab analyzes a capture you already have. Neither uses the AI.

Your API key is only kept in the page's memory and never written to disk.

### Command line

```
py main.py optimize [rounds]                             Run the full loop in Unreal (needs ANTHROPIC_API_KEY). Default 3 rounds
py main.py report <before.csv> <after.csv> <exp.json>    Write a report from two existing captures
```

Each optimize run saves to its own folder: `reports/run_<date>_<time>/summary.md`, plus one `report.md` per round.

### Tests

```
py -m pytest
```

The tests need neither Unreal nor an API key. The AI is replaced by a fake client.

## Project layout

```
main.py         Entry point: no arguments opens the window; otherwise runs a command
controller/     All the Python logic (see code map below)
ui/             server.py (local web server) + index.html (the FrameOptimizer window)
experiments/    allowlist.json (what may be changed) and baseline.json (starting settings)
reports/        One folder per optimize run: summary.md plus a report per round
tests/          pytest tests, one file per controller file; fixtures/ holds a hand-made test CSV
unreal/         Unreal scene and setup notes
```

### Code map (in the order the loop runs)

| Step | File | What it does | Start reading at |
|---|---|---|---|
| Front door | `main.py` | Opens the window or runs the command you typed | `main()` |
| Window | `ui/server.py` | Local server for the page; starts the loop and reports its progress | `Handler` |
| The loop | `controller/pipeline.py` | The one optimization loop, used by both the window and the command line | `optimize()` |
| Propose | `controller/agent.py` | Asks Claude for one experiment, retries once if it's rejected | `propose_experiment()` |
| Validate + benchmark | `controller/benchmark.py` | Checks the allowlist, launches Unreal, finds the new CSV | `validate_experiment()`, `run_benchmark()` |
| Analyze | `controller/analysis.py` | CSV → median/p95 frame time, GPU passes, CPU/GPU bottleneck; compares two runs | `summarize_csv()`, `compare()` |
| Report | `controller/report.py` | Writes each round's before/after report and the run summary | `build_report()`, `build_summary()` |

Every controller file starts with the same header: what it does, its loop step, and which function to read first.

## Honesty notes

- Every number FrameOptimizer shows comes from an Unreal CSV profiler capture that you run or supply. No measurements are invented.
- The test CSV in `tests/fixtures/` is hand-made test input. It is only used by the tests and is never shown as a result.
- The CPU/GPU bottleneck is an estimate from Unreal's measured thread times; very close calls are labeled "mixed".
- Each setting is measured with one Unreal run, so changes under 3% are treated as noise, not improvements.
- Lower graphics settings can reduce visual quality. Each report lists the visual trade-off of every changed setting.
