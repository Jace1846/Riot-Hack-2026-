# FrameOptimizer run summary

**Developer's direction:** make it hit 150 fps at any cost

## Overall: improved

| Metric | Start | Best | Change |
|---|---|---|---|
| Median frame time (ms) | 10.04 | 6.82 | -32.1% |
| p95 frame time (ms) | 11.44 | 7.38 | -35.5% |
| Median FPS | 99.6 | 146.6 | +47.2% |

## Rounds

| Round | Change | FPS | Median | p95 | Verdict | Kept |
|---|---|---|---|---|---|---|
| 0 (potato test) | `r.ScreenPercentage`=70, `r.Shadow.MaxResolution`=512, `r.Shadow.CSM.MaxCascades`=2, `r.PostProcessAAQuality`=2, `r.VolumetricFog`=0, `r.MotionBlurQuality`=0, `r.LensFlareQuality`=0, `r.SceneColorFringeQuality`=0, `r.BloomQuality`=3, `r.DepthOfFieldQuality`=0, `r.SSR.Quality`=1, `r.VolumetricFog.GridPixelSize`=32, `r.ShadowQuality`=1, `r.Lumen.ScreenProbeGather.DownsampleFactor`=32, `r.Nanite.MaxPixelsPerEdge`=4, `r.SkeletalMeshLODBias`=2, `r.ViewDistanceScale`=0.4, `foliage.DensityScale`=0.25, `foliage.LODDistanceScale`=0.5, `r.StaticMeshLODDistanceScale`=2.0, `r.Shadow.DistanceScale`=0.5, `r.Lumen.HardwareRayTracing`=0, `r.Shadow.Virtual.Enable`=0, `r.Lumen.Reflections.Allow`=0, `r.Lumen.DiffuseIndirect.Allow`=0, `r.VolumetricCloud`=0, `r.DistanceFieldShadowing`=0 | 99.6 → 169.4 | -41.2% | -43.5% | improved | no (ceiling test) |
| 1 | `r.Lumen.HardwareRayTracing`=0, `r.ViewDistanceScale`=0.6, `foliage.DensityScale`=0.5, `foliage.LODDistanceScale`=0.5, `r.StaticMeshLODDistanceScale`=2.0, `r.Shadow.DistanceScale`=0.5 | 99.6 → 104.1 | -4.4% | -5.2% | improved | yes |
| 2 | `r.ViewDistanceScale`=0.4, `foliage.DensityScale`=0.25, `r.Lumen.Reflections.Allow`=0, `r.VolumetricCloud`=0, `r.DistanceFieldShadowing`=0, `r.VolumetricFog`=0, `r.MotionBlurQuality`=0, `r.LensFlareQuality`=0, `r.SceneColorFringeQuality`=0 | 104.1 → 120.3 | -13.4% | -15.5% | improved | yes |
| 3 | `r.Shadow.Virtual.Enable`=0, `r.Shadow.CSM.MaxCascades`=2, `r.Shadow.MaxResolution`=1024, `r.Lumen.DiffuseIndirect.Allow`=0, `r.SkeletalMeshLODBias`=1 | 120.3 → 146.6 | -17.9% | -19.4% | improved | yes |

## Settings to apply

- `r.Shadow.MaxResolution`: 2048 → 1024
- `r.Shadow.CSM.MaxCascades`: 4 → 2
- `r.VolumetricFog`: 1 → 0
- `r.MotionBlurQuality`: 4 → 0
- `r.LensFlareQuality`: 2 → 0
- `r.SceneColorFringeQuality`: 1 → 0
- `r.SkeletalMeshLODBias`: 0 → 1
- `r.ViewDistanceScale`: 1.0 → 0.4
- `foliage.DensityScale`: 1.0 → 0.25
- `foliage.LODDistanceScale`: 1.0 → 0.5
- `r.StaticMeshLODDistanceScale`: 1.0 → 2.0
- `r.Shadow.DistanceScale`: 1.0 → 0.5
- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Lumen.Reflections.Allow`: 1 → 0
- `r.Lumen.DiffuseIndirect.Allow`: 1 → 0
- `r.VolumetricCloud`: 1 → 0
- `r.DistanceFieldShadowing`: 1 → 0

FrameOptimizer has not changed your Unreal project. Check the visual trade-off in each round's report, then click Apply to project in the window if you approve.

---
*The AI suggests. Measurements decide. The developer approves.*
