# 🧠 16. C++23 craft

How engine C++ gets written here. Binds the engine's own code. A game may follow it, and owns its own choices ([rule 8](01-thesis.md)).

Agents write this code, so every rule is either a compiler error, a sanitizer failure, a lint, or a test. A rule with no check is a wish.

## ✅ What was verified

As of 2026-11-21, on Linux x86-64, with GCC 16.0.1 (experimental trunk), Clang 22.1.8 and Valgrind 3.22.0.

| Check | GCC 16 | Clang 22 | Valgrind |
|---|---|---|---|
| Listing below builds with `-std=c++23 -Wall -Wextra -Wpedantic -Werror` | pass | pass | n/a |
| Arena, scope, pool and stale-handle test, under ASan + UBSan | pass | pass | clean |
| Read after `ArenaScope` rewind is caught | caught | caught | caught (`Invalid read`) |
| Overflow past a heap-backed arena allocation is caught | caught | caught | not run |
| Same overflow on a **stack-backed** arena at `-O1` | caught | **missed** | not run |
| `import std` single-file build | pass (`--compile-std-module`) | not run | n/a |

Not verified: MSVC, Apple Clang, Windows, macOS, and every other snippet-free rule below. Those are design rules until CI runs them.

**Lesson from the miss:** Clang removed the check because it could prove the read stayed inside the stack array. Back arenas with heap or virtual memory in every sanitizer test.

## 🧰 C++23 features

| Feature | GCC | Clang / libc++ | MSVC | Apple Clang | Use |
|---|---|---|---|---|---|
| `std::expected` | 12 | 16 | 19.33 | 15.0.0 | **Yes.** Default error type inside modules |
| Deducing `this` | 14 | 18 to 19 | 19.32 partial, 19.43 | not listed | Yes, for CRTP-free mixins. Probe Apple first |
| `std::span` (C++20) | yes | yes | yes | yes | **Yes.** Default for buffers, never at the C ABI |
| `std::mdspan` | 16 | 18 | 19.39 | 15.0.0 | Yes, for grids, tilemaps and voxels |
| `std::print` | 14 | 18 | 19.37 | 16.0.0 | Tools and tests only. Never in hot paths |
| `std::flat_map` | 15 | 20 | 19.51 | not listed | Tools only until the baseline has it |
| `std::move_only_function` | 12 | not listed | 19.32 | not listed | **Avoid.** Use a kernel function ref or job struct |
| `import std` | 15 (macOS: 16) | 18.1.2 | 19.36 | not listed | Optional. See below |

Versions are from [cppreference](https://en.cppreference.com/w/cpp/compiler_support/23.html), read 2026-11-21. Library rows use the libc++ column. "Not listed" means the table gives no version, so assume absent until a probe passes. Ubuntu's stock libc++ 18 here has no `<flat_map>`, which matches the table.

Probe, never assume:

```cpp
#include <version>
#if !defined(__cpp_lib_expected)
#error "AnyGame needs std::expected"
#endif
```

### Proposed baseline

| Toolchain | Minimum | Why |
|---|---|---|
| GCC | 16 | `std::mdspan` first appears here |
| Clang | 20 | `flat_map`, deducing `this` |
| MSVC | 19.43 | Complete deducing `this` |
| Apple Clang | Decide by CI probe | The table has gaps for features above |

### Language and library rules

| Rule | Check |
|---|---|
| `-fno-exceptions -fno-rtti` in kernel and runtime modules | Build flags |
| Fallible functions return `std::expected<T, DomainError>` | Review, `[[nodiscard]]` |
| Never call `.value()` on `expected` with exceptions off. Test it, then use `*` | clang-tidy custom check |
| Standard library hardening on in dev: `_GLIBCXX_ASSERTIONS`, `_LIBCPP_HARDENING_MODE` | `dev` preset |
| No `<iostream>`, `<regex>`, `<locale>` in runtime | Include lint |
| No `std::shared_ptr` in runtime. Ownership is a scope, arena or handle | Lint |
| No static initialisers with side effects | Lint on `.init_array` |
| No `new`, `delete`, `malloc` outside the allocator package | Lint plus allocation-count test |
| `constexpr` and `consteval` for tables and schema hashes | Review |
| Concepts on every template parameter that has a requirement | Better errors for agents |

## 📦 Named modules or headers

**Decision proposed: headers plus PCH as the default. Named modules are opt-in, per package, after a spike.** This answers [open question 3](../build/open-questions.md).

| Factor | Evidence |
|---|---|
| Generators | `import std` works with Ninja only. Visual Studio generators cannot build BMIs for imported targets ([CMake 4.5 docs](https://cmake.org/cmake/help/latest/manual/cmake-cxxmodules.7.html)) |
| Compilers | CMake lists support on all three, but with per-platform limits. Ubuntu before 26.04 ships broken `libstdc++.modules.json` (same page) |
| Apple | cppreference lists no Apple Clang version for standard library modules |
| ABI | BMIs are compiler-specific, so they can never be the plugin boundary |
| Plugin boundary | Is plain C headers regardless ([section 5](05-extending.md)) |

Rules:

- Public interfaces are C headers. Always.
- C++ wrappers stay header-only.
- A package may use modules internally if every Phase 0 platform passes.
- Re-check this decision each engine major version.

## 🧱 Memory

### Allocator choice

| Lifetime | Allocator | Free cost |
|---|---|---|
| One frame or tick | Linear frame arena | Reset, O(1) |
| One function or job | `ArenaScope` | Rewind, O(1) |
| Fixed-size, churny (bullets, events) | Pool with generational handles | O(1) |
| Chunks of components | 16 KB chunk pool | O(1) |
| Level or streaming cell | Tagged heap block | Free the tag |
| Unpredictable size and lifetime | TLSF | O(1), bounded |
| Growable with stable addresses | Reserve virtual memory, commit on demand | Decommit |

### Rules

- **Pass the allocator.** No global heap. Context is an explicit parameter.
- **Tag everything.** A tag names the module and the lifetime. `ag profile` reports per tag.
- **Frame arenas per worker.** No lock. Two frames kept alive when render reads extract data.
- **RAII at scope level, not object level.** One `ArenaScope` frees thousands of objects. No per-object destructors in hot data.
- **Arenas hold trivially destructible types only.** The `requires` clause below makes it a compile error.
- **Handles across boundaries.** Raw pointers live for one function call at most.
- **Pointers into chunks die at structural change.** Never hold one across a system boundary.
- **Fail visibly.** Allocation failure returns `nullptr` or `expected`, and the tag's budget report names the owner.

### Components

Every component must satisfy this, or it does not compile:

```cpp
template <class T>
concept Component = std::is_trivially_copyable_v<T>
                 && std::is_standard_layout_v<T>
                 && std::is_trivially_destructible_v<T>;
```

- No pointers, `std::string` or `std::vector` inside a component. Use handles and asset IDs.
- Padding bytes are indeterminate. Snapshot hashes walk schema fields, never `memcmp` the struct.
- `std::has_unique_object_representations_v` is false for floats, so it cannot replace the schema walk.

### Data layout

| Rule | Why |
|---|---|
| SoA by default, one array per hot field | Cache and SIMD |
| Split hot and cold fields into separate components | Smaller iteration stride |
| Iterate linearly, batch by archetype | Prefetcher does the work |
| Pass spans to interfaces, not single items | One indirect call per batch |
| Per-thread counters on separate cache lines | False sharing |
| Use a kernel `AG_CACHE_LINE` constant: 64, or 128 on Apple Silicon | `hardware_destructive_interference_size` varies by flags, so it must not reach an ABI |
| Measure before SIMD intrinsics | Autovectorised loops are often enough |

### Reference listing: arena, scope, pool, handle

Tested as written. See the verification table.

```cpp
#pragma once
#include <cstddef>
#include <cstdint>
#include <expected>
#include <new>
#include <span>
#include <type_traits>
#include <vector>

#if defined(__SANITIZE_ADDRESS__)
#define AG_ASAN 1
#elif defined(__has_feature)
#if __has_feature(address_sanitizer)
#define AG_ASAN 1
#endif
#endif
#ifdef AG_ASAN
#include <sanitizer/asan_interface.h>
#define AG_POISON(p, n) ASAN_POISON_MEMORY_REGION((p), (n))
#define AG_UNPOISON(p, n) ASAN_UNPOISON_MEMORY_REGION((p), (n))
#else
#define AG_POISON(p, n) ((void)(p), (void)(n))
#define AG_UNPOISON(p, n) ((void)(p), (void)(n))
#endif
#ifdef AG_VALGRIND
#include <valgrind/memcheck.h>
#define AG_VG_NOACCESS(p, n) VALGRIND_MAKE_MEM_NOACCESS((p), (n))
#define AG_VG_UNDEFINED(p, n) VALGRIND_MAKE_MEM_UNDEFINED((p), (n))
#else
#define AG_VG_NOACCESS(p, n) ((void)(p), (void)(n))
#define AG_VG_UNDEFINED(p, n) ((void)(p), (void)(n))
#endif

namespace ag {

class Arena {
public:
    explicit Arena(std::span<std::byte> memory) : memory_{memory} {
        AG_POISON(memory_.data(), memory_.size());
        AG_VG_NOACCESS(memory_.data(), memory_.size());
    }
    ~Arena() { AG_UNPOISON(memory_.data(), memory_.size()); AG_VG_UNDEFINED(memory_.data(), memory_.size()); }
    Arena(const Arena&) = delete;
    Arena& operator=(const Arena&) = delete;

    [[nodiscard]] void* allocate(std::size_t size, std::size_t align) noexcept {
        const auto base = reinterpret_cast<std::uintptr_t>(memory_.data());
        const auto aligned = (base + used_ + align - 1) & ~(std::uintptr_t{align} - 1);
        const auto offset = aligned - base;
        if (offset > memory_.size() || size > memory_.size() - offset) return nullptr;
        used_ = offset + size;
        void* result = memory_.data() + offset;
        AG_UNPOISON(result, size);
        AG_VG_UNDEFINED(result, size);
        return result;
    }

    template <class T>
        requires std::is_trivially_destructible_v<T>
    [[nodiscard]] T* create(const T& value) noexcept {
        void* slot = allocate(sizeof(T), alignof(T));
        return slot ? new (slot) T(value) : nullptr;
    }

    [[nodiscard]] std::size_t mark() const noexcept { return used_; }
    void rewind(std::size_t mark) noexcept {
        AG_POISON(memory_.data() + mark, used_ - mark);
        AG_VG_NOACCESS(memory_.data() + mark, used_ - mark);
        used_ = mark;
    }

private:
    std::span<std::byte> memory_;
    std::size_t used_ = 0;
};

class ArenaScope {
public:
    explicit ArenaScope(Arena& arena) noexcept : arena_{arena}, mark_{arena.mark()} {}
    ~ArenaScope() { arena_.rewind(mark_); }
    ArenaScope(const ArenaScope&) = delete;
    ArenaScope& operator=(const ArenaScope&) = delete;

private:
    Arena& arena_;
    std::size_t mark_;
};

struct Handle {
    std::uint32_t index = 0;
    std::uint32_t generation = 0; // 0 is never live
    friend bool operator==(Handle, Handle) = default;
};

enum class PoolError : std::uint8_t { full, stale_handle };

template <class T>
    requires std::is_trivially_copyable_v<T>
class Pool {
public:
    explicit Pool(std::uint32_t capacity) : slots_(capacity) {
        free_.reserve(capacity);
        for (std::uint32_t i = capacity; i > 0; --i) free_.push_back(i - 1);
    }

    [[nodiscard]] std::expected<Handle, PoolError> insert(const T& value) {
        if (free_.empty()) return std::unexpected(PoolError::full);
        const std::uint32_t index = free_.back();
        free_.pop_back();
        Slot& slot = slots_[index];
        slot.value = value;
        slot.generation |= 1; // odd = live
        return Handle{index, slot.generation};
    }

    [[nodiscard]] std::expected<T*, PoolError> get(Handle handle) noexcept {
        if (handle.index >= slots_.size()) return std::unexpected(PoolError::stale_handle);
        Slot& slot = slots_[handle.index];
        if ((handle.generation & 1) == 0 || slot.generation != handle.generation)
            return std::unexpected(PoolError::stale_handle);
        return &slot.value;
    }

    [[nodiscard]] std::expected<void, PoolError> erase(Handle handle) {
        auto found = get(handle);
        if (!found) return std::unexpected(found.error());
        Slot& slot = slots_[handle.index];
        ++slot.generation; // even = dead; wraps after 2^31 reuses of one slot
        free_.push_back(handle.index);
        return {};
    }

private:
    struct Slot { T value{}; std::uint32_t generation = 0; };
    std::vector<Slot> slots_;
    std::vector<std::uint32_t> free_;
};

} // namespace ag
```

The sample `Pool` uses `std::vector` for brevity. The kernel version takes an allocator.

## 🧵 Concurrency and fibres

| Hazard | Rule |
|---|---|
| A fibre can resume on another thread | **No `thread_local` access across a yield** |
| Compilers may cache a TLS address across a call | Read worker context through a non-inlined accessor, after every yield |
| Mutex held across a yield | Forbidden: it may unlock on the wrong thread. Lint it |
| Stack overflow on small fibre stacks | Guard page per stack, plus a debug high-water mark |
| Blocking syscalls stall a worker | I/O goes through the async I/O module |
| Default `seq_cst` hides intent | Write the memory order, with a comment naming the paired operation |
| Lock-free code by instinct | Prefer read/write-set scheduling. Lock-free needs a TSan stress test |
| Parallel output order | Deterministic mode merges by entity or job index, never by finish order |

### Sanitizers need to know about fibres

| Tool | Required integration |
|---|---|
| ASan | `__sanitizer_start_switch_fiber` before a switch, `__sanitizer_finish_switch_fiber` on the new stack |
| TSan | `__tsan_create_fiber`, `__tsan_switch_to_fiber` just before the switch, `__tsan_destroy_fiber` |
| Valgrind | `VALGRIND_STACK_REGISTER` for each fibre stack |

TSan limit: it only knows fibre order through these calls, and a switch synchronises by default. That can hide real races. Keep a **thread-only scheduler mode** that runs each job on a plain thread, and run TSan on it too.

## 🔬 Tools

| Tool | Finds | When | Notes |
|---|---|---|---|
| ASan + UBSan | Overflow, use-after-free, UB | Every test run | `-fno-sanitize-recover=undefined`. Can combine |
| ASan arena poisoning | Use after rewind, overflow inside an arena | Every test run | Without it, ASan cannot see inside arenas |
| TSan | Data races | Pre-merge | Cannot combine with ASan |
| MSan | Uninitialised reads | Nightly | Clang only. All linked code must be instrumented |
| Valgrind memcheck | Uninitialised use, leaks, in uninstrumented binaries | Nightly | About 10x to 50x slower. Never combine with ASan |
| Callgrind | Exact instruction counts | Perf gate | Deterministic, so ideal for CI regression diffs |
| Cachegrind | Simulated cache misses | Perf review | Compare runs, do not trust absolute numbers |
| Massif | Heap over time | On demand | Annotate custom allocators, or it sees one block |
| clang-tidy | Bug patterns, house rules | Changed files | Custom checks for the rules above |
| libFuzzer | Parser and protocol bugs | Nightly, short run pre-merge | Every untrusted-input parser has a target |
| Tracy | Frame timeline | Dev profiling | Compiled out of shipping builds |
| `perf` | Real CPU hotspots, cache events | Performance work | Build with frame pointers in dev |

### Valgrind client requests

| Request | Use |
|---|---|
| `VALGRIND_MAKE_MEM_NOACCESS` | Poison free arena memory (used above) |
| `VALGRIND_MAKE_MEM_UNDEFINED` | Mark fresh allocations uninitialised (used above) |
| `VALGRIND_MALLOCLIKE_BLOCK`, `VALGRIND_FREELIKE_BLOCK` | Track allocator blocks for leak reports and Massif |
| `VALGRIND_CREATE_MEMPOOL`, `VALGRIND_MEMPOOL_ALLOC`, `VALGRIND_MEMPOOL_FREE` | Pools and arenas as first-class objects |

## ⚡ Build speed

Agents rebuild constantly, so build time is agent time.

| Technique | Rule |
|---|---|
| Ninja | Only generator for dev |
| `mold` on Linux, `lld` elsewhere | Linking is the incremental bottleneck |
| `ccache` locally, `sccache` shared with CI | Key on compiler and flags |
| PCH per package | Standard headers and stable kernel headers only |
| Unity builds per package | Full builds only. Incremental dev stays per-file |
| Forward declarations and thin headers | Lint include cost with `-ftime-trace` |
| Templates declared in headers, instantiated once | `extern template` for common types |
| Split debug info | `-gsplit-dwarf` on Linux |
| Plugins as shared libraries in dev | A change relinks one module, not the game |
| Hot reload before rebuild-and-restart | The default path for gameplay changes |

## 🔌 ABI and hot reload

- **C types only** at the boundary: fixed-width integers, POD structs, opaque handles, function pointers.
- **`extern "C"`, `noexcept` behaviour.** An exception crossing a boundary is a bug. Host-facing C++ callbacks catch nothing because nothing throws.
- **No RTTI, STL types, templates or virtual classes** across a boundary.
- **Allocate and free on the same side,** through a passed allocator.
- **Struct growth:** first field is size or version. Append only.
- **ABI test in CI:** compile a `_vN` consumer against the current header, and compare layouts with `static_assert(offsetof(...))`.
- **State lives in Worlds.** No mutable globals in a plugin, or reload loses them.
- **Reload sequence:** drain jobs → serialise module state to schema → unload → load → migrate → resume.
- **No cached function pointers** across a frame. Read through the registry slot.
- **No `thread_local` with destructors in plugins.** It can run after `dlclose`.
- **Never unload code with a parked fibre inside it.**

## 🧪 Testing

| Type | Rule | Example |
|---|---|---|
| Unit | No clock, network, or real filesystem | Pool reuses a slot with a new generation |
| Deterministic | Fixed seed and tick count. Assert the state hash | 600 ticks twice gives the same checksum |
| Snapshot round trip | Save, run, restore, re-run, compare | Foundation of rollback |
| Property | Random operation sequences against a simple model | ECS add/remove matches a `std::map` |
| Fuzz | Every parser of untrusted bytes | Packets, saves, mods, assets |
| Golden | Text scene dumps and image captures, with a reviewed diff | Render tests allow a stated tolerance |
| Allocation count | A hot system allocates **zero** after warmup | Counting allocator asserts in the test |
| Budget | Instruction count via Callgrind, against a stored baseline | Fail over +2% |
| ABI | Old consumer against new header | Layout asserts |
| Conformance | Every interface implementation | `physics.conformance` |

Rules:

- A bug fix starts with a failing test.
- A failing test prints seed, tick, entity, system and a replay command.
- No sleeps. Advance a virtual clock.
- Tests run in parallel, each with its own World.

## 🚦 `bin/check` tiers

Planned. Time targets are goals for a changed package, on a dev machine.

| Tier | Command | Runs | Target | When |
|---|---|---|---|---|
| 0 | `bin/check fast` | Format, changed-file lint, compile changed package | < 10 s | Every edit loop |
| 1 | `bin/check unit` | Tier 0 + package tests under ASan + UBSan | < 60 s | Before reporting a change done |
| 2 | `bin/check pr` | Affected packages, clang-tidy, TSan, ABI, allocation, budget | < 10 min | Pull request gate |
| 3 | `bin/check nightly` | MSan, Valgrind, long fuzz, soak, cross-platform checksums | < 2 h | Nightly |
| 4 | `bin/check device` | Minimum-spec device farm, per-kit frame budgets | < 4 h | Nightly or release |

Every tier supports `--json`: one result per check, with `code`, `file`, `line`, `message`, `fix`.

## 📎 Sources

Read for this doc, 2026-11-21:

- [cppreference: compiler support for C++23](https://en.cppreference.com/w/cpp/compiler_support/23.html)
- [CMake 4.5: cmake-cxxmodules](https://cmake.org/cmake/help/latest/manual/cmake-cxxmodules.7.html)

Found by search, excerpts only:

- [LLVM: TSan fiber test](https://llvm.googlesource.com/llvm-project/+/refs/heads/main/compiler-rt/test/tsan/fiber_simple.cpp)
- [LLVM review: TSan fiber API](https://reviews.llvm.org/D54889)
- [Valgrind manual: advanced topics and client requests](https://snapshots.sourceware.org/valgrind/trunk/latest/html/manual-core-adv.html)
- [Red Hat: Valgrind Memcheck with a custom memory manager](https://developers.redhat.com/articles/2022/03/23/use-valgrind-memcheck-custom-memory-manager)

Valgrind slowdown, tool limits and other unlinked claims are general knowledge. Verify before relying on them.
