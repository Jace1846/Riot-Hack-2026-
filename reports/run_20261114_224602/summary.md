# FrameOptimizer run summary

**Developer's direction:** aim for 150 fps make drastic changes if needed. it has to hit 150 frames by the 3rd pass through

## Overall: no clear change

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 9.77 | 9.77 | +0.0% |
| p95 frame time (ms) | 12.02 | 12.02 | +0.0% |
| Median FPS | 102.4 | 102.4 | +0.0% |

## Rounds

| Round | Change | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|
| 1 | `r.Lumen.HardwareRayTracing`=0, `r.ViewDistanceScale`=0.6 | +2.9% | -4.9% | no clear change | no |
| 2 | `foliage.DensityScale`=0.5 | +2.4% | -6.2% | no clear change | no |
| 3 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2 | +10.1% | +1.0% | worse | no |

## Settings to apply

No tested change gave a clear measured improvement. Keep the starting settings.

---
*The AI suggests. Measurements decide. The developer approves.*
