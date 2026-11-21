# 🎯 32. The quality bar: fast and correct

**AI agents already give developers speed of development. So the engine spends its design on what players feel: performance and correctness.** No more unoptimized games. No more games shipped full of bugs.

Planned design as of 2026-11. Budgets and gates are defaults a game can relax ([rule 8](01-thesis.md#design-rules)), and the engine then reports that plainly.

## SOLID at the boundaries, data-oriented in the hot path

Clean structure and raw speed do not conflict when each applies in the right place.

| Layer | Priority | Rules |
|---|---|---|
| Ports, plugins, packages | **SOLID** | One responsibility, small interfaces, depend on ports, replace by adapter |
| Gameplay features, services, tools | **SRP and clarity** | Small files, one job, easy for the next agent to change |
| Module internals | Both | Clean public surface, free to optimise behind it |
| Per-frame loops over many entities | **Performance wins** | Arrays, batches, no per-entity indirection or allocation |
| Kernel, renderer, physics inner loops | **Performance first** | Measured, budgeted, specialised code is fine |

| Rule | Shape |
|---|---|
| **Abstract per batch, never per entity** | One indirect call on a span of 10,000 items costs almost nothing |
| **Interfaces take arrays** | `step(world, span)` rather than `update(entity)` |
| **Compile-time composition inside a module** | Templates and concepts, with no vtable in hot loops |
| **Break an abstraction only inside a module** | A shortcut never leaks across a port |
| **Performance exceptions carry proof** | A benchmark in the PR, and a comment naming what it buys |
| **Readable by default** | Fast code still has one job, clear names and tests |

Where code runs once per frame or less, prefer clarity. Where it runs per entity, prefer speed. Picks are in [C++ decisions](29-cpp-decisions.md).

## 🏎️ No more unoptimized games

Games usually become slow gradually, then get "optimised" too late. Here, cost is visible from the first commit.

| Common failure | How AnyGame prevents it |
|---|---|
| Shader compilation stutter | Pipelines are compiled at build or load time |
| Traversal stutter | Streaming budgets in ms and MB, tested on a scripted route |
| CPU stuck on one thread | Job graph from declared reads and writes |
| Thousands of idle objects ticking | No per-object update, idle entities sleep |
| Memory leaks and growth | Tagged memory, soak tests |
| Huge installs and patches | Size report, deduplication, per-platform cooks |
| Only runs well on high-end PCs | Budgets checked on the worst supported device |
| Upscaling hiding a slow frame | Frame budget also reported at native input resolution |
| Slow loading | Load-time budget per scene |
| Regressions nobody noticed | CI compares each change against a baseline |

**Performance gate defaults:** p99 frame time within budget on the target device, zero allocations in hot systems after warmup, no shader compilation during play, and no unexplained regression.

## 🐛 No more games full of bugs

No engine can honestly promise zero bugs. It can make whole classes impossible, catch most of the rest before release, and make every remaining one reproducible and quick to fix.

| Layer | Stops | Tool |
|---|---|---|
| 1. Make it impossible | Bad data, wrong units, unsafe ownership | Schemas, strong types, handles, concepts |
| 2. Catch at build | Type errors and rule breaks | Compiler warnings as errors, clang-tidy, custom lints |
| 3. Catch in tests | Logic errors | Unit, property and deterministic tests |
| 4. Catch memory errors | Corruption, races, undefined behaviour | ASan, UBSan, TSan, MSan, Valgrind |
| 5. Attack the inputs | Bad saves, packets, mods, assets | Fuzzing |
| 6. Play the game | Stuck spots, softlocks, crashes | Bots at many times real speed |
| 7. Stress it | Leaks, desyncs, server failures | Soak, load, latency and packet-loss tests |
| 8. Look at it | Visual breakage | Screenshot diffs, automated visual review |
| 9. Verify every platform | Device-only failures | Device farm |
| 10. Reproduce from the field | Whatever still escapes | Opt-in crash report with seed, snapshot and input log |

**The bug loop:** failure → replay from seed and input log → failing test → fix → stored regression test. Once fixed, a bug stays fixed.

**Release gate defaults:** bots finish the game, no open blocker, sanitizers clean, soak test passes, saves from previous versions load, and every target meets its budget.

## 🏅 Games built with AnyGame represent us

**A game built with AnyGame should be good by default, because players judge the engine by it.** We earn that by making the good path the easy one, never by controlling anyone's game.

| Lever | How |
|---|---|
| Good starting point | Every kit starts inside budget, with tests, bots and a clean release gate |
| Playbooks raise the floor | Agents inherit genre know-how, feel checklists and known traps |
| Quality is visible | `ag scorecard` rates performance, stability, loading, size, accessibility and polish |
| Warnings arrive early | A regression is reported on the change that caused it |
| Polish is a checklist | Input latency, menus, settings, remapping, subtitles, saves, pause, error states |
| Reference games set the bar | Each kit's sample game must be something we are proud to show |
| Agents push back honestly | An agent reports a weak result, instead of calling it finished |

**Optional "Verified on AnyGame" badge:** a game may earn it by publishing a passing scorecard from a reproducible build. It is never required, and there is no fee. Games without it are just as welcome, and no game must display our name ([no regrets](31-no-regrets.md)).

## Definition of done for an agent

A feature is done when:

1. It works, and a headless test proves it.
2. It stays inside its CPU, memory and size budget.
3. It adds no allocation to a hot path.
4. Sanitizers are clean.
5. Bots still complete the game.
6. Its cost is reported in the PR.
