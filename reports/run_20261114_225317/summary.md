# FrameOptimizer run summary

**Developer's direction:** hit 150 fps at any cost

## Overall: no clear change

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 9.84 | 9.84 | +0.0% |
| p95 frame time (ms) | 11.2 | 11.2 | +0.0% |
| Median FPS | 101.7 | 101.7 | +0.0% |

## Rounds

| Round | Change | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|
| 1 | `r.Lumen.HardwareRayTracing`=0, `r.ViewDistanceScale`=0.4, `r.Shadow.DistanceScale`=0.5 | +1.3% | +2.6% | no clear change | no |
| 2 | `foliage.DensityScale`=0.25, `foliage.LODDistanceScale`=0.5, `r.StaticMeshLODDistanceScale`=2.0 | +0.5% | +4.7% | no clear change | no |
| 3 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2, `r.Shadow.MaxResolution`=1024 | +13.5% | +15.7% | worse | no |

## Settings to apply

No tested change gave a clear measured improvement. Keep the starting settings.

---
*The AI suggests. Measurements decide. The developer approves.*
