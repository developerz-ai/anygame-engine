# 🏎️ 50. CPU, cache, SIMD and memory layout

**Memory layout usually decides game performance.** Modern CPUs can do many operations per cycle, then spend most of their time waiting for data that is not nearby. Put the right data together, walk it in order, keep branches predictable, and SIMD often comes almost free.

Engine rule, overridable by games ([rule 8](01-thesis.md#design-rules)). Apply it where code runs per entity or per item ([quality bar](32-quality-bar.md#solid-at-the-boundaries-data-oriented-in-the-hot-path)). Use clear code everywhere else.

Sources for depth: [Drepper's memory paper](https://cgvr.informatik.uni-bremen.de/teaching/mpar_literatur/What%20Every%20Programmer%20Should%20Know%20About%20Memory%20-%20Ulrich%20Drepper,%202007.pdf), [Agner Fog's microarchitecture guide](https://mail.agner.org/optimize/microarchitecture.pdf), [Intel's optimization manual](https://intel.com/content/www/us/en/content-details/821612/intel-64-and-ia-32-architectures-optimization-reference-manual-volume-1.html), [Acton's data-oriented design talk](https://www.slideshare.net/cellperformance/data-oriented-design-and-c), [Fabian's Data-Oriented Design](https://dataorienteddesign.com/dodbook/node10.html), and [Game Programming Patterns on data locality](https://gameprogrammingpatterns.com/data-locality.html).

## ✅ What was measured

Measured 2026-11-21 on one machine, while it had other background load. **These numbers illustrate the direction and rough size of an effect. They are not engine benchmarks or promises for another CPU.**

| Item | Value |
|---|---|
| CPU | AMD Ryzen 7 5700X3D, 8 cores, 16 threads, 64-byte cache lines |
| Caches | 256 KiB L1d total, 4 MiB L2 total, 96 MiB L3 |
| Compiler | GCC 16.0.1 |
| Flags | `-std=c++23 -O3 -DNDEBUG -march=x86-64-v3 -pthread` (latency test: `-O2`) |
| Method | Three process runs. Each result is the median of 5 to 11 timed repeats, and the table shows the median of the three |

| Experiment | Slower case | Faster case | Gain |
|---|---|---|---|
| Update 3 positions, 1M entities | AoS, 64-byte struct: 1.504 ns/entity | SoA: 0.252 ns | 6.0x |
| Read one hot field, 2M items | Inside 128-byte struct: 3.313 ns | Split hot array: 0.747 ns | 4.4x |
| Walk 8M nodes | Shuffled linked list: 75.904 ns | Contiguous: 0.551 ns | 138x |
| Linked list laid out in order | 1.309 ns | Contiguous: 0.551 ns | 2.4x |
| 4 threads increment counters | Adjacent, false sharing: 5.533 ns | 128-byte separation: 0.531 ns | 10.4x |
| Sum if `x >= 128`, random data | Branch: 3.044 ns | Branchless: 0.461 ns | 6.6x |
| Same, sorted data | Branchless: 0.461 ns | Branch: 0.390 ns | Branch wins by 1.2x |
| `a*b+c` on 4,096 floats | Scalar: 0.3924 ns/item | Auto-vectorised: 0.1251 ns | 3.1x |
| Same | Auto-vectorised: 0.1251 ns | Hand AVX2: 0.1253 ns | No meaningful gain |

Three lessons: layout gave the biggest wins, **branchless code loses on predictable data**, and **hand-written SIMD added nothing when the compiler had already vectorised the loop**.

### Measured random-access latency

Random pointer chase with 64-byte steps, same machine.

| Working set | 4 KiB pages | Huge pages requested | Roughly hits |
|---|---|---|---|
| 16 KiB | 0.99 ns | 0.99 ns | L1 |
| 256 KiB | 3.03 ns | 3.02 ns | L2 |
| 2 MiB | 13.28 ns | 11.61 ns | L3 |
| 32 MiB | 20.10 ns | 12.78 ns | L3, TLB cost visible |
| 256 MiB | 97.31 ns | 90.86 ns | Mostly RAM |
| 1 GiB | 105.02 ns | 102.80 ns | RAM |

## 🧠 How the CPU sees your code

| Part | What it does | What hurts it | What to do |
|---|---|---|---|
| **Cache lines** | Memory moves in lines, commonly 64 bytes | Hot data spread across many lines | Keep hot data dense |
| **Cache levels** | Small and fast, then larger and slower | Working set larger than a level | Shrink data and process in blocks |
| **Associativity** | An address can live in only a few ways of a set | Many hot addresses mapping to one set | Avoid regular large strides |
| **Hardware prefetcher** | Detects steady access patterns | Random pointers | Walk arrays forward or backward |
| **TLB** | Caches virtual-to-physical page mappings | Touching many pages | Group data, use huge pages for big arenas |
| **Store buffer** | Lets writes finish later | Many writes to contended lines, loads just after partial writes | Batch writes, avoid mixed-size access |
| **Branch predictor** | Guesses control flow ahead of time | Random conditions | Sort, partition, or remove the branch |
| **Out-of-order core** | Runs independent work in parallel | Long dependency chains, pointer chasing | Separate independent calculations |
| **Front end** | Fetches and decodes instructions | Large, scattered hot code | Keep hot paths small, move errors out |
| **Execution ports** | Limit operations of each type per cycle | Too many divides, gathers or shuffles | Use cheaper operations |

### Rough costs

Typical orders of magnitude, recalled and unverified. They vary widely by CPU. Measure what matters.

| Operation | Rough cost |
|---|---|
| Integer add, bitwise, predicted branch | Under 1 to 1 cycle |
| Float add or multiply | 3 to 5 cycles latency, often 2 per cycle throughput |
| Integer or float division | 10 to 40+ cycles |
| Mispredicted branch | 10 to 25 cycles |
| L1 hit | About 4 cycles |
| L2 hit | About 10 to 20 cycles |
| L3 hit | About 30 to 70 cycles |
| RAM | 60 to 120 ns |
| Contended atomic | Tens to hundreds of cycles |
| Allocation from a general heap | Tens of ns or more |
| System call or page fault | Hundreds of ns to microseconds |
| Thread context switch | Microseconds |

## 🧱 Choose a layout

| Access pattern | Layout | Why |
|---|---|---|
| Loop reads a few fields of many entities | **SoA** | Loads only what it uses, and vectorises |
| Fields are nearly always used together | AoS of a small struct | One line holds them all |
| SIMD over grouped fields, with fewer pointers | **AoSoA** | Blocks of 4, 8 or 16 values per field |
| Most code reads a tiny subset | **Hot/cold split** | Smaller stride |
| Rarely present data | Separate sparse component | Common entities stay small |
| Random lookup of stable objects | Pool + generational handle | Safe indirection |
| Frequent insert/remove, order unimportant | Swap-and-pop | Stays dense |
| Spatial queries | Sorted by cell or Morton order | Neighbours are close in memory |
| Tree that is read often | Flat array, breadth-first or van Emde Boas order | Fewer cache misses |

**AnyGame's default** is an archetype ECS with one SoA column per component field in 16 KB chunks ([kernel](04-kernel.md#data-model-archetype-ecs-plus-a-scene-tree-view)). Do not build a parallel layout without a benchmark.

### Struct rules

| Rule | Why |
|---|---|
| Sort fields by descending alignment | Removes padding |
| Use 32-bit indices rather than 64-bit pointers in hot data | Half the size, and serialises directly |
| Quantise values where precision allows | Smaller hot data |
| Replace many `bool`s with a bitmask | One word holds them |
| Keep hot component size at or below a cache line | One access per entity |
| `static_assert` size and field offsets | A later edit cannot silently bloat it |
| Do not use packed structs for hot data | Unaligned, and references become unsafe |
| Use `AG_CACHE_LINE`, never a literal | [Apple Silicon differs](16-cpp23-craft.md#data-layout) |

```cpp
#include <cstddef>
#include <cstdint>

struct MoverHot {
    float x, y, z;
    float speed;
    std::uint32_t target;
    std::uint32_t flags;
};
static_assert(sizeof(MoverHot) == 24);
static_assert(offsetof(MoverHot, target) == 16);
```

### Sharing data between threads

| Situation | Do |
|---|---|
| Per-thread counters | One cache line each, then sum at the end |
| Read-mostly config beside a hot counter | Move them to different lines |
| Parallel writes to one array | Give each job a whole block, not alternating items |
| Many threads update one atomic | Use per-worker values and merge |
| Need detection | `perf c2c` |

Details: [concurrency](45-concurrency.md).

### Order work for the cache

| Trick | Effect |
|---|---|
| Sort entities by archetype or chunk | Linear walks |
| Sort draws by a packed key | Fewer state changes and misses |
| Process spatial cells in tile order | Neighbour data stays warm |
| Loop blocking | Keeps each pass inside a cache level |
| Move a rare branch's work to a second pass | Hot loop stays small |
| Compact after churn | Restores contiguity |
| Allocate related data together | Fewer lines and pages |
| Use huge pages on large arenas after measuring | Fewer TLB misses |

## ⚡ SIMD

**Order of preference:** make the data SoA → let the compiler vectorise → use [Highway](https://google.github.io/highway/en/master/README.html) → use platform intrinsics only for one proven hot function.

### Help the auto-vectoriser

| Blocker | Fix |
|---|---|
| Possible pointer aliasing | Copy to locals, use `__restrict__` in a measured hot function |
| Function call in the loop | Inline it |
| Early exit | Process a block, then test |
| Branch in the loop | Write a select or mask |
| Non-contiguous access | Change the layout |
| Mixed types and widths | Use one width per loop |
| Loop counter wider or narrower than needed | Use `std::size_t` |
| Floating-point reductions | Ordered sums resist vectorisation. Use explicit SIMD or an allowed scoped flag |
| Unknown data dependency | Restructure, so `out[i]` depends only on inputs |

```cpp
#include <cassert>
#include <cstddef>
#include <span>

inline void multiply_add(std::span<float> out, std::span<const float> a,
                         std::span<const float> b, std::span<const float> c) {
    assert(out.size() == a.size() && a.size() == b.size() && b.size() == c.size());
    float* __restrict__ r = out.data();
    const float* __restrict__ x = a.data();
    const float* __restrict__ y = b.data();
    const float* __restrict__ z = c.data();
    for (std::size_t i = 0; i < out.size(); ++i) r[i] = x[i] * y[i] + z[i];
}
```

Only use this when output cannot overlap the inputs. `__restrict__` is a GCC and Clang spelling, so wrap it in a macro for MSVC. Check the compiler's result:

```bash
g++ -O3 -march=x86-64-v3 -fopt-info-vec -fopt-info-vec-missed -c file.cpp
clang++ -O3 -march=x86-64-v3 -Rpass=loop-vectorize -Rpass-missed=loop-vectorize -c file.cpp
```

### Instruction set tiers

| Target | Baseline suggestion | Optional tier | Notes |
|---|---|---|---|
| x86-64 desktop | SSE2 is guaranteed. Consider a higher floor only with player-hardware data | AVX2 + FMA, AVX-512 | Use runtime dispatch |
| Apple Silicon | NEON | None needed at first | Fixed 128-bit |
| Android arm64 | NEON | SVE where present | Vector length varies |
| Browser | WebAssembly SIMD128 | [Relaxed SIMD](https://caniuse.com/mdn-webassembly_relaxed-simd) | Relaxed results can vary by hardware, so keep it out of deterministic code |
| Server | Chosen by the fleet | `x86-64-v3` or arm64 | The build can match known hardware |

### Runtime dispatch

| Rule | Why |
|---|---|
| Dispatch per batch function, never per item | The indirect call is amortised |
| Choose once at startup | Stable and testable |
| Use [Highway's `HWY_DYNAMIC_DISPATCH`](https://google.github.io/highway/en/master/quick_reference.html) by default | One source, many targets |
| Test every compiled target | A rarely used path is where bugs hide |
| Keep scalar fallback | Debugging and unsupported CPUs |
| Do not use `-march=native` for shipped builds | Crashes on other CPUs |
| Deterministic worlds pin behaviour | Different targets must give identical results for the promised [tier](../decisions/012-determinism-guarantee-tiers.md) |

### SIMD techniques

| Technique | Use | Watch out |
|---|---|---|
| Mask and blend | Replace `if` per lane | Both sides are computed |
| Load and store with tails | Finish the last items | Never read past the buffer |
| Masked tail or padded buffers | Avoid a scalar remainder | Padding must be owned memory |
| Gather and scatter | Sparse fields | Often slow. Prefer SoA |
| Shuffle-heavy code | AoS conversion | Often means the layout is wrong |
| Horizontal adds | Reductions | Keep them at loop end |
| Batched math | `sin`, `sqrt`, matrix transforms | Check accuracy and determinism |
| Filter by bitmask | Culling many bounds | Compact results after |
| Alignment | Fixed blocks | Modern unaligned loads are usually fine, so do not add complexity without proof |

### Denormals

| Topic | Rule |
|---|---|
| Problem | Very small floats can be far slower on some CPUs |
| FTZ/DAZ | Set per thread in audio and suitable hot workers, through one kernel helper |
| Fibres and threads | Each worker must set its state, and a job must not leak changed state |
| Determinism | Do not change FP environment inside a deterministic World unless all peers match |
| Better fix | Add damping thresholds and clamp near-zero values in filters and physics |

## 🔀 Branches

| Data pattern | Best choice |
|---|---|
| Almost always one way | Normal branch, cold path moved away |
| Sorted or clustered | Normal branch |
| Truly random condition | Branchless or SIMD mask |
| Many conditions in a loop | Partition items first, then run separate tight loops |
| Dispatch by type | Group by type, then one loop per type |
| Large `switch` per entity | Separate systems or archetypes |

```cpp
#include <cstdint>
#include <span>

inline std::uint64_t sum_at_least(std::span<const std::uint8_t> values, std::uint8_t limit) {
    std::uint64_t sum = 0;
    for (std::uint8_t value : values) {
        const std::uint64_t keep = -static_cast<std::uint64_t>(value >= limit);
        sum += value & keep;
    }
    return sum;
}
```

Measure with real data, since the [sorted case above](#-what-was-measured) favoured the branch.

## 🎯 Prefetching

**Software prefetch is a last resort.** Use it only when a profile shows misses on a pattern the hardware cannot predict.

| Rule | Why |
|---|---|
| Try layout first | It removes the miss |
| Prefetch far enough ahead | Too late does nothing |
| Do not prefetch linear arrays | Hardware already does |
| Keep the benchmark in the PR | It can get slower |
| Re-measure on each target CPU | Distances do not transfer |

## 🔬 Measure, then change

| Question | Tool | Example |
|---|---|---|
| Cache and branch rates | `perf stat` | `perf stat -e cycles,instructions,cache-misses,branch-misses ./game` |
| Where cycles go | `perf record` | `perf record -g ./game` |
| False sharing | `perf c2c` | `perf c2c record ./game` |
| Repeatable cache simulation | Cachegrind | `valgrind --tool=cachegrind ./game` |
| Instruction-count regression | Callgrind | [CI gate](16-cpp23-craft.md#-tools) |
| Struct holes | `pahole` | `pahole -C MoverHot build/game` |
| Loop throughput estimate | `llvm-mca` | `clang++ -O3 -S -o - f.cpp \| llvm-mca` |
| What the compiler generated | Compiler Explorer | Compare compilers and flags |
| Timeline spikes | Tracy | [Profilers](28-libraries-and-profilers.md#-profilers-which-one-answers-my-question) |

## ✔️ Agent checklist for hot code

1. Profile first, in an optimised build with real data.
2. Stop if the code is not hot.
3. Remove work.
4. Fix layout.
5. Batch and sort.
6. Remove allocation.
7. Check that the loop vectorises.
8. Use explicit SIMD only if the benchmark still needs it.
9. Report before and after on the target CPU.
10. Keep the benchmark in the repo.

## Proof

| Check | Passes when |
|---|---|
| Hot struct size | `static_assert` fails on growth |
| Hot-system vectorisation | A compiler report check confirms named loops vectorise |
| Regression | Instruction counts stay within the agreed threshold |
| False sharing | `perf c2c` reports no hot shared-write line |
| SIMD targets | Every compiled target passes the same test vectors |
| Determinism | Deterministic worlds match across selected SIMD targets |
| Tails | ASan passes for lengths 0 through twice the vector width |
