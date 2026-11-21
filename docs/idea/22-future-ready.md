# 🔭 22. Future-ready

**We cannot predict the next 30 years, so we do not bet on them. We make every bet replaceable.** A new GPU API, chip, model or platform should arrive as a new adapter, never as a rewrite, and a game built today should still load and run after it.

Depends on [adapters](05-extending.md#adapters-the-shape-of-every-integration) and [versioned schemas](04-kernel.md#reflection-and-schema). Written 2026-11.

## The architecture stays, the blocks grow

**We provide the building blocks. More will come, and adding them must not change the architecture.**

| Stable contracts (change rarely, only by new major version with an adapter) | Grows freely |
|---|---|
| Registry and C ABI plugin model | Modules, adapters, ports |
| Handles and World | Component and system types |
| Schema and migration system | Assets, formats, importers |
| Job graph with declared reads and writes | Systems, schedules, loop modules |
| Render graph contract | Passes, renderers, upscalers |
| Command protocol | `ag` commands, MCP tools, front ends |
| Package manifest | Packages, kits, genres, platforms |

**A new capability lands in the first row that fits:**

| New thing is | It becomes |
|---|---|
| Content or tuning | Data or an asset type |
| New state or behaviour | Component and system |
| A reaction to the engine | Event subscriber |
| A rendering, AI, audio or PCG step | Graph node |
| Another way to do an existing job | Adapter on an existing port |
| A whole new domain | New port in a package |
| A change to existing behaviour | Interposition wrapper |

**The architecture test:** if a new feature needs a kernel edit, stop. Either an extension point is missing, so add it publicly, or the kernel contract truly must change, which needs a decision record, a new major version and an `ag migrate` path. Run this test against each new module, and prove it by building at least one first-party module per phase using only public APIs.

## What will change, and how the design absorbs it

| What may change | Design answer | Work when it happens |
|---|---|---|
| New graphics API or GPU model | `rhi` port, render graph, shaders from one source | New RHI adapter |
| Neural rendering replaces passes | Passes are replaceable graph nodes | New pass or provider |
| New upscaler or frame generation | `render.upscale` port | New adapter |
| More cores, hybrid cores | Job graph, no main thread, no fixed thread count | Scheduler tuning |
| ARM, RISC-V, new CPU families | No ISA assumptions in core, SIMD behind one layer | New platform and SIMD backend |
| NPUs and on-device models | `ai.*` ports, async, outside deterministic paths | New adapter |
| New consoles, handhelds, devices | Platform layer is a plugin | New platform package |
| XR, new displays, new input | `xr` and `input` ports, action-based input | New adapter |
| Cloud streaming | Headless server plus separate render and input modules | New front end |
| C++26 and later | Schema tool hidden behind generated output; C ABI unaffected | Swap the generator |
| New agents and protocols | One command protocol; MCP is one front end | New front end |
| A dependency dies or changes licence | Every dependency sits behind a port | Replace one adapter |

## Rules

| Rule | Shape |
|---|---|
| **No hard-coded ceilings** | No fixed core count, resolution, refresh rate, player cap, world size or entity limit in public APIs |
| **Query capabilities, never versions** | Ask "supports mesh shaders?", not "is this GPU model X?" |
| **Version everything that persists** | Saves, assets, schemas, wire protocols, manifests and interfaces carry a version |
| **Old data always loads** | Migrations are permanent and tested against stored fixtures |
| **Independent clocks** | Simulation never assumes a display rate, so a game survives 500 Hz screens |
| **Open formats at the edges** | glTF, USD, PNG, EXR, WAV, TOML, markdown. Source content outlives the engine |
| **Reserve room in wire and file formats** | Unknown fields are preserved or skipped, not fatal |
| **Time is 64-bit** | No tick, timestamp or ID that overflows during a game's lifetime |
| **Every dependency has an exit** | Its port has a second adapter or a documented replacement path |
| **Upgrades are automatic** | Each breaking change ships an `ag migrate` codemod an agent can run |

## Promises to a game

These are design goals until tests enforce them.

- A saved game from an old version loads in a new one.
- An old plugin keeps working for at least two engine releases through an adapter.
- A game can pin its engine and package versions indefinitely, and rebuild them from a lockfile.
- A game's source content stays in open formats it owns, so it can leave AnyGame at any time.

## Staying current

- Review [next-gen techniques](17-next-gen-techniques.md) on a schedule, moving each entry between watch, optional and ship now.
- Add a technique as an optional module first. Promote it only after a real game uses it.
- Retire what stops paying for itself, with a deprecation window and a migration.
- Do not adopt something early merely because it is new. Keep the door open and wait for proof.
