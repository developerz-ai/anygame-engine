# Phase 0.03: Registry and ports

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.01](phase-0-01-build-ci-platform.md), [0.02](phase-0-02-memory.md).

## Goal

Plugins load through a stable C ABI, declare what they need and provide, and can wrap one another.

## Design source

- [Extending](../idea/05-extending.md): API registry, adapters and rules.
- [C++23 craft](../idea/16-cpp23-craft.md): ABI and hot reload rules.
- [Architecture map](../idea/33-architecture-map.md): dependency rules.
- [Decision 004](../decisions/004-c-abi-ports-and-adapters.md).

## Files to create or change

- `ports/ag_abi.h`: `ag_version`, status codes, size-prefixed struct convention.
- `ports/ag_registry.h`: C registry interface.
- `kernel/include/ag/registry/registry.hpp`: header-only C++ wrapper.
- `kernel/src/registry/{registry,resolver,loader_posix,loader_win32,loader_static}.cpp`.
- `kernel/tests/registry/*_test.cpp`.
- `kernel/tests/registry/plugins/{greeter,greeter_wrap,needs_missing}/`: sample plugins.
- `conformance/registry/`: reusable registry suite.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `ag_version` | Major, minor, patch |
| `ag_registry` | Opaque registry handle |
| `ag_registry_api` | Get, provide and query through function pointers |
| `ag_provide_desc` | Port name, version, implementation, `wraps`, priority |
| `ag_plugin_desc` | Name, version, needs, provides |
| `ag_load(reg, reload)` | The single plugin entry point |
| `ag_unload(reg, reload)` | Releases what the plugin registered |
| `ag::Registry` | Ergonomic C++ wrapper, header-only |
| `ag::resolve_plugins` | Orders plugins and reports unmet needs |

## Steps

1. Define C headers using fixed-width types, opaque handles and function pointers only. Every struct starts with size or version. verify: `ports/*.h` compile as C11 with `-Wall -Wextra -Werror -pedantic`.
2. Add layout tests. verify: `static_assert(offsetof(...))` covers each public struct, in a test built as C++ and as C.
3. Implement provide and get with semver rules: same major, minor at least the requested. verify: test requesting `1.3` from `1.4` succeeds, and from `1.2` or `2.0` fails with a status code.
4. Implement the resolver as a dependency graph, with cycle detection. verify: tests cover a valid order, a cycle and a missing dependency.
5. Implement shared-library loading on POSIX and Windows. On Windows, load a uniquely named copy so the DLL stays replaceable. verify: `greeter` loads and answers through the port on Linux, Windows and macOS.
6. Implement a static registration table for targets with no dynamic loading. verify: on `wasm32`, `greeter` runs through the same port test.
7. Implement interposition: `provide` with `.wraps` receives the previous implementation. verify: `greeter_wrap` changes one call, while another call returns the original result.
8. Return structured errors with code, plugin, port, requested version and fix. verify: `needs_missing` produces JSON naming the missing port and exits non-zero without a crash.
9. Package the suite in `conformance/registry/`. verify: `ctest --preset linux-asan -L conformance` passes.

## Must not happen

- No C++ type, template, exception or STL type across a boundary.
- No first-party private API.
- No vendor name in a port.
- No cached function pointer across a reload. Read through the registry slot.
- No removal or reorder of a field within a major version.

## Done when

- **Owns exit check:** "An interposing plugin wraps another plugin's interface and forwards unchanged calls."
- **Owns exit check:** "A missing dependency fails with a readable structured error, not a crash."
- Reload with World state is proven later, in [0.07](phase-0-07-clocks-snapshots.md).
