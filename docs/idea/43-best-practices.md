# 🏆 43. Game dev best practices: start here

**The map of everything AnyGame knows about making games.** Find the task, read the one doc it names, and use the existing block before writing anything new. All of it is default guidance a game can override ([rule 8](01-thesis.md#design-rules)).

## I need to...

| Task | Read | Then use |
|---|---|---|
| Turn an idea into a plan | [One prompt to a game](26-one-prompt-to-game.md), [idea to distribution](25-idea-to-distribution.md) | `ag new`, a kit |
| Design the game or a level | [Game and level design](41-game-and-level-design.md) | Bots, balance sims |
| Organise the project | [Project organisation](24-project-organization.md) | Default layout |
| Find an existing block | [Primitives](23-primitives.md) | `ag find` |
| Solve a known problem | [Thirty years of tricks](20-tricks-30-years.md) | Symptom finder |
| Add NPCs or enemies | [NPCs and AI](36-npcs-and-ai.md) | `ai.*` blocks |
| Add abilities, items, quests, progression | [Gameplay mechanics](37-gameplay-mechanics.md) | `gameplay.*` blocks |
| Add collision, vehicles, ragdolls | [Physics](38-physics.md) | `physics.*` adapters |
| Make it feel good | [Animation, camera and feel](39-animation-camera-feel.md) | `anim.*`, `camera`, `input` |
| Add sound and music | [Audio](40-audio.md) | `audio` |
| Build menus, HUD, settings | [UX, accessibility, localisation](42-ux-accessibility-localization.md) | `ui`, `l10n`, `accessibility` |
| Render it | [Rendering](06-rendering.md), [next-gen techniques](17-next-gen-techniques.md) | Render graph |
| Offer pixel art, retro or several looks | [Visual modes](44-visual-modes.md) | Render presets, look packages |
| Use threads safely | [Concurrency](45-concurrency.md) | Job graph |
| Scale servers or build an MMO | [Distributed servers](46-distributed-servers.md) | Zones, fleet, replication layer |
| Build a large world | [World](07-world.md), [load, cache, unload](34-resource-lifecycle.md) | `world.*` |
| Build a single-player or offline game | [Single-player, local and offline](49-single-player-offline.md) | Local World, saves |
| Add multiplayer | [Client and server models](35-client-server-models.md), [online stack](09-online.md) | `net.*`, backend |
| Add layers, rejoin, replays or spectators | [Layers, rejoin, replay, spectate](47-layers-rejoin-replay-spectate.md) | World copies, recorder, relay |
| Build a competitive shooter | [Tactical shooters](48-tactical-shooters.md) | `kit.fps` |
| Build big-battle combat | [Large-scale combat](15-large-scale-combat.md) | Combat blocks |
| Add mods | [Scripting, modding, tools](11-scripting-modding-tools.md) | Packages |
| Write engine C++ | [C++ decisions](29-cpp-decisions.md), [C++23 craft](16-cpp23-craft.md) | `bin/check` |
| Choose a library or profiler | [Libraries and profilers](28-libraries-and-profilers.md) | One default per need |
| Make it fast and small | [Small and fast](21-small-and-fast.md), [quality bar](32-quality-bar.md) | `ag profile` |
| Port to a platform | [Platforms](30-platforms.md) | `platform.*` |
| Ship and operate | [Idea to distribution](25-idea-to-distribution.md) | `ag publish` |

## The big decisions come with primitives

**The hardest calls in game development should not fall on each developer or agent alone.** For each one, AnyGame provides a ready primitive, a sensible default and the guidance to choose differently. The game always has the final say.

| Big decision | Primitive provided | Default | Guidance |
|---|---|---|---|
| How does time work? | `loop.*` | Chosen by the kit | [Kernel](04-kernel.md) |
| How is state stored? | ECS, components, handles | Archetype ECS | [Kernel](04-kernel.md) |
| How is memory managed? | Arenas, pools, tagged heaps | By lifetime | [C++ decisions](29-cpp-decisions.md) |
| How do we use all the cores? | Job graph, workers | Declared reads and writes | [Concurrency](45-concurrency.md) |
| Offline, local or online? | Modes in the manifest | Offline unless the game opts in | [Single-player and offline](49-single-player-offline.md) |
| Who has authority? | `net.*`, authority profiles | Chosen by the kit | [Client and server](35-client-server-models.md) |
| How does it scale? | Zones, instances, hand-off, fleet | Smallest step that fits | [Distributed servers](46-distributed-servers.md) |
| How is data saved? | `persist`, migrations, snapshots | Versioned schemas | [Online stack](09-online.md) |
| How does content load? | Resource lifecycle | On demand, with fallbacks | [Load, cache, unload](34-resource-lifecycle.md) |
| How should it look? | Render presets, looks | Chosen by the game | [Visual modes](44-visual-modes.md) |
| How do NPCs think? | FSM, BT, utility, planners | Simplest that works | [NPCs and AI](36-npcs-and-ai.md) |
| How do mechanics work? | Attributes, effects, abilities | Data-driven | [Gameplay mechanics](37-gameplay-mechanics.md) |
| Which physics? | Physics ports and adapters | Kinematic, then a wrapped solver | [Physics](38-physics.md) |
| Which libraries? | Adapters | One default per need | [Libraries](28-libraries-and-profilers.md) |
| How do we know it is good? | Bots, budgets, `ag verify` | On from day one | [Quality bar](32-quality-bar.md) |

## The twelve habits of a good game build

1. **Find the fun first.** Build the smallest playable loop before any content.
2. **Keep it playable at every commit.**
3. **Reuse before you build.** Use, configure, compose, wrap, replace, and only then write new.
4. **Put tuning in data.** Designers and agents should change a number without a rebuild.
5. **Make the server decide** in online games, and send clients only what they may know.
6. **Budget from day one** on the weakest supported device.
7. **Do less work** before making work faster.
8. **Test what players do.** Bots play the game, not just unit tests.
9. **Make every bug replayable** with a seed and an input log.
10. **Give feedback for every action.** Sight, sound and timing.
11. **Design for everyone.** Remapping, subtitles, readable UI and difficulty options are basics.
12. **Respect the player.** No dark patterns, no hidden data collection, and no paying to escape designed frustration.

## Checks by stage

| Stage | Must be true |
|---|---|
| Prototype | A person can play the core loop, and a bot can complete it |
| Vertical slice | One level at final quality holds budget on the worst target |
| Production | Each feature has a test, tuning data and a reported cost |
| Alpha | Every feature exists, and bots finish the game |
| Beta | Balance sims pass, soak tests pass, accessibility basics are present |
| Release | No blockers, old saves load, stores' checks pass, a human approves |
| Live | Crash rate is watched, patches are small, and rollback is one command |

## What a machine cannot judge

Agents can measure almost everything here, but a person decides whether the game is fun, whether the art has a point of view, and whether the story lands. Agents should put a playable build in front of that person early and often.
