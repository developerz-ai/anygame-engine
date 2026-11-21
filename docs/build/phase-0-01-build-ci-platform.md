# Phase 0.01: Build, CI and platform layer

> Phase: [Phase 0](phase-0-kernel.md). Depends on: nothing.

## Goal

An empty kernel library builds and tests on Linux, Windows, macOS and `wasm32`, with sanitizers and a line budget in the gate.

## Design source

- [C++23 craft](../idea/16-cpp23-craft.md): baseline compilers, flags, build speed, `bin/check` tiers.
- [C++ decisions](../idea/29-cpp-decisions.md): default choices.
- [Libraries and profilers](../idea/28-libraries-and-profilers.md): doctest and adoption rules.
- [Platforms](../idea/30-platforms.md): per-OS rules and browser limits.
- [Architecture map](../idea/33-architecture-map.md): repo layout and dependency rules.
- [Decision 003](../decisions/003-headers-default-modules-optin.md): headers plus PCH.
- [Decision 009](../decisions/009-kernel-targets-wasm32.md): `wasm32` from Phase 0.

## Files to create or change

- `CMakeLists.txt`, `CMakePresets.json`: root build, Ninja only.
- `cmake/AgWarnings.cmake`, `cmake/AgSanitizers.cmake`, `cmake/AgPch.cmake`.
- `kernel/CMakeLists.txt`, `kernel/AGENTS.md`.
- `kernel/include/ag/platform/platform.h`: compiler, OS, cache-line and export macros.
- `kernel/include/ag/platform/vm.h`, `kernel/src/platform/vm_{posix,win32,wasm}.cpp`.
- `kernel/tests/platform_test.cpp`, `third_party/doctest/` at a pinned version.
- `scripts/lib/line-budget.ts`, `scripts/check-kernel-budget.ts`, with tests.
- `bin/check`, `.github/workflows/ci.yml`: extended.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `AG_CACHE_LINE` | 64, or 128 on Apple Silicon |
| `AG_EXPORT`, `AG_PLUGIN_EXPORT` | Symbol visibility on each OS |
| `ag::vm::page_size()` | Query the real page size. Never hard-code it |
| `ag::vm::capabilities()` | Reports whether reserve-and-commit exists |
| `ag::vm::reserve`, `commit`, `decommit`, `release` | Virtual memory where available |
| `ag::vm::alloc_pages`, `free_pages` | Page backend that also works on `wasm32` |

## Steps

1. Create presets `linux-dev`, `linux-asan`, `linux-tsan`, `windows-dev`, `macos-dev`, `wasm32`. verify: `cmake --list-presets` prints all six.
2. Set C++23 with `-fno-exceptions -fno-rtti` (MSVC: `/EHs-c- /GR-`) and warnings as errors for kernel targets. verify: a temporary `throw` in a kernel file fails the build.
3. Add a kernel PCH holding only standard and stable headers. verify: `cmake --build --preset linux-dev` succeeds with PCH on and with `-DAG_PCH=OFF`.
4. Add doctest, wired to CTest with label `kernel`. verify: `ctest --preset linux-asan -L kernel` runs at least one passing test.
5. Implement platform macros and `ag::vm`. On `wasm32`, `capabilities()` reports no reserve-and-commit. verify: `platform_test` asserts `page_size()` is a non-zero power of two on all presets.
6. Add the line-budget script: counts non-blank, non-comment runtime lines in `kernel/include` and `kernel/src`, excluding tests, `tools/` and `third_party/`. It fails above 30,000. verify: a test fixture over budget returns a finding, and `bun scripts/check-kernel-budget.ts --json` prints `"ok": true`.
7. Extend `bin/check` with tiers `fast`, `unit`, `pr`. With no tier it keeps today's checks, and `--json` keeps working. verify: `bin/check unit` runs `ctest --preset linux-asan`, and `bin/check --json` still prints valid JSON.
8. Add a CI matrix for all four platforms. Pin every action to a full SHA. Keep `verify` as one aggregate job. verify: a PR shows green Linux, Windows, macOS and `wasm32` jobs under `verify`.

## Must not happen

- No hard-coded page size, thread count or `long` in a data format.
- No Visual Studio generator in dev or CI.
- No third-party type in a public kernel header.
- No GPL or AGPL dependency linked.
- No edit to game or module directories. They do not exist yet.

## Done when

- Every step's check passes in CI.
- **Owns exit check:** "Kernel stays within the 30k-line budget." `scripts/check-kernel-budget.ts` runs on every PR.
