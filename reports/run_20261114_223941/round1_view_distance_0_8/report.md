# FrameOptimizer report: view_distance_0_8

## What changed

- `r.ViewDistanceScale`: 1.0 → 0.8

**Why the agent proposed it:** The scene is render-thread bound (render 10.35 ms vs GPU 8.16 ms, render slowest in 92.1% of frames), so GPU-only settings won't help much. ViewDistanceScale 0.8 is the lowest-cost CPU lever and cuts draw calls and visibility work on the render thread. The gain toward the 150 fps (6.67 ms) target will likely be modest.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.45 | 10.08 | -3.5% |
| p95 frame time (ms) | 14.03 | 11.96 | -14.8% |
| Worst frame (ms) | 147.86 | 134.84 | -8.8% |
| Median FPS | 95.7 | 99.2 | +3.7% |

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
| GPU/RenderVelocities | 0.03 | 0.03 | +0.0% |
| GPU/NaniteVisBuffer | 0.67 | 0.67 | +0.0% |
| GPU/NaniteBasePass | 0.99 | 0.97 | -2.0% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.24 | 0.25 | +4.2% |
| GPU/RayTracingScene | 0.34 | 0.33 | -2.9% |
| GPU/LumenScreenProbeGather | 0.02 | 0.01 | -50.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.1 | +0.0% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.27 | 0.27 | +0.0% |
| GPU/ShadowDepths | 2.0 | 2.0 | +0.0% |
| GPU/LumenReflections | 0.33 | 0.34 | +3.0% |
| GPU/TranslucentLighting | 0.09 | 0.09 | +0.0% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.03 | 0.21 | +600.0% |
| GPU/DistanceFieldShadows | 0.27 | 0.13 | -51.9% |
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
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.21 | +5.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.02 | 0.01 | -50.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.47 | 0.46 | -2.1% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.13 | 0.17 | +30.8% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 5.95 | 5.1 | -14.3% |
| render | 10.35 | 10.01 | -3.3% |
| gpu | 8.16 | 8.1 | -0.7% |

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.ViewDistanceScale`: Low to medium (CPU lever): small distant objects stop drawing sooner and may pop in closer

---
*The AI suggests. Measurements decide. The developer approves.*
