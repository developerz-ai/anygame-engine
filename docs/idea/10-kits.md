# 🎮 10. Genre kits and reference builds

A genre kit is a package that selects modules, sets conventions and ships a playable template; it is where the "specialisation" lives, so the kernel never has to know what an FPS is.

## Kits

| Kit | Loop | Netcode | Signature modules |
|---|---|---|---|
| `kit.platformer2d` | fixed | none / rollback | Kinematic controller, tilemaps, input buffering, pixel camera |
| `kit.topdown2d` | fixed | replication | Tilemaps, 2D lighting, inventory |
| `kit.fighting` | deterministic | rollback | Frame data editor, hitbox tools, training mode |
| `kit.fps` | fixed | replication | Lag compensation, weapon framework, bot AI |
| `kit.thirdperson` | fixed | optional | Motion matching, camera rigs, melee combat timeline |
| `kit.rts` | deterministic | lockstep | Flow fields, fog of war, selection and command UI, replays |
| `kit.racing` | fixed, sub-stepped | replication | Vehicle physics, track tools, ghosts, rubber-band-free net smoothing |
| `kit.openworld` | fixed | optional | Streaming, population, traffic, missions, day/night, wanted-level style systems |
| `kit.rpg` | variable / turn | optional | Quests, dialogue, stats, saves, party |
| `kit.cardgame` | turn | server-authoritative commands | Rules engine, deck data, animation queue |
| `kit.builder` | deterministic | lockstep | Grid placement, agent sim, production chains |
| `kit.survival` | fixed | replication | Voxel or heightfield terrain, crafting, building, needs |
| `kit.narrative` | variable | none | Script language, branching, localisation, backlog |
| `kit.mmo` | fixed | mmo | Full backend, zones, instancing, economy, guilds |
| `kit.mobile-casual` | variable | async services | Small binary, live ops, offline progress, store integration |

Kits compose: GTA Online is roughly `kit.openworld` + `kit.fps` + `kit.racing` + `kit.mmo`.

## Reference builds: could it carry these games?

These are architecture stress tests, not products to recreate.

| Game shape | Hard requirements | AnyGame answer | Remaining risk |
|---|---|---|---|
| WoW-style MMORPG | Thousands of players per zone, instanced dungeons, phasing, tab-target and action combat, auction house, 20-year persistence | `net.mmo` with area-of-interest grid; zones as server processes; data layers for phasing; ability system; economy, jobs, social; schema migrations for long-lived data | Capital-city crowds: needs replication LOD and possibly time dilation |
| NFS-style online racer | 60 Hz+ feel at 300 km/h, open city streaming, ghosting and collisions between players with 80 ms latency, seamless free-roam sessions | Sub-stepped vehicle physics; predictive streaming along the road graph; `net.replication` with extrapolation and collision arbitration; matchmaking and free-roam instancing | Vehicle-to-vehicle collision fairness under latency is a design problem as much as a technical one |
| Assassin's Creed-style | Dense historical city, parkour on any surface, crowds of hundreds, stealth AI, long single-player campaign | Virtualised geometry; motion matching plus traversal markup generated from geometry; crowd instancing with simulation LOD; perception and planner AI; quest and save systems | Parkour quality is authored animation data, thousands of clips |
| GTA 6-style | Seamless state-sized map, interiors, traffic and pedestrians with believable routines, physical characters and vehicles, ray-traced lighting, missions | `kit.openworld`: 64-bit world, streaming, three-band population, traffic lanes, active ragdolls, RT GI tier, data layers for mission state | Content scale; simulation density per frame at console budgets |
| GTA Online-style | The above, shared by 30+ players, with persistent characters, property, economy, user-made jobs, constant live updates | Add `net.replication` with relevancy, entity ownership migration for vehicles and physics props, `persist`, `economy`, `liveops`, `ugc` | Cheating: needs server authority that the original peer-heavy design lacked |

## What public analysis says about GTA 6

As of 2026-11: GTA 6 launched on consoles this week, and Rockstar has published no engine internals, so the only legitimate sources are frame analysis and observation.

- Digital Foundry's review found ray-traced global illumination and ray-traced reflections on every console version, with ray-traced shadows added on PS5 Pro, at a 30 fps target and roughly 1440p base resolution (summary, KitGuru).
- **Lesson 1: lighting is fully dynamic.** No baked lightmaps means the world can change (time, weather, destruction, interiors) without re-baking. AnyGame's high-end tier is designed the same way, with the probe-based tier as fallback.
- **Lesson 2: the frame budget goes to simulation density** (NPCs, traffic, physics, interiors), and Rockstar accepted 30 fps to pay for it. AnyGame must let a game make that trade explicitly: per-module time budgets visible in one profiler.
- **Lesson 3: RAGE was originally a set of components,** and Rockstar's lead artist described the modern engine as effectively a finished game that each new title builds on (TechRadar interview). That is the genre-kit idea: the reusable asset is the open-world game layer, not just the renderer.

## On reverse engineering

Useful, legal sources: frame-capture studies such as Adrian Courrèges's GTA V graphics study and his compilation of other games, GDC and SIGGRAPH talks, modding-community documentation of file formats, and open engines (id Tech releases, Godot, O3DE, Bevy). Leaked source code and decompiled binaries must stay out of the project: one contributor who has read them can taint the codebase legally. The contribution policy says so from day one: [CONTRIBUTING.md](../../CONTRIBUTING.md).
