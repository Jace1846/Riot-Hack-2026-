# FrameOptimizer report: vsm_off_csm_2

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2

**Why the agent proposed it:** GPU/ShadowDepths is by far the largest GPU pass at 10.77 ms, and you said this cartoony scene doesn't need shadows, so this swaps Virtual Shadow Maps for cheap 2-cascade CSM. The render thread is the slowest part in 99.7% of frames (43.42 ms vs 39.74 ms GPU), so the frame-time gain may be limited until render-thread cost is also reduced; disabling Lumen hardware ray tracing is the next candidate for that.

## Results

Frames analyzed: 580 before, 580 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 43.45 | 45.01 | +3.6% |
| p95 frame time (ms) | 46.82 | 50.0 | +6.8% |
| Worst frame (ms) | 56.5 | 4731.08 | +8273.6% |
| Median FPS | 23.0 | 22.2 | -3.5% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.01 | 0.02 | +100.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.07 | 0.07 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.0 | 0.01 | n/a |
| GPU/GPUSceneUpdate | 0.01 | 0.02 | +100.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.08 | 0.09 | +12.5% |
| GPU/VirtualTexture | 0.01 | 0.02 | +100.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.1 | 0.1 | +0.0% |
| GPU/NaniteVisBuffer | 1.85 | 1.84 | -0.5% |
| GPU/NaniteBasePass | 2.41 | 2.33 | -3.3% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.1 | 0.1 | +0.0% |
| GPU/LightGrid | 0.02 | 0.02 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.16 | 0.15 | -6.3% |
| GPU/CaptureConvolveSkyEnvMap | 0.04 | 0.04 | +0.0% |
| GPU/LumenSceneUpdate | 0.2 | 0.23 | +15.0% |
| GPU/CompositionBeforeBasePass | 0.03 | 0.04 | +33.3% |
| GPU/RayTracingDynamicGeometry | 0.94 | 0.9 | -4.3% |
| GPU/RayTracingScene | 1.2 | 1.18 | -1.7% |
| GPU/LumenScreenProbeGather | 0.39 | 0.34 | -12.8% |
| GPU/SkyAtmosphereEditor | 2.21 | 2.34 | +5.9% |
| GPU/Basepass | 0.22 | 0.18 | -18.2% |
| GPU/RenderDeferredLighting | 1.7 | 1.72 | +1.2% |
| GPU/ShadowDepths | 10.77 | 11.48 | +6.6% |
| GPU/LumenReflections | 1.58 | 4.41 | +179.1% |
| GPU/TranslucentLighting | 0.6 | 0.65 | +8.3% |
| GPU/Lights | 0.45 | 0.51 | +13.3% |
| GPU/ShadowProjection | 0.08 | 0.23 | +187.5% |
| GPU/DistanceFieldShadows | 1.74 | 0.31 | -82.2% |
| GPU/VolumetricFog | 1.25 | 1.08 | -13.6% |
| GPU/TemporalSuperResolution | 3.47 | 3.46 | -0.3% |
| GPU/SkyAtmosphere | 0.05 | 0.05 | +0.0% |
| GPU/Fog | 1.8 | 1.77 | -1.7% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 1.35 | 1.26 | -6.7% |
| GPU/Distortion | 0.32 | 0.31 | -3.1% |
| GPU/Postprocessing | 0.55 | 0.55 | +0.0% |
| GPU/VirtualTextureUpdate | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.49 | 0.49 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 1.47 | 1.44 | -2.0% |
| GPU/VolCloudReconstruction | 0.12 | 0.12 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.42 | 0.41 | -2.4% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Mixed: Render thread (CPU) and GPU**. After: **Mixed: Render thread (CPU) and GPU**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 10.59 | 12.11 | +14.4% |
| render | 43.42 | 44.99 | +3.6% |
| gpu | 39.74 | 40.99 | +3.1% |

## Verdict: worse

This change made performance worse. Recommend reverting to the baseline.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects

---
*The AI suggests. Measurements decide. The developer approves.*
