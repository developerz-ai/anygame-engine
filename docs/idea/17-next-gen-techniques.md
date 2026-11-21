# 🚀 17. Next-gen techniques

What to adopt beyond [rendering](06-rendering.md), [world](07-world.md) and [simulation](08-simulation.md), and what to wrap instead of build. As of 2026-11.

**Evidence level:** technique claims come from search-result extracts of the linked pages, not full reads. Library license, release and activity data was read from GitHub on 2026-11-21. Items marked `unverified` need a primary check before a decision depends on them.

## Adoption rules

- **Every technique is a module or render-graph pass.** Nothing here enters the kernel.
- **Not loaded means not linked.** No vendor SDK, ML runtime or ray-tracing path in a build that does not select it.
- **Every advanced feature has a fallback tier.** A capability check picks the tier at load. A missing GPU feature never crashes a game.
- **Vendor features sit behind a neutral interface.** One `render.upscale` interface, many providers.
- **Inference stays out of deterministic simulation.** Neural output may drive pixels and animation presentation, never `loop.deterministic` state, unless the model is proven bit-exact on every covered platform.
- **A technique graduates by measurement.** It needs a conformance test and a budget on its target tier.

| Maturity | Meaning |
|---|---|
| **Ship now** | Default for its tier |
| **Optional module** | Real and useful, but limited by hardware, license or genre |
| **Watch** | Spike only. No roadmap commitment |

## GPU APIs

| Technique | State as of 2026-11 | Maturity | Module | Tier |
|---|---|---|---|---|
| Bindless resources | Core design assumption of the [RHI](06-rendering.md#foundation) | Ship now | `render.rhi` | Desktop, high-end |
| D3D12 Shader Model 6.9 | [Retail with Agility SDK 1.619, Feb 2026](https://devblogs.microsoft.com/directx/shader-model-6-9-retail-and-more/) | Ship now | `render.rhi.d3d12` | Desktop, high-end |
| Vulkan descriptor heaps | [`VK_EXT_descriptor_heap` is ratified](https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_descriptor_heap.html), [arrived in 1.4.340](https://phoronix.com/news/vulkan-1.4.340-descriptor-heap). [NVIDIA 610+ supports it](https://developer.nvidia.com/blog/streamlining-resource-binding-with-end-to-end-support-for-vulkan-descriptor-heaps/), [Intel ANV is experimental](https://phoronix.com/news/intel-anv-descriptor-heap-merge) | Optional module | `render.rhi.vulkan` | Desktop. Keep a descriptor-indexing path |
| Metal 4 | [Argument tables need Metal 4 and Apple7+. Mesh shading is Metal 3 and 4](https://developer.apple.com/metal/limits) | Ship now on supported devices | `render.rhi.metal` | Mobile, desktop |
| Mesh shaders | Available across D3D12, Vulkan and Metal, with uneven low-end coverage | Ship now with vertex fallback | `render.meshlet` | Desktop, high-end |
| D3D12 work graphs | [Spec v1.012, Feb 2026](https://microsoft.github.io/DirectX-Specs/d3d/WorkGraphs.html). D3D12 only. [Mesh nodes began as experimental](https://devblogs.microsoft.com/directx/d3d12-mesh-nodes-in-work-graphs/); retail status `unverified` | Watch | `render.workgraph` | High-end, never required |

**Rule:** no pass may require work graphs. D3D12-only scheduling would split content across platforms. Compute plus indirect dispatch stays the portable baseline.

## Lighting and path tracing

| Technique | State as of 2026-11 | Maturity | Module | Tier |
|---|---|---|---|---|
| Irradiance probes | Fallback GI that survives weak hardware | Ship now | `render.gi.probes` | Mobile (baked), desktop |
| Radiance cascades, 2D | [Holographic variant reports 1.85 ms at 512² on an RTX 3080 Laptop](https://arxiv.org/abs/2505.02041) | Ship now | `render2d.gi` | 2D, all capable GPUs |
| Radiance cascades, screen-space 3D | [Studied in a 2025 thesis. Off-screen geometry cannot contribute](https://odr.chalmers.se/items/9e42007a-bb60-440f-ba28-04410822758f) | Optional module | `render.gi.cascades` | Desktop |
| Radiance cascades, world-space 3D | [Split Radiance Cascades, sparse probes in a hashmap, 2026](https://gamedev.net/news/4628-split-radiance-cascades-real-time-global-illumination-via-sparse-radiance-probes/) | Watch | `render.gi.cascades` | High-end |
| ReSTIR direct lighting | Many-light sampling through [RTXDI](https://github.com/NVIDIA-RTX/RTXDI), under an NVIDIA license | Optional module | `render.rt.restir` | High-end |
| ReSTIR PT | [ReSTIR PT Enhanced reports 2 to 3x speedup](https://research.nvidia.com/labs/rtr/publication/lin2026restirptenhanced/). No confirmed shipped game found | Watch | `render.rt.path` | High-end |
| Ray-tracing denoising | [NRD](https://github.com/NVIDIA-RTX/NRD) v4.18, under an NVIDIA license | Optional module | `render.denoise` | High-end |

**Default GI ladder:** baked probes, then dynamic probes, then ray-traced GI. Same content on all three.

## Upscaling and frame generation

| Technique | State as of 2026-11 | Maturity | Module | Tier |
|---|---|---|---|---|
| Spatial upscaling | Cheap, no motion vectors | Ship now | `render.upscale.spatial` | Mobile |
| Temporal upscaling | FSR, XeSS, DLSS and MetalFX as providers | Ship now | `render.upscale.*` | Desktop, high-end |
| Denoised upscaling | [MetalFX version needs Apple9](https://developer.apple.com/metal/feature-sets). DLSS Ray Reconstruction is the NVIDIA equivalent | Optional module | `render.upscale.*` | High-end |
| Frame generation | [MetalFX interpolates after tone mapping](https://developer.apple.com/videos/play/wwdc2025/211/). Vendor providers on PC | Optional module | `render.framegen` | High-end |

**Rules:**

- Every geometry pass writes motion vectors and depth from the first 3D renderer, because all temporal providers need them.
- Frame generation is off by default in `kit.fighting`, `kit.fps`, rhythm and VR. Interpolation adds input latency.
- Generated frames never count toward simulation or input timing.
- HUD composes after interpolation where the provider allows it.

## Geometry and new primitives

| Technique | State as of 2026-11 | Maturity | Module | Tier |
|---|---|---|---|---|
| Meshlet culling | Mature, built with meshoptimizer | Ship now | `render.meshlet` | Desktop |
| Cluster LOD DAG | [meshoptimizer ships hierarchical cluster LOD support](https://zeux.io/2025/09/30/billions-of-triangles-in-minutes/) and a [reference `clusterlod.h`](https://raw.githubusercontent.com/zeux/meshoptimizer/master/demo/clusterlod.h) | Optional module | `render.virtualgeo` | High-end |
| Open virtual geometry | [Bevy's implementation](https://jms55.github.io/posts/2025-03-27-virtual-geometry-bevy-0-16) is the best public design log | Study | `render.virtualgeo` | High-end |
| Ray tracing of cluster LOD | [`vk_lod_clusters`](https://github.com/nvpro-samples/vk_lod_clusters) is the reference sample. Hardware reach `unverified` | Watch | `render.virtualgeo.rt` | High-end |
| Gaussian splats | [`KHR_gaussian_splatting` reached release candidate, Feb 2026](https://architosh.com/2026/02/the-khronos-group-announces-gltf-gaussian-splatting-standard/). Ratification and game-engine adoption `unverified` | Optional module | `render.splat` | Desktop, high-end |

**Splats:** use for captured backdrops and static scenes. They are not a replacement for meshes in gameplay, because collision, relighting and animation need separate handling. Import from glTF so the format stays open.

## Animation and character AI

| Technique | State as of 2026-11 | Maturity | Module | Tier |
|---|---|---|---|---|
| Motion matching | Production proven. [Open reference implementation](https://github.com/orangeduck/Motion-Matching) | Ship now | `anim.matching` | Desktop, high-end |
| Learned motion matching | [Ubisoft replaced each stage with networks and removed animation data from memory](https://www.ubisoft.com/en-us/studio/laforge/news/3NWqwcMU9lMfumgfPAEfka/learned-motion-matching). [Reported 70x memory reduction](https://dtf.ru/gameindustry/181778), secondary source | Optional module | `anim.matching.learned` | Mobile to high-end, where memory is the limit |
| GPU skinning and crowd instancing | Standard for the crowd tier | Ship now | `anim.crowd` | Desktop, high-end |
| Physics-based RL controllers | Reinforcement learning trains a simulated character to track a kinematic motion-matching controller. Source link and runtime cost `unverified` | Watch | `anim.physical.rl` | High-end |

**Rule:** learned models need training pipelines and data. Keep them as optional cooked assets with provenance, never as a build requirement.

## Simulation and streaming

| Technique | State as of 2026-11 | Maturity | Module | Tier |
|---|---|---|---|---|
| Sub-stepped soft-constraint 2D solver | [Box2D v3 Soft Step with multithreading and SIMD](https://box2d.org/posts/2024/08/releasing-box2d-3.0) | Ship now | `physics2d.box2d` | All |
| Deterministic 3D physics | [Jolt: same-binary deterministic. A cross-platform build option costs about 8%](https://jrouwe.github.io/JoltPhysics/#deterministic-simulation). Broadphase queries are not deterministic | Ship now | `physics.jolt` | Desktop, high-end |
| Multithreaded cellular sim | [Noita's GDC talk](https://gdcvault.com/play/1025695/Exploring-the-Tech-and-Design): chunks with dirty rects. [Checkerboard chunk updates](https://github.com/BradFitz66/BeefSand) per a secondary source | Ship now | `sim.cellular` | All |
| GPU cellular sim | Fast for local rules, harder for one-pixel-per-tick movement and CPU readback. No shipped reference confirmed | Watch | `sim.cellular.gpu` | Desktop |
| DirectStorage with GPU decompression | [1.4 preview adds Zstandard on CPU and GPU, chunks ≤ 256 KB advised](https://devblogs.microsoft.com/directx/directstorage-1-4-release-adds-support-for-zstandard/). Retail status `unverified` | Optional module | `io.directstorage` | Windows |
| `io_uring` asset I/O | [`liburing`](https://github.com/axboe/liburing) is active. Game-streaming benefit `unverified` | Optional module | `io.uring` | Linux, servers |

**Rules:**

- `io` is one async interface with thread-pool I/O as the portable default.
- Cook assets in chunks ≤ 256 KB so one package format serves every backend.
- Use Jolt's cross-platform option only in deterministic kits. Others keep the 8%.
- In deterministic worlds, broadphase-based gameplay queries need stable ordering or a rule against them.

## ECS storage evidence

| Storage | Wins at | Loses at | Source |
|---|---|---|---|
| Archetype | Large-scale iteration, cache efficiency | Component add/remove | [Staffordshire study, 2025](https://eprints.staffs.ac.uk/9315/1/cgvc20251224.pdf) |
| Sparse set | Cheap add/remove | Iteration scaling | Same study |
| EnTT owning groups | Fastest two-component iteration in one suite | Needs up-front group design | [`ecs_benchmark`](https://github.com/flecs-hub/ecs_benchmark), self-published, older snapshot |

**Consequences for the [kernel](04-kernel.md):**

- Archetype chunks stay the default.
- High-churn tags (stunned, on fire) must not force archetype moves. Provide per-chunk enable bitmasks or a sparse side store.
- Batch all structural changes through command buffers.
- Benchmark on AnyGame's own workloads before accepting a storage change.

## Build vs wrap

Wrap by default. Each row sits behind an AnyGame interface so it can be replaced. License and last release checked on GitHub, 2026-11-21.

| Domain | Library | License | Latest / activity | Decision |
|---|---|---|---|---|
| 3D physics | [Jolt](https://github.com/jrouwe/JoltPhysics) | MIT | v5.7.0, 2026-11 | **Wrap**, default |
| 3D physics, alt | [PhysX](https://github.com/NVIDIA-Omniverse/PhysX) | BSD-3-Clause | Active | Community provider |
| 2D physics | [Box2D](https://github.com/erincatto/box2d) | MIT | v3.2.0, 2026-10 | **Wrap**, default rigid body |
| Navmesh | [Recast/Detour](https://github.com/recastnavigation/recastnavigation) | Zlib | Last push 2026-02 | **Wrap**, watch activity |
| Shaders | [Slang](https://github.com/shader-slang/slang) | Apache-2.0 WITH LLVM-exception | v2026.22.1, 2026-11 | **Wrap**, proposed answer to [open question 9](../build/open-questions.md) |
| Shader cross-compile | [SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross) | Apache-2.0 | Active | Tooling fallback |
| Mesh processing | [meshoptimizer](https://github.com/zeux/meshoptimizer) | MIT | v1.3, 2026-09 | **Wrap** in the cooker |
| Texture transcoding | [Basis Universal](https://github.com/BinomialLLC/basis_universal), [KTX](https://github.com/KhronosGroup/KTX-Software) | Apache-2.0 | Active | **Wrap** |
| glTF import | [cgltf](https://github.com/jkuhlmann/cgltf) | MIT | Last push 2026-02 | **Wrap** in the cooker |
| GPU memory | [VMA](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator), [D3D12MA](https://github.com/GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator) | MIT | Active | **Wrap** |
| Platform layer | [SDL3](https://github.com/libsdl-org/SDL) | Zlib | 3.4.20, 2026-11 | **Wrap** for window and input on desktop and mobile |
| Audio mixer | [miniaudio](https://github.com/mackron/miniaudio) | Public domain or MIT-0 | Active | **Wrap**, default |
| Spatial audio | [Steam Audio](https://github.com/ValveSoftware/steam-audio) | Apache-2.0 | Active | Optional module |
| Scripting | [Luau](https://github.com/luau-lang/luau) | MIT | 0.748, 2026-11 | **Wrap**, default VM |
| Transport | [GameNetworkingSockets](https://github.com/ValveSoftware/GameNetworkingSockets) | BSD-3-Clause | Last push 2026-10 | **Wrap** behind `net.transport` |
| Profiling | [Tracy](https://github.com/wolfpld/tracy) | BSD-3-Clause | Active | **Wrap**, compiled out of shipping builds |
| Debug UI | [Dear ImGui](https://github.com/ocornut/imgui) | MIT | Active | **Wrap**, tools only |
| Async I/O | [liburing](https://github.com/axboe/liburing) | MIT | Active | **Wrap**, Linux module |
| Windows I/O | [DirectStorage](https://github.com/microsoft/DirectStorage) | MIT per GitHub. Check redistributable terms | Active | **Wrap**, Windows module |
| Upscaling | [AMD FSR SDK](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK) | MIT per its README | Active | Optional provider |
| NVIDIA RTX | [RTXDI](https://github.com/NVIDIA-RTX/RTXDI), [NRD](https://github.com/NVIDIA-RTX/NRD), [Streamline](https://github.com/NVIDIA-RTX/Streamline) | **NVIDIA proprietary terms** | Active | External package only, never a default |

### Build ourselves

| Part | Why |
|---|---|
| ECS | It is the data contract, tied to schema, snapshots, change detection and handles. [Flecs](https://github.com/SanderMertens/flecs) (MIT) and [EnTT](https://github.com/skypjack/entt) (MIT) are design references |
| Job scheduler | Needs read/write-set scheduling and deterministic order |
| Allocators and handles | Need module tags and hot-reload survival |
| API registry | The core extension mechanism |
| Reflection and schema | Drives every other system |
| Render graph | The main rendering extension point |
| Netcode models | Depend on schema annotations and snapshots. Transport is wrapped |
| `ag` and the command protocol | The product surface for agents |

### Wrapping rules

These bind the engine's own packages. A game can swap any default or add any dependency it chooses ([rule 8](01-thesis.md#design-rules)).

- No third-party type crosses a module boundary. Only the `ag_*` C ABI does.
- Every wrapped library is pinned, with its license recorded in the package manifest.
- A CI check fails on a dependency whose license is not on the allowlist.
- Copyleft and proprietary libraries never enter the default kit. They can exist as external packages the game opts into.
- Each wrapper passes its domain's conformance suite, so a replacement can prove parity.
