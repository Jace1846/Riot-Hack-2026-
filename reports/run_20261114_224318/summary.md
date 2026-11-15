# FrameOptimizer run summary

**Developer's direction:** aim for 150 fps make drastic changes if needed

## Overall: no clear change

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 10.1 | 10.1 | +0.0% |
| p95 frame time (ms) | 11.63 | 11.63 | +0.0% |
| Median FPS | 99.0 | 99.0 | +0.0% |

## Rounds

| Round | Change | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|
| 1 | `r.Lumen.HardwareRayTracing`=0, `r.ViewDistanceScale`=0.8 | -2.6% | -2.0% | no clear change | no |
| 2 | `foliage.DensityScale`=0.5 | -0.5% | -0.9% | no clear change | no |
| 3 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2 | +8.8% | +40.9% | worse | no |

## Settings to apply

No tested change gave a clear measured improvement. Keep the starting settings.

---
*The AI suggests. Measurements decide. The developer approves.*
