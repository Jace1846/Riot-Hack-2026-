# FrameOptimizer run summary

## Overall: no clear change

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 10.01 | 10.01 | +0.0% |
| p95 frame time (ms) | 11.47 | 11.47 | +0.0% |
| Median FPS | 99.9 | 99.9 | +0.0% |

## Rounds

| Round | Change | FPS | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|---|
| 0 (potato test) | `r.ScreenPercentage`=50, `r.Shadow.MaxResolution`=512, `r.Shadow.CSM.MaxCascades`=1, `r.PostProcessAAQuality`=0, `r.VolumetricFog`=0, `r.MotionBlurQuality`=0, `r.LensFlareQuality`=0, `r.SceneColorFringeQuality`=0, `r.BloomQuality`=0, `r.DepthOfFieldQuality`=0, `r.SSR.Quality`=0, `r.VolumetricFog.GridPixelSize`=32, `r.ShadowQuality`=1, `r.Lumen.ScreenProbeGather.DownsampleFactor`=32, `r.Nanite.MaxPixelsPerEdge`=4, `r.SkeletalMeshLODBias`=2, `r.ViewDistanceScale`=0.4, `foliage.DensityScale`=0.25, `foliage.LODDistanceScale`=0.5, `r.StaticMeshLODDistanceScale`=3.0, `r.Shadow.DistanceScale`=0.25, `r.Lumen.HardwareRayTracing`=0, `r.Shadow.Virtual.Enable`=0, `r.Lumen.Reflections.Allow`=0, `r.Lumen.DiffuseIndirect.Allow`=0, `r.VolumetricCloud`=0, `r.DistanceFieldShadowing`=0 | 99.9 → 217.3 | -54.0% | -44.6% | improved | no (ceiling test) |
| 1 | `r.Lumen.HardwareRayTracing`=0, `r.Shadow.DistanceScale`=0.75, `r.ViewDistanceScale`=0.8, `foliage.LODDistanceScale`=0.75, `r.StaticMeshLODDistanceScale`=1.5 | 99.9 → 100.8 | -0.9% | -0.4% | no clear change | no |
| 2 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2, `r.DistanceFieldShadowing`=0 | 99.9 → 96.3 | +3.8% | +2.8% | worse | no |
| 3 | `foliage.DensityScale`=0.5, `r.ViewDistanceScale`=0.6, `r.Shadow.DistanceScale`=0.5 | 99.9 → 101.5 | -1.6% | -2.0% | no clear change | no |

## Settings to apply

No tested change gave a clear measured improvement. Keep the starting settings.

---
*The AI suggests. Measurements decide. The developer approves.*
