# FrameOptimizer report: shadow_quality_3

## What changed

- `r.ShadowQuality`: 5 → 3

**Why the agent proposed it:** GPU/ShadowDepths is the largest GPU pass at 9.68 ms, and the developer says this cartoony scene doesn't need shadows, so I'm dropping r.ShadowQuality straight to the lowest allowed value (3) instead of stepping to 4. Disabling VSM for CSM was already tried and made things 15.2% worse, so I'm keeping VSM on. The render thread is the bottleneck in 94.1% of frames (41.9 ms vs 38.68 ms GPU), so the frame-time gain will likely be small unless shadow work also eases the render thread.

## Results

Frames analyzed: 580 before, 580 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 41.92 | 40.29 | -3.9% |
| p95 frame time (ms) | 47.68 | 45.71 | -4.1% |
| Worst frame (ms) | 70.44 | 62.35 | -11.5% |
| Median FPS | 23.9 | 24.8 | +3.8% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.09 | 0.1 | +11.1% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.02 | 0.01 | -50.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.05 | 0.05 | +0.0% |
| GPU/VirtualTexture | 0.02 | 0.02 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.11 | 0.1 | -9.1% |
| GPU/NaniteVisBuffer | 1.79 | 1.77 | -1.1% |
| GPU/NaniteBasePass | 3.71 | 3.29 | -11.3% |
| GPU/HZB | 0.03 | 0.03 | +0.0% |
| GPU/BeginOcclusionTests | 0.09 | 0.09 | +0.0% |
| GPU/LightGrid | 0.02 | 0.02 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.16 | 0.15 | -6.3% |
| GPU/CaptureConvolveSkyEnvMap | 0.04 | 0.04 | +0.0% |
| GPU/LumenSceneUpdate | 0.42 | 0.36 | -14.3% |
| GPU/CompositionBeforeBasePass | 0.07 | 0.08 | +14.3% |
| GPU/RayTracingDynamicGeometry | 0.0 | 0.0 | n/a |
| GPU/RayTracingScene | 0.0 | 0.0 | n/a |
| GPU/LumenScreenProbeGather | 0.55 | 0.59 | +7.3% |
| GPU/SkyAtmosphereEditor | 1.79 | 1.9 | +6.1% |
| GPU/Basepass | 0.35 | 0.36 | +2.9% |
| GPU/RenderDeferredLighting | 1.55 | 1.55 | +0.0% |
| GPU/ShadowDepths | 9.68 | 9.3 | -3.9% |
| GPU/LumenReflections | 2.46 | 2.51 | +2.0% |
| GPU/TranslucentLighting | 0.6 | 0.59 | -1.7% |
| GPU/Lights | 0.31 | 0.35 | +12.9% |
| GPU/ShadowProjection | 0.09 | 0.09 | +0.0% |
| GPU/DistanceFieldShadows | 1.19 | 1.22 | +2.5% |
| GPU/VolumetricFog | 1.24 | 1.24 | +0.0% |
| GPU/TemporalSuperResolution | 3.5 | 3.46 | -1.1% |
| GPU/SkyAtmosphere | 0.05 | 0.05 | +0.0% |
| GPU/Fog | 1.79 | 1.81 | +1.1% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.2 | 0.23 | +15.0% |
| GPU/Distortion | 0.05 | 0.05 | +0.0% |
| GPU/Postprocessing | 0.54 | 0.54 | +0.0% |
| GPU/VirtualTextureUpdate | 0.02 | 0.02 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.52 | 0.5 | -3.8% |
| GPU/GlobalDistanceFieldUpdate | 0.75 | 0.56 | -25.3% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.03 | 0.04 | +33.3% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/LumenSceneLighting | 0.7 | 0.71 | +1.4% |
| GPU/VolumetricCloud | 1.23 | 1.44 | +17.1% |
| GPU/VolCloudReconstruction | 0.12 | 0.12 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.38 | 0.38 | +0.0% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Mixed: Render thread (CPU) and GPU**. After: **Mixed: Render thread (CPU) and GPU**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 12.55 | 12.92 | +2.9% |
| render | 41.9 | 40.25 | -3.9% |
| gpu | 38.68 | 37.83 | -2.2% |

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.ShadowQuality`: Medium: shadows get softer and less precise

---
*The AI suggests. Measurements decide. The developer approves.*
