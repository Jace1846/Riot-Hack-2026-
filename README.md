# FrameOptimizer

An AI-assisted frame-rate optimizer for Unreal Engine 5, built for **DevHacks 2026**, Riot Games Track 2: Agentic Development.

> **Status:** final hackathon build (Nov 15, 2026). The full loop has run end to end against a real Unreal project:
> measure, AI proposes, Unreal tests, keep what helps, report, and apply with undo. All 67 tests pass.

**Core rule:** the AI suggests. Measurements decide. The developer approves.
[![Watch the video](https://youtube.com)][(https://www.youtube.com/watch?v=97deAAmdtPg)]


## What it does

Tuning a game's graphics settings for weaker PCs usually means hours of manual profiling. FrameOptimizer automates that loop:

1. **Measure:** launches your Unreal scene and records frame times with Unreal's CSV profiler.
2. **Find the ceiling:** a *potato test* runs every setting at its lowest allowed value once. This shows the most FPS that settings alone can buy. It is never kept.
3. **Diagnose:** finds the bottleneck (game thread, render thread, or GPU) and the most expensive GPU passes.
4. **Propose:** an AI agent (Claude) reads the measurements and your direction, then picks 1–3 approved settings to change.
5. **Validate:** any setting or value that isn't on the allowlist is rejected before Unreal runs.
6. **Benchmark:** Unreal runs the same scene again with the change, at the same resolution and test length.
7. **Verify:** plain Python, not the AI, compares median and p95 frame time. Only a measured improvement is kept.
8. **Repeat:** the AI is told every result and proposes the next change on top of what was kept.
9. **Approve:** you review the summary and the visual trade-offs, then click **Apply to project** (with backup and **Undo**).

## Example result (real Unreal run)

This is one real 10-test run from Nov 15, 2026 on our benchmark desktop (Ryzen 5 7600, RX 7600 XT, 1920x1080).
Direction given to the AI: *aim for 150 FPS, keep the colorful look, shadows don't matter.* Quality freedom: 100%.

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time | 10.38 ms | 5.33 ms | -48.7% |
| p95 frame time | 12.27 ms | 6.89 ms | -43.8% |
| Median FPS | 96.4 | 187.7 | +94.7% |

- The potato test set the ceiling at **199.9 FPS**. The AI reached 187.7 FPS without keeping every setting at its lowest.
- Of 9 AI rounds: 5 were kept, 2 gave no clear change, and 2 made it worse (both discarded).
- The biggest single gain was turning off Lumen global illumination (143.1 → 187.7 FPS). That has a **severe** visual cost, which the report flags.
- This was an aggressive result, because the direction said shadows didn't matter. With a lower Quality freedom setting the AI stays closer to the original look.

Run reports aren't committed to Git (`reports/run_*` is ignored). These numbers come from that run's `summary.md`.

## Scope

**Built and working**

- Real measurements from Unreal's CSV profiler: frame time, game/render/GPU thread time, and per-pass GPU cost.
- 27 approved rendering settings in `experiments/allowlist.json`, each with allowed values and a visual-quality note. Settings that help a CPU-bound scene are marked "CPU lever".
- An allowlist validator that blocks anything not approved, even if the AI asks for it.
- A multi-round AI loop (1–10 rounds) that keeps only measured improvements.
- Controls for the developer: a written direction (for example "hit 150 FPS"), a Quality freedom slider, test length, and number of rounds.
- A potato ceiling test, so you can see when settings can't fix the bottleneck.
- A Markdown report for every test plus a run summary, including the visual trade-off of every changed setting.
- **Apply to project** writes the kept settings into `Config/DefaultEngine.ini` after making a backup. **Undo** restores the backup.
- A local window (Python standard-library server + one HTML page) and a command line.

**Out of scope (on purpose)**

- Changing shaders, assets, meshes, or Blueprints. Only engine console settings are changed.
- Automatic visual-quality scoring (screenshots or image comparison). The developer judges visuals, using the trade-off notes in each report.
- Databases, cloud services, Docker, multiple AI agents, or remote benchmark machines.
- Per-platform or packaged-build tuning. Tests run the project in `-game` mode from the Unreal editor install.

**Known limits**

- Each test is one Unreal run, so changes under 3% are treated as noise, not improvements.
- Unreal is found automatically only in the default Epic launcher folder. Otherwise, paste the path to `UnrealEditor.exe` under **More options**.
- The command-line `optimize` has no Quality freedom limit and no potato test. Those are only available in the window.
- Applied settings go in `[SystemSettings]`, which overrides Unreal's scalability presets for everyone using that project.

## Setup

Requirements: Windows, Python 3.12+, Unreal Engine 5, and an Anthropic API key (only for the AI step).

```
git clone https://github.com/Jace1846/FrameForge--Riot-Hack-2026-.git FrameOptimizer
cd FrameOptimizer
py -m pip install -r requirements.txt
py main.py
```

Paste the path to your `.uproject` file into the **Unreal project** box. FrameOptimizer finds the matching Unreal version
and the project's default map by itself. It saves this to `config.local.json`, which Git ignores, so your paths stay on your machine.

## Usage

### The FrameOptimizer window (recommended)

Run `py main.py`. In the **Optimize** panel:

| Control | What it does | Default |
|---|---|---|
| Anthropic API key | Used for this run only. It stays in the page's memory and is never saved to disk. | — |
| Direction for the AI | Optional goal in your own words, e.g. *"Keep shadows and fog, aim for 60 FPS"*. | blank |
| Quality freedom | How far down each setting may go. 0% keeps only top quality, 100% allows every approved value. Above 0%, the potato test runs first. | 50% |
| Test length | Frames recorded per Unreal run (600–3600). The first 60 frames are skipped as warm-up. | 1200 |
| AI rounds | How many experiments to try. Each one is a separate Unreal run. | 3 |

Click **▶ Optimize**. Unreal opens and closes once per test, so leave its window alone. When the run finishes, you'll see:

- **Result:** start vs best FPS, median and p95 frame time, and the list of settings to apply.
- **Tests:** one card per test with its verdict (kept, no clear gain, worse, or ceiling test), its FPS, and the AI's reason.
- **Measurements:** charts for the best run showing frame time, the CPU vs GPU bottleneck, and the cost of each GPU pass.

**Benchmark** (top right) measures only the starting settings, and the **CSV** tab analyzes a capture you already have. Neither one uses the AI.

### Command line

```
py main.py optimize [rounds]                             Run the full loop in Unreal (needs ANTHROPIC_API_KEY). Default 3 rounds
py main.py report <before.csv> <after.csv> <exp.json>    Write a report from two existing captures (no Unreal or AI)
```

Each optimize run writes `reports/run_<date>_<time>/summary.md` plus one `report.md` per test.
Starting a new run deletes older `run_*` folders, so only the newest run is kept.

### Tests

```
py -m pytest
```

The tests don't need Unreal or an API key. A fake client replaces the AI, and a fake benchmark replaces Unreal.

## Project layout

```
main.py         Entry point: no arguments opens the window; otherwise runs a command
controller/     All the Python logic (see the code map below)
ui/             server.py (local web server) + index.html (the FrameOptimizer window)
experiments/    allowlist.json (what may be changed) and baseline.json (starting settings, all at top quality)
reports/        The newest optimize run: summary.md plus a report per test (not committed)
tests/          pytest tests, one file per controller file; fixtures/ holds a hand-made test CSV
```

### Code map (in the order the loop runs)

| Step | File | What it does | Start reading at |
|---|---|---|---|
| Front door | `main.py` | Opens the window or runs the command you typed | `main()` |
| Window | `ui/server.py` | Local server for the page; starts the loop and reports its progress | `Handler` |
| The loop | `controller/pipeline.py` | The single optimization loop, used by both the window and the command line. Also handles Quality freedom and the potato test. | `optimize()` |
| Propose | `controller/agent.py` | Asks Claude for one experiment; retries once if it's rejected | `propose_experiment()` |
| Validate + benchmark | `controller/benchmark.py` | Checks the allowlist, launches Unreal, finds the new CSV | `validate_experiment()`, `run_benchmark()` |
| Analyze | `controller/analysis.py` | CSV → median/p95 frame time, GPU passes, CPU/GPU bottleneck; compares two runs | `summarize_csv()`, `compare()` |
| Report | `controller/report.py` | Writes each test's before/after report and the run summary | `build_report()`, `build_summary()` |
| Apply | `controller/apply.py` | Writes approved settings into `DefaultEngine.ini` with a backup, and undoes it | `apply_settings()`, `undo_apply()` |

Every controller file starts with the same header: what it does, its loop step, and which function to read first.

## Changes in the final build

- **Quality freedom slider:** limits how far down each setting the AI may go. The validator enforces the trimmed list, so it's a real limit, not just a hint.
- **Potato test:** a ceiling test before the AI starts. If even that doesn't help, the AI says the bottleneck isn't something settings can fix.
- **Test length slider:** 600–3600 frames per run, for steadier numbers on noisy scenes.
- **FPS targets:** the AI converts a target like "150 FPS" into a frame-time gap and takes bigger steps when the gap is large.
- **CPU levers:** the allowlist grew from 21 to 27 settings, adding view distance, foliage, LOD, and shadow-distance settings that help CPU-bound scenes. The AI picks CPU or GPU settings based on the measured bottleneck.
- **Up to 3 settings per round** (more at 75%+ Quality freedom), so large targets can be reached in fewer rounds.
- **Apply to project / Undo:** writes kept settings to the project's config file, with a backup.
- **Reports:** the summary now shows FPS before → after for each test. Only the newest run is kept on disk, and run reports are no longer committed.
- **Window:** new Tests cards (tap one to see its settings and the AI's reason), FPS before → after on every test, and a larger default window.

## Honesty notes

- Every number FrameOptimizer shows comes from an Unreal CSV profiler capture that you run or supply. No measurements are invented.
- The test CSV in `tests/fixtures/` is hand-made test input. It is only used by the tests and is never shown as a result.
- The CPU/GPU bottleneck is an estimate from Unreal's measured thread times. Very close calls are labeled "mixed".
- Each setting is measured with one Unreal run, so changes under 3% count as noise. A change is kept only if the median improves by at least 3% and p95 doesn't get worse by 3% or more.
- Lower graphics settings reduce visual quality. Every report lists the visual trade-off of each changed setting, and nothing touches your project until you click **Apply to project**.
