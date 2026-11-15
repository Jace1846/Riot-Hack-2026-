# FrameOptimizer report: cpu_render_thread_batch

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.Shadow.DistanceScale`: 1.0 → 0.75
- `r.ViewDistanceScale`: 1.0 → 0.8
- `foliage.LODDistanceScale`: 1.0 → 0.75
- `r.StaticMeshLODDistanceScale`: 1.0 → 1.5

**Why the agent proposed it:** The render thread takes 9.99 ms and is the slowest part in 99% of frames (GPU 8.06 ms), so this targets CPU levers. Hardware RT scene building (RayTracingScene 0.31 + DynamicGeometry 0.19 ms GPU, plus its render-thread work), shadow casters (ShadowDepths 1.99 ms) and draw distance all add render-thread cost. The potato test showed up to -54% is available, so this combines moderate steps of the lower-cost CPU levers rather than the severe ones.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.01 | 9.92 | -0.9% |
| p95 frame time (ms) | 11.47 | 11.42 | -0.4% |
| Worst frame (ms) | 23.01 | 22.33 | -3.0% |
| Median FPS | 99.9 | 100.8 | +0.9% |

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
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.02 | -33.3% |
| GPU/VirtualTexture | 0.0 | 0.01 | n/a |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.04 | +33.3% |
| GPU/NaniteVisBuffer | 0.67 | 0.7 | +4.5% |
| GPU/NaniteBasePass | 0.86 | 0.46 | -46.5% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.12 | 0.15 | +25.0% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.02 | +100.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.08 | +700.0% |
| GPU/SkyAtmosphereEditor | 0.1 | 0.03 | -70.0% |
| GPU/Basepass | 0.08 | 0.34 | +325.0% |
| GPU/RenderDeferredLighting | 0.23 | 0.27 | +17.4% |
| GPU/ShadowDepths | 1.99 | 1.76 | -11.6% |
| GPU/LumenReflections | 0.24 | 0.54 | +125.0% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.07 | 0.17 | +142.9% |
| GPU/ShadowProjection | 0.02 | 0.23 | +1050.0% |
| GPU/DistanceFieldShadows | 0.31 | 0.06 | -80.6% |
| GPU/VolumetricFog | 0.2 | 0.2 | +0.0% |
| GPU/TemporalSuperResolution | 0.56 | 0.54 | -3.6% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.07 | 0.08 | +14.3% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.25 | 0.08 | -68.0% |
| GPU/Distortion | 0.05 | 0.03 | -40.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.17 | -15.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.04 | 0.01 | -75.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.46 | 0.51 | +10.9% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.17 | 0.2 | +17.6% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.31 | 4.69 | +8.8% |
| render | 9.99 | 9.91 | -0.8% |
| gpu | 8.06 | 8.19 | +1.6% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate
- `r.Shadow.DistanceScale`: Medium (CPU and GPU lever): shadows stop being drawn closer to the camera, so fewer objects are processed for shadows; distant objects lose their shadows
- `r.ViewDistanceScale`: Low to severe (CPU lever): distant objects stop drawing sooner; at 0.2 much of the scene pops in close to the camera
- `foliage.LODDistanceScale`: Low (CPU lever): plants switch to simpler models closer to the camera
- `r.StaticMeshLODDistanceScale`: Low (CPU lever): non-Nanite meshes switch to simpler models sooner (higher = simpler sooner)

---
*The AI suggests. Measurements decide. The developer approves.*
