# 🧱 23. Primitives: client and server, ready to use

**AnyGame ships the full stack for a game: client, game server and backend, from one project and one schema.** An agent declares what the game is. The engine supplies the rest on each side. Every primitive is an [adapter-based](05-extending.md#adapters-the-shape-of-every-integration) default a game can replace or leave out.

Planned design as of 2026-11. Build order: [primitives by phase](../build/primitives-by-phase.md).

## The twelve things an agent declares

Everything in a game is one of these. Like [Ultimate](18-agent-dev-cycle.md#ultimate-but-for-games)'s primitives, each declaration projects everywhere it is needed.

| Primitive | What it is | Runs on |
|---|---|---|
| `component` | Schema-described data on an entity | Client, server |
| `system` | Logic over a query, with declared reads and writes | Client, server, or both |
| `event` | Typed fact that something happened | Client, server |
| `command` | Player or agent intent, validated by the authority | Sent by client, decided by server |
| `asset` | Versioned content with a schema | Cooked per target |
| `prefab` | Reusable entity template | Client, server |
| `world` | Scene, level or match built from code or data | Client, server |
| `service` | Typed RPC outside the simulation | Server |
| `job` | Durable background work | Server |
| `policy` | Who may do or see what | Server, enforced on every path |
| `migration` | Upgrade for saved data, schemas or protocol | Client, server |
| `test` | Headless gameplay check with bots | CI, local |

### One declaration, every side

```cpp
// Illustrative, the API is not final.
struct [[ag::component, ag::replicated]] Health {
    [[ag::predicted, ag::quantise(0.1)]] float current;
    [[ag::owner_only]] float regen;
    float max;
};
```

| That declaration provides | Where |
|---|---|
| Storage, queries, change detection | Client, server |
| Save and load, with migrations | Client, server, database |
| Network replication, prediction, interest filtering | Client, server |
| Lua bindings and HUD data binding | Client, server scripts |
| `ag describe`, `ag query`, MCP access | Tooling |
| Replay, snapshot and rollback | Client, server |
| Test fixtures | CI |

## Shared by client and server

| Area | Primitives |
|---|---|
| Foundation | Allocators, handles, jobs, clocks, RNG, logging, errors, maths, config |
| Data | ECS, relationships, queries, events, schema, serialisation, migrations |
| Simulation | Loops, snapshots, replay, physics 2D/3D, collision queries, navigation |
| Gameplay | Abilities, effects, attributes, inventory, damage, timers, state machines, rules, quests, dialogue |
| AI | FSM, behaviour trees, utility, planners, perception, director |
| World | Coordinates, partitioning, data layers, streaming queries, PCG |
| Scripting | Sandboxed VM, quotas, generated bindings |
| Content | Packages, [on-demand loading, caching and unloading](34-resource-lifecycle.md), mods, hot reload |
| Netcode | Transport, rollback, lockstep, replication, prediction, MMO |

## Client: the game

| Area | Primitives |
|---|---|
| Rendering | RHI, render graph, 2D, 3D tiers, materials, lighting, VFX, upscaling, frame pacing |
| Animation | Clips, blending, IK, motion matching, cloth, physical animation |
| Audio | Mixer, buses, spatial audio, music, voice |
| Input | Actions, rebinding, gamepad, touch, gyro, haptics, buffering |
| UI | HUD, menus, data binding, layout, immediate-mode debug, fonts |
| Camera | Rigs, shake, collision, split screen |
| Presentation | Interpolation, client prediction, reconciliation, sequencer, subtitles |
| Player services | Local saves, settings, l10n, accessibility, photo mode, replay viewer |
| Platform | Windowing, lifecycle, storage, achievements, store, overlays, thermal governor |
| Shipping | Boot flow, patcher, crash capture, on-demand content |

## Game server

| Area | Primitives |
|---|---|
| Hosting | Headless runtime, dedicated server, listen server, session lifecycle, graceful drain |
| Authority | [Authority profiles, per-field visibility](35-client-server-models.md), command validation, movement and hit validation, lag compensation, server fog of war |
| Replication | Delta compression, relevancy, priority and bandwidth budgets, interest management |
| Scale | [World copies](47-layers-rejoin-replay-spectate.md), [zones](46-distributed-servers.md), instancing, phasing, entity hand-off, replication layer, time dilation |
| Reliability | Crash replacement, reconnect, state recovery, tick budget enforcement |
| Fair play | Replay verification, server detectors, trust scores, cheater-pool matching |
| Observability | Per-tick metrics, traces, match recording, admin commands |
| Testing | Bot clients, load tests, soak tests, simulated latency and packet loss |

## Backend

| Area | Primitives |
|---|---|
| Accounts | Identity, platform login, sessions, parties, presence |
| Matchmaking | Tickets, rules, lobbies, backfill, regions, trust input |
| Fleet | Start, scale, drain, regions, local process manager, orchestrator adapter |
| Data | Persistence, migrations, cache, cloud saves, leaderboards, match history |
| Async | Durable jobs, cron, pub/sub, idempotency |
| Economy | Wallets, inventory, trades, ledger, purchase reconciliation |
| Social | Friends, guilds, chat, mail, reporting, moderation |
| Live ops | Remote config, flags, events, A/B tests, content patches, workshop |
| Telemetry | Metrics, logs, traces, crash dumps, analytics |

For a website, portal or admin UI on top, [Ultimate is the suggested option](19-companion-tools.md).

## A huge catalogue, a tiny build

**Give agents a lot to work with. Ship only what the game loads.** The catalogue should keep growing, because every block in it is something no agent has to rebuild, and an unused block costs a game nothing.

| What agents get | Examples |
|---|---|
| Engine blocks | Everything in the tables above |
| Ready-made gameplay blocks | Character controllers, weapons, projectiles, melee, vehicles, turrets, doors, ladders, pickups, checkpoints, spawners, health, status effects, crafting, building, shops, loot tables, cooldowns, wave spawners, objectives, scoring, fog of war, minimaps, day/night, weather |
| Game-feel blocks | Coyote time, input buffering, hit-stop, trauma shake, aim assist, juice presets |
| AI blocks | Patrol, chase, flee, cover, squads, crowds, traffic, formations, companions, directors, ready-made bots |
| World blocks | Dungeon, terrain, road, city, biome and maze generators, auto-tiling |
| UI blocks | HUD widgets, inventory, menus, settings, lobby, scoreboard, chat, dialogue box, tutorial prompts |
| Online blocks | Lobby flows, parties, ranked matchmaking, leaderboards, seasons, battle-tested server templates |
| Kits and sample games | One complete, original, playable game per kit |
| Recipes | Short task guides: "add double jump", "add ranked mode", "make it run on a phone" |
| Knowledge | [Tricks](20-tricks-30-years.md), [techniques](17-next-gen-techniques.md), genre notes |
| Verification | Conformance suites, bots, balance sims, load tests, screenshot checks |

**Every block ships ready for an agent:**

| Part | Why |
|---|---|
| `AGENTS.md`: purpose, invariants, how to test | Understood without reading all the source |
| Schema and `ag describe` entry | No guessed APIs |
| Runnable example | A working pattern to copy |
| Tests, and a conformance suite if it has a port | Proof it works and stays working |
| Declared CPU, memory and size cost | The price is known before loading it |
| Tunable data | Most changes need no code |
| Client and server behaviour stated | Works online or says it does not |

Blocks stay small and composable. A block never assumes a genre, and a game can take one, change it, or ignore it.

## How a game uses them

- **Single-player:** client only, fully offline. No server or backend code ships ([single-player and offline](49-single-player-offline.md)).
- **Local or listen server:** the same simulation runs in a second World in-process.
- **Dedicated server:** the same game without render, audio and input modules.
- **Full online:** `ag dev` runs client, server, database and jobs on one machine, then deploys through fleet adapters.

| Rule | Shape |
|---|---|
| **One codebase, both sides** | Shared logic is written once and built per target |
| **Client code never reaches the server binary** | And server-only logic and secrets never ship to players |
| **The client sends intent, the server decides** | Default for online games, with prediction for responsiveness |
| **Load only what is used** | Each primitive not in the manifest costs nothing |
| **Replace any of it** | A game can use its own server, backend or netcode through the same ports |
