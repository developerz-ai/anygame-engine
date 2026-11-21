# Phase 0.05: ECS and Worlds

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.02](phase-0-02-memory.md), [0.04](phase-0-04-reflection-schema.md).

## Goal

Archetype storage in 16 KB chunks, with relationships, queries, change detection and several isolated Worlds per process.

## Design source

- [Kernel: Data model](../idea/04-kernel.md).
- [Architecture map](../idea/33-architecture-map.md).
- [Quality bar](../idea/32-quality-bar.md): abstract per batch, never per entity.
- [C++23 craft](../idea/16-cpp23-craft.md): data layout and component rules.
- [Decision 005](../decisions/005-single-ecs-data-model.md).
- Reference only: [Flecs and EnTT](../idea/28-libraries-and-profilers.md).

## Files to create or change

- `kernel/include/ag/ecs/{entity,world,archetype,chunk,query,command_buffer,relationship,resource}.h`.
- `kernel/src/ecs/*.cpp`.
- `kernel/tests/ecs/*_test.cpp`.
- `kernel/benchmarks/ecs_bench.cpp`: nanobench.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `ag::Entity` | Generational handle |
| `ag::World` | Owns all entities, resources and allocators for one simulation |
| `ag::Archetype`, `ag::Chunk` | SoA columns in 16 KB chunks |
| `ag::Query<...>` | Iterates matching chunks as spans |
| `ag::CommandBuffer` | Defers structural changes |
| `ag::relate`, `ag::targets` | First-class relationships |
| `Chunk::changed_since(tick)` | Column change detection |
| `World::insert_resource`, `resource<T>` | Per-World singletons |

## Steps

1. Implement entity allocation on generational handles. verify: a destroyed entity's old handle fails `is_alive`.
2. Implement archetypes keyed by a sorted component set. verify: two spawn orders of the same components share one archetype.
3. Implement 16 KB chunks with aligned SoA columns from a chunk pool. verify: a test asserts chunk size, column alignment and capacity for mixed component sizes.
4. Implement add, remove and destroy with swap-remove. verify: a seeded property test of 1,000,000 operations matches a simple `std::map` model.
5. Implement chunk-span queries with include, exclude and optional terms. verify: query results match the model for every filter combination.
6. Add `CommandBuffer`, played back in recorded order. Structural change during iteration goes through it. verify: debug builds abort with a coded message on direct structural change during a query.
7. Implement per-column change ticks. verify: writing one column marks only that column and chunk.
8. Implement relationships, including parent/child and a scene tree view over them. verify: destroying a parent applies the declared cleanup, with no dangling target.
9. Prove World isolation. verify: two Worlds using identical entity IDs do not affect each other, and no kernel global holds World state.
10. Add benchmark and allocation checks. verify: iterating 1,000,000 entities performs zero allocations, and the benchmark result is printed as JSON.

## Must not happen

- No per-entity virtual call or heap allocation.
- No pointer into a chunk held across a structural change.
- No second object model or stored scene graph.
- No hidden global state.
- No hash-map iteration affecting simulation order.

## Done when

- All ECS tests pass on Linux, Windows, macOS and `wasm32`, under sanitizers where available.
- Zero-allocation iteration is enforced by a test.
- Owns no Phase 0 exit check directly. It supplies the World that [0.06](phase-0-06-jobs.md) and [0.07](phase-0-07-clocks-snapshots.md) prove.
