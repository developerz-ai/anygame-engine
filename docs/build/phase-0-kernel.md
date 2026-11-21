# Phase 0: Kernel

**Proves:** the plugin model and hot reload. **Depends on:** decisions [003](../decisions/003-headers-default-modules-optin.md), [009](../decisions/009-kernel-targets-wasm32.md), [011](../decisions/011-kernel-scope-and-budget.md), [012](../decisions/012-determinism-guarantee-tiers.md). **Read:** [kernel](../idea/04-kernel.md), [extending](../idea/05-extending.md), [AI-first](../idea/12-ai-first.md), [C++ decisions](../idea/29-cpp-decisions.md), [C++23 craft](../idea/16-cpp23-craft.md), [libraries](../idea/28-libraries-and-profilers.md), [platforms](../idea/30-platforms.md), [architecture map](../idea/33-architecture-map.md), [concurrency](../idea/45-concurrency.md), [CPU, cache, SIMD](../idea/50-cpu-cache-simd-layout.md), [veteran C++ tricks](../idea/51-veteran-cpp-tricks.md).

## Build order

1. Build, CI and platform layer for Windows, Linux, macOS.
2. Memory: tagged allocators, arenas, pools, TLSF, handles.
3. Registry: C ABI, versioned interfaces, `ag_load`, capability negotiation, interposition.
4. Reflection: annotated C++ to schema, versioned migrations.
5. ECS: archetypes, 16 KB chunks, relationships, change detection, multiple Worlds.
6. Jobs: fibres, work stealing, read/write-set scheduling, deterministic mode.
7. Clocks and World snapshot/restore.
8. `ag`: `new`, `build`, `run --headless`, `describe`, `query`, `test`, with JSON errors.

## Slices

Execute in order. Each is one PR.

1. [Phase 0.01: Build, CI and platform layer](phase-0-01-build-ci-platform.md)
2. [Phase 0.02: Memory](phase-0-02-memory.md)
3. [Phase 0.03: Registry and ports](phase-0-03-registry-ports.md)
4. [Phase 0.04: Reflection and schema](phase-0-04-reflection-schema.md)
5. [Phase 0.05: ECS and Worlds](phase-0-05-ecs.md)
6. [Phase 0.06: Jobs and system scheduling](phase-0-06-jobs.md)
7. [Phase 0.07: Clocks, snapshots and hot reload](phase-0-07-clocks-snapshots.md)
8. [Phase 0.08: `ag` CLI](phase-0-08-ag-cli.md)

## Exit checks

- A sample plugin is rebuilt and reloaded in a running headless process with no lost World state.
- An interposing plugin wraps another plugin's interface and forwards unchanged calls.
- A missing dependency fails with a readable structured error, not a crash.
- Snapshot, simulate, restore, re-simulate gives byte-identical World state.
- Deterministic job mode gives identical checksums across repeated runs.
- Loading old data runs its migration and drops no fields.
- `ag describe` emits the full schema as JSON.
- All checks pass in CI on Windows, Linux and macOS.
- The kernel compiles to `wasm32` and passes its headless tests in thread-only mode, with no `mmap` or fibre dependency.
- Kernel stays within the 30k-line budget.
