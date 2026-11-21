# 🧙 51. Veteran C++ and engine tricks

**A trick earns its place by solving a measured problem.** This is the toolbox experienced engine programmers reach for, with when to use each and, just as important, when not to.

Engine guidance as of 2026-11. Games may choose differently ([rule 8](01-thesis.md#design-rules)). Start with [C++ decisions](29-cpp-decisions.md). Memory rules are in [C++23 craft](16-cpp23-craft.md), hardware in [CPU, cache and SIMD](50-cpu-cache-simd-layout.md), threads in [concurrency](45-concurrency.md), and libraries in [libraries and profilers](28-libraries-and-profilers.md).

**Verification, 2026-11-21:** every C++ snippet in this page and [doc 50](50-cpu-cache-simd-layout.md) compiled with GCC 16.0.1 and Clang 22.1.8 using `-std=c++23 -Wall -Wextra -Werror`, and passed behaviour tests under ASan and UBSan. MSVC and Apple Clang were not tested. Unlinked advice is recalled general practice.

## 🧺 Containers and data structures

| Trick | Use when | Cost | Do not use when |
|---|---|---|---|
| **Flat array + linear search** | Under about 32 items | Very little | Large sets |
| **Swap-and-pop** | Order does not matter | Moves one item | Stable order is needed |
| **Free list inside unused slots** | Fixed-size pool | No extra memory per free slot | Types with destructors, unless handled |
| **Slot map / handle table** | Stable references with reuse detection | Indirection + generation | Pure linear processing |
| **Sparse set** | Fast add, remove, contains, dense iteration | Sparse index memory | IDs span a huge, sparse range |
| **Bitset** | Flags, occupancy, query masks | One bit per item | Rare members in a huge range |
| **Ring buffer** | Queues, history, audio | Fixed capacity | Unbounded growth |
| **Intrusive list** | Object is already in stable memory and on several lists | Pointers in the object | Hot iteration |
| **Small-buffer optimisation** | Most instances are tiny | Larger object | Value is usually large |
| **Sorted flat map** | Read-mostly lookup | Slow insert | Frequent changes |
| **Stable bucket array** | Stable addresses with mostly dense memory | Bucket overhead | Plain vector is enough |
| **Radix sort** | Many integer keys | Temporary buffer | Few items or complex comparisons |
| **Packed sort key** | Render and job order | Field limits | Keys cannot fit |
| **Interned strings** | Repeated names and fast compare | Table lifetime | Short-lived unique text |

**Free list in unused memory:** while a pool slot is free, its bytes store the next free index, so the free list costs no extra memory. The tested pool with generations is in [C++23 craft](16-cpp23-craft.md#reference-listing-arena-scope-pool-handle).

### Sparse set

```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

template <std::uint32_t Capacity>
class SparseSet {
    std::array<std::uint32_t, Capacity> sparse_{};
    std::array<std::uint32_t, Capacity> dense_{};
    std::uint32_t size_ = 0;

public:
    [[nodiscard]] bool contains(std::uint32_t id) const {
        return id < Capacity && sparse_[id] < size_ && dense_[sparse_[id]] == id;
    }
    bool insert(std::uint32_t id) {
        if (id >= Capacity || contains(id)) return false;
        sparse_[id] = size_;
        dense_[size_++] = id;
        return true;
    }
    bool erase(std::uint32_t id) {
        if (!contains(id)) return false;
        const std::uint32_t last = dense_[--size_];
        dense_[sparse_[id]] = last;
        sparse_[last] = sparse_[id];
        return true;
    }
    [[nodiscard]] std::span<const std::uint32_t> items() const { return {dense_.data(), size_}; }
};
```

**Ring buffer:** use a power-of-two capacity and index with `head & (capacity - 1)`. Let counters grow, so `write - read` is the size. For threaded queues, use [correct memory ordering](45-concurrency.md) or a [proven library](28-libraries-and-profilers.md#-containers-and-concurrency).

### Packed sort key and radix sort

```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <utility>

constexpr std::uint64_t draw_key(std::uint8_t layer, std::uint16_t pipeline,
                                 std::uint16_t material, std::uint32_t depth24) {
    return std::uint64_t{layer} << 56 | std::uint64_t{pipeline} << 40 |
           std::uint64_t{material} << 24 | (depth24 & 0xFF'FFFFu);
}

inline void radix_sort(std::span<std::uint32_t> keys, std::span<std::uint32_t> scratch) {
    std::span<std::uint32_t> from = keys, to = scratch;
    for (int shift = 0; shift < 32; shift += 8) {
        std::array<std::size_t, 256> offset{};
        for (auto key : from) ++offset[(key >> shift) & 0xFF];
        std::size_t total = 0;
        for (auto& count : offset) {
            const std::size_t next = total + count;
            count = total;
            total = next;
        }
        for (auto key : from) to[offset[(key >> shift) & 0xFF]++] = key;
        std::swap(from, to);
    }
}
```

`scratch` must be the same size as `keys`. After four passes the sorted result is back in `keys`.

### Bit tricks, using the standard library

| Need | Use | Avoid |
|---|---|---|
| Count set bits | `std::popcount` | Hand-written loops |
| First set bit | `std::countr_zero` | Macros |
| Round up to power of two | `std::bit_ceil` | Bit-smearing code |
| Is a power of two | `std::has_single_bit` | Clever expressions |
| Rotate | `std::rotl`, `std::rotr` | Shift by a possibly full width |
| Reinterpret a value's bits | `std::bit_cast` | Pointer casts, union punning |
| Byte order | `std::byteswap`, `std::endian` | Assumptions |

## 🏷️ Pointers and handles

| Trick | Use when | Portability limit |
|---|---|---|
| **Low-bit tag** | Aligned pointer needs a small state | Limited by `alignof(T)` |
| **High-bit tag** | Rarely, and only inside one platform package | **Avoid.** Address width, ARM top-byte features and memory tagging make it target-specific |
| **32-bit index** | Default in hot data | Needs a base array |
| **Generational handle** | Reference that can go stale | Slight lookup cost |
| **Relative offset** | Position-independent cooked data | Base must stay known |

Low-bit tags: mask with `alignof(T) - 1`, assert the pointer is aligned, and keep the conversion inside one small type.

## 🧬 Compile-time and generic code

| Trick | Use for | Prefer instead when |
|---|---|---|
| `constexpr` tables | Lookup data, schema IDs | Table is huge, which hurts builds |
| Compile-time hash | IDs from string literals | Input comes from a player |
| Concepts | Better errors on templates | Nothing is generic |
| CRTP | Static interface on older code | **Deducing this or concepts** in C++23 |
| Deducing `this` | One function for const and non-const | Simple overload is clearer |
| Non-owning function reference | Callback during a call | Callback must outlive the call |
| `std::move_only_function` | Stored owner callback | Hot paths |
| `[[no_unique_address]]` | Empty allocator or policy members | **MSVC needs `[[msvc::no_unique_address]]`**, so wrap in a macro |
| X-macros | Generated enum tables with no tooling | **Prefer the schema generator** |
| Extern templates | Common instantiations | Rarely used templates |

### Stable compile-time hash

```cpp
#include <cstdint>
#include <string_view>

constexpr std::uint64_t fnv1a(std::string_view text) {
    std::uint64_t hash = 14695981039346656037ull;
    for (char c : text) {
        hash ^= static_cast<unsigned char>(c);
        hash *= 1099511628211ull;
    }
    return hash;
}
static_assert(fnv1a("") == 14695981039346656037ull);
```

Good for stable IDs. Do not use it for security or attacker-controlled hash tables. Check for collisions at cook time.

### Callback with no heap

```cpp
#include <functional>
#include <memory>
#include <type_traits>
#include <utility>

template <class Signature> class FunctionRef;

template <class R, class... Args>
class FunctionRef<R(Args...)> {
    void* object_;
    R (*call_)(void*, Args...);

public:
    template <class F>
        requires(!std::is_same_v<std::remove_cvref_t<F>, FunctionRef> &&
                 std::is_invocable_r_v<R, F&, Args...>)
    FunctionRef(F& function)
        : object_(const_cast<void*>(static_cast<const void*>(std::addressof(function)))),
          call_([](void* object, Args... args) -> R {
              return std::invoke(*static_cast<F*>(object), std::forward<Args>(args)...);
          }) {}
    R operator()(Args... args) const { return call_(object_, std::forward<Args>(args)...); }
};
```

**Never store it.** It refers to a callable owned by the caller.

**Deducing `this`:** write `auto&& at(this auto&& self, std::size_t i)` and return `std::forward_like<decltype(self)>(self.items[i])`, so one function serves const and non-const callers.

## 🛟 Lifetime, UB and safe low-level code

| Need | Correct tool | Do not |
|---|---|---|
| Reinterpret a trivially copyable value | `std::bit_cast` | `*(int*)&f` |
| Read bytes from a file buffer | `std::memcpy` into a value | Cast and dereference a possibly unaligned pointer |
| Object in raw storage | `std::construct_at` | Assign into uninitialised memory |
| Treat bytes as existing objects | `std::start_lifetime_as`, once available | Assume all compilers support it |
| Signed overflow | Unsigned math or checked add | Rely on wraparound |
| Large shift | Check width first | Shift by the full type width |
| Compare float bits | Explicit schema-aware compare | `memcmp` on structs |
| Hash a struct | Hash each schema field | Hash padding bytes |

**`std::start_lifetime_as` status:** C++23 added it, but support is uneven. [GCC's bug tracker shows library work for GCC 16](https://gcc.gnu.org/pipermail/gcc-bugs/2025-September/930455.html), and [Clang and libc++ work was still under review in May 2026](https://lists.llvm.org/pipermail/libcxx-commits/2026-May/123220.html). Use `memcpy` until a CI probe proves every platform.

**Trivial relocation:** [C++26's P2786 feature was removed at Kona in 2025](https://quuxplusone.github.io/blog/2025/11/18/kona-trip-report), per [P3920](https://open-std.org/JTC1/SC22/WG21/docs/papers/2025/p3920r0.html). AnyGame instead relies on its [`Component` concept](16-cpp23-craft.md#components): trivially copyable components can move with `memcpy`.

### Optimiser hints

| Hint | Use | Danger |
|---|---|---|
| `[[likely]]`, `[[unlikely]]` | Only after a profile | A wrong hint makes code slower |
| `[[assume(x)]]` | Hot code with a proven invariant | **False assumption is undefined behaviour** |
| `std::unreachable()` | A truly impossible branch | Same. In debug, assert first |
| `[[gnu::cold]]`, `noinline` | Error and rare paths | Compiler-specific, so wrap in a macro |
| `__restrict__` | Measured non-overlapping loops | Overlap is undefined behaviour |

```cpp
#include <cstdio>
#include <cstdlib>

#if defined(_MSC_VER)
#define AG_COLD __declspec(noinline)
#else
#define AG_COLD [[gnu::cold, gnu::noinline]]
#endif

AG_COLD inline void report_bad_index(unsigned index, unsigned size) {
    std::fprintf(stderr, "bad index %u of %u\n", index, size);
}

inline bool checked_read(const int* data, unsigned size, unsigned index, int& out) {
    if (index >= size) [[unlikely]] {
        report_bad_index(index, size);
        return false;
    }
    out = data[index];
    return true;
}
```

**Scope guard:** a small move-disabled type whose destructor runs a callback restores temporary state on every exit path. It must not throw.

## 🐞 Debugging tricks

| Trick | What it catches | Notes |
|---|---|---|
| **Assert levels** | Cheap always in dev, expensive in debug, invariant checks in tests | Ship only crash-safe checks |
| **Memory poisoning** | Use after free in arenas | [ASan and Valgrind hooks](16-cpp23-craft.md#-tools) |
| **Fill patterns** | Reads of uninitialised or freed data | Distinct byte per state in debug |
| **Canaries and guard pages** | Buffer overruns | Guard pages for fibre stacks |
| **Generation counters** | Stale handles | Keep on in release if cheap |
| **Debug draw** | Spatial bugs | Command buffer, compiled out of shipping |
| **State hash per tick** | Desyncs | Binary search for the first bad tick |
| **Frame allocator high-water mark** | Budget creep | Report per tag |
| **Allocation-count test** | Hidden hot-path allocation | Should be zero after warmup |
| **Deterministic hash seed** | Nondeterministic iteration | Never iterate hash maps in simulation |
| **`rr` record and replay** | Rare crashes | Linux |

### Per-frame strings

| Do | Avoid |
|---|---|
| Format into a frame arena or fixed buffer | Heap `std::string` every frame |
| Use interned IDs in logs and events | Building names in hot code |
| Update text only when its value changes | Reformatting every HUD label |
| Defer debug formatting until displayed | Formatting logs that are filtered out |

## 🚀 Build and link tricks

| Trick | Benefit | Use | Caution |
|---|---|---|---|
| **LTO** | Cross-file inlining | Shipping | Slower link. Use ThinLTO for iteration |
| **PGO** | Layout and inlining from real play | Shipping, with bot-driven profiles | Profile must represent the game |
| **[BOLT](https://llvm.googlesource.com/llvm-project.git/+/refs/heads/main/bolt/docs/index.md)** | Post-link code layout | Large x86-64 or AArch64 ELF binaries | Needs relocations and a profile |
| `-fvisibility=hidden` | Fewer exports, better optimisation | All modules | Export the C ABI explicitly |
| `-fno-plt` | Fewer indirect stubs on ELF | After measuring | Platform-specific |
| Section garbage collection | Removes unused code | Shipping size | Keep plugin entry points |
| Unity builds | Faster full builds | CI | Hide include and name issues |
| PCH | Faster headers | Per package | Stable headers only |
| Forward declarations | Fewer rebuilds | Public headers | Do not obscure ownership |
| `-ftime-trace` | Shows slow includes and templates | When builds slow | |
| Pimpl | Isolates a heavy dependency | Non-hot classes | Adds indirection |

More: [build speed](16-cpp23-craft.md#-build-speed).

### Fast-math

**Keep `-ffast-math` off by default.** It permits changes that can break NaN and infinity handling and floating-point reproducibility, and linking it can alter process-wide floating-point state on some toolchains.

| Instead | When |
|---|---|
| Rewrite the formula | Most cases |
| Local SIMD reduction | Sums and dot products |
| Narrow flags in one translation unit | Non-deterministic, measured code |
| `-ffp-contract` policy set explicitly | FMA can change results, so deterministic modules pin it |

## ❌ Tricks that aged badly

| Old trick | Why to avoid now | Use instead |
|---|---|---|
| Fast inverse square root | Hardware and SIMD are better | `sqrt`, SIMD estimate with refinement |
| Duff's device | Compilers do this better | Plain loop |
| XOR swap | Slower and fails on aliases | `std::swap` |
| Hand-unrolled loops | Often blocks vectoriser | Compiler flags |
| Lookup table for cheap math | Cache misses can cost more | Measure |
| Union type punning | Undefined in C++ | `std::bit_cast` |
| `volatile` for threads | Not synchronisation | `std::atomic` |
| `register`, `inline` as a speed hint | Ignored or removed | Profile-guided optimisation |
| Macros for constants | No type or scope | `constexpr` |
| Custom `memcpy` | Standard one is highly tuned | `std::memcpy` |
| Pointer tricks with high bits | Portability hazards | Index or handle |

## Choosing a trick

1. Is it a measured problem? If not, write the plain version.
2. Does [C++ decisions](29-cpp-decisions.md) already answer it? Use that.
3. Does a proven library do it? [Wrap it](28-libraries-and-profilers.md).
4. Is the trick in this page? Follow its limits.
5. Add a test and a benchmark.
6. Name what it buys in a comment.

Anything involving undefined behaviour, custom memory ordering or a public ABI needs [review](29-cpp-decisions.md#stop-and-escalate).
