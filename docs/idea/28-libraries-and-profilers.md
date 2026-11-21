# 🧰 28. Allocators, libraries and profilers

**Start from the best proven parts.** Each row has one default, so an agent can pick without research. Every choice sits behind a port or a thin wrapper and can be replaced ([adapters](05-extending.md#adapters-the-shape-of-every-integration)).

As of 2026-11-21: licenses and activity were read from each GitHub repo. **Defaults are proposals. Nothing here has been benchmarked for AnyGame yet.** Choose a final default per port by measuring a real workload.

Rendering, physics, audio, scripting and networking libraries are in [next-gen techniques](17-next-gen-techniques.md#build-vs-wrap). When to use which allocator is in [C++23 craft](16-cpp23-craft.md#allocator-choice).

## How to adopt a library

| Rule | Why |
|---|---|
| Never expose its types across a module boundary | The C ABI stays stable and the library stays swappable |
| Pin an exact version in the lockfile | Reproducible builds |
| Route its allocations through AnyGame if it supports that | Memory stays tagged and visible |
| Build it with `-fno-exceptions -fno-rtti` where supported, or contain it in one package | Matches runtime rules |
| Fuzz any parser that reads untrusted bytes | Saves, mods, packets and assets are attack surface |
| Add it only to the package that needs it | A game pays only for what it loads |
| Check license on upgrade | Licenses can change |
| Never link GPL or AGPL code into runtime modules | Games must stay free to choose their license. Using such tools in development is fine |

## 🧠 Memory allocators

The engine's arenas, pools and tagged heaps handle most allocations. A general heap serves what remains.

| Need | Default | Alternatives | License | Notes |
|---|---|---|---|---|
| General heap, client | [mimalloc](https://github.com/microsoft/mimalloc) | [rpmalloc](https://github.com/mjansson/rpmalloc), [snmalloc](https://github.com/microsoft/snmalloc) | MIT | Keep behind the `mem.heap` port |
| General heap, long-running server | mimalloc, then compare | [jemalloc](https://github.com/jemalloc/jemalloc) (BSD), [TCMalloc](https://github.com/google/tcmalloc) (Apache-2.0) | MIT | Compare fragmentation in a soak test |
| Bounded-time heap | Engine TLSF | [mattconte/tlsf](https://github.com/mattconte/tlsf) (BSD) | BSD | Reference repo last pushed 2021, so own the code if used |
| Vulkan memory | [VulkanMemoryAllocator](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator) | None needed | MIT | |
| D3D12 memory | [D3D12MemoryAllocator](https://github.com/GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator) | None needed | MIT | |
| Frame, scope, pool, chunk | Engine allocators | None | | Listing in [C++23 craft](16-cpp23-craft.md) |

## 📦 Containers and concurrency

| Need | Default | Alternatives | License |
|---|---|---|---|
| Hash map | [ankerl::unordered_dense](https://github.com/martinus/unordered_dense) | [Boost.Unordered](https://github.com/boostorg/unordered) flat map (BSL-1.0), [Abseil](https://github.com/abseil/abseil-cpp) (Apache-2.0), [parallel-hashmap](https://github.com/greg7mdp/parallel-hashmap) (Apache-2.0) | MIT |
| Game-oriented STL with custom allocators | Kernel containers | [EASTL](https://github.com/electronicarts/EASTL) (BSD-3) | |
| Stable-address bucket container | [plf::colony](https://github.com/mattreecebentley/plf_colony) | Pool with handles | Zlib |
| MPMC queue, unbounded | [moodycamel::ConcurrentQueue](https://github.com/cameron314/concurrentqueue) | | BSD or Boost |
| MPMC queue, bounded | [rigtorp/MPMCQueue](https://github.com/rigtorp/MPMCQueue) | | MIT |
| Fibre switch | [Boost.Context](https://github.com/boostorg/context) `fcontext` | [minicoro](https://github.com/edubart/minicoro) (MIT-0 or public domain, last pushed 2024) | BSL-1.0 |
| Task scheduler reference | Kernel scheduler | [enkiTS](https://github.com/dougbinks/enkiTS) (Zlib), [Taskflow](https://github.com/taskflow/taskflow) (MIT) | |
| ECS reference | Kernel ECS | [Flecs](https://github.com/SanderMertens/flecs), [EnTT](https://github.com/skypjack/entt) (both MIT) | |

Avoid [google/marl](https://github.com/google/marl) for new work: the repo is archived.

## ⚡ SIMD, maths, hashing, compression

| Need | Default | Alternatives | License |
|---|---|---|---|
| Portable SIMD | [Highway](https://github.com/google/highway) | [xsimd](https://github.com/xtensor-stack/xsimd) (BSD-3) | Apache-2.0 or BSD-3 |
| Port existing intrinsics | [SIMDe](https://github.com/simd-everywhere/simde) | | MIT |
| Graphics maths | [GLM](https://github.com/g-truc/glm) | [DirectXMath](https://github.com/microsoft/DirectXMath), [cglm](https://github.com/recp/cglm) (both MIT) | MIT or Happy Bunny |
| Deterministic maths | Engine fixed-point or strict module | | |
| Non-crypto hash | [xxHash](https://github.com/Cyan4973/xxHash) XXH3 | | BSD-2 library |
| Package compression | [Zstandard](https://github.com/facebook/zstd) | | BSD option |
| Fast decompression while streaming | [LZ4](https://github.com/lz4/lz4), `lib/` only | | BSD-2 in `lib/`, GPL elsewhere |
| Deflate and gzip | [libdeflate](https://github.com/ebiggers/libdeflate) | | MIT |

Do not use a non-crypto hash for security. Package integrity and signing need a cryptographic hash.

## 📄 Data and assets

| Need | Default | Alternatives | License |
|---|---|---|---|
| Formatting | `std::format` where build cost allows | [{fmt}](https://github.com/fmtlib/fmt) | MIT |
| Logging | Kernel structured log | [spdlog](https://github.com/gabime/spdlog) in tools | MIT |
| JSON | [simdjson](https://github.com/simdjson/simdjson) to parse | | Apache-2.0 |
| TOML | [toml++](https://github.com/marzer/tomlplusplus) | | MIT |
| Bit-packed network and save data | Schema-generated, using [bitsery](https://github.com/fraillt/bitsery) ideas | | MIT |
| Zero-copy tooling formats | [FlatBuffers](https://github.com/google/flatbuffers) | [Cap'n Proto](https://github.com/capnproto/capnproto) (MIT) | Apache-2.0 |
| glTF | [fastgltf](https://github.com/spnda/fastgltf) | [cgltf](https://github.com/jkuhlmann/cgltf) | MIT |
| Image decode in tools | [stb](https://github.com/nothings/stb) | | MIT or public domain |
| GPU textures | [KTX-Software](https://github.com/KhronosGroup/KTX-Software), [Basis Universal](https://github.com/BinomialLLC/basis_universal) | | Check `LICENSE.md`, Apache-2.0 |

Fuzz image and model parsers before they read mods or downloads. `stb_image` in particular should stay in trusted tooling.

## 🧪 Testing

| Need | Default | Alternatives | License |
|---|---|---|---|
| Unit tests | [doctest](https://github.com/doctest/doctest), for fast compiles | [Catch2](https://github.com/catchorg/Catch2), [GoogleTest](https://github.com/google/googletest) | MIT |
| Micro-benchmarks | [nanobench](https://github.com/martinus/nanobench) | [Google Benchmark](https://github.com/google/benchmark) | MIT |
| Property tests | [RapidCheck](https://github.com/emil-e/rapidcheck) | [FuzzTest](https://github.com/google/fuzztest) | BSD-2 |
| Fuzzing | libFuzzer | [AFL++](https://github.com/AFLplusplus/AFLplusplus) as an external tool, AGPL: never link | |
| Record and replay debugging | [rr](https://github.com/rr-debugger/rr) on Linux | | Dev tool |

## 🔥 Profilers: which one answers my question?

| Question | Use first | Then | Platform |
|---|---|---|---|
| Why did this frame spike? | [Tracy](https://github.com/wolfpld/tracy) | `perf` | All desktop, Android |
| Which function burns CPU? | `perf record`, [Hotspot](https://github.com/KDAB/hotspot) | [samply](https://github.com/mstange/samply), [FlameGraph](https://github.com/brendangregg/FlameGraph) | Linux |
| Same, on Windows | Windows Performance Analyzer, [PerfView](https://github.com/microsoft/perfview) | Superluminal (paid), VTune | Windows |
| Same, on Apple | Instruments | samply | macOS, iOS |
| Same, on CPU-vendor counters | Intel VTune, AMD uProf | `perf stat` | Desktop |
| Did this PR get slower? | **Callgrind instruction count** | nanobench | CI, Linux |
| Cache misses? | `perf stat`, `perf c2c` for false sharing | Cachegrind | Linux |
| Who allocates, and who leaks? | [heaptrack](https://github.com/KDE/heaptrack) | Massif, Tracy memory | Linux |
| Struct padding and layout? | `pahole` from [dwarves](https://github.com/acmel/dwarves) | `-Wpadded` | Linux |
| Why is the binary large? | [Bloaty](https://github.com/google/bloaty) | Link map | All |
| Why is the build slow? | `-ftime-trace`, [ClangBuildAnalyzer](https://github.com/aras-p/ClangBuildAnalyzer) | [include-what-you-use](https://github.com/include-what-you-use/include-what-you-use) | Clang |
| Scheduling or kernel stalls? | [bpftrace](https://github.com/bpftrace/bpftrace), `perf sched` | Tracy context switches | Linux |
| What did the GPU draw? | [RenderDoc](https://github.com/baldurk/renderdoc) | PIX, Xcode Metal debugger | All desktop, Android |
| Why is the GPU slow? | PIX, NVIDIA Nsight Graphics, Radeon GPU Profiler | Vendor tools | By GPU |
| Mobile GPU and power? | Android GPU Inspector, Arm Performance Studio, Snapdragon Profiler | Xcode | Mobile |
| Network behaviour? | `ag` net stats, Wireshark | `tc netem` for latency and loss | All |

[Optick](https://github.com/bombomby/optick) last saw a push in 2024 and [google/orbit](https://github.com/google/orbit) is archived, so Tracy is the default.

### Profiler rules for agents

- **Measure a Release-with-debug-info build,** with frame pointers on. Never profile a Debug build.
- **Profile the same scripted scene every time,** so before and after are comparable.
- **Report p50, p99 and worst frame.** An average hides stutter.
- **Use instruction counts for CI** because they are stable. Use wall time and hardware counters to confirm a real win.
- **Check for profiler overhead.** Tracy zones stay out of inner per-entity loops.
- **Compile instrumentation out of shipping builds.**
- **`ag profile` should wrap the common cases** and return JSON, so agents do not need to parse each tool.
