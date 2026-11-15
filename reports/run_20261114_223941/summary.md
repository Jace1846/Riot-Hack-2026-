# FrameOptimizer run summary

**Developer's direction:** aim for 150 fps

## Overall: improved

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 10.45 | 10.08 | -3.5% |
| p95 frame time (ms) | 14.03 | 11.96 | -14.8% |
| Median FPS | 95.7 | 99.2 | +3.7% |

## Rounds

| Round | Change | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|
| 1 | `r.ViewDistanceScale`=0.8 | -3.5% | -14.8% | improved | yes |
| 2 | `foliage.DensityScale`=0.75 | -0.7% | -1.5% | no clear change | no |
| 3 | `r.ViewDistanceScale`=0.6 | -0.8% | -4.9% | no clear change | no |

## Settings to apply

- `r.ViewDistanceScale`: 1.0 → 0.8

FrameOptimizer has not changed your Unreal project. Check the visual trade-off in each round's report, then click Apply to project in the window if you approve.

---
*The AI suggests. Measurements decide. The developer approves.*
