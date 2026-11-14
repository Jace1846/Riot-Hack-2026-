# FrameForge report: shadow_02

> ⚠ **SYNTHETIC TEST DATA.** These numbers are not real Unreal measurements.

## What changed

- `r.Shadow.MaxResolution`: 2048 → 1024

**Why the agent proposed it:** Shadow depths are the second-biggest GPU cost; halve the shadow map resolution

## Results

Frames analyzed: 280 before, 280 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 14.1 | 14.1 | +0.0% |
| p95 frame time (ms) | 14.67 | 14.67 | +0.0% |
| Worst frame (ms) | 33.2 | 33.2 | +0.0% |
| Median FPS | 70.9 | 70.9 | +0.0% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/BasePass | 3.95 | 3.95 | +0.0% |
| GPU/ShadowDepths | 3.31 | 3.31 | +0.0% |
| GPU/Lights | 1.95 | 1.95 | +0.0% |
| GPU/PostProcessing | 1.5 | 1.5 | +0.0% |
| GPU/Translucency | 0.8 | 0.8 | +0.0% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.Shadow.MaxResolution`: Blurrier, more pixelated shadow edges

---
*The AI suggests. Measurements decide. The developer approves.*
