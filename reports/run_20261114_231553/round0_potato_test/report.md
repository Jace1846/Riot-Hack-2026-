# FrameOptimizer report: potato_test

## What changed

- `r.ScreenPercentage`: 100 → 50
- `r.Shadow.MaxResolution`: 2048 → 512
- `r.Shadow.CSM.MaxCascades`: 4 → 1
- `r.PostProcessAAQuality`: 4 → 0
- `r.VolumetricFog`: 1 → 0
- `r.MotionBlurQuality`: 4 → 0
- `r.LensFlareQuality`: 2 → 0
- `r.SceneColorFringeQuality`: 1 → 0
- `r.BloomQuality`: 5 → 0
- `r.DepthOfFieldQuality`: 2 → 0
- `r.SSR.Quality`: 3 → 0
- `r.VolumetricFog.GridPixelSize`: 16 → 32
- `r.ShadowQuality`: 5 → 1
- `r.Lumen.ScreenProbeGather.DownsampleFactor`: 16 → 32
- `r.Nanite.MaxPixelsPerEdge`: 1 → 4
- `r.SkeletalMeshLODBias`: 0 → 2
- `r.ViewDistanceScale`: 1.0 → 0.4
- `foliage.DensityScale`: 1.0 → 0.25
- `foliage.LODDistanceScale`: 1.0 → 0.5
- `r.StaticMeshLODDistanceScale`: 1.0 → 3.0
- `r.Shadow.DistanceScale`: 1.0 → 0.25
- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Lumen.Reflections.Allow`: 1 → 0
- `r.Lumen.DiffuseIndirect.Allow`: 1 → 0
- `r.VolumetricCloud`: 1 → 0
- `r.DistanceFieldShadowing`: 1 → 0

**Why the agent proposed it:** Ceiling test: every setting at its lowest allowed value.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.01 | 4.6 | -54.0% |
| p95 frame time (ms) | 11.47 | 6.35 | -44.6% |
| Worst frame (ms) | 23.01 | 59.43 | +158.3% |
| Median FPS | 99.9 | 217.3 | +117.5% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.0 | 0.01 | n/a |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.04 | 0.03 | -25.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.02 | -33.3% |
| GPU/VirtualTexture | 0.0 | 0.0 | n/a |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.03 | +0.0% |
| GPU/NaniteVisBuffer | 0.67 | 0.51 | -23.9% |
| GPU/NaniteBasePass | 0.86 | 0.19 | -77.9% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.01 | -50.0% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.01 | -90.0% |
| GPU/Basepass | 0.08 | 0.04 | -50.0% |
| GPU/RenderDeferredLighting | 0.23 | 0.08 | -65.2% |
| GPU/ShadowDepths | 1.99 | 0.62 | -68.8% |
| GPU/TranslucentLighting | 0.09 | 0.07 | -22.2% |
| GPU/Lights | 0.07 | 0.02 | -71.4% |
| GPU/ShadowProjection | 0.02 | 0.01 | -50.0% |
| GPU/TemporalSuperResolution | 0.56 | 0.35 | -37.5% |
| GPU/SkyAtmosphere | 0.01 | 0.0 | -100.0% |
| GPU/Fog | 0.07 | 0.0 | -100.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.25 | 0.05 | -80.0% |
| GPU/Distortion | 0.05 | 0.02 | -60.0% |
| GPU/Postprocessing | 0.13 | 0.03 | -76.9% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.12 | -40.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.04 | 0.01 | -75.0% |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Mixed: Render thread (CPU) and Game thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.31 | 4.16 | -3.5% |
| render | 9.99 | 4.45 | -55.5% |
| gpu | 8.06 | 2.99 | -62.9% |

Note: the bottleneck moved from Render thread (CPU) to Mixed: Render thread (CPU) and Game thread (CPU). The GPU is no longer the main limit, so further graphics-setting cuts will help less.

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.ScreenPercentage`: Renders at lower internal resolution, so the image looks softer; 50 is very blurry
- `r.Shadow.MaxResolution`: Blurrier, more pixelated shadow edges
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects
- `r.PostProcessAAQuality`: More jagged or shimmering edges; 0 is almost no anti-aliasing
- `r.VolumetricFog`: Removes light shafts and fog volumes
- `r.MotionBlurQuality`: Low (cosmetic): less or no motion blur; many players turn it off anyway
- `r.LensFlareQuality`: Low (cosmetic): removes lens flares around bright lights
- `r.SceneColorFringeQuality`: Low (cosmetic): removes chromatic aberration (color fringing at screen edges)
- `r.BloomQuality`: Low: glow around bright areas is less smooth; 0 removes bloom
- `r.DepthOfFieldQuality`: Low: background/foreground blur is rougher; 0 removes it
- `r.SSR.Quality`: Medium: screen-space reflections get noisier; 0 turns them off
- `r.VolumetricFog.GridPixelSize`: Low: coarser fog and light shafts (fog stays on)
- `r.ShadowQuality`: Medium to severe: shadows get softer and less precise; 0 turns dynamic shadows off
- `r.Lumen.ScreenProbeGather.DownsampleFactor`: Medium: Lumen indirect lighting gets blotchier, especially in small details
- `r.Nanite.MaxPixelsPerEdge`: Low to medium: Nanite meshes use fewer triangles, fine detail softens
- `r.SkeletalMeshLODBias`: Low: characters use lower levels of detail
- `r.ViewDistanceScale`: Low to severe (CPU lever): distant objects stop drawing sooner; at 0.2 much of the scene pops in close to the camera
- `foliage.DensityScale`: Low at 0.75 up to severe at 0 (CPU lever): sparser grass and plants; 0 removes them
- `foliage.LODDistanceScale`: Low (CPU lever): plants switch to simpler models closer to the camera
- `r.StaticMeshLODDistanceScale`: Low (CPU lever): non-Nanite meshes switch to simpler models sooner (higher = simpler sooner)
- `r.Shadow.DistanceScale`: Medium (CPU and GPU lever): shadows stop being drawn closer to the camera, so fewer objects are processed for shadows; distant objects lose their shadows
- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate
- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Lumen.Reflections.Allow`: Medium (GPU lever): turns off Lumen reflections; shiny surfaces fall back to simpler reflections
- `r.Lumen.DiffuseIndirect.Allow`: Severe (GPU lever): turns off Lumen global illumination; bounced light disappears and shaded areas get flat and dark
- `r.VolumetricCloud`: Medium (GPU lever): removes volumetric clouds from the sky
- `r.DistanceFieldShadowing`: Medium (GPU lever): removes distance field shadows (soft shadows from distant objects)

---
*The AI suggests. Measurements decide. The developer approves.*
