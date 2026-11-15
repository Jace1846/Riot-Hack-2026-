# FrameOptimizer report: vsm_off_csm2_res1024

## What changed

- `r.Shadow.Virtual.Enable`: 1 → 0
- `r.Shadow.CSM.MaxCascades`: 4 → 2
- `r.Shadow.MaxResolution`: 2048 → 1024

**Why the agent proposed it:** The render thread is the bottleneck (9.82 ms, slowest in 97.7% of frames), and both strong CPU-lever combos made no clear change (+1.3% and +0.5%), so this tries the shadow path instead: ShadowDepths is the largest GPU pass at 2.03 ms, and swapping Virtual Shadow Maps for 2 cascades at 1024 may cut shadow setup work. Reaching 150 FPS (6.67 ms) needs about 3.2 ms off the render thread, which is likely out of reach with the approved settings, and cascaded shadows could even add draw calls.

## Results

Frames analyzed: 1140 before, 1140 after.

| Metric | Before | After | Change |
|---|---|---|---|
| Median frame time (ms) | 9.84 | 11.17 | +13.5% |
| p95 frame time (ms) | 11.2 | 12.96 | +15.7% |
| Worst frame (ms) | 22.77 | 143.79 | +531.5% |
| Median FPS | 101.7 | 89.5 | -12.0% |

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
| GPU/NaniteVisBuffer | 0.67 | 0.69 | +3.0% |
| GPU/NaniteBasePass | 0.94 | 0.99 | +5.3% |
| GPU/HZB | 0.01 | 0.01 | +0.0% |
| GPU/BeginOcclusionTests | 0.02 | 0.02 | +0.0% |
| GPU/LightGrid | 0.01 | 0.01 | +0.0% |
| GPU/LightFunctionAtlasGeneration | 0.0 | 0.0 | n/a |
| GPU/SkyAtmosphereLUTs | 0.06 | 0.06 | +0.0% |
| GPU/CaptureConvolveSkyEnvMap | 0.02 | 0.02 | +0.0% |
| GPU/LumenSceneUpdate | 0.15 | 0.16 | +6.7% |
| GPU/CompositionBeforeBasePass | 0.02 | 0.02 | +0.0% |
| GPU/RayTracingDynamicGeometry | 0.24 | 0.25 | +4.2% |
| GPU/RayTracingScene | 0.33 | 0.34 | +3.0% |
| GPU/LumenScreenProbeGather | 0.01 | 0.01 | +0.0% |
| GPU/SkyAtmosphereEditor | 0.11 | 0.1 | -9.1% |
| GPU/Basepass | 0.09 | 0.09 | +0.0% |
| GPU/RenderDeferredLighting | 0.26 | 0.26 | +0.0% |
| GPU/ShadowDepths | 2.03 | 2.89 | +42.4% |
| GPU/LumenReflections | 0.3 | 0.37 | +23.3% |
| GPU/TranslucentLighting | 0.08 | 0.09 | +12.5% |
| GPU/Lights | 0.06 | 0.06 | +0.0% |
| GPU/ShadowProjection | 0.02 | 0.05 | +150.0% |
| GPU/DistanceFieldShadows | 0.27 | 0.3 | +11.1% |
| GPU/VolumetricFog | 0.19 | 0.17 | -10.5% |
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
| GPU/VolCloudComposeOverScene | 0.18 | 0.17 | -5.6% |
| GPU/BuildRenderingCommands | 0.0 | 0.0 | n/a |

### CPU vs GPU bottleneck

Before: **Render thread (CPU)**. After: **Render thread (CPU)**.

| Part (median ms) | Before | After | Change |
|---|---|---|---|
| game | 4.77 | 5.25 | +10.1% |
| render | 9.82 | 11.09 | +12.9% |
| gpu | 7.97 | 9.16 | +14.9% |

## Verdict: worse

This change made performance worse. Recommend reverting to the baseline.

## Visual trade-off

- `r.Shadow.Virtual.Enable`: Medium (GPU lever): swaps Virtual Shadow Maps for older cascaded shadows; distant shadows get softer. The r.Shadow.MaxResolution and CSM settings only take effect when this is 0
- `r.Shadow.CSM.MaxCascades`: Less shadow detail on distant objects
- `r.Shadow.MaxResolution`: Blurrier, more pixelated shadow edges

---
*The AI suggests. Measurements decide. The developer approves.*
