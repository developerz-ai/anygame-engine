# Phase 0.06: Jobs and system scheduling

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.01](phase-0-01-build-ci-platform.md), [0.05](phase-0-05-ecs.md).

## Goal

Systems declare reads and writes, and the scheduler runs them in parallel on fibres, on plain threads, or deterministically.

## Design source

- [Kernel: Jobs](../idea/04-kernel.md).
- [C++23 craft](../idea/16-cpp23-craft.md): concurrency, fibres, TSan limits.
- [Platforms](../idea/30-platforms.md): Windows fibres and browser threads.
- [Libraries and profilers](../idea/28-libraries-and-profilers.md): fibre switch and queues.
- [Decision 009](../decisions/009-kernel-targets-wasm32.md).

## Files to create or change

- `kernel/include/ag/jobs/{scheduler,job,counter,system,schedule}.h`.
- `kernel/src/jobs/{scheduler,worker,deque,schedule}.cpp`.
- `kernel/src/jobs/backend_{fibre,thread,single}.cpp`.
- `kernel/src/jobs/fibre_{fcontext,win32}.cpp`.
- `kernel/tests/jobs/*_test.cpp`.

## Public interface sketch

| Name | Responsibility |
|---|---|
| `ag::JobScheduler` | Owns workers. Created explicitly, never global |
| `ag::JobMode` | `fibre`, `thread`, `single` |
| `ag::JobCounter` | Waits for a group of jobs |
| `ag::SystemDesc` | Name, reads, writes, labels, before and after |
| `ag::Schedule` | Builds and runs the system dependency graph |
| `ag::ExecutionOrder` | `parallel` or `deterministic` |
| `ag::world_checksum` | Schema-walked hash of a World |

## Steps

1. Implement `single` mode. verify: job tests pass on every preset with one worker.
2. Implement `thread` mode with work stealing. verify: a stress test of 1,000,000 jobs completes under `linux-tsan`.
3. Implement `fibre` mode with Boost.Context `fcontext` on POSIX and `CreateFiber` on Windows, guard pages and a stack high-water mark. verify: a job that yields resumes correctly on Linux, Windows and macOS.
4. Annotate fibre switches for ASan, TSan and Valgrind. verify: fibre tests pass under `linux-asan`, `linux-tsan` and Valgrind.
5. Add a debug check for a mutex held across a yield, and read worker context through a non-inlined accessor after each yield. verify: a test holding a lock across a yield aborts with a coded message.
6. Build the schedule from read and write sets and ordering labels. verify: conflicting systems never overlap in a recorded trace, and non-conflicting systems run concurrently.
7. Report conflicts and cycles. verify: a cycle returns a structured error naming each system.
8. Implement deterministic mode: stable job order, and merges by entity or job index. verify: a test runs the sample simulation for 600 ticks at 1, 2, 4 and 8 workers and asserts one identical `world_checksum`.
9. Build `wasm32` with `thread` and `single` modes only, no fibres. verify: the kernel link on `wasm32` has no Asyncify flag and no fibre object.
10. Run all kernel headless tests in thread-only mode on `wasm32` under Node. verify: the `wasm32` CI job runs `ctest --preset wasm32` and passes.

## Must not happen

- No privileged main thread in the scheduler. Browser main-thread rules stay in the platform layer.
- No `thread_local` access across a yield.
- No lock held across a yield.
- No finish-order dependence in deterministic mode.
- No `mmap` or fibre dependency in the `wasm32` kernel.

## Done when

- **Owns exit check:** "Deterministic job mode gives identical checksums across repeated runs."
- **Owns exit check:** "The kernel compiles to `wasm32` and passes its headless tests in thread-only mode, with no `mmap` or fibre dependency."
- The guarantee is same-binary. Cross-platform checksums wait for the fixed-point or software-float module.
