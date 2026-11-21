# Phase 0.07: Clocks, snapshots and hot reload

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.03](phase-0-03-registry-ports.md), [0.04](phase-0-04-reflection-schema.md), [0.05](phase-0-05-ecs.md), [0.06](phase-0-06-jobs.md).

## Goal

Every World has its own clock and RNG, can save and restore exactly, and survives a plugin reload.

## Design source

- [Kernel: Time and simulation models](../idea/04-kernel.md).
- [Extending](../idea/05-extending.md): hot reload rules.
- [C++23 craft](../idea/16-cpp23-craft.md): reload sequence, ABI, deterministic and snapshot tests.
- [Client and server models](../idea/35-client-server-models.md): why replay and rewind need this.

## Files to create or change

- `kernel/include/ag/time/{clock,tick,rng}.h`, `kernel/src/time/*.cpp`.
- `kernel/include/ag/ecs/snapshot.h`, `kernel/src/ecs/snapshot.cpp`.
- `kernel/include/ag/registry/reload.hpp`, `kernel/src/registry/reload.cpp`.
- `kernel/tests/time/*_test.cpp`, `kernel/tests/snapshot/*_test.cpp`.
- `kernel/tests/reload/plugin_counter/`: sample stateful plugin, two versions.
- `kernel/tests/reload/reload_host.cpp`: running headless process.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `ag::Tick` | 64-bit tick counter |
| `ag::Clock` | Per-World time, with virtual advance for tests |
| `ag::Rng` | Seeded per-World generator, stored in snapshots |
| `ag::Snapshot` | Serialised World in schema form |
| `ag::snapshot_world`, `ag::restore_world` | Save and restore |
| `ag::world_checksum` | Reused from [0.06](phase-0-06-jobs.md) |
| `ag::reload_plugin` | Drain, serialise, unload, load, migrate, resume |

## Steps

1. Implement `Tick` and `Clock`, with no wall-clock read in simulation paths. verify: a test advances 1,000,000 virtual ticks in under 1 s with no sleep.
2. Implement `Rng` as a fixed algorithm with explicit state. verify: a stored golden sequence matches on all CI platforms.
3. Implement World snapshot through the schema: entities, generations, components, relationships, resources, clock and RNG. verify: restoring into an empty World yields the same `world_checksum`.
4. Make snapshot output canonical. verify: two snapshots of equal state are byte-identical, even when entities were created in a different chunk layout.
5. Run the core proof: snapshot, simulate 600 ticks, record the output, restore, simulate again. verify: both serialized outputs are byte-identical, at 1 and at 8 workers.
6. Handle snapshots from older schemas through migrations. verify: a stored v1 World snapshot restores on the current schema.
7. Fuzz snapshot loading. verify: a libFuzzer target runs 60 s under ASan and UBSan with no crash.
8. Implement reload: drain jobs, serialise module state, unload, load, migrate, resume. Refuse while a fibre is parked in that module's code. verify: a test with a parked fibre returns `AG_RELOAD_FIBRE_PARKED`.
9. Prove live reload. `reload_host` runs a World, rebuilds `plugin_counter` to version 2 and reloads it. verify: the process ID is unchanged, the checksum of non-plugin state matches, the counter keeps its value, and the new behaviour is observed.
10. On static targets, report reload as unsupported through a capability. verify: `wasm32` returns `AG_RELOAD_UNSUPPORTED`, with no crash.

## Must not happen

- No wall clock, global RNG or unordered iteration in simulation.
- No raw struct bytes in a snapshot.
- No mutable global state in a plugin.
- No code unloaded while a job or fibre is inside it.
- No reload that silently discards state.

## Done when

- **Owns exit check:** "Snapshot, simulate, restore, re-simulate gives byte-identical World state."
- **Owns exit check:** "A sample plugin is rebuilt and reloaded in a running headless process with no lost World state."
