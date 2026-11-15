# FrameOptimizer report: foliage_density_0p5

## What changed

- `foliage.DensityScale`: 1.0 → 0.5

**Why the agent proposed it:** The render thread is the bottleneck in 93.8% of frames (10.05 ms render vs 8.14 ms GPU), so only CPU levers can move frame time. Foliage density is an untried CPU lever, and halving it cuts foliage instances and draw calls; I am jumping straight to 0.5 because you asked for drastic changes toward 150 fps. Even so, expect only a modest gain, since ViewDistanceScale 0.8 tried together with software ray tracing gave just -2.6%.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.1 | 10.05 | -0.5% |
| p95 frame time (ms) | 11.63 | 11.53 | -0.9% |
| Worst frame (ms) | 137.05 | 134.06 | -2.2% |
| Median FPS | 99.0 | 99.5 | +0.5% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.05 | 0.04 | -20.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.04 | 0.04 | +0.0% |
| GPU/NaniteVisBuffer | 0.68 | 0.69 | +1.5% |
| GPU/NaniteBasePass | 0.97 | 0.94 | -3.1% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.25 | 0.24 | -4.0% |
| GPU/RayTracingScene | 0.33 | 0.31 | -6.1% |
| GPU/LumenScreenProbeGather | 0.01 | 0.02 | +100.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.1 | +0.0% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.28 | 0.24 | -14.3% |
| GPU/ShadowDepths | 2.02 | 1.99 | -1.5% |
| GPU/LumenReflections | 0.35 | 0.28 | -20.0% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.03 | 0.23 | +666.7% |
| GPU/DistanceFieldShadows | 0.28 | 0.06 | -78.6% |
| GPU/VolumetricFog | 0.19 | 0.2 | +5.3% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.07 | +16.7% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.06 | 0.07 | +16.7% |
| GPU/Distortion | 0.03 | 0.03 | +0.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.21 | +5.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.46 | 0.45 | -2.2% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.2 | +17.6% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.98 | 4.97 | -0.2% |
| render | 10.05 | 10.01 | -0.4% |
| gpu | 8.14 | 8.06 | -1.0% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `foliage.DensityScale`: Low at 0.75, medium at 0.5 (CPU lever): sparser grass and plants

---
*The AI suggests. Measurements decide. The developer approves.*
