# FrameOptimizer report: lumen_swrt_viewdist_0p8

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.ViewDistanceScale`: 1.0 → 0.8

**Why the agent proposed it:** The render thread is the bottleneck: 10.05 ms median, slowest in 93.8% of frames, while the GPU takes 8.14 ms. Turning off hardware ray tracing cuts render-thread ray-tracing scene setup, and with it the GPU RayTracingScene (0.33 ms) and RayTracingDynamicGeometry (0.25 ms) passes. Lowering ViewDistanceScale to 0.8 reduces draw and visibility work. Together they are a drastic step toward the 150 fps target (6.67 ms), but the gain may be modest unless ray tracing is driving the render-thread cost.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.1 | 9.84 | -2.6% |
| p95 frame time (ms) | 11.63 | 11.4 | -2.0% |
| Worst frame (ms) | 137.05 | 135.09 | -1.4% |
| Median FPS | 99.0 | 101.7 | +2.7% |

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
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.02 | -33.3% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.04 | 0.04 | +0.0% |
| GPU/NaniteVisBuffer | 0.68 | 0.66 | -2.9% |
| GPU/NaniteBasePass | 0.97 | 0.57 | -41.2% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.01 | -50.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.09 | +800.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.03 | -70.0% |
| GPU/Basepass | 0.09 | 0.33 | +266.7% |
| GPU/RenderDeferredLighting | 0.28 | 0.35 | +25.0% |
| GPU/ShadowDepths | 2.02 | 1.78 | -11.9% |
| GPU/LumenReflections | 0.35 | 0.55 | +57.1% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.06 | 0.22 | +266.7% |
| GPU/ShadowProjection | 0.03 | 0.26 | +766.7% |
| GPU/DistanceFieldShadows | 0.28 | 0.07 | -75.0% |
| GPU/VolumetricFog | 0.19 | 0.2 | +5.3% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.06 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.06 | 0.04 | -33.3% |
| GPU/Distortion | 0.03 | 0.02 | -33.3% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.17 | -15.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.46 | 0.01 | -97.8% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.18 | +5.9% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.98 | 4.75 | -4.6% |
| render | 10.05 | 9.76 | -2.9% |
| gpu | 8.14 | 8.15 | +0.1% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate
- `r.ViewDistanceScale`: Low to medium (CPU lever): small distant objects stop drawing sooner and may pop in closer

---
*The AI suggests. Measurements decide. The developer approves.*
