# 🎨 6. Rendering

The renderer is a library of render-graph passes over a thin GPU abstraction; a "renderer" is just a graph preset, and games add, remove or reorder passes without touching engine code.

## Foundation

- **RHI.** Modern-API-shaped (command lists, bindless descriptors, explicit barriers) over D3D12, Vulkan and Metal.
- **Render graph.** Frostbite's frame graph: passes declare inputs and outputs, the graph culls unused passes, allocates transient targets and inserts barriers. This is the extension point: a mod can add a pass between lighting and post.
- **GPU-driven scene.** All instances live in GPU buffers; culling and draw generation happen in compute. CPU cost stops scaling with object count.
- **Extract step.** The simulation world is copied into a render world each frame (Bevy, Unreal, Destiny). Simulation and rendering then run in parallel, and deterministic sims never see render state.
- **Material graph** to shader permutations, with a layered BSDF model in the spirit of Unreal's Substrate, plus a stylised/toon path.

## 3D feature tiers

| Feature | Mobile tier | Desktop tier | High-end tier |
|---|---|---|---|
| Geometry | Classic LOD + instancing | Meshlet culling | Virtualised micro-geometry (Nanite-class), incl. foliage and skinned meshes |
| Lighting | Forward+, baked probes | Clustered deferred, irradiance-probe GI | Ray-traced / software-traced dynamic GI and reflections, stochastic many-light sampling |
| Shadows | Cascades | Cascades + cached local | Virtual shadow maps, ray-traced |
| Textures | Compressed, streamed mips | Virtual texturing | Virtual texturing + runtime procedural |
| Upscaling | Spatial | Temporal (FSR/XeSS/DLSS/MetalFX plugins) | Temporal + frame generation |
| Atmosphere | Analytic sky | Volumetric fog, clouds | Volumetrics, water simulation, weather |

Unreal 5.8 added an irradiance-field GI mode aimed at 60 fps on handhelds, which confirms the tiering: the same art direction must survive on weak hardware.

## 2D is a first-class renderer, not 3D with an orthographic camera

- Sprite batcher that draws 100k+ sprites per frame from ECS chunks.
- Tilemaps (orthogonal, isometric, hex), auto-tiling, chunked infinite maps.
- Pixel-perfect pipeline: integer scaling, sub-pixel camera smoothing, palette effects.
- 2D lighting with normal-mapped sprites, soft shadows from occluder polygons, 2D global illumination (radiance cascades).
- Skeletal 2D (Spine-style), mesh deformation, vector shapes and SDF text.
- Cellular "falling sand" simulation as a GPU or multithreaded module (Noita).
- 2D and 3D compose in one graph: 2.5D, 3D worlds with 2D characters, 2D UI in world space.

## UI

Two modules: a retained, data-bound, styleable UI for game HUDs and menus (flexbox layout, animation, localisation, controller navigation), and an immediate-mode UI for tools and debug. The live viewer and debug tools use the same UI modules as games.

## VFX

GPU particle graphs (Niagara-class) with data access to the scene (depth, distance fields, ECS queries), so effects can react to gameplay.
