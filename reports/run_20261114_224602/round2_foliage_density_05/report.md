# FrameOptimizer report: foliage_density_05

## What changed

- `foliage.DensityScale`: 1.0 → 0.5

**Why the agent proposed it:** The render thread is the bottleneck: it is slowest in 91.8% of frames at 9.64 ms, versus 7.68 ms for the GPU. foliage.DensityScale is the only CPU lever not yet tried (HWRT off plus view distance 0.6 gave no clear change), so I'm going straight to 0.5 per the 150 fps target. Since the scene is CPU-bound, the gain may be small if foliage is not a major source of draw calls.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.77 | 10.0 | +2.4% |
| p95 frame time (ms) | 12.02 | 11.27 | -6.2% |
| Worst frame (ms) | 146.58 | 23.53 | -83.9% |
| Median FPS | 102.4 | 100.0 | -2.3% |

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
| GPU/BuildRenderingCommandsDeferred | 0.02 | 0.03 | +50.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.62 | 0.67 | +8.1% |
| GPU/NaniteBasePass | 0.95 | 0.96 | +1.1% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.01 | 0.02 | +100.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.25 | 0.24 | -4.0% |
| GPU/RayTracingScene | 0.33 | 0.31 | -6.1% |
| GPU/LumenScreenProbeGather | 0.01 | 0.02 | +100.0% |
| GPU/SkyAtmosphereEditor | 0.11 | 0.1 | -9.1% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.26 | 0.27 | +3.8% |
| GPU/ShadowDepths | 1.96 | 2.0 | +2.0% |
| GPU/LumenReflections | 0.29 | 0.35 | +20.7% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.21 | 0.02 | -90.5% |
| GPU/DistanceFieldShadows | 0.1 | 0.27 | +170.0% |
| GPU/VolumetricFog | 0.19 | 0.19 | +0.0% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.06 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.05 | 0.06 | +20.0% |
| GPU/Distortion | 0.02 | 0.03 | +50.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.2 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.01 | 0.44 | +4300.0% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.14 | 0.17 | +21.4% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 5.17 | 5.01 | -3.1% |
| render | 9.64 | 9.97 | +3.4% |
| gpu | 7.68 | 8.07 | +5.1% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `foliage.DensityScale`: Low at 0.75, medium at 0.5 (CPU lever): sparser grass and plants

---
*The AI suggests. Measurements decide. The developer approves.*
