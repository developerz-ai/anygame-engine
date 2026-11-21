# 🧵 45. Multithreading and concurrency

**Declare what each system reads and writes, and let the scheduler run it in parallel.** Most engine and game code should never touch a thread, lock or atomic. If a row below fits, use it.

Planned design as of 2026-11, checked against search extracts of the linked pages. Unlinked items are recalled general practice and unverified. All numbers are starting points to measure. These defaults bind engine code, and a game can override them ([rule 8](01-thesis.md#design-rules)).

C++ hazards and sanitizer setup live in [C++23 craft](16-cpp23-craft.md#-concurrency-and-fibres). Web limits live in [platforms](30-platforms.md#-browser-webassembly--webgpu). Servers are in [game servers and scaling](46-distributed-servers.md).

## Which tool do I use?

| I need to | Use | Do not |
|---|---|---|
| Update many entities | System over a query | Spawn threads |
| Split a large array | Parallel-for over chunks | One job per entity |
| Run work after other work | Job graph dependency | Poll a flag |
| Change entity structure during a system | Command buffer | Mutate the archetype in place |
| Tell other systems something happened | Deferred event | Call them directly |
| Read a file or socket | Async I/O module | Block a worker |
| Compute something slow over many frames | Background job with cancellation | Run it in the frame |
| Collect per-thread results | Per-worker buffers, then merge | Shared vector with a mutex |
| Count something | Per-worker counter, summed later | Hot shared atomic |
| Protect rarely used shared state | `std::scoped_lock` around a short section | Lock-free code |
| Publish one finished value | Atomic with acquire and release | `volatile` |
| Pass work between two threads | Bounded queue | Unbounded queue |
| Call an OS window or UI API | Main-thread task queue | Call it from a worker |

## Execution modes

The job API stays the same. Only the backend changes.

| Mode | How it runs | Use for |
|---|---|---|
| `fibers` | Work-stealing workers, jobs can yield while waiting | Desktop, console, mobile runtime |
| `threads` | Thread pool, jobs run to completion | Browser, TSan, simple tools |
| `inline` | One thread, in schedule order | Debugging, smallest targets, unit tests |
| `deterministic` | Fixed order and merge, on any backend | Replay, rollback, lockstep |

Fibres let a job wait without blocking its worker, as in [Naughty Dog's fibre job system](https://gdcvault.com/play/1022187/Parallelizing-the-Naughty-Dog-Engin). Bungie similarly [turned almost all of Destiny's engine into a job graph](https://gdcvault.com/play/1022164/Multithreading). Because the browser build [needs a thread-only mode](../decisions/009-kernel-targets-wasm32.md), **no system may require fibres to be correct**.

## The worker pool

| Rule | Starting point |
|---|---|
| One pool for the process | No module owns private CPU-bound threads |
| Workers per process | Logical cores minus reserved main, render submit and I/O needs |
| Query the core count | Never hard-code it |
| Own deque per worker, steal when empty | Local work stays cache-warm |
| Priorities | `critical`, `frame`, `background`, with no starvation of background |
| Long jobs | Split them, or use the background class |
| Blocking calls | Forbidden on frame workers |
| Idle workers | Spin briefly, then sleep, to save battery |
| Worker-local state | Arena, RNG stream, log buffer, command buffer |

## The job graph

```text
system declares reads and writes -> scheduler builds a graph -> compatible systems overlap
```

| Access | Can overlap with |
|---|---|
| `read A` | Other `read A`, anything not writing A |
| `write A` | Nothing else touching A |
| `read A`, `write B` | Systems not writing A and not touching B |
| Resource or singleton | Declared exactly like a component |
| Exclusive system | Nothing. Use rarely, and report it in the profiler |

Rules:

- **Undeclared access is a bug.** Debug builds check each access against the declaration.
- **Order by labels** such as `before: movement`, never by registration order.
- **Ambiguous writers are reported,** because two unordered systems writing the same data can change results.
- `ag profile --jobs` shows the critical path, idle time and the systems blocking parallelism.

## Frame pipelining

Overlap frames so simulation and rendering do not wait on each other.

```text
Frame N:    [ simulate ][ extract ][ render jobs ][ GPU ]
Frame N+1:              [ simulate ][ extract ][ render jobs ][ GPU ]
```

| Stage | May read | May write |
|---|---|---|
| Simulate | Simulation World | Simulation World |
| Extract | Simulation World | Render World. Short sync point |
| Render jobs | Render World | Command lists |
| GPU | Frame's buffers | Targets |

- Keep extract small: copy only changed data. Destiny's renderer talk notes [the cost of a full extra copy of game state](https://advances.realtimerendering.com/destiny/gdc_2015/Tatarchuk_GDC_2015__Destiny_Renderer_web.pdf).
- Limit frames in flight, because each one adds input latency and memory. Start at two.
- Per-frame arenas live until the GPU finishes that frame.
- Input is sampled as late as the loop allows, and latency is measured ([feel](39-animation-camera-feel.md)).

## Task size and parallel-for

| Rule | Why |
|---|---|
| Split by ECS chunk | Natural cache-friendly batch |
| Target about 50 to 500 µs per task, then measure | Too small wastes time scheduling. Too large hurts balance |
| Run inline below a threshold | Few entities do not justify a job |
| Use deterministic chunk order when required | Stable merge |
| Keep the body free of locks | A lock serialises the parallel loop |
| Write only to the current chunk or a worker buffer | No shared mutation |

## Structural changes, events and merge

| Need | Pattern |
|---|---|
| Spawn, destroy, add or remove a component | Per-worker command buffer, applied at a sync point |
| Refer to an entity not yet spawned | Temporary handle resolved on apply |
| Emit an event from a parallel system | Per-worker event buffer, delivered next stage |
| Deterministic merge | Sort by stable key: system, entity, then sequence |
| Random numbers | Stream derived from world seed, system and entity |
| Sum or minimum | Commutative reduction |

**Never merge by completion order.** It changes from run to run.

## Platform rules

| Platform | Must stay on the main thread | Threading notes |
|---|---|---|
| macOS, iOS | [AppKit state](https://developer.apple.com/videos/play/wwdc2021/10054/), UIKit, the [main SDL entry path](https://wiki.libsdl.org/SDL3/README-macos) | Use QoS classes, do not pin cores (unverified detail) |
| Windows | Window message pump on the creating thread | Prefer `CreateFiber`, per [platforms](30-platforms.md#-windows) |
| Linux | Windowing through the SDL path | Good target for TSan and `perf` |
| Android | Activity lifecycle and surface callbacks | Avoid pinning. Thermal state changes what cores can sustain |
| Browser | DOM, input and most browser APIs | Simulation in a worker. The main thread never blocks |
| Servers | None | Consider NUMA and core pinning |

### Hybrid cores and NUMA

| Situation | Default |
|---|---|
| Performance and efficiency cores | Let the OS schedule. Give frame work a high priority hint |
| Efficiency cores | Background, streaming and decode jobs |
| Work stealing across core types | Allowed, but avoid leaving a critical job on a slow core |
| Thermal throttling on mobile | Governor lowers work before the OS throttles |
| Multi-socket server | One process per NUMA node. Riot's [VALORANT servers raised local memory access to 97–99%](https://technology.riotgames.com/news/valorants-128-tick-servers) by alternating NUMA placement |
| Many instances on one host | Test together, since [shared L3 contention slowed Riot's instances](https://technology.riotgames.com/news/valorants-128-tick-servers) |

## I/O and async

| Target | Backend |
|---|---|
| Linux | [`io_uring`](https://man7.org/linux/man-pages/man7/io_uring.7.html), with thread fallback |
| Windows | IOCP, IoRing or DirectStorage for assets |
| Apple | Dispatch I/O |
| Android | Thread pool |
| Browser | Async browser APIs in a worker |

| Rule | Why |
|---|---|
| I/O completes by posting a job | Workers never block |
| Every request has a deadline and cancellation | No leaks, and no stale work |
| Every queue is bounded | Backpressure instead of memory growth |
| Avoid C++ coroutines in hot paths until measured | Their frame allocation must use engine allocators |
| A continuation names its resume context | Prevents touching main-thread APIs from a worker |

## Locks, atomics, lock-free

Choose the first one that works.

| Rank | Tool | Use when |
|---|---|---|
| 1 | No sharing | Job graph, per-worker data, message passing |
| 2 | Immutable data | Build once, then read from many threads |
| 3 | Mutex | Short, rare, no I/O and no yield inside |
| 4 | Read-write lock | Reads vastly outnumber writes, proven by profiling |
| 5 | Atomic counter or flag | One independent value |
| 6 | Proven library queue | Producer-consumer ([library picks](28-libraries-and-profilers.md#-containers-and-concurrency)) |
| 7 | Custom lock-free | **Escalate first** ([C++ decisions](29-cpp-decisions.md#stop-and-escalate)) |

### Memory order

| Pattern | Order |
|---|---|
| Statistic with no dependent data | `relaxed` |
| Publish data, then set a flag | Writer `release`, reader `acquire` |
| Read-modify-write that hands off data | `acq_rel` |
| Not sure | `seq_cst`, with a comment. Do not weaken it without a test and a reason |

Every non-`seq_cst` atomic names its paired operation in a comment.

### Hazards

| Hazard | Prevention | How to see it |
|---|---|---|
| Data race | Declared access, no shared mutation | TSan |
| Deadlock | Global lock order, one lock at a time by default, no callbacks under a lock | Lock-order checker |
| Waiting on your own job | Wait only through the scheduler | Debug graph validation |
| Priority inversion | No locks shared across priorities, keep critical sections short | Tracy lock view |
| False sharing | Separate writers by `AG_CACHE_LINE` | `perf c2c` |
| Lock convoy | Reduce sharing | Tracy contention |
| Starvation | Aging on background priority | Queue wait histogram |
| ABA | Generational handles, tagged indices | Stress test |
| Use after cancel | Owner outlives its job, or job holds a handle | ASan |
| Queue overflow | Bounded queues, a stated drop or block policy | Queue depth metric |
| Thread-local across yield | Re-fetch context after each yield | Fibre debug check |

## Backpressure and cancellation

| Queue full | Policy |
|---|---|
| Latest state only (position, camera) | Replace old item |
| Optional work (cosmetic VFX, far LOD) | Drop and count |
| Required work (commands, saves) | Slow the producer and report |
| Overloaded frame | Shed in the declared order: cosmetic, then far AI, then lower update rates |

Cancellation is cooperative: long jobs check a token at batch boundaries, then release resources through scope ownership.

## Logging and diagnostics

- Each worker appends to a lock-free local buffer, flushed by a background job.
- A log call in a hot path is compiled out or sampled.
- Every record carries tick, worker, job and system.
- A crash handler flushes buffers without allocating.

## Testing

| Test | Finds | When |
|---|---|---|
| **TSan on `threads` mode** | Data races | Pull request |
| Access validation | Undeclared reads and writes | Every debug test |
| **Schedule fuzzing** | Hidden order dependence: random steal, delay and system order within the graph, using a logged seed | Nightly |
| Stress | Rare interleavings, repeated at high core counts | Nightly |
| One-worker and many-worker runs | Accidental parallel or serial assumptions | Pull request |
| Determinism under shuffle | Merge bugs: same checksum on 1, 2 and N workers | Pull request |
| Deadlock watchdog | A job graph that stops progressing | All tests |
| Scaling benchmark | Speedup at 1, 2, 4, 8 and N workers | Performance gate |
| Contention profile | Slow locks and shared cache lines | Performance review |

## Definition of done

1. No new thread, lock or atomic unless the table above calls for it.
2. All data access is declared.
3. TSan is clean in `threads` mode.
4. Deterministic worlds keep the same checksum across worker counts.
5. It still runs in `inline` mode and on the browser target.
6. No worker blocks on I/O.
7. Scaling and contention are reported for hot systems.
