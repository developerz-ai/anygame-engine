# Phase 0.02: Memory

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.01](phase-0-01-build-ci-platform.md).

## Goal

Tagged allocators, arenas, pools, a bounded heap and generational handles, with no global `new` in the kernel.

## Design source

- [Kernel: Memory](../idea/04-kernel.md).
- [C++23 craft](../idea/16-cpp23-craft.md): allocator choice, arena rules, ASan and Valgrind integration, tested reference listing.
- [C++ decisions](../idea/29-cpp-decisions.md): "Pick an allocation".
- [Libraries and profilers](../idea/28-libraries-and-profilers.md): general heap behind a port.
- [Platforms](../idea/30-platforms.md): browser memory limits.

## Files to create or change

- `kernel/include/ag/memory/{tag,allocator,arena,scope,pool,tlsf,handle}.h`.
- `kernel/src/memory/{tag,arena,pool,tlsf,page_backend}.cpp`.
- `kernel/src/memory/sanitizer.h`: one wrapper for ASan and Valgrind annotations.
- `kernel/tests/memory/*_test.cpp`.
- `scripts/lib/no-raw-alloc.ts`, with tests, wired into `bin/check`.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `ag::MemTag` | Names module and lifetime |
| `ag::Allocator` | Passed explicitly. Alloc, free, tag |
| `ag::PageBackend` | Virtual memory, or fixed page blocks on `wasm32` |
| `ag::Arena` | Linear allocation for trivially destructible types |
| `ag::ArenaScope` | RAII rewind |
| `ag::Pool<T>` | Fixed-size slots with free list |
| `ag::Tlsf` | Bounded-time general allocator |
| `ag::Handle<T>` | Index plus generation |
| `ag::HandlePool<T>` | Issues, resolves and invalidates handles |
| `ag::memory_report()` | Live bytes and peak per tag |

## Steps

1. Implement tags and per-tag counters. verify: test allocates under two tags and `memory_report()` shows exact bytes for each.
2. Implement `PageBackend` on `ag::vm`, with a block fallback when reserve-and-commit is absent. verify: the arena test passes on `linux-asan` and `wasm32`.
3. Implement `Arena` and `ArenaScope`. A `requires` clause rejects non-trivially-destructible types. verify: a compile-fail test for `Arena::make<std::string>` fails to compile.
4. Poison free arena memory for ASan and Valgrind. Back sanitizer tests with heap or virtual memory, never a stack buffer. verify: death tests detect use-after-rewind and overflow under `linux-asan`.
5. Implement `Pool` and `HandlePool`. verify: a freed slot reused gets a new generation, and the stale handle resolves to null.
6. Implement `Tlsf`. verify: a seeded property test of 1,000,000 random operations against a simple model has no overlap and no lost bytes.
7. Allocation failure returns `nullptr` or `std::expected`, and names the tag. verify: exhausting a small arena returns the error with the correct tag.
8. Add the raw-allocation lint for `new`, `delete`, `malloc`, `free` in `kernel/` outside `kernel/src/memory/`. verify: a fixture containing `new int` produces a finding.
9. Run Valgrind on the memory test binary. verify: `valgrind --error-exitcode=1` exits 0 on a non-ASan Linux build.

## Must not happen

- No global heap use outside the allocator package.
- No per-object destructors in arena data.
- No `std::shared_ptr`.
- No raw pointer stored across a frame or module boundary.
- No silent allocation failure.

## Done when

- All memory tests pass on Linux, Windows, macOS and `wasm32`.
- The raw-allocation lint runs in `bin/check`.
- Owns no Phase 0 exit check directly. It supplies the memory the others depend on.
