# FrameOptimizer report: csm_2cascades_vsm_off

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2

**Why the agent proposed it:** The scene is render-thread bound (render 9.64 ms of a 9.77 ms median, slowest in 91.8% of frames), so GPU-only settings will likely give only a small gain. The CPU levers already tried (HW ray tracing plus view distance, and foliage density) showed no clear change. Per the request for drastic changes, this targets the largest GPU pass, ShadowDepths at 1.96 ms, by swapping Virtual Shadow Maps for 2-cascade CSM, which may also cut render-thread shadow setup and per-view culling work.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.77 | 10.76 | +10.1% |
| p95 frame time (ms) | 12.02 | 12.14 | +1.0% |
| Worst frame (ms) | 146.58 | 27.88 | -81.0% |
| Median FPS | 102.4 | 92.9 | -9.3% |

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
| GPU/BuildRenderingCommandsDeferred | 0.02 | 0.03 | +50.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.03 | +0.0% |
| GPU/NaniteVisBuffer | 0.62 | 0.69 | +11.3% |
| GPU/NaniteBasePass | 0.95 | 0.91 | -4.2% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.01 | 0.02 | +100.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.25 | 0.25 | +0.0% |
| GPU/RayTracingScene | 0.33 | 0.32 | -3.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.11 | 0.1 | -9.1% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.26 | 0.24 | -7.7% |
| GPU/ShadowDepths | 1.96 | 2.81 | +43.4% |
| GPU/LumenReflections | 0.29 | 0.28 | -3.4% |
| GPU/TranslucentLighting | 0.09 | 0.09 | +0.0% |
| GPU/Lights | 0.06 | 0.05 | -16.7% |
| GPU/ShadowProjection | 0.21 | 0.04 | -81.0% |
| GPU/DistanceFieldShadows | 0.1 | 0.24 | +140.0% |
| GPU/VolumetricFog | 0.19 | 0.17 | -10.5% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.07 | +16.7% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.05 | 0.09 | +80.0% |
| GPU/Distortion | 0.02 | 0.03 | +50.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.2 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.01 | 0.46 | +4500.0% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.14 | 0.2 | +42.9% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 5.17 | 4.74 | -8.3% |
| render | 9.64 | 10.74 | +11.4% |
| gpu | 7.68 | 8.84 | +15.1% |

## Verdict: worse

This change made performance worse. Recommend reverting to the baseline.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects

---
*The AI suggests. Measurements decide. The developer approves.*
