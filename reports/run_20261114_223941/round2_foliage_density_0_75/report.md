# FrameOptimizer report: foliage_density_0_75

## What changed

- `foliage.DensityScale`: 1.0 → 0.75

**Why the agent proposed it:** The render thread limits 93% of frames (render 10.01 ms vs GPU 8.1 ms), so GPU-only settings won't help. Foliage density is a low-cost CPU lever that cuts draw and instance work on the render thread. Expect a modest gain, well short of the 6.67 ms needed for 150 fps.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.08 | 10.01 | -0.7% |
| p95 frame time (ms) | 11.96 | 11.78 | -1.5% |
| Worst frame (ms) | 134.84 | 137.32 | +1.8% |
| Median FPS | 99.2 | 99.9 | +0.7% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.05 | 0.04 | -20.0% |
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
| GPU/RenderVelocities | 0.03 | 0.03 | +0.0% |
| GPU/NaniteVisBuffer | 0.67 | 0.66 | -1.5% |
| GPU/NaniteBasePass | 0.97 | 0.97 | +0.0% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.25 | 0.25 | +0.0% |
| GPU/RayTracingScene | 0.33 | 0.32 | -3.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.11 | +10.0% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.27 | 0.28 | +3.7% |
| GPU/ShadowDepths | 2.0 | 2.04 | +2.0% |
| GPU/LumenReflections | 0.34 | 0.3 | -11.8% |
| GPU/TranslucentLighting | 0.09 | 0.09 | +0.0% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.21 | 0.21 | +0.0% |
| GPU/DistanceFieldShadows | 0.13 | 0.14 | +7.7% |
| GPU/VolumetricFog | 0.19 | 0.19 | +0.0% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.06 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.06 | 0.05 | -16.7% |
| GPU/Distortion | 0.03 | 0.02 | -33.3% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.21 | 0.2 | -4.8% |
| GPU/VolumetricCloud | 0.46 | 0.44 | -4.3% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.17 | +0.0% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 5.1 | 5.01 | -1.8% |
| render | 10.01 | 9.94 | -0.7% |
| gpu | 8.1 | 8.05 | -0.6% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `foliage.DensityScale`: Low at 0.75, medium at 0.5 (CPU lever): sparser grass and plants

---
*The AI suggests. Measurements decide. The developer approves.*
