# FrameOptimizer report: cpu_levers_combo_150fps

## What changed

- `r.Lumen.HardwareRayTracing`: 1 → 0
- `r.ViewDistanceScale`: 1.0 → 0.6
- `foliage.DensityScale`: 1.0 → 0.5
- `foliage.LODDistanceScale`: 1.0 → 0.5
- `r.StaticMeshLODDistanceScale`: 1.0 → 2.0
- `r.Shadow.DistanceScale`: 1.0 → 0.5

**Why the agent proposed it:** The frame is render-thread bound (render 10.02 ms, slowest in 98.7% of frames). Reaching 150 FPS (6.67 ms) needs about a 34% cut, close to the potato ceiling of -41%. So this stacks the CPU levers that cut draw, shadow and ray-tracing scene work (RayTracingScene + DynamicGeometry 0.56 ms, ShadowDepths 1.96 ms). It leaves out the GPU-only settings, which cannot help this frame, but the target may still sit at the edge of what these settings can buy.

## Results

Frames analyzed: 540 before, 540 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 10.04 | 9.6 | -4.4% |
| p95 frame time (ms) | 11.44 | 10.84 | -5.2% |
| Worst frame (ms) | 29.14 | 11.65 | -60.0% |
| Median FPS | 99.6 | 104.1 | +4.5% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.04 | 0.04 | +0.0% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/UpdateLumenSceneBuffers | 0.01 | 0.01 | +0.0% |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.03 | 0.03 | +0.0% |
| GPU/NaniteVisBuffer | 0.67 | 0.68 | +1.5% |
| GPU/NaniteBasePass | 0.86 | 0.47 | -45.3% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.13 | 0.11 | -15.4% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.01 | +0.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.08 | +700.0% |
| GPU/SkyAtmosphereEditor | 0.12 | 0.03 | -75.0% |
| GPU/Basepass | 0.09 | 0.21 | +133.3% |
| GPU/RenderDeferredLighting | 0.23 | 0.27 | +17.4% |
| GPU/ShadowDepths | 1.96 | 1.64 | -16.3% |
| GPU/LumenReflections | 0.25 | 0.56 | +124.0% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.06 | 0.19 | +216.7% |
| GPU/ShadowProjection | 0.23 | 0.29 | +26.1% |
| GPU/DistanceFieldShadows | 0.08 | 0.1 | +25.0% |
| GPU/VolumetricFog | 0.2 | 0.2 | +0.0% |
| GPU/TemporalSuperResolution | 0.55 | 0.56 | +1.8% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.07 | 0.1 | +42.9% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.24 | 0.25 | +4.2% |
| GPU/Distortion | 0.04 | 0.04 | +0.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.21 | 0.17 | -19.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.5 | 0.47 | -6.0% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.2 | 0.17 | -15.0% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.62 | 3.86 | -16.5% |
| render | 10.02 | 9.59 | -4.3% |
| gpu | 8.11 | 7.89 | -2.7% |

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.Lumen.HardwareRayTracing`: Medium (CPU and GPU lever): Lumen switches from hardware ray tracing to cheaper software tracing; lighting and reflections get slightly less accurate
- `r.ViewDistanceScale`: Low to severe (CPU lever): distant objects stop drawing sooner; at 0.2 much of the scene pops in close to the camera
- `foliage.DensityScale`: Low at 0.75 up to severe at 0 (CPU lever): sparser grass and plants; 0 removes them
- `foliage.LODDistanceScale`: Low (CPU lever): plants switch to simpler models closer to the camera
- `r.StaticMeshLODDistanceScale`: Low (CPU lever): non-Nanite meshes switch to simpler models sooner (higher = simpler sooner)
- `r.Shadow.DistanceScale`: Medium (CPU and GPU lever): shadows stop being drawn closer to the camera, so fewer objects are processed for shadows; distant objects lose their shadows

---
*The AI suggests. Measurements decide. The developer approves.*
