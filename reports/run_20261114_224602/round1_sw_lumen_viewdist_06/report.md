# FrameOptimizer report: sw_lumen_viewdist_06

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.ViewDistanceScale`: 1.0 → 0.6

**Why the agent proposed it:** The render thread is the bottleneck at 9.64 ms (91.8% of frames), while the GPU takes only 7.68 ms. GPU/RayTracingScene (0.33 ms) and RayTracingDynamicGeometry (0.25 ms) suggest hardware ray tracing also adds render-thread work to build the ray-tracing scene each frame. To reach the 150 FPS (6.67 ms) target within three passes, this pairs software Lumen tracing with the strongest view-distance cut to reduce draw calls. Because only the CPU levers apply here, the gain may be modest unless these two cut render-thread time substantially.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.77 | 10.05 | +2.9% |
| p95 frame time (ms) | 12.02 | 11.43 | -4.9% |
| Worst frame (ms) | 146.58 | 21.55 | -85.3% |
| Median FPS | 102.4 | 99.5 | -2.8% |

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
| GPU/BuildRenderingCommandsDeferred | 0.02 | 0.02 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.62 | 0.68 | +9.7% |
| GPU/NaniteBasePass | 0.95 | 0.56 | -41.1% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.01 | 0.02 | +100.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.09 | +800.0% |
| GPU/SkyAtmosphereEditor | 0.11 | 0.03 | -72.7% |
| GPU/Basepass | 0.09 | 0.32 | +255.6% |
| GPU/RenderDeferredLighting | 0.26 | 0.39 | +50.0% |
| GPU/ShadowDepths | 1.96 | 1.78 | -9.2% |
| GPU/LumenReflections | 0.29 | 0.56 | +93.1% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.06 | 0.21 | +250.0% |
| GPU/ShadowProjection | 0.21 | 0.26 | +23.8% |
| GPU/DistanceFieldShadows | 0.1 | 0.07 | -30.0% |
| GPU/VolumetricFog | 0.19 | 0.2 | +5.3% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.06 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.05 | 0.08 | +60.0% |
| GPU/Distortion | 0.02 | 0.03 | +50.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.17 | -15.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.01 | 0.46 | +4500.0% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.14 | 0.18 | +28.6% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 5.17 | 4.67 | -9.7% |
| render | 9.64 | 10.04 | +4.1% |
| gpu | 7.68 | 8.34 | +8.6% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate
- `r.ViewDistanceScale`: Low to medium (CPU lever): small distant objects stop drawing sooner and may pop in closer

---
*The AI suggests. Measurements decide. The developer approves.*
