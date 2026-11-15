# FrameOptimizer report: lumen_hwrt_off

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0

**Why the agent proposed it:** The render thread limits 99.7% of frames (43.42 ms), so turning off hardware ray tracing is the strongest CPU lever available. It also removes the GPU RayTracingScene (1.2 ms) and RayTracingDynamicGeometry (0.94 ms) passes. Shadow cuts like ShadowDepths (10.77 ms) can follow, since you don't need shadows, but VSM-off was already 3.6% worse, and with the render thread this high, 100 fps is unlikely from these settings alone.

## Results

Frames analyzed: 580 before, 580 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 43.45 | 42.54 | -2.1% |
| p95 frame time (ms) | 46.82 | 44.68 | -4.6% |
| Worst frame (ms) | 56.5 | 49.07 | -13.2% |
| Median FPS | 23.0 | 23.5 | +2.2% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.07 | 0.07 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.0 | 0.0 | n/a |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.08 | 0.07 | -12.5% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.1 | 0.1 | +0.0% |
| GPU/NaniteVisBuffer | 1.85 | 1.82 | -1.6% |
| GPU/NaniteBasePass | 2.41 | 2.77 | +14.9% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.1 | 0.1 | +0.0% |
| GPU/LightGrid | 0.02 | 0.02 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.16 | 0.15 | -6.3% |
| GPU/CaptureConvolveSkyEnvMap | 0.04 | 0.04 | +0.0% |
| GPU/LumenSceneUpdate | 0.2 | 0.19 | -5.0% |
| GPU/CompositionBeforeBasePass | 0.03 | 0.04 | +33.3% |
| GPU/RayTracingDynamicGeometry | 0.94 | 0.0 | -100.0% |
| GPU/RayTracingScene | 1.2 | 0.0 | -100.0% |
| GPU/LumenScreenProbeGather | 0.39 | 0.6 | +53.8% |
| GPU/SkyAtmosphereEditor | 2.21 | 1.43 | -35.3% |
| GPU/Basepass | 0.22 | 0.5 | +127.3% |
| GPU/RenderDeferredLighting | 1.7 | 1.68 | -1.2% |
| GPU/ShadowDepths | 10.77 | 6.02 | -44.1% |
| GPU/LumenReflections | 1.58 | 5.06 | +220.3% |
| GPU/TranslucentLighting | 0.6 | 0.61 | +1.7% |
| GPU/Lights | 0.45 | 1.34 | +197.8% |
| GPU/ShadowProjection | 0.08 | 0.17 | +112.5% |
| GPU/DistanceFieldShadows | 1.74 | 1.62 | -6.9% |
| GPU/VolumetricFog | 1.25 | 1.22 | -2.4% |
| GPU/TemporalSuperResolution | 3.47 | 3.45 | -0.6% |
| GPU/SkyAtmosphere | 0.05 | 0.05 | +0.0% |
| GPU/Fog | 1.8 | 1.79 | -0.6% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 1.35 | 1.34 | -0.7% |
| GPU/Distortion | 0.32 | 0.31 | -3.1% |
| GPU/Postprocessing | 0.55 | 0.55 | +0.0% |
| GPU/VirtualTextureUpdate | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.49 | 0.48 | -2.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.02 | 0.03 | +50.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 1.47 | 1.46 | -0.7% |
| GPU/VolCloudReconstruction | 0.12 | 0.11 | -8.3% |
| GPU/VolCloudComposeOverScene | 0.42 | 0.41 | -2.4% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Mixed: Render thread (CPU) and GPU**. After: **Mixed: Render thread (CPU) and GPU**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 10.59 | 9.94 | -6.1% |
| render | 43.42 | 42.52 | -2.1% |
| gpu | 39.74 | 39.42 | -0.8% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate

---
*The AI suggests. Measurements decide. The developer approves.*
