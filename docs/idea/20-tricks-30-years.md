# 🎩 20. Thirty years of tricks

**Before solving a game problem, look here: it was probably solved around 1996 to 2026.** A lookup catalogue, organised by problem.

> **Attribution status (as of 2026-11):** linked claims were checked against search excerpts of the linked page, not read in full. Attributions without a link are recalled and unverified: use them as search terms, not citations.

Every trick is an optional tool. A game picks what it wants, ignores the rest, and can replace any implementation ([design rule 8](01-thesis.md#design-rules)). Named games are technique references only. Module names are proposed.

Elsewhere: [large-scale combat](15-large-scale-combat.md) · [C++23, memory and tooling](16-cpp23-craft.md) · [current rendering and libraries](17-next-gen-techniques.md).

## 🧭 Find your problem

| Symptom | Go to |
|---|---|
| Too many objects, too far away | [Faking](#-faking-what-the-player-sees), [visibility](#-visibility-and-culling) |
| Lighting too slow or too flat | [Lighting](#-lighting-and-shadows) |
| Image shimmers or looks low-res | [Image quality](#-image-quality) |
| Precision errors, jitter, big data | [Maths](#-maths-and-numbers), [data](#-data-and-memory) |
| Objects explode, tunnel or jitter | [Physics](#-simulation-and-physics) |
| Characters slide, pop or feel stiff | [Animation](#-animation) |
| Enemies look dumb or cost too much | [AI](#-ai-and-pathing) |
| Online play feels laggy | [Netcode](#-netcode) |
| Controls feel unfair or dead | [Game feel](#-game-feel) |
| Need endless content | [Procedural](#-procedural-generation) |
| Sound is muddy or repetitive | [Audio](#-audio) |
| Menus and HUD fight the player | [UI](#-ui-and-ux) |
| Slow iteration, late bugs, big patches | [Production](#-production-and-shipping) |

## 🪄 Universal patterns

Most tricks below are one of these eight moves.

| Pattern | Rule | Examples |
|---|---|---|
| **Fake it** | Compute only what the player can perceive | Impostors, interior mapping |
| **Precompute** | Move runtime cost to build time | Lightmaps, PVS, LUTs |
| **Amortise** | Spread work across frames | TAA, time-sliced AI, shadow cache |
| **Level of detail** | Spend by importance | Mesh, animation, AI and network LOD |
| **Quantise** | Store only the precision that matters | Octahedral normals, bit-packed snapshots |
| **Send intent** | Share causes, not results | Lockstep, replays, command logs |
| **Predict, then correct** | Show a guess now, fix it quietly | Client prediction, rollback, inertialization |
| **Lie in the player's favour** | Bend the rules toward feeling fair | Coyote time, last-health bonus |

## 🎭 Faking what the player sees

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Billboard impostor | Replace a distant mesh with a camera-facing quad | Far objects; pops without a crossfade | Common since the 1990s | `render.lod` |
| Octahedral impostor | Bake many view angles into an atlas, blend the nearest frames | Trees and props; texture memory | Commonly attributed to Fortnite tooling | `render.lod` |
| Skybox | Draw a cubemap at infinite depth | Any outdoor scene; static | Quake-era engines | `render.sky` |
| 3D skybox | Render a miniature scene at scaled distance | Vistas beyond the playable area | Source engine | `render.sky` |
| Matte backdrop | Unreachable art hides where the level ends | Linear levels; nearly free | Common | `content` |
| Normal mapping | Perturb shading normals from a texture | Nearly everything; tangent data | Doom 3 popularised per-pixel use | `render.material` |
| Parallax mapping | Offset UVs by height and view angle | Cheap depth on walls; breaks at grazing angles | Kaneko et al., 2001 | `render.material` |
| Parallax occlusion mapping | Ray-march a height field in the pixel shader | Close-up surfaces; costs pixel time | Tatarchuk, 2006 | `render.material` |
| Decals | Project a texture onto existing geometry | Bullet holes, grime, variation | Universal | `render.decals` |
| Deferred decals | Modify G-buffer inside a projected box | Many decals; needs a G-buffer | Common since deferred | `render.decals` |
| Baked AO | Store occlusion in a texture or vertex colour | Static contact darkening; free at runtime | Universal | `assets.bake` |
| Vertex-colour tint | Vary instances through per-vertex or per-instance colour | Forests, crowds; almost free | Universal | `render.instancing` |
| Matcap | Look up shading from a sphere image by view-space normal | Stylised and mobile; no real lights | ZBrush popularised it | `render.material` |
| Flipbook | Animate a texture atlas on a quad | Smoke, fire, explosions | Universal | `vfx` |
| Soft particles | Fade particles near scene depth | Hides hard intersections | Common | `vfx` |
| Motion-vector flipbook | Blend frames using baked flow | Slow smoke from few frames | Common in modern VFX | `vfx` |
| Vertex animation texture | Store vertex positions per frame in a texture | Huge crowds, baked destruction; fixed clips | Houdini VAT tools | `anim.crowd` |
| Shader wind | Sway vertices using painted weights and noise | All foliage; no simulation | Universal | `render.foliage` |
| Hair cards | Alpha-tested strips instead of strands | Real-time hair; overdraw | Universal | `anim.hair` |
| Interior mapping | [Ray-cast fake rooms in the shader](https://www.gamedeveloper.com/programming/interior-mapping-rendering-real-rooms-without-geometry) | City windows; no real geometry | van Dongen, 2008 | `render.material` |
| Fake volumetric cones | Additive meshes shaped like light shafts | Cheap god rays | Common | `vfx` |
| Screen-space god rays | Radial blur from the sun | Cheap; fails off-screen | Common | `render.post` |
| Planar reflection | Render the scene mirrored once | Flat water and floors; doubles draw cost | Common | `render.reflection` |
| Parallax-corrected cubemap | Intersect reflection ray with a proxy box | Indoor reflections | Lagarde, 2012 | `render.reflection` |
| Fog as draw distance | Fade to fog before the far plane | Hides pop-in, weak hardware | Silent Hill commonly cited | `render.atmosphere` |
| Loading corridor | Squeeze, elevator or slow door hides streaming | No loading screens | Mass Effect elevators commonly cited | `world.stream` |
| Portal trick room | Connect spaces that do not fit geometrically | Impossible architecture | Portal, Antichamber | `render.portals` |
| Camera-cut swap | Change the world while the camera looks away | Set dressing, spawn, despawn | Universal | `world.population` |
| First-person weapon pass | Draw weapon with own FOV and depth range | Stops clipping through walls | Universal in FPS | `render.layers` |
| Off-screen despawn | Remove bodies and debris out of view | Caps entity count | Universal | `world.population` |

## 👁️ Visibility and culling

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| BSP tree | Split space by planes for ordered traversal | Static indoor maps; slow to build | Doom, Quake | `render.visibility` |
| Potentially visible set | Precompute which cells can see which | Static levels; bake time | Quake | `render.visibility` |
| Portals and sectors | Clip the view through doorways | Indoors; authored or generated | Build engine, Descent | `render.portals` |
| Frustum culling | Skip bounds outside the camera | Always | Universal | `render.visibility` |
| Hierarchical bounds | Cull a whole group with one test | Big scenes | Universal | `render.visibility` |
| Distance and screen-size cull | Drop objects below N pixels | Small props; cheap win | Universal | `render.lod` |
| Depth pre-pass | Lay down depth first to stop overdraw | Expensive pixel shaders | Common | `render.graph` |
| Hi-Z occlusion | Test bounds against a depth pyramid | Dense scenes | Greene, 1993; GPU-driven pipelines | `render.visibility` |
| Two-pass occlusion | Draw last frame's visible set, then recheck the rest | GPU-driven scenes | Haar and Aaltonen, 2015 | `render.visibility` |
| CPU software occlusion | Rasterise few occluders on CPU | No async GPU readback | Frostbite-era talks | `render.visibility` |
| Back-face cluster culling | Reject whole meshlets by normal cone | Meshlet pipelines | Modern GPU-driven | `render.gpu_scene` |
| Discrete LOD | Swap meshes by distance | Universal | Universal | `render.lod` |
| Dithered LOD crossfade | Screen-door blend between LODs | Hides pops; needs TAA or fine dither | Common | `render.lod` |
| HLOD | Merge a far group into one mesh | Open worlds | Unreal HLOD | `world.partition` |
| Geomipmapping | Terrain patches at varying resolution | Heightfields | de Boer, 2000 | `world.terrain` |
| Geometry clipmaps | Nested rings centred on the camera | Huge terrain | Losasso and Hoppe, 2004 | `world.terrain` |
| Instancing | One draw, many transforms | Repeated meshes | Universal | `render.instancing` |
| Draw sort key | Encode state in an integer, then sort | Minimises state changes | Common | `render.queue` |
| Texture atlas and arrays | Share one binding across many objects | Batching | Universal | `render.batch` |

## 💡 Lighting and shadows

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Lightmaps | Bake lighting into a second UV set | Static worlds; no dynamic change | Quake | `render.gi.baked` |
| Directional lightmaps | Store dominant light direction | Baked light with normal maps | Half-Life 2 basis | `render.gi.baked` |
| Spherical harmonics | Compress low-frequency light into few coefficients | Probes and ambient | Ramamoorthi and Hanrahan, 2001 | `render.gi.probes` |
| Precomputed radiance transfer | Bake how a surface responds to light | Static objects, dynamic light | Sloan et al., 2002 | `render.gi.baked` |
| Light probes | Sample baked light at grid points | Dynamic objects in baked scenes | Greger et al., 1998 | `render.gi.probes` |
| Dynamic probe grids | Ray-trace probes over time | Dynamic GI on mid hardware | DDGI, Majercik et al., 2019 | `render.gi.probes` |
| Hemisphere ambient | Blend sky and ground colour by normal | Cheapest believable ambient | Common | `render.light` |
| Deferred shading | Write surface data, light it afterward | Many lights; transparency is hard | Deering, 1988; shipped widely in the 2000s | `render.deferred` |
| Light pre-pass | Render lighting before material shading | Older hardware | Engel, 2008 | `render.deferred` |
| Tiled shading | [Bin lights into 2D screen tiles](https://research.chalmers.se/en/publication/161726) | Many lights | Olsson and Assarsson, 2011 | `render.clustered` |
| Forward+ | Tiled culling with forward materials | MSAA and varied materials | Harada et al., 2012 | `render.clustered` |
| Clustered shading | [Bin lights in 3D view clusters](https://research.chalmers.se/en/publication/161725) | Default for many lights | Olsson et al., 2012 | `render.clustered` |
| Physically based shading | [Energy-aware, measured material model](https://cgvr.cs.uni-bremen.de/teaching/cg_literatur/Physically-Based%20Shading%20at%20Disney%20-%20Ken%20Burley,%202012,%20v3.pdf) | Consistent art under any light | Burley, 2012 | `render.material` |
| Split-sum IBL | [Pre-filter environment plus a BRDF LUT](https://cgvr.informatik.uni-bremen.de/teaching/cg_literatur/Brian%20Karis%20-%20Real%20Shading%20in%20Unreal%20Engine%204,%202013%20Siggraph%20Course.pdf) | Real-time image-based lighting | Karis, 2013 | `render.material` |
| Filmic tonemapping | Roll off highlights with a film curve | HDR to display | Hable curve; ACES | `render.post` |
| Colour-grade LUT | Apply a 3D colour table | Art-directed look, nearly free | Universal | `render.post` |
| Auto exposure | Adapt to scene luminance histogram | HDR scenes | Common | `render.post` |
| Blob shadow | Dark decal under a character | Mobile, stylised, platformers | Universal | `render.shadows` |
| Planar projected shadow | Flatten mesh onto the ground | Single flat floor | Common | `render.shadows` |
| Stencil shadow volumes | Extrude silhouettes, count in stencil | Historic; hard edges | Doom 3 | `render.shadows` |
| Shadow maps + PCF | Compare depth from the light, filter samples | Default | Universal | `render.shadows` |
| Cascaded shadow maps | Split the frustum into shadow ranges | Sun shadows | Engel and Zhang et al., 2006 | `render.shadows` |
| Texel snapping | Move cascades in whole texels | Stops shadow shimmer | Common | `render.shadows` |
| Variance / exponential shadows | Store filterable depth statistics | Soft shadows; light bleeding | Donnelly and Lauritzen, 2006; Annen et al., 2008 | `render.shadows` |
| Cached shadow pages | Rerender only what changed | Static-heavy scenes | Virtual shadow maps | `render.shadows` |
| Contact shadows | Short screen-space ray march | Fine detail near surfaces | Common | `render.post` |
| SSAO | [Estimate occlusion from depth](https://www.advances.realtimerendering.com/s2007/Mittring-Finding_NextGen_CryEngine2(Siggraph07).pdf) | Cheap contact shading | Mittring, CryEngine 2, 2007 | `render.post` |
| HBAO | [Integrate horizon angle in depth](https://history.siggraph.org/learning/image-space-horizon-based-ambient-occlusion-by-bavoil-sainz-and-dimitrov/) | Better AO quality | Bavoil et al., 2008 | `render.post` |
| Screen-space reflections | Ray-march depth buffer | Wet floors; fails off-screen | McGuire and Mara, 2014 | `render.reflection` |
| Light cookies | Project a texture through a light | Cheap patterned light | Universal | `render.light` |

## 🖼️ Image quality

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Mipmapping | Pre-filter textures by distance | Always | Williams, 1983 | `render.texture` |
| Anisotropic filtering | Sample along the pixel footprint | Grazing surfaces; cheap | Universal | `render.texture` |
| FXAA | Blur detected edges in post | Weak hardware | Lottes, 2009 | `render.aa` |
| TAA | [Accumulate jittered frames over time](https://research.nvidia.com/labs/rtr/publication/yang2020survey) | Modern default; can ghost | Survey: Yang et al., 2020 | `render.aa` |
| Neighbourhood clipping | Clamp history to current nearby colours | Reduces ghosting | Karis, 2014 | `render.aa` |
| Low-discrepancy jitter | Use Halton or R2 sample offsets | Better TAA convergence | Common | `render.aa` |
| Temporal accumulation | Reuse reprojected history for any effect | AO, reflections, GI | Universal now | `render.temporal` |
| Checkerboard rendering | Shade half the pixels, reconstruct the rest | Console 4K | Popularised on PS4 Pro | `render.scaling` |
| Dynamic resolution | Lower render size when frame time rises | Holds frame rate | Common | `render.scaling` |
| Variable rate shading | Shade low-detail areas coarsely | Saves pixel cost | Modern APIs | `render.scaling` |
| Half-res particles | Composite transparency from a small target | Overdraw spikes | Common | `vfx` |
| Blue-noise dithering | Error looks like fine grain | Gradients, stochastic effects | Christoph Peters' textures | `render.post` |
| Interleaved gradient noise | Cheap per-pixel noise formula | Short sample counts | Jimenez, 2014 | `render.post` |
| Output dithering | Add noise before 8-bit output | Stops sky banding | Common | `render.post` |
| Integer scaling | Scale pixel art by whole numbers | Crisp 2D | Universal in pixel art | `render2d` |
| Sub-pixel camera | Render at native size, offset final blit | Smooth pixel-art scrolling | Common | `render2d` |
| Palette swap | Index colours through a lookup texture | Variants, damage flashes | Decades of 2D | `render2d` |

## 🔢 Maths and numbers

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Fast inverse square root | Float bit hack + one Newton step | **History only:** use hardware instructions | [Quake III; origin disputed](https://en.wikipedia.org/wiki/Fast_inverse_square_root) | n/a |
| Squared distance | Compare `d²`, skip the root | All range checks | Universal | `math` |
| Fixed point | Integers with an implied fraction | Cross-platform determinism | RTS and fighting games | `math.fixed` |
| Quaternions | Four numbers for rotation, no gimbal lock | All 3D rotation | Universal | `math` |
| nlerp | Linear blend, then normalise | Close rotations; fast, commutative | Jonathan Blow's essay on slerp | `math` |
| Shortest-arc check | Negate one quaternion if dot < 0 | Every quaternion blend | Universal | `math` |
| Dual-quaternion skinning | Blend rigid transforms | Stops candy-wrapper joints | Kavan et al., 2007 | `anim.skin` |
| Exponential smoothing | `a = lerp(a, b, 1 - exp(-k*dt))` | Frame-rate-independent follow | Common | `math` |
| Critically damped spring | Closed-form spring with no overshoot | Cameras, UI, aim | Game Programming Gems lineage | `math` |
| Easing curves | Remap `t` through a shaped function | All motion and UI | Universal | `math` |
| Quantisation | Map a float range to N bits | Network, vertices, animation | Universal | `math.quantise` |
| Octahedral normals | [Map a unit vector to 2D](https://jcgt.org/published/0003/02/01/paper.pdf) | G-buffers, vertices | Cigolle et al., 2014 | `math.encode` |
| Smallest-three quaternion | [Drop the largest component](https://www.gafferongames.com/post/snapshot_compression/) | Network rotation | Fiedler | `net.compress` |
| Floating origin | Re-centre the world around the camera | Large worlds | KSP commonly cited | `world.coords` |
| Camera-relative rendering | Subtract camera position before GPU upload | Any large world | Common | `world.coords` |
| Reversed-Z | [Map near to 1, far to 0 with float depth](https://www.reedbeta.com/blog/depth-precision-visualized/) | Default depth setup | Reed, 2015 | `render.camera` |
| Lookup tables | Precompute costly curves | Check first: caches can beat LUTs | Universal | `math` |
| SIMD batches | Process 4 to 16 values at once | Hot loops | Universal | `math.simd` |
| Morton codes | Interleave coordinate bits | Spatial sort, grids, BVH | Common | `math.spatial` |
| Seeded RNG streams | Separate generator per system | Reproducible sims | Common | `rng` |
| Stateless hash noise | Hash coordinates into randomness | Order-independent generation | Common | `rng` |

## 🧱 Data and memory

Allocator and sanitizer detail: [C++23 craft](16-cpp23-craft.md).

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Structure of arrays | Group the same field contiguously | Hot loops | Data-oriented design | `ecs` |
| Hot/cold split | Move rare fields elsewhere | Large structs | Common | `ecs` |
| Object pools | Reuse fixed-size objects | Bullets, particles | Universal | `kernel.memory` |
| Intrusive free list | Store next-free index in dead slots | Pools with no overhead | Universal | `kernel.memory` |
| Frame arena | Bump allocate, reset each frame | Temporary data | Naughty Dog tagged heaps | `kernel.memory` |
| Generational handles | Index + version instead of pointers | Safe references | Universal in ECS | `kernel.handles` |
| Swap-and-pop | Move last element into a removed slot | Unordered arrays | Universal | `ecs` |
| Sparse set | Sparse index into dense array | Fast membership | EnTT | `ecs` |
| Dirty flags | Recompute only when input changes | Transforms, UI, shadows | Universal | `kernel` |
| String hashing | Compare compile-time hashes | IDs at runtime | Universal | `kernel.names` |
| String interning | Store each string once | Names, tags | Universal | `kernel.names` |
| Flat binary load-in-place | Load a file and fix up offsets | Near-instant loads | Console engines | `assets.format` |
| Relative pointers | Store offsets instead of addresses | Relocatable data | Common | `assets.format` |
| Pack files | Combine assets into one indexed archive | Fewer seeks | Quake PAK and later | `assets.pack` |
| Disc-order layout | Place co-used assets adjacently | Spinning media | Console era | `assets.pack` |
| Duplicate data on disc | Trade size for fewer seeks | HDD only, avoid on SSD | Common | `assets.pack` |
| Texture block compression | GPU-readable compressed formats | All textures | BCn, ASTC | `assets.cook` |
| Mip streaming | Load only needed resolution | Open worlds | Universal | `world.stream` |
| Virtual texturing | Page texture tiles on demand | Huge unique detail | id's Rage | `render.texture` |
| Delta patches | Ship changed chunks only | Live games | Content-addressed patching | `boot` |
| Time-sliced work | Limit a job to N ms per frame | Long tasks | Universal | `kernel.jobs` |

## 🧲 Simulation and physics

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Fixed-timestep accumulator | [Tick at fixed dt, keep the remainder](https://gafferongames.com/post/fix_your_timestep/) | Stable physics | Fiedler | `loop.fixed` |
| Render interpolation | Draw between two ticks by leftover alpha | Smooth display at any rate | Fiedler | `loop.fixed` |
| Spiral-of-death clamp | Cap the catch-up time per frame | Always with fixed steps | Common | `loop.fixed` |
| Sub-stepping | Run physics several times per tick | Vehicles, stacks, ropes | Racing sims | `sim.fixed` |
| Sleeping islands | Skip resting groups of bodies | Most physics scenes | Universal | `physics` |
| Sweep and prune | Sort bounds along axes | Coherent broadphase | Universal | `physics.broadphase` |
| Uniform grid | Hash objects into cells | Similar-sized objects | Universal | `physics.broadphase` |
| Dynamic BVH | Tree of fattened bounds | General broadphase | Box2D lineage | `physics.broadphase` |
| GJK + EPA | Distance and penetration for convex shapes | Narrow phase | Universal | `physics.narrow` |
| Convex collision proxies | Collide with simple shapes, not the render mesh | Always | Universal | `physics` |
| Sequential impulses | Iterate contact constraints | Rigid-body default | Erin Catto's talks | `physics.solver` |
| Warm starting | Seed solver with last frame's impulses | Stable stacks | Common | `physics.solver` |
| Verlet + relaxation | [Particles with iterated constraints](https://gamedeveloper.com/programming/advanced-character-physics) | Cloth, ropes, ragdolls | Jakobsen, Hitman, 2001 | `physics.soft` |
| Position Based Dynamics | [Solve constraints on positions](https://diglib.eg.org/items/deb0a7a1-2ddf-496f-889a-fe0df1feeb73) | Stable soft bodies | Müller et al., 2006 | `physics.soft` |
| XPBD | [Iteration-independent stiffness](https://matthias-research.github.io/pages/publications/XPBD.pdf) | Modern PBD default | Macklin et al., 2016 | `physics.soft` |
| Continuous collision | Sweep fast shapes along their path | Bullets, fast cars | Universal | `physics.ccd` |
| Hitscan for bullets | Ray test instead of a moving body | Fast projectiles | Universal in FPS | `physics.query` |
| Speculative contacts | Add contacts before touching | Cheap anti-tunnelling | Common | `physics.solver` |
| Thicken thin walls | Make collision thicker than visuals | Stops tunnelling | Universal | `content` |
| Kinematic capsule | Move and slide with sweeps, not forces | Player characters | Universal | `physics.character` |
| Step-up / snap-down | Lift over stairs, stick to slopes | Character controllers | Universal | `physics.character` |
| Raycast wheels | Suspension springs from ray hits | Arcade to mid-sim vehicles | Common | `physics.vehicle` |
| Fake mass ratios | Clamp extreme mass differences | Stops solver explosions | Common | `physics.solver` |
| Max depenetration speed | Cap how fast overlaps resolve | Stops objects launching | Common | `physics.solver` |
| Physics LOD | Simplify or freeze far bodies | Crowded worlds | Common | `sim.lod` |
| Prebaked destruction | Fracture offline, play at runtime | Cinematic collapse | Common | `physics.destruction` |
| Belt segments | Simulate a line as one unit | Factory games | Factorio dev blogs | `sim.batch` |

## 🏃 Animation

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Root motion | Clip drives the character's movement | Weighty melee, stops foot slide | Common | `anim.events` |
| Blend trees | Parameter-driven clip mixes | Locomotion | Universal | `anim.graph` |
| Sync markers | Align blends on foot phase | Walk to run | Common | `anim.graph` |
| Additive layers | Add a delta pose on top | Breathing, recoil, hit reactions | Universal | `anim.graph` |
| Aim offsets | Blend poses by aim direction | Shooters | Common | `anim.graph` |
| Bone masks | Blend upper and lower body separately | Run and shoot | Universal | `anim.graph` |
| Two-bone IK | Analytic arm and leg solve | Feet and hands | Universal | `anim.ik` |
| FABRIK | Iterative forward/backward chain solve | Tails, spines | Aristidou and Lasenby, 2011 | `anim.ik` |
| Foot locking | Pin planted foot, then release | Stops sliding | Common | `anim.ik` |
| Stride warping | Scale stride to match speed | Fewer clips | Modern engines | `anim.warp` |
| Motion warping | Bend root path to hit a target | Vaults, finishers | Modern engines | `anim.warp` |
| Turn-in-place | Keep feet still until angle exceeds limit | Third-person idle | Common | `anim.graph` |
| Inertialization | [Decay pose offset as a post-process](https://gdcvault.com/play/1025165/Inertialization-High-Performance-Animation-Transitions) | [Cheaper transitions](https://history.siggraph.org/?p=84136) | Bollo, Gears of War | `anim.blend` |
| Motion matching | Search mocap for the best next frame | High-quality locomotion; data heavy | Clavet, For Honor, 2016 | `anim.matching` |
| Procedural secondary motion | Springs on tails, gear, ears | Life for free | Common | `anim.procedural` |
| Procedural walk | Pose from a few keyframes plus maths | Small teams | Overgrowth GDC talk, 2014 | `anim.procedural` |
| Procedural legs | Move feet when too far from rest targets | Spiders, mechs | Common | `anim.procedural` |
| Powered ragdoll | Physics motors chase animation | Stumbles, reactions | Euphoria | `anim.physical` |
| Ragdoll blend-out | Blend from physics to a get-up clip | Recovery | Common | `anim.physical` |
| Curve keyframe reduction | Remove keys within error tolerance | Clip memory | ACL library | `anim.compress` |
| Update-rate LOD | Animate far characters less often | Crowds | Common | `anim.lod` |
| GPU skinning | Skin in compute | Many characters | Universal | `anim.skin` |
| Squash and stretch | Scale by velocity | Stylised impact | Classic animation principle | `anim.procedural` |

## 🧠 AI and pathing

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Finite state machine | Explicit states and transitions | Simple enemies | Universal | `ai.fsm` |
| Behaviour tree | [Hierarchy of prioritised behaviours](https://www.gamedeveloper.com/programming/gdc-2005-proceeding-handling-complexity-in-the-i-halo-2-i-ai) | Most action AI | Isla, Halo 2, 2005 | `ai.bt` |
| GOAP | [A* over actions, tiny FSM executes](https://pages.cs.wisc.edu/~dyer/cs540/handouts/gdc2006_orkin_jeff_fear.pdf) | Emergent tactics | Orkin, F.E.A.R., 2006 | `ai.planning` |
| HTN planning | Decompose tasks into subtasks | Authored plans | Killzone 2 commonly cited | `ai.planning` |
| Utility AI | Score options, choose the best | Needs-based sims | The Sims; Dave Mark's talks | `ai.utility` |
| Smart objects | Object advertises its interactions | Life sims, cover, props | The Sims | `gameplay.smartobjects` |
| Blackboard | Shared memory for AI | BT and squads | Common | `ai.blackboard` |
| Monte Carlo tree search | Sample future games | Turn-based and card AI | Common | `ai.planning` |
| A* on navmesh | Polygons as search graph | 3D default | Recast/Detour | `ai.nav` |
| Hierarchical pathfinding | Plan across regions, then locally | Large maps | Botea et al., 2004 | `ai.nav` |
| Jump point search | Skip symmetric grid paths | Uniform grids | Harabor and Grastien, 2011 | `ai.nav` |
| Flow fields | [One field steers everyone to a goal](https://grail.cs.washington.edu/projects/crowd-flows/) | Huge groups | Treuille et al., 2006 | `ai.nav` |
| Dijkstra maps | Distance grids combined by weight | Roguelikes | Brogue commonly cited | `ai.nav` |
| Path smoothing | String-pull along corners | Natural paths | Funnel algorithm | `ai.nav` |
| Steering behaviours | Combine seek, flee, separation | Local motion | Reynolds, 1999 | `ai.crowd` |
| Boids | Separation, alignment, cohesion | Flocks, schools | Reynolds, 1987 | `ai.crowd` |
| RVO / ORCA | Reciprocal velocity avoidance | Crowds | van den Berg et al. | `ai.crowd` |
| Influence maps | Grids of threat and control | Strategy AI | Common | `ai.strategy` |
| Tactical point scoring | Score nearby positions | Cover selection | Common | `ai.perception` |
| Last-known position | Agents chase memory, not truth | Fair stealth | Common | `ai.perception` |
| Vision and alert meters | Detection builds over time | Stealth fairness | Thief, Metal Gear lineage | `ai.perception` |
| Attack tokens | Limit how many enemies attack at once | Melee crowds | Common | `ai.director` |
| Fake group tactics | [Barks announce independent behaviour as a plan](https://pages.cs.wisc.edu/~dyer/cs540/handouts/gdc2006_orkin_jeff_fear.pdf) | Perceived intelligence | F.E.A.R. | `ai.barks` |
| Barks | Short lines expose AI state | Makes AI readable | Universal | `ai.barks` |
| Telegraphing | Wind-up before attack | Fair combat | Universal | `gameplay.combat` |
| AI Director | [Pacing based on player stress](https://cdn.fastly.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf) | Replayable co-op | Booth, Left 4 Dead | `ai.director` |
| Cheating AI | Give hidden info or resources | Difficulty on a budget; keep it unnoticed | Strategy games | `ai.strategy` |
| Staggered AI ticks | Update N agents per frame | Large groups | Universal | `ai.lod` |
| AI LOD | Far agents use simple rules | Open worlds | Universal | `sim.lod` |

## 🌐 Netcode

Large-battle specifics: [large-scale combat](15-large-scale-combat.md).

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Deterministic lockstep | [Send commands, simulate identically](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond) | RTS; needs determinism | Age of Empires | `net.lockstep` |
| Command turn delay | Schedule commands a few turns ahead | Hides latency in RTS | Age of Empires | `net.lockstep` |
| Desync checksums | Hash state periodically | Any deterministic game | Universal | `net.lockstep` |
| Dead reckoning | Extrapolate from last velocity | Vehicles, slow updates | Military simulation lineage | `net.replication` |
| Entity interpolation | [Render others slightly in the past](https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking) | Smooth remote players | Source | `net.replication` |
| Client prediction | [Apply inputs locally, reconcile with server](https://developer.valvesoftware.com/wiki/Latency_Compensating_Methods_in_Client/Server_In-game_Protocol_Design_and_Optimization) | Shooters | Bernier, 2001 | `net.replication` |
| Input replay reconciliation | Rewind to server state, reapply unacked inputs | With prediction | Bernier, 2001 | `net.replication` |
| Error smoothing | Blend visual position after a correction | Hides snaps | Common | `net.replication` |
| Lag compensation | [Rewind hitboxes to the shooter's view](https://gabrielgambetta.com/lag-compensation.html) | Hitscan; "shot behind cover" | Source | `net.replication` |
| Max rewind limit | Cap compensation time | Protects low-ping players | Common | `net.replication` |
| Delta snapshots | [Encode against an acked baseline](https://www.gafferongames.com/post/snapshot_compression/) | State replication | Quake 3 lineage; Fiedler | `net.compress` |
| Bit packing | Write fields at exact bit width | All replication | Universal | `net.compress` |
| Entropy coding | Static Huffman or range coding | Last bandwidth savings | Common | `net.compress` |
| Redundant inputs | Send the last N inputs each packet | Survives loss with no resend | Common | `net.transport` |
| Reliability over UDP | Ack bitfields per channel | Mixed traffic | Common | `net.transport` |
| Priority accumulator | [Rank objects per client, send what fits](https://opentnl.sourceforge.net/doxydocs/history.html) | Bandwidth budgets | Tribes lineage | `net.replication` |
| Interest management | Send only nearby or relevant entities | Large worlds | Universal in MMOs | `net.mmo` |
| Server-side fog of war | Do not send what cannot be perceived | Anti-wallhack | [Online stack](09-online.md) | `net.replication` |
| Network LOD | Update far entities less often | High player counts | Common | `net.replication` |
| Jitter buffer | Hold packets briefly and release evenly | Unstable connections | VoIP lineage | `net.transport` |
| Clock sync | Estimate server time from round trips | All prediction | Common | `net.clock` |
| Tick dilation | Client runs slightly faster or slower | Keeps input buffer full | Overwatch GDC talk commonly cited | `net.clock` |
| Time dilation | Slow the whole simulation under load | Huge fights | EVE Online | `net.mmo` |
| Rollback | [Predict, restore, re-simulate](https://words.infil.net/w02-netcode-p5.html) | Fighting, small-action games | [GGPO](https://en.wikipedia.org/wiki/GGPO) | `net.rollback` |
| Tuned input delay | Trade a few frames of delay for fewer rollbacks | With rollback | Common | `net.rollback` |
| Input-stream spectating | Replay inputs on a delay | Spectators, esports | Fighting games, RTS | `replay` |
| Host migration | Promote a peer when host leaves | P2P sessions | Common | `net.session` |

## 🕹️ Game feel

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Coyote time | [Allow a jump shortly after leaving a ledge](https://maddymakesgames.com/articles/celeste_and_forgiveness/) | Platformers | Celeste | `input.buffer` |
| Jump buffering | [Early press fires on landing](https://maddymakesgames.com/articles/celeste_and_forgiveness/) | Platformers | Celeste | `input.buffer` |
| General input buffer | Queue actions during busy states | Action and fighting games | Universal in fighters | `input.buffer` |
| Variable jump height | Cut velocity on early release | Platformers | Mario lineage | `physics2d.kinematic` |
| Apex hang | [Halve gravity at the top while held](https://maddymakesgames.com/articles/celeste_and_forgiveness/) | Air control | Celeste | `physics2d.kinematic` |
| Fast fall | Raise gravity while descending | Snappy jumps | Common | `physics2d.kinematic` |
| Corner correction | [Nudge the player around a ledge corner](https://maddymakesgames.com/articles/celeste_and_forgiveness/) | Stops unfair bonks | Celeste | `physics2d.kinematic` |
| Ledge magnetism | Snap a near-miss grab | 3D platforming | Common | `physics.character` |
| Hit-stop | Freeze attacker and target for a few frames | Melee weight | Fighting games, action games | `gameplay.combat` |
| Trauma screen shake | [Add trauma, shake by trauma² with noise](https://gdcvault.com/play/1023146/Math-for-Game-Programmers-Juicing) | Impacts; offer an accessibility toggle | Eiserloh, 2016 | `camera` |
| Camera look-ahead | Lead in movement direction | Platformers, racing | Common | `camera` |
| FOV kick | Widen FOV with speed | Sense of velocity | Racing, shooters | `camera` |
| Hit flash | One frame of white on damage | Clear feedback | Universal | `render2d` |
| Knockback | Push target from impact direction | Readable hits | Universal | `gameplay.combat` |
| Muzzle and impact pair | Sync flash, sound, particle, decal, recoil | Weapon feel | Universal | `gameplay.weapons` |
| Damage numbers | Pop text at the point of impact | RPG reward | Common | `ui` |
| Invulnerability frames | Brief immunity after hit or dodge | Prevents stun-lock | Universal | `gameplay.combat` |
| Forgiving player hitbox | Player hurtbox smaller than sprite | Fair dodging | Bullet hell | `gameplay.combat` |
| Generous enemy hitbox | Enemy target larger than sprite | Feels accurate | Universal | `gameplay.combat` |
| Last-health bonus | [Final HP sliver counts for more](https://www.pcgamer.com/developers-share-their-hidden-mechanics-on-twitter/) | Tense survival | Assassin's Creed, Doom | `gameplay.tuning` |
| Last-hit grace | [Brief invulnerability instead of dying](https://www.pcgamesn.com/surgeon-simulator-2013/in-game-developer-secrets-tweets) | Near-death drama | BioShock, reported | `gameplay.tuning` |
| Last-bullet bonus | [Final round does more damage](https://www.pcgamer.com/developers-share-their-hidden-mechanics-on-twitter/) | Clutch moments | System Shock, reported | `gameplay.tuning` |
| Intentional first miss | [Enemies miss the opening shot](https://www.gamesradar.com/did-you-know-that-games-like-assassins-creed-doom-bloodborne-and-more-have-hidden-mechanics-to-make-you-feel-like-a-badass) | Lets players react | BioShock, reported | `gameplay.tuning` |
| Aim friction | Slow the reticle over targets | Controllers | Halo lineage | `input.aim` |
| Aim magnetism | Pull shots slightly toward target | Controllers | Halo lineage | `gameplay.weapons` |
| Rubber-banding | Help trailing players, slow leaders | Party racing; disclose in competitive | Mario Kart items | `gameplay.tuning` |
| Dynamic difficulty | Adjust by repeated failure | Single-player | Crash Bandicoot commonly cited | `gameplay.tuning` |
| Pseudo-random distribution | Chance rises after each miss | Streak-free procs | Warcraft III, Dota lineage | `rng` |
| Pity timer | Guarantee reward after N failures | Loot; disclose odds | Common in card games | `gameplay.loot` |
| Checkpoint before challenge | Keep retry time near zero | Hard games | Super Meat Boy, Celeste | `persist.save` |
| Instant restart | One button, no load | Skill games | Trackmania lineage | `boot` |
| Rising pitch combo | Each pickup plays higher | Pickups | Common | `audio` |

## 🌱 Procedural generation

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Seeded everything | All content derives from a seed | Shareable, testable worlds | Elite, roguelikes | `pcg`, `rng` |
| Hierarchical seeds | Derive child seeds by coordinates | Generate any chunk in any order | Minecraft-style worlds | `pcg` |
| Perlin / simplex noise | Smooth gradient noise | Terrain, textures | Perlin, 1985 and 2001 | `pcg.noise` |
| fBm | Sum noise at rising frequencies | Natural detail | Universal | `pcg.noise` |
| Domain warping | Distort noise inputs with noise | Organic terrain | Inigo Quilez's articles | `pcg.noise` |
| Worley noise | Distance to scattered points | Cells, stone, clouds | Worley, 1996 | `pcg.noise` |
| Hydraulic erosion | Simulate droplets carving terrain | Believable mountains | Common | `pcg.terrain` |
| Biome tables | Pick biome by temperature and moisture | Worlds | Common | `pcg.terrain` |
| Poisson-disc sampling | Random points with minimum spacing | Trees, rocks | Bridson, 2007 | `pcg.place` |
| Wave function collapse | [Solve tile adjacency by least entropy](https://en.wikipedia.org/wiki/Model_synthesis) | Tile maps, buildings | Merrell, 2007; Gumin, 2016 | `pcg.wfc` |
| L-systems | Rewrite symbols into branching forms | Plants | Lindenmayer, 1968 | `pcg.grammar` |
| BSP dungeons | Split rooms recursively, connect siblings | Roguelikes | Common | `pcg.dungeon` |
| Drunkard's walk | Random carver | Caves | Common | `pcg.dungeon` |
| Cellular automata caves | Smooth noise by neighbour rules | Natural caves | Common | `pcg.dungeon` |
| Room templates | Assemble authored rooms along a critical path | Guaranteed solvable | Spelunky | `pcg.dungeon` |
| Lock-and-key graphs | Generate progression first, then geometry | Designed dungeons | Dormans' graph grammars | `pcg.grammar` |
| Solvability check | Bot or flood fill rejects bad seeds | All generated levels | Common | `testing` |
| Run vs meta state | Separate per-run and permanent progress | Roguelites | Hades | `persist.save` |
| Weighted bags | Draw without replacement | Item and tile fairness | Tetris randomiser | `rng` |
| Markov names | Generate names from letter statistics | Flavour text | Common | `pcg.text` |

## 🔊 Audio

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Voice limiting | Cap simultaneous sounds by priority | Always | Universal | `audio` |
| Voice virtualisation | Track inaudible sounds without mixing | Large scenes | Middleware standard | `audio` |
| Per-event cooldown | Drop duplicate sounds in a short window | Machine guns, swarms | Common | `audio` |
| Ducking | Lower music under dialogue | Clarity | Universal | `audio.mix` |
| HDR audio | Loud events temporarily mask quieter ones | Battlefields | Battlefield commonly cited | `audio.mix` |
| Pitch and volume variance | Randomise slightly per play | Removes machine-gun effect | Universal | `audio` |
| Round-robin clips | Never repeat the same sample | Footsteps, impacts | Universal | `audio` |
| Layered one-shots | Build sounds from transient, body, tail | Weapons | Common | `audio.design` |
| Surface switching | Choose sound by physics material | Footsteps, impacts | Universal | `audio` |
| Occlusion filter | Low-pass when a ray is blocked | Spatial realism | Common | `audio.spatial` |
| Reverb zones | Blend reverb by room | Spaces | Universal | `audio.spatial` |
| Speed-of-sound delay | Delay far explosions | Scale | Military shooters | `audio.spatial` |
| Distance-layered sounds | Swap near and far samples | Gunfire across a map | Common | `audio.spatial` |
| Vertical remixing | Fade stems by intensity | Adaptive music | Common | `audio.music` |
| Horizontal resequencing | Jump between sections on beat | Adaptive music | iMUSE | `audio.music` |
| Stingers | Quantised one-shots on events | Musical reward | Common | `audio.music` |
| DSP clock scheduling | Schedule on the audio clock | Rhythm | Rhythm games | `audio.clock` |
| Latency calibration | Player measures offset | Rhythm | Rhythm games | `audio.clock` |
| Granular engines | Play grains by RPM | Vehicles | Racing games | `audio.synth` |

## 🖱️ UI and UX

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Nine-slice | Stretch panel edges and centre separately | Scalable panels | Universal | `ui` |
| SDF text | Store glyph distance for sharp scaling | World and HUD text | Green, Valve, 2007 | `ui.text` |
| Multi-channel SDF | Preserve sharp font corners | Crisp small atlases | Chlumský | `ui.text` |
| Delayed damage bar | Ghost bar drains behind real health | Readable burst damage | Fighting games | `ui.hud` |
| Diegetic HUD | Put information in the world | Immersion | Dead Space | `ui.hud` |
| Directional hit marker | Show where damage came from | Shooters | Universal | `ui.hud` |
| Context ping | One button marks and communicates | Team play with no voice | Apex Legends | `social.comms` |
| Dynamic input glyphs | Swap icons to the active device | Any controller support | Common | `input` |
| Safe zones | Keep UI away from screen edges | TV, phones | Platform requirement | `ui` |
| Pseudo-localisation | Fake long accented strings in dev | Finds layout bugs early | Common | `l10n` |
| Controller focus graph | Auto-navigate focus by layout | Console UI | Common | `ui` |
| Optimistic UI | Show action instantly, reconcile later | Menus over network | Common | `ui` |
| Real progress reporting | Weight progress bars by actual work | Loading | Common | `boot` |
| Playable loading | Mini-game or free movement while loading | Long loads | Commonly cited Namco patent history | `boot` |

## 🚢 Production and shipping

Agent-specific loop: [agent dev cycle](18-agent-dev-cycle.md).

| Trick | How it works | Use when / cost | Known example | Module |
|---|---|---|---|---|
| Data-driven tuning | Keep numbers in text assets | All balance | Paradox, Bungie sandbox | `data` |
| Hot reload | Swap code or assets in a running game | Always | Lisp-based GOAL at Naughty Dog | `kernel.registry` |
| Console and cheats | Dev commands in non-shipping builds | Reach any state fast | Quake console | `ag` |
| Vertical slice | Build one complete piece first | Before scaling content | Universal | process |
| Grey-boxing | Prove a level with blocks | Before art | Universal | process |
| Replay debugging | Reproduce from seed plus inputs | Any deterministic system | RTS, fighting games | `replay` |
| Time-travel capture | Keep a ring buffer of states | Rare bugs | Modern engines | `sim.snapshot` |
| Crash capture | Save minidump, state and inputs | All shipped builds | Universal | `telemetry` |
| Frame budget | Give each system milliseconds | From day one | Universal | `ag profile` |
| Memory budgets | Assign MB per tag | Consoles, mobile | Universal | `kernel.memory` |
| Worst-case capture | Profile the heaviest scene | Before each milestone | Universal | `testing` |
| Shader pre-caching | Compile pipelines before gameplay | Stops stutter | PSO caches | `render.pipeline` |
| Permutation discipline | Keep the shader variant count small | Fast builds and loads | Modern engines | `render.material` |
| Content-addressed cook | Hash inputs, reuse results | Fast incremental builds | Modern pipelines | `assets.cook` |
| Patch-friendly layout | Stable, content-defined chunks | Smaller updates | Modern live games | `assets.pack` |
| Heatmaps | Log deaths and paths to a map | Level balance | Halo 3 commonly cited | `telemetry` |
| Automated playthroughs | Bots run levels each build | Regression | Sea of Thieves test talk | `testing` |
| Screenshot regression | Compare captures with a threshold | Render changes | Common | `testing` |
| Soak test | Run for hours looking for leaks | Pre-ship | Universal | `testing` |
| Feature flags | Toggle features remotely | Live ops | Universal | `liveops` |
| Frame pacing | Present at even intervals | Smooth at any fps | Modern platform APIs | `render.frame_pacing` |

## 🕰️ Famous constraint hacks, as lessons

| Hack | What happened | Lesson |
|---|---|---|
| Crash Bandicoot streaming | [Paged 64K chunks from disc, with 32 to 40 MB levels on a 2 MB machine](https://gamedeveloper.com/design/how-naughty-dog-broke-sony-s-hardware-rules-to-create-i-crash-bandicoot-i-) | Constrain the camera, then precompute what it can see |
| 1500 archers on a modem | [Synced commands because syncing units needed about 175 kB/s](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond) | Send causes, not results |
| Fast inverse square root | [A famous constant with a disputed author](https://en.wikipedia.org/wiki/Fast_inverse_square_root) | Hacks expire. Measure on today's hardware |
| Mario clouds and bushes | Widely reported to share one sprite with a palette swap | Reuse is invisible when context changes |
| Silent Hill fog | Commonly cited as draw-distance cover that became the mood | Make the limitation part of the art |
| Wing Commander exit crash | Widely reported: a memory error at exit was reworded into a thank-you message | Know when a harmless bug can ship, then fix it properly |
| Fallout 3 train hat | Widely reported: a moving train was an NPC wearing it as a hat | A strange hack that ships beats an ideal system that does not |
| F.E.A.R. squad talk | [A three-state FSM plus planning read as coordinated tactics](https://pages.cs.wisc.edu/~dyer/cs540/handouts/gdc2006_orkin_jeff_fear.pdf) | Perceived intelligence beats actual intelligence |
| Elite's galaxies | Commonly cited: galaxies generated from seeds in tiny memory | Store the recipe, not the output |

## 🤖 How an agent should use this

1. Name the problem, then find its section here.
2. Prefer the simplest row that meets the kit's budget.
3. Measure before and after with `ag profile --budget`.
4. For hidden assists, expose values in data so the developer can tune or remove them.
5. Disclose systems that affect fairness or paid outcomes, such as pity timers and competitive rubber-banding.
6. Verify an attribution before quoting it outside this catalogue.
