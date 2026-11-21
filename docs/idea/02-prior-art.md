# 🕹️ 2. What to steal: 30 years, every genre

Each genre solved one problem better than anyone else, and that solution belongs in the engine as a general primitive. The "Lands in" column names the AnyGame module that receives it ([section 3](03-architecture.md)).

## By genre

| Genre | Reference | Idea to steal | Lands in |
|---|---|---|---|
| Arena / tactical FPS | Quake, Source, Overwatch | Client prediction, server reconciliation, lag-compensated hit rewind, snapshot delta compression | `net.replication` |
| Fighting | GGPO, Killer Instinct, MK | Rollback: save state, predict input, re-simulate; frame data and hitboxes as data | `net.rollback`, `sim.fixed` |
| RTS | Age of Empires, StarCraft, Supreme Commander | Deterministic lockstep (send inputs, not state), flow-field pathing, fog of war, command queues | `net.lockstep`, `ai.nav` |
| Factory / automation | Factorio, Satisfactory | 100k+ active entities by sleeping idle ones, batch-simulating belts as segments, bit-exact cross-platform determinism | `ecs`, `sim.fixed` |
| Grand strategy / 4X | Paradox titles, Civilization | Whole game defined in moddable text data; event and modifier systems; tick-rate decoupled from frame | `data`, `gameplay.modifiers` |
| City builder / colony sim | Cities: Skylines, RimWorld, Dwarf Fortress | Agent simulation at scale, job/need systems, simulation LOD, emergent storytelling | `ai.utility`, `sim.lod` |
| Open-world action | GTA, RDR2, Spider-Man, Horizon | Sector streaming at traversal speed, ambient population that only exists near the player, physics-driven character reactions, GPU-driven procedural placement | `world.stream`, `world.population`, `anim.physical` |
| Racing | Gran Turismo, Forza, iRacing | Physics sub-stepping at 360 Hz+ independent of render, tyre models, ghost/replay from input logs | `sim.fixed`, `physics.vehicle` |
| Flight / space sim | MSFS, KSP, Elite, Star Citizen | 64-bit world coordinates, floating origin, nested physics grids (walking inside a moving ship), planet-scale streaming | `world.coords`, `physics.grids` |
| MMORPG | WoW, EVE, GW2, Star Citizen | Area-of-interest filtering, instancing and phasing, time dilation under load, state held outside the sim server so servers can crash or hand off | `net.mmo`, `persist` |
| Battle royale | Fortnite, PUBG, Apex | 100-player relevancy graphs, prioritised bandwidth budgets, huge map with destructible/buildable state | `net.replication` |
| MOBA | Dota 2, LoL | Data-driven ability system (effects, tags, cooldowns), perfect replays and spectating from input streams | `gameplay.abilities`, `replay` |
| Action RPG / soulslike | Dark Souls, Monster Hunter | Animation-driven combat: root motion, per-frame hit volumes, cancel windows authored on the timeline | `anim.events`, `gameplay.combat` |
| CRPG / JRPG | Baldur's Gate 3, Divinity, Persona | Systemic rules (surfaces, statuses interacting), quest/dialogue graphs, turn schedulers, deep save games | `gameplay.rules`, `narrative`, `persist` |
| Immersive sim | Thief, Deus Ex, Prey | Stimulus/response: objects emit "fire", "water", "noise"; anything can react. Sound propagation for AI perception | `gameplay.stim`, `ai.perception` |
| Stealth / tactical shooter | F.E.A.R., Halo, Hitman, The Last of Us | GOAP planners, behaviour trees, squad coordination, dense non-combat crowds | `ai.planning`, `ai.crowd` |
| Co-op horde | Left 4 Dead, Helldivers 2 | AI Director: pacing as a system that reads player stress and spawns accordingly | `ai.director` |
| Sports | EA FC, NBA 2K | Motion matching over huge mocap sets, physically blended contacts, ML-driven animation | `anim.matching` |
| Life sim | The Sims | Smart objects: the object advertises what an agent can do with it; utility AI picks | `ai.utility`, `gameplay.smartobjects` |
| Survival / voxel sandbox | Minecraft, Valheim, Teardown | Chunked editable worlds, voxel meshing, player-built structures with structural integrity, full destruction | `world.voxel`, `physics.destruction` |
| Physics sandbox | BeamNG, Noita, Tears of the Kingdom | Soft-body vehicles, per-pixel falling-sand simulation, physics objects as a combinable gameplay language | `physics.soft`, `sim.cellular` |
| 2D platformer | Celeste, Hollow Knight, Mario | Game feel as engine features: coyote time, input buffering, sub-pixel movement, hit-stop, pixel-perfect camera | `input.buffer`, `render2d`, `physics2d.kinematic` |
| Roguelike / procedural | Spelunky, Hades, No Man's Sky | Seeded generation, wave-function collapse, run state vs. meta state, everything reproducible from a seed | `pcg`, `rng` |
| Bullet hell / survivors-like | Touhou, Vampire Survivors | 50k sprites and colliders in one batch; pooled, cache-linear entities with no per-object overhead | `ecs`, `render2d.batch` |
| Puzzle / time manipulation | Braid, Baba Is You, Portal | Universal undo and rewind from state snapshots; rules as data; portal rendering and physics through seams | `sim.snapshot`, `render.portals` |
| Rhythm | Beat Saber, Guitar Hero | Audio clock is the master clock; latency calibration; sample-accurate scheduling | `audio.clock`, `time` |
| Narrative / visual novel / adventure | Ink, Ren'Py, SCUMM, Disco Elysium | A writer-facing script language that compiles to a state machine; localisation built in from the first line | `narrative`, `l10n` |
| Card / board / tactics | Hearthstone, Slay the Spire, XCOM, Into the Breach | Rules engine on a command stack: every action is a reversible, serialisable, server-verifiable command | `gameplay.commands`, `sim.turn` |
| Tower defence / auto-battler | Bloons, TFT | Deterministic sim that can run headless at 100x for balancing and AI playtesting | `sim.fixed`, `headless` |
| VR / AR | Half-Life: Alyx, Beat Saber | Late reprojection, fixed foveation, hand-presence physics, strict frame-time budgets | `xr`, `render.frame_pacing` |
| Mobile / idle / casual | Clash Royale, Genshin, Cookie Clicker | Tiny install and patch size, thermal and battery governors, offline progress computed from elapsed time, live-ops config | `platform.mobile`, `liveops` |
| UGC platforms | Roblox, Fortnite Creative, Dreams | Sandboxed scripting with CPU/memory quotas, in-game editor, content moderation hooks, publish in one click | `script.sandbox`, `ugc` |

## By engine

| Engine | Idea to steal |
|---|---|
| Unreal Engine 5 | Virtualised geometry (Nanite), dynamic GI with a cheap tier (Lumen Lite), virtual shadow maps, World Partition with one file per actor, Mass for crowds, Iris replication, PCG graphs, reflection-driven editor |
| RAGE (Rockstar) | One world, no loading; streaming tuned to vehicle speed; layered ambient simulation; physically reactive characters. Internals are not public, so AnyGame copies the observable behaviour, not the code |
| id Tech | Job system with no privileged main thread; brutal frame-time discipline; megatexture lessons (virtual texturing done right the second time) |
| Frostbite | Frame graph: the whole frame as a DAG of passes with automatic resource lifetime. Also the warning: an engine built for one genre hurts every other genre forced onto it |
| Decima (Guerrilla) | GPU procedural placement, node-graph everything, one editor for all disciplines |
| Naughty Dog | Fibre-based job system; frame-centric memory (tagged allocators freed per frame) |
| Source / Source 2 | Entity I/O that designers wire without code; the cleanest prediction/lag-compensation model; mod culture |
| Unity (DOTS) | Burst-style compiled jobs over ECS chunks; huge asset store proves the value of a package ecosystem |
| Godot | Scene-as-node-tree simplicity; text scene files that diff and merge; tiny footprint |
| Bevy | Every engine feature is a plugin added to an app; systems declare the data they read and write, so the scheduler parallelises safely |
| The Machinery / Bitsquid | Plugins are DLLs that register structs of function pointers in a versioned API registry; C ABI; hot reload of engine code |
| O3DE / Lumberyard | "Gems" as distributable modules with dependencies; cautionary tale on build complexity |
| Factorio / custom indie engines | A small engine written for exactly one simulation model beats a general engine at that model. Hence: swappable simulation models |
| Roblox | The engine is a service: cloud-hosted, scripted, multiplayer by default |
