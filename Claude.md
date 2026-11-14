CLAUDE.md: FrameForge
What this is

FrameForge is an AI-assisted frame-rate optimizer for Unreal Engine 5, built for DevHacks 2026 (Ohio State), Riot Games Track 2: Agentic Development.

Deadline: Sunday Nov 15, 2026, 11:00 AM Eastern. No extensions. Submission = Devpost + 3-minute video + public GitHub repo. Plan to freeze features around 8 AM Sunday.

Loop: run a fixed Unreal benchmark → AI agent proposes ONE experiment from an allowlist → Python validates it → Unreal runs it → deterministic Python verifies the measured result → best verified result becomes a reviewable config change (git branch in the Unreal project), with the baseline preserved.

Core rule: the agent suggests; measurements decide. Never trust the agent to report its own success.

What Riot's judges want (from the kickoff deck)
Demo format: agent → code change → verified result.
Show feedback guiding the agent (it reads measured results and picks the next experiment).
Evidence: compare against a simpler workflow (exhaustive sweep of the same allowlist and/or Unreal's built-in Low/Med/High/Epic presets). Report runs and time needed to hit a target.
"Verify the result yourself. Don't trust the agent saying it's done."
The team must be able to explain its architecture and trade-offs.
About the developer (Jason)
Beginner in Python, new to Unreal, not comfortable with C++. Solo.
Uses VS Code's Source Control UI for Git, not the terminal. Windows.
Explanations: short, scannable bullets and tables, no long paragraphs. Explain any Unreal concept the first time it comes up.
Prefer small, working, tested steps over big rewrites. Tell him exactly which file to edit and what command to run to check it.
Hardware
Framework 13 laptop (Ryzen 7040, 16 GB): coding, no Unreal benchmarking.
Windows desktop (Ryzen 5 7600, RX 7600 XT 16 GB, 32 GB RAM): Unreal benchmarks, available later Saturday.
Code moves between them through GitHub (Sync in VS Code). No remote execution setup.
Hard rules (guardrails)
Allowlist only. Never run a setting that hasn't passed validate_experiment(). The LLM never writes shell commands, console commands, or edits arbitrary files.
No fabricated measurements. Any fake data must be labeled synthetic in its file name AND contents. Real captures are labeled actual.
Preserve the baseline and raw CSVs. Never overwrite. Each run gets a unique output folder under reports/.
Only claim "better" when the evidence supports it: improvement must exceed run-to-run noise (≥3 runs per config, compare medians, report spread).
Don't claim visual equivalence unless it was checked (screenshot pair / image similarity).
Manual mode must always work without an API key (AI step is optional; mock mode for tests).
Python 3.12 + standard library first. Allowed extras: pytest, an LLM SDK, Pillow/numpy only if needed for screenshot comparison. Ask before adding anything else.
Never commit secrets. API key comes from an environment variable; real paths live in config.local.json (gitignored). config.example.json is the committed template.
Current state
Done and tested (46 pytest tests passing):
main.py → argparse CLI (only validate command wired up so far)
controller/benchmark.py → load_allowlist, load_json, validate_experiment (returns list of errors; empty = allowed), to_exec_cmds, run_benchmark (dry_run prints the Unreal command), collect_csv
controller/analysis.py → parse_csv (Unreal CSV → summary), compare (baseline vs candidate verdict)
controller/report.py → new_run_dir, build_results, write_report (results.json + report.md)
experiments/allowlist.json → 7 settings: sg.ShadowQuality, sg.ViewDistanceQuality, sg.PostProcessQuality, sg.GlobalIlluminationQuality, sg.ReflectionQuality, sg.EffectsQuality (0–4), r.ScreenPercentage (50–100)
experiments/baseline.json (all sg = 3, 100%), experiments/shadow_02.json
Experiment format: {"id": "shadow_02", "description": "...", "changes": {"sg.ShadowQuality": 2}}
Empty placeholders: agent.py, requirements.txt, unreal/README.md.
Branches: main (always works, what judges see), dev (work here, merge at checkpoints).
Project layout
main.py                 entry point + CLI: py main.py <command>
controller/             benchmark (validate + run Unreal), analysis (parse CSV + verify), report, agent
experiments/            allowlist.json, baseline.json, one JSON per experiment
tests/                  pytest; fixtures/ holds synthetic CSVs
reports/                run outputs: raw CSVs, results.json, report.md/html
unreal/                 Unreal project + setup notes (created on desktop)

Run: py main.py <command> · Test: py -m pytest

Next steps, in order
DONE: tests/fixtures/sample_synthetic.csv in Unreal CSV profiler format (labeled synthetic) → controller/analysis.py (parse_csv) → tests/test_analysis.py.
Output per capture: median frame time (ms), p95 frame time (ms), FPS estimate (1000 / median), median GPU time, frame count, bottleneck guess (GPU-bound if GPUTime ≈ FrameTime).
Look up columns by header name, never by position. Expect 100+ columns.
Stop reading data at a row starting with [ or a repeated header row (Unreal appends metadata like [platform],Windows,[config],Development,...). Keep that metadata in the result.
Skip blank/non-numeric cells.
DONE: controller/analysis.py compare(): baseline vs candidate across repeated runs; "improved" only if median improvement > run-to-run spread. Deterministic, fully tested.
DONE: controller/report.py: write results.json (stable schema, the source for any UI later) + report.md (report.html if time).
DONE: controller/benchmark.py run_benchmark(dry_run=True) prints the exact Unreal command; config.example.json for paths. TODO: wire benchmark/compare commands into main.py.
Laptop: controller/agent.py with a mock mode. Input: compact baseline summary incl. per-pass GPU/... timings + allowlist. Output JSON: setting, value, hypothesis, reason. Validate before use. Max 3 experiments. Its hypothesis should cite the measured GPU breakdown (e.g. shadows = 35% of GPU time → try shadows).
Desktop: build the Unreal scene, capture the first REAL CSV, fix column names in analysis.py against it.
Desktop: real runs → agent loop → write winning config to the Unreal project on a git branch → re-benchmark to confirm.
Desktop: comparison against exhaustive sweep / presets → final report → video → Devpost.
Unreal facts to get right
Measure in a separate game process, not inside the editor: UnrealEditor.exe <Project>.uproject -game -windowed -ResX=1920 -ResY=1080 (no packaging needed). If packaging, use Development (Shipping strips the CSV profiler).
Disable VSync and the frame cap (r.VSync 0, t.MaxFPS 0) or every run measures ~16.67 ms.
Apply settings with -ExecCmds="sg.ShadowQuality 2,r.ScreenPercentage 75" (built by to_exec_cmds). Confirm in the log that they applied.
Level Blueprint does the timing: wait ~5 s warm-up → csvprofile frames=1500 → wait → quit. Python only launches, waits with a timeout, and collects the CSV.
CSVs land in <Project>/Saved/Profiling/CSV/. Copy them into reports/<run_id>/ (Saved/ is gitignored).
Make the scene GPU-bound (Lumen, virtual shadow maps, many shadow-casting lights, 1440p if needed), so settings changes are measurable.
Verify actual column names (FrameTime, GPUTime, GPU/...) on the first real file before hard-coding anything.
Out of scope (don't build unless asked)

C++ Unreal plugin, React/FastAPI dashboard, Docker, remote execution, shader/asset/mesh changes, arbitrary code editing. Optional only after the full loop works on real data: Editor Utility Widget button, backend-free React viewer of results.json, PyInstaller exe.

Fallbacks (from the plan)
Unreal measurement still blocked ~7 h in → simpler controlled benchmark, state limits clearly.
Command-line automation blocked → manually triggered captures, Python compares them.
LLM blocked → deterministic candidate selection, state autonomy as future work.
Always reserve time for validation, video, README, Devpost.