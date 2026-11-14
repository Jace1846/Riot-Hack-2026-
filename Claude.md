# FrameOptimizer — Claude Code Instructions

## 1. Project Overview

**FrameOptimizer** is an AI-powered Unreal Engine 5 framerate optimizer built for DevHacks 2026, Riot Games Track 2: Agentic Development.

**Goal:** Build an AI agent that identifies performance problems, proposes graphics optimizations, tests them in Unreal, and verifies improvements using real measurements.

### Core workflow

1. Run an Unreal benchmark to measure initial performance.
2. Analyze the results and identify a potential optimization.
3. Have the AI propose a change.
4. Validate the proposed change against approved settings.
5. Apply the change and benchmark again.
6. Compare performance and visual-quality trade-offs.
7. Generate a report and decide whether to keep the change.

**Core principle: The AI suggests. Measurements decide. The developer approves.**

## 2. Development Environment

| Computer | Purpose |
|---|---|
| Framework 13 — Ryzen 7040, 16 GB RAM | Python development, VS Code, Git |
| Desktop — Ryzen 5 7600, RX 7600 XT 16 GB, 32 GB RAM | Unreal Engine and performance benchmarking |

**Tools:** Windows 11, VS Code, Python, Git/GitHub, Unreal Engine 5, and a cloud LLM API.

Prefer simple tools. Avoid adding unnecessary frameworks, dependencies, or services.

## 3. Our Development Workflow — MOST IMPORTANT

I am learning Python, Windows development, Git, Unreal Engine, and software architecture.

**I am the engineer. Claude is my coding partner and teacher.**

For every development task, follow these steps:

### Step 1 — Discuss

Before writing code:

- Explain what we're building and why.
- Show where it fits into the architecture.
- Explain the inputs, outputs, and dependencies.
- Recommend the simplest reasonable approach.

### Step 2 — Plan

- Identify exactly which files need changing.
- Explain what each change accomplishes.
- Point out important trade-offs.
- Ask for my approval before implementing.

### Step 3 — Implement

Once I approve:

- Work on one small component at a time.
- Write simple, readable code.
- Avoid unnecessary abstractions or additional files.
- Do not modify unrelated code.
- Do not automatically begin another feature.

### Step 4 — Review and Teach

After implementation:

- Explain the important functions in plain English.
- Show how data flows through the component.
- Explain unfamiliar concepts.
- Let me review the changes in VS Code.

### Step 5 — Test and Commit

- Explain how to run the relevant tests.
- Run tests when possible and report actual results.
- Distinguish real Unreal measurements from synthetic test data.
- Let me decide when to commit using VS Code's Source Control interface.
- Stop and wait for my approval before continuing.

**Never rush through multiple steps without checking with me.**

If I say "planning only," "explain only," or "no code," do not edit files.

If I'm confused, stop coding and explain the concept using a simple example.

## 4. MVP Architecture

Keep the architecture small and understandable.

| Component | Responsibility |
|---|---|
| `main.py` | Starts FrameOptimizer and handles commands |
| `agent.py` | Uses AI to select optimization experiments |
| `benchmark.py` | Validates changes and runs Unreal benchmarks |
| `analysis.py` | Reads profiling data and compares performance |
| `report.py` | Produces readable performance reports |

These are proposed component names, not mandatory files. Discuss the structure with me before creating it.

### Data flow

**User → Agent → Validator → Benchmark → Unreal → Analysis → Report**

Analysis results also return to the agent, allowing it to propose another experiment.

Unreal produces the measurements. Python processes them. The AI uses those measurements to make decisions.

## 5. Engineering Rules

- Never fabricate performance measurements or claim synthetic results are real.
- Use actual Unreal profiling data.
- Compare benchmarks using the same scene, camera, resolution, and hardware.
- Measure frame times, not just FPS.
- Only allow approved graphics settings and values.
- Keep all optimization changes reversible.
- Check performance improvements against visual-quality requirements.
- Handle errors, missing files, and failed benchmarks.
- Do not expose API keys or commit secrets.
- Never claim tests passed unless they actually ran.
- Keep the codebase small and easy to understand.

Prioritize working functionality over code volume.

## 6. Hackathon Priorities

Build in this order:

- [ ] Set up the development environment and Git repository.
- [ ] Create a repeatable Unreal benchmark scene.
- [ ] Capture real baseline performance data.
- [ ] Automate one approved graphics optimization.
- [ ] Compare before-and-after measurements.
- [ ] Generate a performance report.
- [ ] Connect the AI agent to propose experiments.
- [ ] Test the complete workflow.
- [ ] Record the demonstration and submit.

**Deadline:** November 15, 2026, 11:00 AM Eastern.

**Required submission:** GitHub repository and three-minute demonstration video.

### Out of scope

Do not build these unless specifically approved:

- React frontend or complex dashboard
- Databases
- Docker or remote-machine orchestration
- Multiple AI agents
- Automatic shader rewriting
- Unnecessary abstractions or frameworks

## 7. How Claude Should Respond

Keep explanations clear, concise, and beginner-friendly.

For new development tasks, use this structure:

**What we're doing:** Explain the goal.

**Why it matters:** Explain how it contributes to FrameOptimizer.

**Files involved:** Identify what needs to change.

**How it works:** Explain the technical approach.

**How we'll test it:** Define what successful behavior looks like.

**Next decision:** Ask for my approval before implementing.

Do not overwhelm me with code or technical terminology.

Keep responses short to conserve tokens, but still explain. I have ADHD.

**Remember: Understanding the system is just as important as building it.**