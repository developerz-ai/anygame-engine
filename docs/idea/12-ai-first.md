# 🤖 12. AI-first development

An AI agent should be able to build, run, observe, test and fix a game with no GUI and no human relaying error messages; every design choice above was picked partly because it makes that true.

The incumbents are retrofitting this. Unity shipped an official MCP server exposing scene hierarchy, code and editor state to agents, and as of 2026-11 its package docs deprecate that server in favour of the Unity CLI ([sources](sources.md)); Unreal 5.8 added an open-standard plugin for LLM tooling, and Epic says UE6 will be built on an open MCP foundation. AnyGame can design for it from the first commit instead.

## What makes an engine agent-friendly

| Property | Why agents need it | How AnyGame provides it |
|---|---|---|
| Text everywhere | Models read and write text; binary scenes are opaque | Scenes, prefabs, graphs, materials, config are text with schemas |
| Machine-readable API | Avoids hallucinated function names | `ag describe` emits the full schema: components, systems, events, commands, with docs and examples |
| Headless, fast loop | Agents iterate hundreds of times | `ag run --headless --ticks 600` in seconds; hot reload under 1 s for scripts |
| Structured errors | "Segfault" teaches nothing | Errors carry code, entity, system, source location and a suggested fix, as JSON |
| Observability | The agent cannot see the screen | Query world state (`ag query 'Health < 10'`), capture screenshots, record video, dump frame timings, all by command |
| Verifiable outcomes | Agents need a pass/fail signal | Gameplay tests as scripts: "spawn player, hold right 2 s, assert x > 10"; deterministic replays; screenshot comparison |
| Small, isolated units | Limited context windows | Packages with explicit dependencies; an `AGENTS.md` per package stating purpose, invariants and how to test |
| Safe sandbox | Agents make mistakes | Commands are reversible; worlds snapshot and restore; scripts are quota-limited |
| Strong conventions | Less to specify, less to get wrong | Rails-style layout and generators ([section 3](03-architecture.md)) |

## The interface

- **One command protocol, three front ends:** a fast interpreted Bun CLI (`ag`, [decision 017](../decisions/017-ag-cli-bun-wrapper.md)), an MCP server, and a read-mostly live viewer. The agent's interface is the primary one; humans use the same commands.
- **Playtest agents.** Bot clients driven by scripts or models run the game headless at many times real speed to find stuck spots, balance problems and crashes. Deterministic kits make every failure reproducible from seed plus input log.
- **Generation hooks, not lock-in.** Asset import accepts any generator (textures, meshes, audio, animation, dialogue) through a provider interface, with provenance metadata recorded per asset for licensing and store disclosure.
- **Runtime AI as a module.** `ai.llm` offers an async interface for NPC dialogue or directors, with on-device and server providers. It is optional and never in the deterministic simulation path.

## The agent's inner loop

The developer-experience target: an agent goes from a one-line request to a verified change without a human in the loop, in under a minute per iteration.

```console
$ ag describe gameplay.abilities --format json     # learn the API, with examples
$ ag generate ability Dash --kit thirdperson       # scaffold code + data + test
$ ag check                                         # schema, lint, types: JSON errors with fix hints
$ ag test abilities::dash --headless               # deterministic, seconds
  FAIL dash_crosses_gap: expected x >= 6.0, got 4.2
       at game/abilities/dash.cpp:31  hint: Dash.distance (4.0) < gap width (6.0)
$ ag run --headless --script tests/dash_demo.lua --capture out/   # screenshots + state dump
$ ag query "Player.Transform, Player.Velocity" --at tick=120      # inspect any tick
$ ag profile --budget                              # per-module ms and MB against budgets
```

Supporting rules:

- **Errors are the documentation.** Every diagnostic names the rule, the location and the likely fix, and links to a doc page shipped in the repo.
- **Docs live with the code,** as markdown with runnable examples that CI executes, so examples never rot.
- **One way to do each thing.** Fewer equivalent APIs means fewer wrong guesses.
- **Stable names.** Renames ship with an automated codemod (`ag migrate`), so agent knowledge of older versions degrades gracefully.
- **Fast builds.** Headers with PCH by default (named modules opt-in, see [C++23 craft](16-cpp23-craft.md)), unity builds per package, and a shared compile cache; gameplay iteration happens mostly in hot-reloaded Lua or hot-reloaded C++ modules.

## Why no-fork matters more with AI

An agent working in a fork cannot benefit from upstream fixes and loses the shared documentation its training and tooling rely on. Extension points with conformance tests give the agent a contract to satisfy and a test to prove it did.
