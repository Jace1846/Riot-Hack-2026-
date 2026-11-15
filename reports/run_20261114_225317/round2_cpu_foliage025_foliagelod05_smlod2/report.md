# FrameOptimizer report: cpu_foliage025_foliagelod05_smlod2

## What changed

- `foliage.DensityScale`: 1.0 → 0.25
- `foliage.LODDistanceScale`: 1.0 → 0.5
- `r.StaticMeshLODDistanceScale`: 1.0 → 2.0

**Why the agent proposed it:** The render thread is the bottleneck in 97.7% of frames (9.82 ms vs 7.97 ms GPU), and 150 FPS needs 6.67 ms, a gap of about 32%. Hardware ray tracing off, view distance and shadow distance gave no clear change, so this tries the remaining untested CPU levers at their strongest values (foliage density 0.25, foliage LOD distance 0.5, static mesh LOD distance 2.0). Even if this works, the GPU at 7.97 ms would still sit above the 6.67 ms target, so 150 FPS likely also needs GPU cuts and may be out of reach with the approved settings.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.84 | 9.89 | +0.5% |
| p95 frame time (ms) | 11.2 | 11.73 | +4.7% |
| Worst frame (ms) | 22.77 | 138.58 | +508.6% |
| Median FPS | 101.7 | 101.1 | -0.6% |

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
| GPU/RenderVelocities | 0.03 | 0.03 | +0.0% |
| GPU/NaniteVisBuffer | 0.67 | 0.65 | -3.0% |
| GPU/NaniteBasePass | 0.94 | 0.94 | +0.0% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.15 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.24 | 0.24 | +0.0% |
| GPU/RayTracingScene | 0.33 | 0.3 | -9.1% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.11 | 0.1 | -9.1% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.26 | 0.24 | -7.7% |
| GPU/ShadowDepths | 2.03 | 1.92 | -5.4% |
| GPU/LumenReflections | 0.3 | 0.36 | +20.0% |
| GPU/TranslucentLighting | 0.08 | 0.09 | +12.5% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.02 | 0.2 | +900.0% |
| GPU/DistanceFieldShadows | 0.27 | 0.08 | -70.4% |
| GPU/VolumetricFog | 0.19 | 0.19 | +0.0% |
| GPU/TemporalSuperResolution | 0.54 | 0.54 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.06 | 0.06 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.15 | 0.06 | -60.0% |
| GPU/Distortion | 0.03 | 0.03 | +0.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.2 | 0.2 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/VolumetricCloud | 0.41 | 0.47 | +14.6% |
| GPU/VolCloudReconstruction | 0.02 | 0.02 | +0.0% |
| GPU/VolCloudComposeOverScene | 0.18 | 0.16 | -11.1% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.77 | 5.1 | +6.9% |
| render | 9.82 | 9.82 | +0.0% |
| gpu | 7.97 | 7.94 | -0.4% |

## Verdict: no clear change

No clear performance gain, so it isn't worth the visual cost. Recommend keeping the baseline.

## Visual trade-off

- `foliage.DensityScale`: Low at 0.75, medium at 0.5, high at 0.25 (CPU lever): sparser grass and plants
- `foliage.LODDistanceScale`: Low (CPU lever): plants switch to simpler models closer to the camera
- `r.StaticMeshLODDistanceScale`: Low (CPU lever): non-Nanite meshes switch to simpler models sooner (higher = simpler sooner)

---
*The AI suggests. Measurements decide. The developer approves.*
