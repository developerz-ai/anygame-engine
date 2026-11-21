# 💡 Idea

The AnyGame architecture blueprint, one section per file. Blueprint date: 2026-11-21. This is the **why and what**. **For any game task, start at [best practices](43-best-practices.md).** The order of work is in [../build/](../build/README.md).

| # | Doc | Read before |
|---|---|---|
| 1 | [Thesis](01-thesis.md) | Anything. Holds the objective and twelve design rules |
| 2 | [Prior art](02-prior-art.md) | Designing a module: what each genre and engine solved |
| 3 | [Architecture](03-architecture.md) | Project layout, generators, platforms |
| 4 | [Kernel](04-kernel.md) | Memory, jobs, ECS, reflection, clocks |
| 5 | [Extending](05-extending.md) | Plugin API, registry, packages |
| 6 | [Rendering](06-rendering.md) | RHI, render graph, 2D, 3D tiers, UI, VFX |
| 7 | [World](07-world.md) | Coordinates, streaming, simulation LOD, PCG |
| 8 | [Simulation](08-simulation.md) | Physics, animation, AI, audio, gameplay |
| 9 | [Online](09-online.md) | Netcode, servers, backend, fair play |
| 10 | [Kits](10-kits.md) | Genre kits and reference builds |
| 11 | [Scripting, modding, tools](11-scripting-modding-tools.md) | Lua, mods, HUD, assets, code-first tooling |
| 12 | [AI-first](12-ai-first.md) | `ag`, MCP, agent inner loop |
| 13 | [Engineering practices](13-engineering-practices.md) | Budgets, CI enforcement, performance targets |
| 14 | [Risks](14-risks.md) | Scope calls and what not to build |
| 15 | [Large-scale combat](15-large-scale-combat.md) | Vehicles, armour, destruction, high player counts |
| 16 | [C++23 craft](16-cpp23-craft.md) | Writing any engine C++: memory, RAII, sanitizers, testing |
| 17 | [Next-gen techniques](17-next-gen-techniques.md) | Choosing a technique, or whether to build or wrap a library |
| 18 | [Agent dev cycle](18-agent-dev-cycle.md) | Designing any command, error or test |
| 19 | [Companion tools](19-companion-tools.md) | Adding a website, generated assets or media (optional) |
| 20 | [Thirty years of tricks](20-tricks-30-years.md) | Solving any game problem: check whether it was already solved |
| 21 | [Small and fast](21-small-and-fast.md) | Adding anything that costs size, memory, time or energy |
| 22 | [Future-ready](22-future-ready.md) | Any public API, file format, wire format or dependency |
| 23 | [Primitives](23-primitives.md) | Building anything: the full client, server and backend catalogue |
| 24 | [Project organisation](24-project-organization.md) | Starting or structuring a game: layout and where things go |
| 25 | [Idea to distribution](25-idea-to-distribution.md) | Planning, managing, releasing or operating a game |
| 26 | [One prompt to a game](26-one-prompt-to-game.md) | The target experience: "build a game like X" |
| 27 | [The flywheel](27-flywheel.md) | How each game built makes the engine better for the next |
| 28 | [Libraries and profilers](28-libraries-and-profilers.md) | Picking an allocator, library or profiler |
| 29 | [C++ decisions](29-cpp-decisions.md) | Writing any C++: the answers are already chosen |
| 30 | [Platforms](30-platforms.md) | Anything OS-specific: Linux, Windows, macOS, Android, iPhone, browser |
| 31 | [No regrets](31-no-regrets.md) | Any choice affecting licensing, lock-in, upgrades or trust |
| 32 | [Quality bar](32-quality-bar.md) | SOLID vs performance, and what "done" means |
| 33 | [Architecture map](33-architecture-map.md) | Deciding where code goes and what may depend on what |
| 34 | [Load, cache, unload](34-resource-lifecycle.md) | Anything that loads: lazy loading, streaming, caching, eviction |
| 35 | [Client and server models](35-client-server-models.md) | Any online feature: authority, visibility, reconnects, spectators |
| 36 | [NPCs and AI](36-npcs-and-ai.md) | Enemies, companions, crowds, directors, LLM NPCs |
| 37 | [Gameplay mechanics](37-gameplay-mechanics.md) | Abilities, damage, items, loot, progression, quests |
| 38 | [Physics](38-physics.md) | Collision, controllers, vehicles, ragdolls, destruction |
| 39 | [Animation, camera and feel](39-animation-camera-feel.md) | Motion, cameras, input latency, juice |
| 40 | [Audio](40-audio.md) | Mixing, spatial sound, music, loudness |
| 41 | [Game and level design](41-game-and-level-design.md) | Core loops, balance, pacing, levels, playtesting |
| 42 | [UX, accessibility, localisation](42-ux-accessibility-localization.md) | Menus, HUD, settings, inclusive design, translation |
| 43 | [Best practices](43-best-practices.md) | **Start here for any game task** |
| 44 | [Visual modes](44-visual-modes.md) | Pixel art, retro, remasters, switchable looks |
| 45 | [Concurrency](45-concurrency.md) | Threads, jobs, atomics, async I/O |
| 46 | [Distributed servers](46-distributed-servers.md) | Server scaling, MMO zones, hand-off, persistence |
| 47 | [Layers, rejoin, replay, spectate](47-layers-rejoin-replay-spectate.md) | World copies, reconnects, replays, live viewing |
| 48 | [Tactical shooters](48-tactical-shooters.md) | Hit registration, fair shots, round-based play |
| 49 | [Single-player, local and offline](49-single-player-offline.md) | Offline games, saves, split-screen, optional online |
| | [Sources](sources.md) | Checking a claim |
