# FrameOptimizer report: cpu_scene_cull_strong

## What changed

- `foliage.DensityScale`: 1.0 → 0.5
- `r.ViewDistanceScale`: 1.0 → 0.6
- `r.Shadow.DistanceScale`: 1.0 → 0.5

**Why the agent proposed it:** The render thread is the bottleneck in 99% of frames (render 9.99 ms vs GPU 8.06 ms). A milder batch (ViewDistance 0.8, ShadowDistance 0.75, LOD scales) gave no clear change (-0.9%), while the potato test reached 217 FPS, so this pushes the untried foliage density lever plus stronger draw-distance and shadow-distance culling. The goal is fewer draw calls and fewer shadow casters on the render thread.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.01 | 9.85 | -1.6% |
| p95 frame time (ms) | 11.47 | 11.24 | -2.0% |
| Worst frame (ms) | 23.01 | 21.93 | -4.7% |
| Median FPS | 99.9 | 101.5 | +1.6% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.0 | 0.01 | n/a |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.04 | 0.04 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.0 | 0.01 | n/a |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.67 | 0.68 | +1.5% |
| GPU/NaniteBasePass | 0.86 | 0.86 | +0.0% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.12 | 0.15 | +25.0% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.01 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.19 | 0.24 | +26.3% |
| GPU/RayTracingScene | 0.31 | 0.3 | -3.2% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.1 | +0.0% |
| GPU/Basepass | 0.08 | 0.09 | +12.5% |
| GPU/RenderDeferredLighting | 0.23 | 0.21 | -8.7% |
| GPU/ShadowDepths | 1.99 | 1.92 | -3.5% |
| GPU/LumenReflections | 0.24 | 0.25 | +4.2% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.07 | 0.06 | -14.3% |
| GPU/ShadowProjection | 0.02 | 0.2 | +900.0% |
| GPU/DistanceFieldShadows | 0.31 | 0.05 | -83.9% |
| GPU/VolumetricFog | 0.2 | 0.2 | +0.0% |
| GPU/TemporalSuperResolution | 0.56 | 0.54 | -3.6% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.07 | 0.07 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.25 | 0.13 | -48.0% |
| GPU/Distortion | 0.05 | 0.03 | -40.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.21 | +5.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.04 | 0.01 | -75.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.46 | 0.53 | +15.2% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.19 | +11.8% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.31 | 4.73 | +9.7% |
| render | 9.99 | 9.83 | -1.6% |
| gpu | 8.06 | 7.94 | -1.5% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `foliage.DensityScale`: Low at 0.75 up to severe at 0 (CPU lever): sparser grass and plants; 0 removes them
- `r.ViewDistanceScale`: Low to severe (CPU lever): distant objects stop drawing sooner; at 0.2 much of the scene pops in close to the camera
- `r.Shadow.DistanceScale`: Medium (CPU and GPU lever): shadows stop being drawn closer to the camera, so fewer objects are processed for shadows; distant objects lose their shadows

---
*The AI suggests. Measurements decide. The developer approves.*
