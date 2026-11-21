# ⚡ 18. The agent dev cycle

**Humans bring ideas. Coding agents use the kernel and modules to build them.** The primary user of every API, error and command is an agent. A human should never need to open a tool to relay what went wrong.

Extends [AI-first development](12-ai-first.md). All times below are targets until CI measures them.

## The loop

```text
idea -> game spec -> pick kit + modules -> generate -> check -> test -> observe -> fix -> verified build
                                              ^                                  |
                                              +----------------------------------+
```

| Stage | Command | Agent gets back | Target |
|---|---|---|---|
| Learn | `ag describe <module> --format json` | Schema, commands, examples | < 1 s |
| Scaffold | `ag new`, `ag generate <kind> <name>` | Code, data and a test | < 2 s |
| Static check | `ag check --changed` | JSON errors with a fix | < 5 s |
| Reload | `ag reload <module>` | Pass/fail, state preserved | Script < 1 s, C++ < 5 s |
| Focused test | `ag test <name> --headless` | Failure, tick, entity, source, hint | < 10 s |
| Observe | `ag run --headless --capture`, `ag query` | Images, state, timings | < 30 s |
| Budget | `ag profile --budget` | Per-module ms and MB against budget | < 30 s |
| Full gate | `ag verify --json` | Every step with a verdict | Green means shippable |

## Rules for an agent-first engine

| Rule | Shape |
|---|---|
| **Every failure is actionable** | Stable code, cause, location, and an exact `fix:` command |
| **Every claim has a command** | Docs name the command that proves a number, rather than storing the number |
| **Output is bounded** | Summaries by default, `--full` on request, so a log never floods agent context |
| **Every run is reproducible** | A failure prints its seed, input log and replay command |
| **Bad states are unrepresentable** | Schema validation and lints refuse a mistake before a build starts |
| **One way per task** | One generator, one test form, one path for each module kind |
| **Everything is replaceable** | Each module has an interface and conformance suite an agent can target |
| **The agent can see** | Screenshots, contact sheets, depth and ID buffers, video, all by command |
| **Mistakes are cheap** | Snapshots, sandboxed scripts, reversible commands |
| **Gates advise the game** | Game-level checks and budgets are configurable in the manifest. A game can relax or skip any of them, and the engine reports that plainly |

## Judging a game without a human

"It compiles" says nothing about whether a game is good. Each kit ships checks for what a person would otherwise notice.

| Human judgement | Machine check |
|---|---|
| Can it be finished? | Bot completes the level or match headless |
| Does it feel responsive? | Input-to-effect latency in ticks, against a kit budget |
| Is it balanced? | Thousands of headless bot matches, with win-rate bounds |
| Does it look broken? | Screenshot diff, missing-asset and z-fighting checks, vision-model review |
| Does it hitch? | Frame-time percentiles on a scripted route |
| Is it stable? | Soak test, fuzzed inputs, sanitizer builds |
| Is it fun? | **Human review.** Bots can flag pacing problems, and the idea's owner decides |

## Do not reinvent the wheel

**Agents get a lot to work with, so their effort goes into the game.** Before writing a system, an agent climbs this ladder and stops at the first step that works:

| Step | Action | Example |
|---|---|---|
| 1. Find | `ag find "<need>"` searches blocks, kits, packages and [known tricks](20-tricks-30-years.md) | "coyote time" finds `input.buffer` |
| 2. Use | Load the block in the manifest | Add `physics2d.kinematic` |
| 3. Configure | Change its data or settings | Tune jump buffer ticks |
| 4. Compose | Combine blocks with new components and systems | Stamina plus abilities |
| 5. Wrap | Interpose on an implementation | Add a custom physics query filter |
| 6. Replace | Provide a new adapter that passes conformance | A game-specific solver |
| 7. Improve | Send the better version upstream | Faster pathfinding with a benchmark |

**Sometimes the wheel can be better.** An agent may improve a block when it has evidence:

- A measured benchmark, failing test or real game need shows the gap.
- The change passes the block's conformance suite and keeps its public contract.
- It stays in the game as an overlay until accepted, so the game is never blocked on upstream.
- Useful improvements are offered back as a pull request or package, at the developer's choice.

Reuse is the default, not a restriction. A game can write its own version of anything.

## Ultimate, but for games

AnyGame is to games what [Ultimate](https://github.com/developerz-ai/ultimate) is to web apps: a framework whose primary developer is an AI agent.

| Ultimate habit | AnyGame equivalent |
|---|---|
| One `action` projects into route, client, job, MCP tool and test | One schema projects into serialisation, replication, script bindings, `ag describe` and tests |
| `x verify --json`: green means shippable | `ag verify --json` |
| Every error has a stable code, cause and `fix:` command | Same, plus tick, entity and replay command |
| `x g <kind> <name>` generators | `ag generate <kind> <name>` |
| `llms.txt` link map for agents | Same, at the repo root and per package |
| Facts are commands, not stored numbers | Sizes, budgets and benchmarks come from `ag` commands |
| Embedded dev stack, zero setup | `ag dev` runs the whole game stack locally |

**The one deliberate difference:** Ultimate is opinionated with one fixed stack and no plugin API. A game engine cannot be, because games differ too much. AnyGame keeps the same agent experience, and every part stays pluggable, extendable and replaceable.

## From idea to game

1. Human states the idea in a paragraph.
2. Agent writes a game spec: core loop, win condition, scope, target platforms, budgets.
3. Agent picks a kit, or composes modules with a manifest.
4. Agent builds the smallest playable slice first and proves it with a bot.
5. Agent adds systems one at a time, each with a test.
6. Human plays a build and replies with direction, not bug reports.

## Fast C++ for agents

Compile time is the agent's main wait. Tactics, compiler support and sanitizer tiers are in [C++23 craft](16-cpp23-craft.md).
