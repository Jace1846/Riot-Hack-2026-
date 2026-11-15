# FrameOptimizer report: view_distance_0_6

## What changed

- `r.ViewDistanceScale`: 0.8 → 0.6

**Why the agent proposed it:** The render thread is the bottleneck (10.01 ms, slowest in 93% of frames, while the GPU sits at 8.1 ms), and the previous view-distance step from 1.0 to 0.8 cut the median by 3.5%. Dropping to 0.6 is the next CPU lever with low-to-medium visual cost. Expect a gain of a few percent at most, far short of the 6.7 ms needed for 150 fps, so heavier CPU levers like disabling hardware ray tracing will likely be needed next.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.08 | 10.0 | -0.8% |
| p95 frame time (ms) | 11.96 | 11.37 | -4.9% |
| Worst frame (ms) | 134.84 | 22.89 | -83.0% |
| Median FPS | 99.2 | 100.0 | +0.8% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.05 | 0.05 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.67 | 0.67 | +0.0% |
| GPU/NaniteBasePass | 0.97 | 0.96 | -1.0% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.25 | 0.25 | +0.0% |
| GPU/RayTracingScene | 0.33 | 0.33 | +0.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.1 | +0.0% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.27 | 0.24 | -11.1% |
| GPU/ShadowDepths | 2.0 | 2.02 | +1.0% |
| GPU/LumenReflections | 0.34 | 0.28 | -17.6% |
| GPU/TranslucentLighting | 0.09 | 0.09 | +0.0% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.21 | 0.19 | -9.5% |
| GPU/DistanceFieldShadows | 0.13 | 0.12 | -7.7% |
| GPU/VolumetricFog | 0.19 | 0.19 | +0.0% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.06 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.06 | 0.06 | +0.0% |
| GPU/Distortion | 0.03 | 0.03 | +0.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.21 | 0.21 | +0.0% |
| GPU/VolumetricCloud | 0.46 | 0.44 | -4.3% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.18 | +5.9% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 5.1 | 5.12 | +0.4% |
| render | 10.01 | 9.95 | -0.6% |
| gpu | 8.1 | 8.08 | -0.2% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.ViewDistanceScale`: Low to medium (CPU lever): small distant objects stop drawing sooner and may pop in closer

---
*The AI suggests. Measurements decide. The developer approves.*
