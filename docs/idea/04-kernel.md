# ⚙️ 4. Core runtime (the kernel)

The kernel is the only code every game ships. It has six parts (memory, jobs, data model with snapshots, reflection, [registry](05-extending.md#api-registry) and time) and a hard size budget of about 30k lines of C++23 for the shipped runtime ([decision 011](../decisions/011-kernel-scope-and-budget.md)).

## Memory

- No global `new`. Every subsystem receives an allocator: linear per-frame arenas, pool, TLSF general heap, virtual-memory-backed growable arrays.
- Allocations carry a tag, so a live memory map by module is always available (Naughty Dog's tagged-heap idea).
- Handles (index + generation) instead of raw pointers across module boundaries. Handles survive hot reload, serialise trivially, and replicate over the network.

## Jobs

- Fibre-based work-stealing scheduler; no privileged main thread (id Tech, Naughty Dog).
- Systems declare read and write sets on component types. The scheduler builds the dependency graph and runs non-conflicting systems in parallel (Bevy, Unity DOTS).
- A deterministic mode fixes job ordering and merge order so parallel execution gives bit-identical results, within the [promised tier](../decisions/012-determinism-guarantee-tiers.md).
- A thread-only mode runs without fibres, for the browser and for race detection.

## Data model: archetype ECS plus a scene tree view

- Storage is an archetype/chunk ECS: entities with the same component set sit in contiguous 16 KB chunks. This is what makes 100k units, bullets or crowd agents viable.
- Relationships (parent/child, "owned by", "targets") are first-class, in the style of Flecs. The familiar scene tree is a view over the ECS, not a second object model.
- Change detection per chunk column drives replication, rendering updates and live-viewer refresh without polling.
- Multiple Worlds per process: client world, server world, rollback scratch world, test world, each with its own clock.

Unreal ended up with two models, Actors and Mass, with a bridge between them. AnyGame starts with one and offers an OOP-style convenience layer (Entity wrapper, script components) on top.

## Reflection and schema

- Every component, event, asset and API is described by a schema generated at build time from annotated C++ (a clang-based tool, later C++26 static reflection).
- One schema drives serialisation, versioned migration, network replication, inspector views, script bindings, and the machine-readable API description that AI agents read.
- Schemas are versioned. Loading old data runs registered migration functions; nothing is ever silently dropped.

## Time and simulation models

The kernel owns clocks, not a game loop. A game's manifest chooses a loop module:

| Loop module | Behaviour | Used by |
|---|---|---|
| `loop.variable` | Variable delta, interpolated | Casual, narrative, most single-player |
| `loop.fixed` | Fixed tick with render interpolation and sub-stepping | Racing, physics-heavy, shooters |
| `loop.deterministic` | Fixed tick, fixed-point, software-float or strict-IEEE maths by tier, ordered jobs, snapshot/restore | Fighting, RTS, factory, replays |
| `loop.turn` | Advances on commands, not time | Card, board, tactics |
| `loop.audio` | Audio clock is master | Rhythm |

Snapshot/restore of a World is a kernel feature because rollback, rewind, replays, save games, undo and test fixtures all reduce to it.
