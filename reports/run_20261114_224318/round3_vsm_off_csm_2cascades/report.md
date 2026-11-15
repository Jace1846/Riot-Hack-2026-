# FrameOptimizer report: vsm_off_csm_2cascades

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2

**Why the agent proposed it:** The render thread is the limit at 10.05 ms (93.8% of frames) against 8.14 ms GPU, so any gain will likely be small. HWRT, view distance and foliage changes barely moved it, so this swaps Virtual Shadow Maps for 2-cascade CSM to cut ShadowDepths (2.02 ms, the largest GPU pass) while keeping cascade draw submission on the CPU low.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.1 | 10.99 | +8.8% |
| p95 frame time (ms) | 11.63 | 16.39 | +40.9% |
| Worst frame (ms) | 137.05 | 144.44 | +5.4% |
| Median FPS | 99.0 | 91.0 | -8.1% |

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
| GPU/RenderVelocities | 0.04 | 0.04 | +0.0% |
| GPU/NaniteVisBuffer | 0.68 | 0.7 | +2.9% |
| GPU/NaniteBasePass | 0.97 | 0.93 | -4.1% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.16 | +6.7% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.25 | 0.26 | +4.0% |
| GPU/RayTracingScene | 0.33 | 0.34 | +3.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.02 | +100.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.09 | -10.0% |
| GPU/Basepass | 0.09 | 0.1 | +11.1% |
| GPU/RenderDeferredLighting | 0.28 | 0.21 | -25.0% |
| GPU/ShadowDepths | 2.02 | 2.88 | +42.6% |
| GPU/LumenReflections | 0.35 | 0.3 | -14.3% |
| GPU/TranslucentLighting | 0.09 | 0.09 | +0.0% |
| GPU/Lights | 0.06 | 0.05 | -16.7% |
| GPU/ShadowProjection | 0.03 | 0.04 | +33.3% |
| GPU/DistanceFieldShadows | 0.28 | 0.26 | -7.1% |
| GPU/VolumetricFog | 0.19 | 0.17 | -10.5% |
| GPU/TemporalSuperResolution | 0.54 | 0.55 | +1.9% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.08 | +33.3% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.06 | 0.06 | +0.0% |
| GPU/Distortion | 0.03 | 0.02 | -33.3% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.21 | +5.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.46 | 0.48 | +4.3% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.19 | +11.8% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.98 | 5.74 | +15.3% |
| render | 10.05 | 10.91 | +8.6% |
| gpu | 8.14 | 9.03 | +10.9% |

## Verdict: worse

This change made performance worse. Recommend reverting to the baseline.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects

---
*The AI suggests. Measurements decide. The developer approves.*
