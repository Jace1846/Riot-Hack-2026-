# FrameOptimizer run summary

**Developer's direction:** this is a colurful cartoony scene so it doesnt need any shadows and try and get it to run at max fps

## Overall: improved

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 44.27 | 40.29 | -9.0% |
| p95 frame time (ms) | 49.8 | 45.71 | -8.2% |
| Median FPS | 22.6 | 24.8 | +9.7% |

## Rounds

| Round | Change | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|
| 1 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2 | +15.2% | +22.2% | worse | no |
| 2 | `r.Lumen.HardwareRayTracing`=0 | -5.3% | -4.3% | improved | yes |
| 3 | `r.ShadowQuality`=3 | -3.9% | -4.1% | improved | yes |

## Settings to apply

- `r.ShadowQuality`: 5 → 3
- `r.Lumen.HardwareRayTracing`: 1 → 0

FrameOptimizer has not changed your Unreal project. Check the visual trade-off in each round's report, then apply the settings you approve yourself.

---
*The AI suggests. Measurements decide. The developer approves.*
