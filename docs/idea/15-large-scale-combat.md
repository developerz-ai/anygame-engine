# 🪖 15. Large-scale combat

**Rule: the server owns every shot, every plate and every collapse. Clients get only what they can perceive, at a rate set by how much it matters to them.**

Scope: 64+ players, infantry and vehicles, large maps, destructible terrain. As of 2026-11. These games are architecture references only. AnyGame kits and samples use original names, vehicles, art and maps.

## 🔎 Evidence labels

| Label | Meaning |
|---|---|
| **Primary** | Developer or vendor page, opened for this doc |
| **Press** | Interview or news page, opened for this doc |
| **Excerpt** | Search excerpt only. The page blocked automated reading, so re-check it |
| **Unverified** | Community claim or inference. Do not design on it without a measurement |
| **Proposal** | AnyGame design, not a claim about any game |

## 🎯 What to steal

| Game / engine | Technique | Evidence | Lands in |
|---|---|---|---|
| Battlefield 6 (Frostbite) | Part-based destruction and debris spawning built to be extensible, so collapse feeds other gameplay such as damage to players underneath | Primary: [EA](https://www.ea.com/news/how-battlefield-6-redefined-destruction) | `world.destruction`, `gameplay.stim` |
| Battlefield 6 (Frostbite) | Destruction events get their own network treatment: bandwidth optimisation, prioritisation, and culling of part destruction and debris spawning | Primary: [EA](https://www.ea.com/news/how-battlefield-6-redefined-destruction) | `net.replication`, `world.destruction` |
| Frostbite 2 | Destruction masks from signed volume distance fields, placed with spheres, replacing a UV-map workflow for each destructible part | Primary: [SIGGRAPH 2010](https://www.advances.realtimerendering.com/s2010/Kihl-Destruction%20in%20Frostbite(SIGGRAPH%202010%20Advanced%20RealTime%20Rendering%20Course).pdf) | `render.destruction` |
| Battlefield 2042 | 45 Hz server tick on PC, PS5 and Xbox Series X/S | Press: [MP1st](https://mp1st.com/news/battlefield-2042-tick-rate-changes-and-ping-value-in-scoreboard-not-in-the-cards-for-now) | Budget reference |
| World of Tanks | Spotting tests specific points on the vehicle, not its whole silhouette | Primary: [Wargaming](https://worldoftanks.com/en/news/general-news/20-secrets) | `net.spotting` |
| World of Tanks | Spotting checks run less often at longer range | Primary: [Wargaming](https://worldoftanks.com/en/news/general-news/20-secrets) | `net.spotting` |
| World of Tanks | Penetration compared with armour along the surface normal, plus dispersion on every shot | Excerpt: [Wargaming wiki](https://wiki.wargaming.net/cs/Gunnery_%26_Armor_Penetration_(WoT)) | `gameplay.armor`, `physics.ballistics` |
| War Thunder (Dagor) | Vehicles are a collision model of named modules and crew. Armour protects them, and destroying key modules or crew destroys the vehicle | Primary: [Gaijin](https://warthunder.com/en/news/384-Developers-Diaries-Ground-Forces-Damage-Model-Part-2-en) | `gameplay.armor` |
| War Thunder | Armour groups carry thickness, material and structural strength as data | Primary: [Gaijin](https://warthunder.com/en/news/384-Developers-Diaries-Ground-Forces-Damage-Model-Part-2-en) | `gameplay.armor` |
| War Thunder | Penetration from published formulas (DeMarr, Lanz-Odermatt), openly adjusted for gameplay | Primary: [Gaijin](https://warthunder.com/en/news/6010-development-improved-calculation-of-armour-penetration-in-the-game-en) | `physics.ballistics` |
| Dagor Engine | Engine and tools published as source under BSD 3-Clause, so it is a legal reference when credited | Primary: [GitHub](https://github.com/GaijinEntertainment/DagorEngine) | Prior art |
| PlanetSide 2 (ForgeLight) | Developer claim of 2,000 players per server and 200+ on screen. Treat as a marketing ceiling | Press: [Shacknews](https://shacknews.com/article/78613/sony-online-entertainment-to-use-planetside-2-engine-for-all) | `net.mmo` stress target |
| Arma Reforger (Enfusion) | Ownership and authority are separate concepts: ownership can move, authority stays put | Excerpt: [BI wiki](https://community.bistudio.com/wiki/Arma_Reforger:Multiplayer_Scripting) | `net.replication` |
| Foxhole | Profile the server under realistic load: real save game plus many bot clients. Some costs appeared only at 128+ players | Primary: [Siege Camp](https://www.foxholegame.com/post/devblog-58) | `testing`, `telemetry` |
| Hell Let Loose | Large AI populations used to test and tune netcode for 100 players | Excerpt: [PCGamesN](https://www.pcgamesn.com/hell-let-loose/hell-let-loose-50v50) | `testing` |
| Unreal Replication Graph | Shared per-cell actor lists, so each actor stops evaluating every connection. Epic cites 100 players and about 50,000 replicated actors | Primary: [Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine) | `net.replication` |

**Could not establish from public sources:** Squad's replication design, PlanetSide 2's hit-validation model, World of Tanks' server internals, and how Battlefield schedules per-entity updates. A community post claims [some entities update at 5 Hz](https://forums.ea.com/discussions/battlefield-2042-general-discussion-en/server-tickrate/7001040/replies/7001058) (Unverified).

## 🧰 Proposal: `kit.combined-arms`

| Field | Choice | Why |
|---|---|---|
| Loop | `loop.fixed`, 60 Hz simulation, physics sub-stepped per vehicle class | Vehicles need stable physics. Full determinism is too costly at this entity count |
| Netcode | `net.replication` with server authority | Every client is untrusted, and players join and leave mid-match |
| Scale path | `net.mmo` for persistent wars | Same components and annotations |
| World | `world.stream`, `world.coords`, `world.destruction` | Large maps that change during play |
| Damage | `physics.ballistics`, `gameplay.armor` | Data-driven and server-verifiable |
| Perception | `net.spotting` | Fog of war enforced before replication |
| Vehicles | `physics.vehicle`, seats, turrets, crew roles | Infantry and vehicles share one entity model |
| AI | `ai.nav`, `ai.planning`, bot clients | Fill matches and generate load tests |
| Sample | One small original game with fictional vehicles | Each kit ships a complete game |

### New modules

| Module | Owns | Interface sketch |
|---|---|---|
| `physics.ballistics` | Projectile flight, drag, drop, penetration curves | Batch step over projectile arrays, returning hit records |
| `gameplay.armor` | Plates, modules, crew, damage resolution | Hit record + vehicle damage asset → ordered damage events |
| `world.destruction` | Part graph, structural support, debris classes | Damage event → destruction events |
| `render.destruction` | Masks, detail meshes, debris visuals | Reads destruction state. Never affects simulation |
| `net.spotting` | Per-team visibility and per-client filtering | Entity + observer set → visible set |

Each is an interface with a simple and a full implementation, per [section 8](08-simulation.md).

## 🎯 Server-authoritative hit and armour model

Pipeline (Proposal), all on the server:

| Step | Input | Output | Rule |
|---|---|---|---|
| 1. Intent | Timestamped fire input | Validated shot | Check ammo, reload, turret limits, seat |
| 2. Rewind | Shot time, bounded client latency | Past hit volumes | Cap the rewind window. Beyond it, the shot resolves at present time |
| 3. Flight | Muzzle state, seeded dispersion | Trajectory | RNG is server-side, seeded per shot, and logged |
| 4. Impact | Trajectory, armour mesh | Plate, angle, effective thickness | Resolve in plate order |
| 5. Penetration | Shell data, plate data | Pass, fail or ricochet | Pure function of data |
| 6. Damage | Residual energy, modules, crew | Damage events | Ordered and logged |
| 7. Feedback | Damage events | Replicated outcome | Client shows prediction, server confirms |

Rules:

- **Client predicts effects, never outcomes.** Muzzle flash and tracers are immediate. Damage waits for the server.
- **Damage resolution is a pure function.** Same shell, plate, angle and seed give the same result, so it can be unit-tested and replayed offline.
- **All tuning is data.** Shells, plates and modules are schema-described text assets. Formula constants are data too.
- **Log every resolved shot** with its inputs. This powers kill-cams, bug reports and the [fair-play detectors](09-online.md#fair-play-an-opinionated-stance).
- **Tell the player why.** Emit a structured reason (`ricochet`, `no_penetration`, `module_hit`) for UI and agent tests.

## 💥 Destruction replication

Rule: **replicate the cause and the resulting part state. Never replicate debris.**

| Data | Authority | Replicated as | Reliability |
|---|---|---|---|
| Part state (intact, damaged, destroyed) | Server | Compact bitset per destructible object | Reliable, delta-compressed |
| Destruction event | Server | Object id, part id, seed, impulse | Prioritised by distance and visibility |
| Gameplay-relevant collision | Server | Derived from part state | Must match on server and client |
| Cosmetic debris and particles | Client | Not replicated, spawned from event seed | None |
| Large scripted collapse | Server | Start tick + seed, then plays locally | Reliable |

Rules:

- **Late joiners rebuild from part state,** not from an event history.
- **Debris that blocks movement or shots is gameplay,** so it needs server authority. Everything else is cosmetic.
- **Cull by relevance.** A far collapse is sent as final state, without its intermediate events.
- **Budget it.** A burst of explosions must not starve player movement updates. Destruction has its own bandwidth class.
- **Change detection comes free** from per-chunk column tracking in the [kernel](04-kernel.md).

## 👁️ Spotting and fog of war

Rule: **a client cannot leak what it never received.** Visibility runs on the server before replication.

| Stage | What it does |
|---|---|
| Broad phase | Spatial grid selects candidates within the maximum spotting range |
| Check schedule | Near pairs check often, far pairs rarely |
| Line of sight | Rays to several points on the target, against terrain and destruction state |
| Concealment | Foliage, smoke, movement and firing modify detection |
| Team share | Spotted state propagates to the team through a typed channel |
| Filter | Only visible entities enter that client's replication list |
| Grace period | Keep sending briefly after loss of sight to prevent pop-in |

Costs to design for:

- **Peeker's advantage.** Late reveal can make enemies pop in. Send slightly early for entities about to become visible.
- **Audio leaks position.** Filter sound events by the same rules.
- **Destruction changes sight lines.** A collapsed wall must invalidate cached visibility.
- **Batch rays.** Run per-cell jobs over arrays. Never one query per pair per tick.

## 📊 Tick and bandwidth budgets

All numbers here are **Proposals** for a 128-player match, to be measured in CI.

| Budget | Target | Derivation |
|---|---|---|
| Simulation tick | 60 Hz | 16.67 ms per tick |
| Snapshot send rate | 30 Hz | Every second tick |
| Downstream per client | 256 kbit/s | 32,000 B/s |
| Snapshot size | about 1,066 B | 32,000 ÷ 30, fits one typical UDP packet |
| Server egress per match | about 33 Mbit/s | 128 × 256 kbit/s |

Server frame allocation at 60 Hz:

| System | Budget (ms) |
|---|---|
| Input and validation | 1.0 |
| Vehicles and physics | 5.0 |
| Ballistics and damage | 1.5 |
| Destruction | 1.0 |
| Spotting | 1.5 |
| AI | 1.5 |
| Replication | 3.0 |
| Reserve | 2.17 |
| **Total** | **16.67** |

Update rate by relevance:

| Band | Entities | Rate |
|---|---|---|
| Critical | Own vehicle, current target, shooter | Every snapshot (30 Hz) |
| Near | Visible and close | 15 to 30 Hz |
| Mid | Visible and far | 5 to 10 Hz |
| Far | Spotted on map only | 1 to 2 Hz, position only |
| Hidden | Not perceived | Not sent |

## ✅ Proof checks for the kit

- 128 headless bot clients complete a match with p99 server tick under 16.67 ms.
- p99 downstream stays under 256 kbit/s per client during a scripted mass-destruction event.
- A packet capture shows no state for any entity the client cannot perceive.
- The same shot inputs and seed resolve to identical damage events across 10,000 replayed shots.
- A client joining mid-match matches the server's part-state hash.
- A modified client cannot deal damage outside the server's validation rules.
