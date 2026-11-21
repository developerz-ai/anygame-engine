# 🎮 AnyGame Engine

> **We provide the building blocks for your game. We never stand between you and it.**
>
> A toolbox for your coding agent: a small kernel, replaceable blocks, and the know-how to use them.

AnyGame is an open-source game engine design: a roughly 30k-line C++23 kernel plus a catalogue of replaceable modules. A game is a manifest that picks which modules to load, so a pixel-art platformer never pays for virtual geometry and an RTS never fights a variable-step loop.

**Humans bring ideas. Coding agents build them.** AnyGame distils the best ideas from 30 years of game engines into primitives an agent can use to create any kind of next-gen 2D or 3D game, with every part pluggable, extendable and replaceable. Think [Ultimate](https://github.com/developerz-ai/ultimate), but for games.

> 🚧 **Status: design stage.** This repo currently holds the architecture and build plan. There is no engine code to run yet, every performance number is a target, and the project is not maintained until it is ready.

## 🏆 The goal

**To become the best game engine in the world for building with coding agents.** We have not earned that yet. We will measure it with real games, and publish the results.

## 🧠 The idea

Monolithic engines bake in one answer to four questions, and each answer rules out whole genres. AnyGame makes all four swappable modules:

| Question | Baked-in answer | What it breaks | AnyGame |
|---|---|---|---|
| Who owns time? | Variable-step loop | Fighting, lockstep, replays | `loop.*` modules |
| Who owns state? | Object graph with `Tick()` | Huge RTS, MMO density | Archetype ECS |
| Who owns authority? | One server per match | MMOs, P2P rollback | `net.*` modules |
| Who owns the frame? | Fixed 3D renderer | Pixel art, stylised, mobile | Render-graph presets |

## ✨ Principles

- 🧩 **Everything above the kernel is a plugin**, with no private APIs for first-party modules.
- 🔌 **Adapter-based:** physics, audio, upscaling (DLSS, FSR, XeSS), databases and more plug in through ports, and your manifest picks.
- 📄 **Data is the contract:** schema-described, versioned, diffable, readable by agents.
- 🔁 **Determinism is opt-in** per world, and designed in from day one.
- 🚫 **Never fork:** six extension mechanisms, up to wrapping any implementation.
- 🤖 **Headless first:** no GUI editor in the core. Every operation is a command or a text file.
- 🪶 **Pay only for what you load.**
- 🏎️ **Small and fast by default:** faster hardware should buy a better game, not a heavier one.
- 🔭 **Ready for the future:** new blocks, hardware, APIs and models arrive as modules and adapters, without changing the architecture, and old games and saves keep working.
- 📦 **Huge catalogue, tiny build:** a lot of ready-made blocks to work with, and your game ships only what it loads.
- ♻️ **No reinventing the wheel:** agents start from proven blocks, spend their effort on the game, and improve a block when they can prove it.
- 🔁 **Every game makes it better:** real problems become better blocks, errors and playbooks for the next game. Sharing is always opt-in.
- 🤝 **No regrets:** MIT, no royalties, no lock-in, no forced upgrades, no hidden telemetry. You can always leave with everything.
- 📱 **Every platform:** Linux, Windows, macOS, Android, iPhone and the browser (WebAssembly + WebGPU) from one project.
- 🎯 **No more unoptimized or buggy games:** agents bring the dev speed, so the engine focuses on performance and correctness. SOLID at the boundaries, data-oriented in hot paths.
- ♻️ **Load on demand, cache, unload:** nothing stays in memory unless the player is about to need it.
- 🏅 **Good games by default:** kits, playbooks and scorecards make the high-quality path the easy one.
- 🙌 **Help, then get out of the way:** every kit, convention, gate and recommendation is a default your game can override.
- 🛡️ **Fair play without ring-0:** server authority and server-side detection, no kernel anti-cheat.

## 🔮 The target developer experience

Planned, not yet implemented. A human opens a coding agent and says:

> build an arcade street racer with AnyGame

The agent already has the playbooks, blocks and tricks. It builds an original playable slice, proves it with bots, and asks where to take it next ([how it works](docs/idea/26-one-prompt-to-game.md)). Under the hood:

```console
$ ag new mygame --kit platformer2d
$ ag generate ability Dash
$ ag test abilities::dash --headless
  FAIL dash_crosses_gap: expected x >= 6.0, got 4.2
       at game/abilities/dash.cpp:31  hint: Dash.distance (4.0) < gap width (6.0)
$ ag query "Player.Transform, Player.Velocity" --at tick=120
```

## 📚 Docs

- 💡 **[Idea](docs/idea/README.md):** the full architecture blueprint.
- 🏗️ **[Build](docs/build/README.md):** the phased roadmap, with exit checks.
- 🗺️ **[Architecture map](docs/idea/33-architecture-map.md):** layers and dependency rules on one page.
- 🧭 **[Decisions](docs/decisions/README.md)** and **[how we work](docs/build/how-we-work.md):** why things are this way, and how work moves.
- ❓ **[Open questions](docs/build/open-questions.md):** what still needs deciding.
- 🧱 **[Primitives](docs/idea/23-primitives.md):** everything planned for the game client, game server and backend.
- 🗂️ **[Project organisation](docs/idea/24-project-organization.md):** how agents structure a game, from jam to live service.
- 🚢 **[Idea to distribution](docs/idea/25-idea-to-distribution.md):** the full cycle, from pitch and project management to stores and live ops.
- 🎯 **[Quality bar](docs/idea/32-quality-bar.md):** how performance and correctness are enforced.
- 🧠 **[C++23 craft](docs/idea/16-cpp23-craft.md):** memory, RAII, sanitizers, testing.
- 🧭 **[C++ decisions](docs/idea/29-cpp-decisions.md):** lookup tables, so any model makes the high-return choice.
- 🧰 **[Libraries and profilers](docs/idea/28-libraries-and-profilers.md):** the best allocators, libraries and profilers, one default per need.
- ⚡ **[Agent dev cycle](docs/idea/18-agent-dev-cycle.md):** from a human idea to a verified build.
- 🤝 **[Companion tools](docs/idea/19-companion-tools.md):** optional recommendations for web, 3D assets and media.

## 🗺️ Roadmap

| Phase | Deliverable |
|---|---|
| 0 | Kernel: memory, jobs, ECS, reflection, registry, snapshots, CLI |
| 1 | 2D stack, Lua, `kit.platformer2d`, mobile |
| 2 | Determinism, rollback, lockstep, `kit.fighting`, `kit.rts` |
| 3 | 3D desktop, `net.replication`, `kit.fps`, `kit.thirdperson` |
| 4 | Backend and `ag dev` full stack |
| 5 | Large worlds, `kit.openworld`, `kit.racing` |
| 6 | High-end rendering, motion matching, crowds |
| 7 | `net.mmo`, `kit.mmo` |

## 🤖 Backed by developerz.ai

AnyGame is built with AI agents. Once it is ready, [developerz.ai](https://www.developerz.ai) will maintain it. **Until then the project is not maintained, so issues and pull requests may go unanswered.** It sits alongside open-source tools like [Ultimate](https://github.com/developerz-ai/ultimate), [ts23d](https://github.com/developerz-ai/ts23d) and [wurk](https://github.com/developerz-ai/wurk), all [optional](docs/idea/19-companion-tools.md).

## 🤝 Contributing

Design feedback is welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first, especially the clean-room policy.

## 📄 License

[MIT](LICENSE)
