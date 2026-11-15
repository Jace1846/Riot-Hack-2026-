# FrameOptimizer report: cpu_shadow_lumen_cut_150fps

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2
- `r.Shadow.MaxResolution`: 2048 → 1024
- `r.Lumen.DiffuseIndirect.Allow`: 1 → 0
- `r.SkeletalMeshLODBias`: 0 → 1

**Why the agent proposed it:** The frame is render-thread bound (render 8.28 ms vs GPU 6.68 ms, slowest in 99.6% of frames), and every CPU lever is already at its minimum. The target needs about a 20% cut (8.31 ms to 6.67 ms), and the potato test reached 169 FPS, so the remaining render-thread savings must come from shadow and Lumen setup. This change swaps Virtual Shadow Maps for cheaper CSM (2 cascades, 1024) to cut shadow setup work and the top GPU pass (ShadowDepths at 1.69 ms). It also turns off Lumen GI to drop Lumen scene update work, which will flatten bounced light, and lowers character LOD. Resolution and post-process settings stay unchanged because the GPU is not the limit.

## Results

Frames analyzed: 540 before, 540 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 8.31 | 6.82 | -17.9% |
| p95 frame time (ms) | 9.16 | 7.38 | -19.4% |
| Worst frame (ms) | 10.51 | 8.03 | -23.6% |
| Median FPS | 120.3 | 146.6 | +21.9% |

### GPU passes (median ms)

| Pass | Before | After | Change |
|---|---|---|---|
| GPU/RayTracingGeometry | 0.0 | 0.0 | n/a |
| GPU/DistanceFields | 0.03 | 0.03 | +0.0% |
| GPU/GlobalDistanceFieldUpdate | 0.17 | 0.08 | -52.9% |
| GPU/AllocateRendertargets | 0.0 | 0.0 | n/a |
| GPU/NiagaraGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/NiagaraStatelessGPUSimulation | 0.01 | 0.01 | +0.0% |
| GPU/VisibilityCommands | 0.0 | 0.0 | n/a |
| GPU/GPUSceneUpdate | 0.01 | 0.01 | +0.0% |
| GPU/NaniteStreaming | 0.0 | 0.0 | n/a |
| GPU/NaniteReadback | 0.01 | 0.03 | +200.0% |
| GPU/NiagaraGPUComputeFreeIDs | 0.0 | 0.0 | n/a |
| GPU/FXSystemPreRender | 0.0 | 0.0 | n/a |
| GPU/BuildRenderingCommandsDeferred | 0.03 | 0.03 | +0.0% |
| GPU/VirtualTexture | 0.01 | 0.01 | +0.0% |
| GPU/Prepass | 0.0 | 0.0 | n/a |
| GPU/RenderVelocities | 0.04 | 0.04 | +0.0% |
| GPU/NaniteVisBuffer | 0.61 | 0.61 | +0.0% |
| GPU/NaniteBasePass | 0.47 | 0.42 | -10.6% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.01 | 0.01 | +0.0% |
| GPU/CompositionBeforeBasePass | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.03 | 0.03 | +0.0% |
| GPU/Basepass | 0.21 | 0.05 | -76.2% |
| GPU/RenderDeferredLighting | 0.44 | 0.15 | -65.9% |
| GPU/ShadowDepths | 1.69 | 1.68 | -0.6% |
| GPU/ScreenSpaceReflections | 0.07 | 0.02 | -71.4% |
| GPU/TranslucentLighting | 0.09 | 0.08 | -11.1% |
| GPU/Lights | 0.17 | 0.05 | -70.6% |
| GPU/ShadowProjection | 0.31 | 0.03 | -90.3% |
| GPU/TemporalSuperResolution | 0.55 | 0.55 | +0.0% |
| GPU/SkyAtmosphere | 0.01 | 0.01 | +0.0% |
| GPU/Fog | 0.01 | 0.01 | +0.0% |
| GPU/LocalFogVolumeVolumes | 0.01 | 0.01 | +0.0% |
| GPU/PostRenderOpsFX | 0.0 | 0.0 | n/a |
| GPU/FXSystemPostRenderOpaque | 0.0 | 0.0 | n/a |
| GPU/Translucency | 0.31 | 0.29 | -6.5% |
| GPU/Distortion | 0.05 | 0.05 | +0.0% |
| GPU/Postprocessing | 0.13 | 0.13 | +0.0% |
| GPU/VirtualTextureUpdate | 0.01 | 0.01 | +0.0% |
| GPU/SlateUI | 0.01 | 0.01 | +0.0% |
| GPU/Unaccounted | 0.15 | 0.13 | -13.3% |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 3.95 | 3.67 | -7.1% |
| render | 8.28 | 6.82 | -17.6% |
| gpu | 6.68 | 5.27 | -21.1% |

## Verdict: improved

Measurements support keeping this change. Check the visual trade-off below before approving.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects
- `r.Shadow.MaxResolution`: Blurrier, more pixelated shadow edges
- `r.Lumen.DiffuseIndirect.Allow`: Severe (GPU lever): turns off Lumen global illumination; bounced light disappears and shaded areas get flat and dark
- `r.SkeletalMeshLODBias`: Low: characters use lower levels of detail

---
*The AI suggests. Measurements decide. The developer approves.*
