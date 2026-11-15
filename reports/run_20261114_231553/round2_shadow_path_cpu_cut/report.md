# FrameOptimizer report: shadow_path_cpu_cut

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2
- `r.DistanceFieldShadowing`: 1 → 0

**Why the agent proposed it:** The frame is render-thread bound (render 9.99 ms vs GPU 8.06 ms, slowest in 99% of frames), and the potato test shows a 54% ceiling, but the distance/LOD/HWRT batch gave only -0.9%. Shadow setup is the next likely render-thread cost, and ShadowDepths is also the largest GPU pass at 1.99 ms, so this swaps Virtual Shadow Maps for 2-cascade CSM and drops distance field shadows (0.31 ms GPU) to test that hypothesis.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.01 | 10.39 | +3.8% |
| p95 frame time (ms) | 11.47 | 11.79 | +2.8% |
| Worst frame (ms) | 23.01 | 21.47 | -6.7% |
| Median FPS | 99.9 | 96.3 | -3.6% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.0 | 0.01 | n/a |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.04 | 0.05 | +25.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.0 | 0.01 | n/a |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.67 | 0.7 | +4.5% |
| GPU/NaniteBasePass | 0.86 | 0.87 | +1.2% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.12 | 0.15 | +25.0% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.02 | +100.0% |
| GPU/RayTracingDynamicGeometry | 0.19 | 0.25 | +31.6% |
| GPU/RayTracingScene | 0.31 | 0.32 | +3.2% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.1 | +0.0% |
| GPU/Basepass | 0.08 | 0.1 | +25.0% |
| GPU/RenderDeferredLighting | 0.23 | 0.2 | -13.0% |
| GPU/ShadowDepths | 1.99 | 2.81 | +41.2% |
| GPU/LumenReflections | 0.24 | 0.25 | +4.2% |
| GPU/TranslucentLighting | 0.09 | 0.09 | +0.0% |
| GPU/Lights | 0.07 | 0.05 | -28.6% |
| GPU/ShadowProjection | 0.02 | 0.04 | +100.0% |
| GPU/DistanceFieldShadows | 0.31 | 0.0 | -100.0% |
| GPU/VolumetricFog | 0.2 | 0.17 | -15.0% |
| GPU/TemporalSuperResolution | 0.56 | 0.54 | -3.6% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.07 | 0.07 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.25 | 0.11 | -56.0% |
| GPU/Distortion | 0.05 | 0.03 | -40.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.2 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.04 | 0.01 | -75.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.46 | 0.51 | +10.9% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.21 | +23.5% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.31 | 4.71 | +9.3% |
| render | 9.99 | 10.37 | +3.8% |
| gpu | 8.06 | 8.53 | +5.8% |

## Verdict: worse

This change made performance worse. Recommend reverting to the baseline.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects
- `r.DistanceFieldShadowing`: Medium (GPU lever): removes distance field shadows (soft shadows from distant objects)

---
*The AI suggests. Measurements decide. The developer approves.*
