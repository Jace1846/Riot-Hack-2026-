# FrameOptimizer report: shadow_quality_3

## What changed

- `r.ShadowQuality`: 5 → 3

**Why the agent proposed it:** ShadowDepths is the largest GPU pass at 10.77 ms, and you said this cartoony scene does not need shadows, so this jumps straight to the lowest allowed shadow quality (3) rather than stepping to 4. The render thread is the slowest part in 99.7% of frames (43.42 ms vs GPU 39.74 ms), so the frame-time gain may be small, and 100 FPS (10 ms) is far beyond what one setting can deliver.

## Results

Frames analyzed: 580 before, 580 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 43.45 | 43.12 | -0.8% |
| p95 frame time (ms) | 46.82 | 45.68 | -2.4% |
| Worst frame (ms) | 56.5 | 51.56 | -8.7% |
| Median FPS | 23.0 | 23.2 | +0.9% |

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
| GPU/BuildRenderingCommandsDeferred | 0.08 | 0.08 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.1 | 0.1 | +0.0% |
| GPU/NaniteVisBuffer | 1.85 | 1.83 | -1.1% |
| GPU/NaniteBasePass | 2.41 | 2.37 | -1.7% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.1 | 0.1 | +0.0% |
| GPU/LightGrid | 0.02 | 0.02 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.16 | 0.15 | -6.3% |
| GPU/CaptureConvolveSkyEnvMap | 0.04 | 0.04 | +0.0% |
| GPU/LumenSceneUpdate | 0.2 | 0.19 | -5.0% |
| GPU/CompositionBeforeBasePass | 0.03 | 0.04 | +33.3% |
| GPU/RayTracingDynamicGeometry | 0.94 | 0.92 | -2.1% |
| GPU/RayTracingScene | 1.2 | 1.19 | -0.8% |
| GPU/LumenScreenProbeGather | 0.39 | 0.4 | +2.6% |
| GPU/SkyAtmosphereEditor | 2.21 | 2.18 | -1.4% |
| GPU/Basepass | 0.22 | 0.22 | +0.0% |
| GPU/RenderDeferredLighting | 1.7 | 1.69 | -0.6% |
| GPU/ShadowDepths | 10.77 | 10.77 | +0.0% |
| GPU/LumenReflections | 1.58 | 1.53 | -3.2% |
| GPU/TranslucentLighting | 0.6 | 0.59 | -1.7% |
| GPU/Lights | 0.45 | 0.45 | +0.0% |
| GPU/ShadowProjection | 0.08 | 0.08 | +0.0% |
| GPU/DistanceFieldShadows | 1.74 | 1.73 | -0.6% |
| GPU/VolumetricFog | 1.25 | 1.23 | -1.6% |
| GPU/TemporalSuperResolution | 3.47 | 3.46 | -0.3% |
| GPU/SkyAtmosphere | 0.05 | 0.05 | +0.0% |
| GPU/Fog | 1.8 | 1.79 | -0.6% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 1.35 | 1.34 | -0.7% |
| GPU/Distortion | 0.32 | 0.32 | +0.0% |
| GPU/Postprocessing | 0.55 | 0.55 | +0.0% |
| GPU/VirtualTextureUpdate | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.49 | 0.5 | +2.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 1.47 | 1.47 | +0.0% |
| GPU/VolCloudReconstruction | 0.12 | 0.11 | -8.3% |
| GPU/VolCloudComposeOverScene | 0.42 | 0.41 | -2.4% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Mixed: Render thread (CPU) and GPU**. After: **Mixed: Render thread (CPU) and GPU**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 10.59 | 10.61 | +0.2% |
| render | 43.42 | 43.07 | -0.8% |
| gpu | 39.74 | 39.39 | -0.9% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.ShadowQuality`: Medium: shadows get softer and less precise

---
*The AI suggests. Measurements decide. The developer approves.*
