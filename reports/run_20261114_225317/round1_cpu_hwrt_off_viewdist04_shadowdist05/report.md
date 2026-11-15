# FrameOptimizer report: cpu_hwrt_off_viewdist04_shadowdist05

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.ViewDistanceScale`: 1.0 → 0.4
- `r.Shadow.DistanceScale`: 1.0 → 0.5

**Why the agent proposed it:** The render thread is the bottleneck in 97.7% of frames (9.82 ms median), and 150 FPS needs 6.67 ms, a cut of about 32%, so this combines three strong CPU levers at aggressive values. Disabling hardware ray tracing removes the RayTracingScene/DynamicGeometry setup, while view distance 0.4 and shadow distance 0.5 cut draw calls and shadow casters (ShadowDepths is also the top GPU pass at 2.03 ms); even this may fall short of 150 FPS.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.84 | 9.97 | +1.3% |
| p95 frame time (ms) | 11.2 | 11.49 | +2.6% |
| Worst frame (ms) | 22.77 | 21.87 | -4.0% |
| Median FPS | 101.7 | 100.3 | -1.4% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.05 | 0.05 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.67 | 0.66 | -1.5% |
| GPU/NaniteBasePass | 0.94 | 0.53 | -43.6% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.1 | +900.0% |
| GPU/SkyAtmosphereEditor | 0.11 | 0.03 | -72.7% |
| GPU/Basepass | 0.09 | 0.31 | +244.4% |
| GPU/RenderDeferredLighting | 0.26 | 0.28 | +7.7% |
| GPU/ShadowDepths | 2.03 | 1.8 | -11.3% |
| GPU/LumenReflections | 0.3 | 0.58 | +93.3% |
| GPU/TranslucentLighting | 0.08 | 0.08 | +0.0% |
| GPU/Lights | 0.06 | 0.12 | +100.0% |
| GPU/ShadowProjection | 0.02 | 0.25 | +1150.0% |
| GPU/DistanceFieldShadows | 0.27 | 0.08 | -70.4% |
| GPU/VolumetricFog | 0.19 | 0.2 | +5.3% |
| GPU/TemporalSuperResolution | 0.54 | 0.55 | +1.9% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.07 | +16.7% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.15 | 0.14 | -6.7% |
| GPU/Distortion | 0.03 | 0.03 | +0.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.17 | -15.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.41 | 0.47 | +14.6% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.18 | 0.2 | +11.1% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.77 | 4.55 | -4.6% |
| render | 9.82 | 9.97 | +1.5% |
| gpu | 7.97 | 8.27 | +3.8% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate
- `r.ViewDistanceScale`: Low to medium (CPU lever): small distant objects stop drawing sooner and may pop in closer; 0.4 is Unreal's Low preset and pop-in is noticeable
- `r.Shadow.DistanceScale`: Medium (CPU and GPU lever): shadows stop being drawn closer to the camera, so fewer objects are processed for shadows; distant objects lose their shadows

---
*The AI suggests. Measurements decide. The developer approves.*
