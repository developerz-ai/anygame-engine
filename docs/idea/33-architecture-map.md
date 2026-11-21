# 🗺️ 33. Architecture map

**One page to answer: what depends on what, where does this code go, and what must never happen.** Planned structure as of 2026-11. No engine code exists yet.

## Layers

Each layer depends only on the layers below it.

```text
┌────────────────────────────────────────────────────────────────┐
│ GAME            game/  client/  server/  content/  schema/     │
├────────────────────────────────────────────────────────────────┤
│ KITS            platformer2d  fps  racing  rts  mmo  ...       │  picks and configures blocks
├────────────────────────────────────────────────────────────────┤
│ BLOCKS          abilities  inventory  vehicles  ai.*  ui.*     │  ready-made gameplay
├────────────────────────────────────────────────────────────────┤
│ DOMAIN MODULES  render  physics  anim  audio  net  world       │  implement ports
│                 input  script  persist  services               │
├────────────────────────────────────────────────────────────────┤
│ ADAPTERS        vulkan  d3d12  metal  webgpu  jolt  dlss  fsr  │  wrap vendors and libraries
├────────────────────────────────────────────────────────────────┤
│ PORTS           versioned C ABI interfaces                     │  the stable contract
├────────────────────────────────────────────────────────────────┤
│ KERNEL          memory  jobs  ECS  reflection  clocks          │  the only code every game ships
│                 registry  snapshots                            │
├────────────────────────────────────────────────────────────────┤
│ PLATFORM        Linux  Windows  macOS  Android  iOS  browser   │
└────────────────────────────────────────────────────────────────┘

BESIDE THE STACK  ag (Bun wrapper) · ag-host (native) · MCP · live viewer · asset cooker · test bots
                  separate processes, same public commands, never in the shipped binary
```

Adapters implement ports and may call vendor code. Domain modules call other modules only through ports.

## Dependency rules

| Rule | Allowed | Forbidden |
|---|---|---|
| Direction | Upper layer calls lower layer | Kernel knowing about any module |
| Module to module | Through a port, or through ECS data and events | Including another module's internals |
| Vendor code | Inside one adapter | A vendor type above a port |
| Client and server | Both depend on shared `game/` | Server code depending on `client/` |
| Simulation and render | Extract step copies data one way | Simulation reading render state |
| Determinism | Deterministic systems use World clock and RNG | Wall clock, unordered iteration, `ai.llm` |
| Tools | Use the public command protocol | Tooling code paths in the runtime |
| First-party code | The same public APIs as everyone | Private APIs |

CI should enforce these with an include-graph check once code exists.

## How data and control flow

```text
input -> command -> [authority validates] -> systems mutate World -> events
                                                 |
                       snapshot / replay <-------+-------> replication -> clients
                                                 |
                                         extract -> render world -> render graph -> GPU
```

## Planned engine repository

```text
kernel/            memory, jobs, ecs, reflect, clock, registry, snapshot
ports/             C headers: one versioned interface per domain
modules/<domain>/  implementations of a port, with AGENTS.md and tests
adapters/<vendor>/ thin wrappers over third-party libraries
blocks/<name>/     ready-made gameplay
kits/<genre>/      template, sample game, playbook
tools/ag/          Bun + TypeScript CLI, MCP, generators, run with no compile step
tools/ag-host/     small C++ host exposing the kernel to ag
conformance/       one suite per port
scripts/           Bun repo tooling, scripts/lib for shared code
docs/              idea, build, decisions
```

## What every package contains

| File | Purpose |
|---|---|
| `anygame.toml` | Name, version, needs, provides, budgets |
| `AGENTS.md` | Purpose, invariants, how to test |
| `include/`, `src/` | Public surface and private implementation |
| `tests/` | Unit and behaviour tests |
| `examples/` | A runnable pattern to copy |

Related: [kernel](04-kernel.md), [resource lifecycle](34-resource-lifecycle.md), [adapters](05-extending.md#adapters-the-shape-of-every-integration), [stable contracts](22-future-ready.md#the-architecture-stays-the-blocks-grow), [quality bar](32-quality-bar.md). Decisions behind this map: [decision records](../decisions/README.md).
