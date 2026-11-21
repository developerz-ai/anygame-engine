# 017 — The `ag` CLI is an interpreted Bun wrapper

Status: accepted
Date: 2026-11-21

## Context
`ag` is the command every agent runs constantly. It orchestrates builds, tests and tools, so its value is fast startup and fast iteration, not raw compute.

## Decision
`ag` is TypeScript run directly by Bun, with no compile step. It is a thin wrapper: commands load lazily, and engine work runs in native executables. A small C++ `ag-host` exposes the kernel over a versioned JSON protocol using public APIs only.

## Alternatives
- C++23 CLI: why not, slower to change, and every edit needs a rebuild.
- `bun build --compile` binary: why not, it adds a build step and a large binary for no benefit to agents.

## Consequences
Developing with AnyGame requires Bun. Shipped games never contain Bun, TypeScript or `ag`. Heavy work stays in native tools, and `ag --help` has a startup budget of 50 ms as a target until CI measures it.
