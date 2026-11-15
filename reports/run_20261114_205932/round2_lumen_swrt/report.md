# FrameOptimizer report: lumen_swrt

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0

**Why the agent proposed it:** The render thread limits 95.9% of frames (44.25 ms render vs 40.82 ms GPU), so the CPU lever that also cuts GPU work comes first. Hardware ray tracing costs about 2.86 ms of GPU time (RayTracingScene 1.53 + RayTracingDynamicGeometry 1.33) plus render-thread work to build that geometry each frame. ShadowDepths (10.81 ms) is the biggest GPU pass and a target for later, but shadow-only cuts will likely gain little while the render thread is the limit.

## Results

Frames analyzed: 580 before, 580 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 44.27 | 41.92 | -5.3% |
| p95 frame time (ms) | 49.8 | 47.68 | -4.3% |
| Worst frame (ms) | 241.88 | 70.44 | -70.9% |
| Median FPS | 22.6 | 23.9 | +5.8% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.02 | 0.01 | -50.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.1 | 0.09 | -10.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.02 | +100.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.06 | 0.05 | -16.7% |
| GPU/VirtualTexture | 0.02 | 0.02 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.13 | 0.11 | -15.4% |
| GPU/NaniteVisBuffer | 1.76 | 1.79 | +1.7% |
| GPU/NaniteBasePass | 2.46 | 3.71 | +50.8% |
| GPU/HZB | 0.06 | 0.03 | -50.0% |
| GPU/BeginOcclusionTests | 0.06 | 0.09 | +50.0% |
| GPU/LightGrid | 0.02 | 0.02 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.16 | 0.16 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.04 | 0.04 | +0.0% |
| GPU/LumenSceneUpdate | 0.36 | 0.42 | +16.7% |
| GPU/CompositionBeforeBasePass | 0.07 | 0.07 | +0.0% |
| GPU/RayTracingDynamicGeometry | 1.33 | 0.0 | -100.0% |
| GPU/RayTracingScene | 1.53 | 0.0 | -100.0% |
| GPU/LumenScreenProbeGather | 0.44 | 0.55 | +25.0% |
| GPU/SkyAtmosphereEditor | 3.24 | 1.79 | -44.8% |
| GPU/Basepass | 0.4 | 0.35 | -12.5% |
| GPU/RenderDeferredLighting | 1.68 | 1.55 | -7.7% |
| GPU/ShadowDepths | 10.81 | 9.68 | -10.5% |
| GPU/LumenReflections | 2.64 | 2.46 | -6.8% |
| GPU/TranslucentLighting | 0.6 | 0.6 | +0.0% |
| GPU/Lights | 0.38 | 0.31 | -18.4% |
| GPU/ShadowProjection | 0.09 | 0.09 | +0.0% |
| GPU/DistanceFieldShadows | 1.2 | 1.19 | -0.8% |
| GPU/VolumetricFog | 1.22 | 1.24 | +1.6% |
| GPU/TemporalSuperResolution | 3.5 | 3.5 | +0.0% |
| GPU/SkyAtmosphere | 0.05 | 0.05 | +0.0% |
| GPU/Fog | 1.79 | 1.79 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.21 | 0.2 | -4.8% |
| GPU/Distortion | 0.06 | 0.05 | -16.7% |
| GPU/Postprocessing | 0.55 | 0.54 | -1.8% |
| GPU/VirtualTextureUpdate | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.53 | 0.52 | -1.9% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.02 | 0.03 | +50.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 1.25 | 1.23 | -1.6% |
| GPU/VolCloudReconstruction | 0.12 | 0.12 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.36 | 0.38 | +5.6% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Mixed: Render thread (CPU) and GPU**. After: **Mixed: Render thread (CPU) and GPU**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 14.36 | 12.55 | -12.6% |
| render | 44.25 | 41.9 | -5.3% |
| gpu | 40.82 | 38.68 | -5.2% |

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate

---
*The AI suggests. Measurements decide. The developer approves.*
