# FrameOptimizer report: cpu_max_plus_pass_cuts_150fps

## What changed

- `r.ViewDistanceScale`: 0.6 → 0.4
- `foliage.DensityScale`: 0.5 → 0.25
- `r.Lumen.Reflections.Allow`: 1 → 0
- `r.VolumetricCloud`: 1 → 0
- `r.DistanceFieldShadowing`: 1 → 0
- `r.VolumetricFog`: 1 → 0
- `r.MotionBlurQuality`: 4 → 0
- `r.LensFlareQuality`: 2 → 0
- `r.SceneColorFringeQuality`: 1 → 0

**Why the agent proposed it:** The render thread is the bottleneck at 9.59 ms on 100% of frames, and 150 FPS needs 6.67 ms, a gap of about 30%. The potato test reached 169 FPS, so the target is within reach. This pushes the remaining CPU levers to their minimum (view distance 0.4, foliage density 0.25) and removes whole render passes, which cuts render-thread setup work: Lumen reflections (0.56 ms GPU), volumetric clouds (0.47 + 0.17 ms compose), distance-field shadows, volumetric fog and the cosmetic post effects. Lumen GI and virtual shadows stay on, because disabling GI is severe and switching to cascaded shadows could add draw calls on the CPU.

## Results

Frames analyzed: 540 before, 540 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.6 | 8.31 | -13.4% |
| p95 frame time (ms) | 10.84 | 9.16 | -15.5% |
| Worst frame (ms) | 11.65 | 10.51 | -9.8% |
| Median FPS | 104.1 | 120.3 | +15.6% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.04 | 0.03 | -25.0% |
| GPU/GlobalDistanceFieldUpdate | 0.17 | 0.17 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.68 | 0.61 | -10.3% |
| GPU/NaniteBasePass | 0.47 | 0.47 | +0.0% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.01 | -50.0% |
| GPU/LumenSceneUpdate | 0.11 | 0.12 | +9.1% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.01 | +0.0% |
| GPU/LumenSceneLighting | 0.16 | 0.16 | +0.0% |
| GPU/LumenScreenProbeGather | 0.08 | 0.07 | -12.5% |
| GPU/SkyAtmosphereEditor | 0.03 | 0.03 | +0.0% |
| GPU/Basepass | 0.21 | 0.21 | +0.0% |
| GPU/RenderDeferredLighting | 0.27 | 0.44 | +63.0% |
| GPU/ShadowDepths | 1.64 | 1.69 | +3.0% |
| GPU/TranslucentLighting | 0.08 | 0.09 | +12.5% |
| GPU/Lights | 0.19 | 0.17 | -10.5% |
| GPU/ShadowProjection | 0.29 | 0.31 | +6.9% |
| GPU/TemporalSuperResolution | 0.56 | 0.55 | -1.8% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.1 | 0.01 | -90.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.25 | 0.31 | +24.0% |
| GPU/Distortion | 0.04 | 0.05 | +25.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.17 | 0.15 | -11.8% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 3.86 | 3.95 | +2.3% |
| render | 9.59 | 8.28 | -13.7% |
| gpu | 7.89 | 6.68 | -15.3% |

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.ViewDistanceScale`: Low to severe (CPU lever): distant objects stop drawing sooner; at 0.2 much of the scene pops in close to the camera
- `foliage.DensityScale`: Low at 0.75 up to severe at 0 (CPU lever): sparser grass and plants; 0 removes them
- `r.Lumen.Reflections.Allow`: Medium (GPU lever): turns off Lumen reflections; shiny surfaces fall back to simpler reflections
- `r.VolumetricCloud`: Medium (GPU lever): removes volumetric clouds from the sky
- `r.DistanceFieldShadowing`: Medium (GPU lever): removes distance field shadows (soft shadows from distant objects)
- `r.VolumetricFog`: Removes light shafts and fog volumes
- `r.MotionBlurQuality`: Low (cosmetic): less or no motion blur; many players turn it off anyway
- `r.LensFlareQuality`: Low (cosmetic): removes lens flares around bright lights
- `r.SceneColorFringeQuality`: Low (cosmetic): removes chromatic aberration (color fringing at screen edges)

---
*The AI suggests. Measurements decide. The developer approves.*
