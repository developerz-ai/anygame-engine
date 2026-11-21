# Phase 0: Kernel

**Proves:** the plugin model and hot reload. **Depends on:** [open questions](open-questions.md) 1 to 4. **Read:** [kernel](../idea/04-kernel.md), [extending](../idea/05-extending.md), [AI-first](../idea/12-ai-first.md).

## Build order

1. Build, CI and platform layer for Windows, Linux, macOS.
2. Memory: tagged allocators, arenas, pools, TLSF, handles.
3. Registry: C ABI, versioned interfaces, `ag_load`, capability negotiation, interposition.
4. Reflection: annotated C++ to schema, versioned migrations.
5. ECS: archetypes, 16 KB chunks, relationships, change detection, multiple Worlds.
6. Jobs: fibres, work stealing, read/write-set scheduling, deterministic mode.
7. Clocks and World snapshot/restore.
8. `ag`: `new`, `build`, `run --headless`, `describe`, `query`, `test`, with JSON errors.

## Exit checks

- A sample plugin is rebuilt and reloaded in a running headless process with no lost World state.
- An interposing plugin wraps another plugin's interface and forwards unchanged calls.
- A missing dependency fails with a readable structured error, not a crash.
- Snapshot, simulate, restore, re-simulate gives byte-identical World state.
- Deterministic job mode gives identical checksums across repeated runs.
- Loading old data runs its migration and drops no fields.
- `ag describe` emits the full schema as JSON.
- All checks pass in CI on Windows, Linux and macOS.
- Kernel stays within the 30k-line budget.
