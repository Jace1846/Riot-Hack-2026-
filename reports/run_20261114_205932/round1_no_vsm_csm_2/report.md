# FrameOptimizer report: no_vsm_csm_2

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2

**Why the agent proposed it:** GPU/ShadowDepths is the largest GPU pass at 10.81 ms, and the developer says this cartoony scene doesn't need shadows. This test turns off Virtual Shadow Maps and drops the fallback cascaded shadows to 2 cascades. The render thread is the slowest part in 95.9% of frames, so the frame-time gain may be smaller than the GPU saving until render-thread cost also drops.

## Results

Frames analyzed: 580 before, 580 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 44.27 | 51.01 | +15.2% |
| p95 frame time (ms) | 49.8 | 60.88 | +22.2% |
| Worst frame (ms) | 241.88 | 249.22 | +3.0% |
| Median FPS | 22.6 | 19.6 | -13.3% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.1 | 0.11 | +10.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.06 | 0.09 | +50.0% |
| GPU/VirtualTexture | 0.02 | 0.02 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.13 | 0.11 | -15.4% |
| GPU/NaniteVisBuffer | 1.76 | 1.78 | +1.1% |
| GPU/NaniteBasePass | 2.46 | 2.43 | -1.2% |
| GPU/HZB | 0.06 | 0.07 | +16.7% |
| GPU/BeginOcclusionTests | 0.06 | 0.05 | -16.7% |
| GPU/LightGrid | 0.02 | 0.02 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.16 | 0.16 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.04 | 0.05 | +25.0% |
| GPU/LumenSceneUpdate | 0.36 | 0.45 | +25.0% |
| GPU/CompositionBeforeBasePass | 0.07 | 0.11 | +57.1% |
| GPU/RayTracingDynamicGeometry | 1.33 | 1.38 | +3.8% |
| GPU/RayTracingScene | 1.53 | 2.0 | +30.7% |
| GPU/LumenScreenProbeGather | 0.44 | 0.42 | -4.5% |
| GPU/SkyAtmosphereEditor | 3.24 | 3.8 | +17.3% |
| GPU/Basepass | 0.4 | 0.49 | +22.5% |
| GPU/RenderDeferredLighting | 1.68 | 1.8 | +7.1% |
| GPU/ShadowDepths | 10.81 | 14.22 | +31.5% |
| GPU/LumenReflections | 2.64 | 5.18 | +96.2% |
| GPU/TranslucentLighting | 0.6 | 0.6 | +0.0% |
| GPU/Lights | 0.38 | 0.42 | +10.5% |
| GPU/ShadowProjection | 0.09 | 0.34 | +277.8% |
| GPU/DistanceFieldShadows | 1.2 | 0.74 | -38.3% |
| GPU/VolumetricFog | 1.22 | 1.05 | -13.9% |
| GPU/TemporalSuperResolution | 3.5 | 3.47 | -0.9% |
| GPU/SkyAtmosphere | 0.05 | 0.04 | -20.0% |
| GPU/Fog | 1.79 | 0.46 | -74.3% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.21 | 0.21 | +0.0% |
| GPU/Distortion | 0.06 | 0.06 | +0.0% |
| GPU/Postprocessing | 0.55 | 0.55 | +0.0% |
| GPU/VirtualTextureUpdate | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.53 | 0.5 | -5.7% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.0 | -100.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 1.25 | 0.84 | -32.8% |
| GPU/VolCloudReconstruction | 0.12 | 0.12 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.36 | 0.29 | -19.4% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Mixed: Render thread (CPU) and GPU**. After: **Mixed: Render thread (CPU) and GPU**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 14.36 | 19.01 | +32.4% |
| render | 44.25 | 50.98 | +15.2% |
| gpu | 40.82 | 46.63 | +14.2% |

## Verdict: worse

This change made performance worse. Recommend reverting to the baseline.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects

---
*The AI suggests. Measurements decide. The developer approves.*
