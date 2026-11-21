# 🧭 29. C++ decisions, already made

**A model of any strength should write good engine C++ by following this page.** The highest-return decisions are made here, so an agent looks up the answer instead of reasoning it out. If a row fits, use it. Deviate only with a measurement or a stated reason.

These defaults bind engine code. A game may choose differently ([rule 8](01-thesis.md#design-rules)). Deep reasoning: [C++23 craft](16-cpp23-craft.md). Library picks: [libraries and profilers](28-libraries-and-profilers.md). Hot paths: [CPU, cache, SIMD](50-cpu-cache-simd-layout.md). Advanced techniques: [veteran tricks](51-veteran-cpp-tricks.md). Proposed as of 2026-11.

## The ten highest-return rules

Ordered by how much they usually matter.

1. **Choose the right data layout.** Arrays of small components beat any later micro-optimisation.
2. **Do less work.** Skip idle, hidden or unchanged things before speeding them up.
3. **Process in batches.** One call on a span, not one call per entity.
4. **No allocation in a hot path.** Use the frame arena or a pool.
5. **Group memory by lifetime,** then free the whole group at once.
6. **Use handles, not long-lived pointers.**
7. **Keep hot data small and contiguous.** Move cold fields elsewhere.
8. **Run systems in parallel by declaring reads and writes,** rather than adding locks.
9. **Measure before optimising,** with the [right profiler](28-libraries-and-profilers.md#-profilers-which-one-answers-my-question).
10. **Run sanitizers on every test run.** Most memory bugs die here.

## Pick a container

| I need | Use | Not |
|---|---|---|
| A list | `std::vector` or kernel array, reserved | `std::list` |
| Fixed small list | `std::array` or inline-capacity array | Heap vector |
| Temporary list this frame | Arena-backed array | `std::vector` in a hot loop |
| A view of data | `std::span` | `const std::vector&` |
| Multidimensional view | `std::mdspan` | Nested vectors |
| Key lookup, large | Dense hash map | `std::unordered_map` |
| Key lookup, under about 32 items | Linear search on an array | Any map |
| Sorted lookup, rarely changed | Sorted array or `std::flat_map` | `std::map` |
| Set of small integers | Bitset | Hash set |
| Objects referenced by others | Pool + generational handle | `shared_ptr` |
| FIFO | Ring buffer | `std::deque` |
| Many-thread queue | Bounded MPMC queue | Mutex + vector |
| Remove from unordered list | Swap with last, then pop | Erase from the middle |

## Pick an allocation

| Data lives for | Use |
|---|---|
| This function or job | `ArenaScope` |
| This frame or tick | Frame arena |
| Fixed-size, frequently created | Pool |
| A level or streaming cell | Tagged heap, freed by tag |
| The whole game | Startup arena, never freed one by one |
| Unknown size and lifetime | TLSF or general heap, last resort |
| GPU resource | VMA or D3D12MA through the RHI |

## Pick a type or signature

| Situation | Use |
|---|---|
| Function can fail | `std::expected<T, DomainError>`, `[[nodiscard]]` |
| Value may be absent | `std::optional<T>` |
| Read small value (up to 16 bytes, trivially copyable) | By value |
| Read large value | `const T&` |
| Read a range | `std::span<const T>` |
| Read text without keeping it | `std::string_view` |
| Keep text | Interned ID or arena copy |
| Output many values | Caller-provided `std::span<T>`, return count |
| Unique ownership outside hot data | `std::unique_ptr` with custom deleter, or scope |
| Shared ownership | Redesign with handles or one owner |
| Reference across frames, modules or network | Handle |
| Closed set of variants | `enum` + `switch`, or `std::variant` |
| Open set across plugins | Registered C function table |
| Non-copyable callback | `std::move_only_function`, never in hot loops |
| Hot callback | Template parameter or function pointer plus context |
| Compile-time table | `constexpr` |
| Assets, entity types and names | Hashed ID at runtime, readable string in debug |
| Physical quantities | Strong types, such as `Metres` and `Seconds` |
| Integer size in hot structs | Smallest that holds the range; indices are `uint32_t` |

## RAII: what to do

| Resource | Pattern |
|---|---|
| Arena memory | `ArenaScope` rewinds at scope end |
| Lock | `std::scoped_lock`, never across a fibre yield |
| File, socket, GPU object | Move-only wrapper, destructor releases |
| Profiler zone | Scope macro |
| Temporary state change | Scope guard restoring it |
| Components | No destructors. They must be trivial |
| Many small objects | One group owner. No per-object destructor |

**Rule of zero** by default. If a type owns a resource, delete copy, implement move, and release in the destructor.

## Make hot code fast

Work top to bottom. Stop as soon as the budget is met.

| Step | Trick | Typical cost |
|---|---|---|
| 1 | Do not run it: sleep, cull, skip unchanged | Low |
| 2 | Run less often: time-slice, LOD | Low |
| 3 | Better algorithm or spatial structure | Medium |
| 4 | Better layout: SoA, hot/cold split, sorted data | Medium |
| 5 | Batch and remove virtual or indirect calls | Medium |
| 6 | Parallelise through the job graph | Medium |
| 7 | Remove aliasing, branches and divisions | Medium |
| 8 | SIMD through Highway | High |
| 9 | Build with LTO and PGO | Low, shipping only |
| 10 | Prefetch, `[[likely]]`, `[[assume]]`, manual tweaks | Only with proof |

### Small tricks that are usually safe

| Trick | Use |
|---|---|
| Compare squared distances | Avoid `sqrt` |
| Multiply by a reciprocal | When dividing many values by one number |
| Sort by key before processing | Fewer cache misses and state changes |
| Store a sort key as one integer | Fast render and job ordering |
| Power-of-two capacity with a mask | Fast ring buffers |
| Bitmasks for flags and queries | Many tests in one operation |
| Early-out on the cheapest test first | Fewer expensive checks |
| Replace a branch with a table | When the branch is unpredictable |
| Reserve capacity once | No reallocation spikes |
| Reuse buffers | `clear()` keeps capacity |
| Pass a local copy of a member into a loop | Avoids reloading through aliases |
| `static_assert(sizeof(T) == N)` on hot structs | Catches accidental growth |

## Never do this

| Mistake | Why it hurts | Do instead |
|---|---|---|
| Virtual `update()` per entity | Cache misses, no batching | System over a query |
| `new` or `malloc` in gameplay | Stalls and fragmentation | Arena or pool |
| `std::shared_ptr` in runtime | Atomic costs, unclear ownership | Handles |
| Hold a pointer across structural change | Use-after-move | Handle or re-query |
| Hold `span` or `string_view` past its owner | Dangling | Copy or scope it |
| Use a reference into a vector, then push | Dangling after growth | Index |
| `thread_local` across a fibre yield | Reads the wrong thread | Re-fetch context |
| Lock held across a yield | Deadlock or wrong-thread unlock | Finish before yielding |
| `volatile` for threads | Not synchronisation | `std::atomic` |
| `memcmp` on a struct | Compares padding | Compare by schema |
| Signed overflow, invalid cast, strict-aliasing break | Undefined behaviour | `std::bit_cast`, checked maths |
| Float in a deterministic simulation without its mode | Desync | Deterministic maths module |
| `rand()`, wall clock in simulation | Not reproducible | World RNG and clock |
| Iterating a hash map for simulation order | Nondeterminism | Stable sort or index order |
| Global mutable state | Breaks tests, reload and worlds | World or explicit context |
| STL type across a plugin boundary | ABI break | C types |
| Heavy include in a public header | Slow builds | Forward declare |
| Optimising without measuring | Wasted effort, worse code | Profile first |

## When something goes wrong

| Symptom | First tool |
|---|---|
| Crash or corrupted memory | ASan + UBSan build |
| Random failure across runs | Replay with seed, then TSan or `rr` |
| Uninitialised value | MSan or Valgrind memcheck |
| Replay diverges | Compare per-tick state hashes, find first bad tick |
| Stutter | Tracy, worst frame |
| Slowly rising memory | heaptrack, tag report |
| Slower after a change | Callgrind diff |
| Scaling stops with more cores | `perf c2c`, job graph view |
| Build got slower | `-ftime-trace` |
| Binary got bigger | Bloaty diff |

## Agent checklist before saying done

1. Used an existing block or library instead of writing a new one.
2. No allocation added to a hot path.
3. Every fallible call is handled.
4. No new pointer outlives its frame or crosses a module.
5. Tests pass under ASan and UBSan.
6. Threaded code passes TSan.
7. Deterministic worlds still match their checksum.
8. Budget diff is reported.
9. No new warning.

## Stop and escalate

Do not guess on these. Write a decision record or ask for review:

- Changing a public C ABI, schema version or wire format.
- Writing lock-free code or custom memory ordering.
- Adding a new runtime dependency.
- Making a kernel change.
- Using `reinterpret_cast`, inline assembly, or anything undefined made to "work".
