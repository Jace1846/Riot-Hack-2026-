# FrameOptimizer run summary

**Developer's direction:** this is a colurful cartoony scene so it doesnt need any shadows and try and get it to run at 100 fps

## Overall: no clear change

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 43.45 | 43.45 | +0.0% |
| p95 frame time (ms) | 46.82 | 46.82 | +0.0% |
| Median FPS | 23.0 | 23.0 | +0.0% |

## Rounds

| Round | Change | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|
| 1 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2 | +3.6% | +6.8% | worse | no |
| 2 | `r.Lumen.HardwareRayTracing`=0 | -2.1% | -4.6% | no clear change | no |
| 3 | `r.ShadowQuality`=3 | -0.8% | -2.4% | no clear change | no |

## Settings to apply

No tested change gave a clear measured improvement. Keep the starting settings.

---
*The AI suggests. Measurements decide. The developer approves.*
