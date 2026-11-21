# 💻 30. Platform playbook: Linux, Windows, macOS, Android, iPhone

**One project, five first-class targets.** Game code never touches an OS API. The `platform.*` and `rhi` ports hide the differences, and this page tells an agent what is different when it must care.

Store and OS rules change, so re-check linked pages before a release. Rules with a link were checked on 2026-11-21 from search extracts of official pages. Unlinked entries are recalled and need confirming on real hardware. **None of this has run in AnyGame yet.**

## At a glance

| | Linux | Windows | macOS | Android | iPhone / iPad |
|---|---|---|---|---|---|
| Toolchain | GCC or Clang | MSVC or clang-cl | Apple Clang | NDK Clang | Apple Clang |
| Graphics | Vulkan | D3D12, Vulkan optional | Metal | Vulkan | Metal |
| Plugin linking | Shared in dev and ship | DLL in dev and ship | Signed dylib | Shared library in the app | **Static** in shipping |
| Virtual memory | `mmap` | `VirtualAlloc` | `mmap` | `mmap` | `mmap`, tight limits |
| Page size | 4 KB, can vary | 4 KB | **16 KB on Apple Silicon** | 4 KB or **16 KB** | **16 KB** |
| Async I/O | `io_uring`, thread fallback | IoRing, DirectStorage, IOCP | Dispatch I/O | Thread pool | Dispatch I/O |
| Script VM | JIT allowed | JIT allowed | JIT with entitlement | JIT possible | **Interpreter or AOT** |
| Memory sanitizer | ASan, TSan, UBSan, MSan | **ASan only on MSVC** | ASan, TSan, UBSan | **HWASan** | ASan, TSan, UBSan |
| CPU profiler | `perf`, Tracy | WPA, Tracy | Instruments, Tracy | Simpleperf, Perfetto | Instruments |
| GPU debugger | RenderDoc | PIX, RenderDoc | Xcode Metal tools | AGI, RenderDoc | Xcode Metal tools |
| Ship through | Steam, itch, Flatpak, AppImage | Steam, Epic, GOG, itch | Steam, App Store, direct | Google Play, other stores | App Store, where allowed others |

## Rules for all platforms

| Rule | Why |
|---|---|
| **Never hard-code page size** | Query it. A 4 KB assumption crashes on 16 KB devices |
| **Align with `AG_CACHE_LINE`, not a literal** | 64 on most, 128 on Apple Silicon |
| **Use fixed-width types in data and ABI** | `long` differs between Windows and the others |
| **Little-endian, with an explicit format** | Saves and packets go through the schema |
| **Filesystems differ** | Case-insensitive on Windows and often macOS. Asset IDs are lowercase |
| **Paths go through `platform.fs`** | Sandboxes differ on each OS |
| **No fixed thread count or affinity assumptions** | Hybrid cores everywhere |
| **Handle lost device and lost surface** | GPU reset, driver update, app switch |
| **CI builds every target on each PR, and tests on real devices nightly** | A port left for later never catches up |

## 🐧 Linux

| Topic | Do |
|---|---|
| Role | Primary platform for agents, CI and dedicated servers |
| Compatibility | Build in the [Steam Linux Runtime SDK](https://github.com/ValveSoftware/steam-runtime). Valve recommends 4.0 for new native games |
| glibc trap | A binary built on a new distro fails on older hosts. Enforce a maximum `GLIBC_` symbol version in CI |
| Display | Support Wayland and X11, through SDL3 |
| Steam Deck | Test controller UI, 1280×800 text, sleep and resume |
| Server | Headless build, no GPU libraries linked, small container |
| Memory | Use `madvise` huge pages for large arenas, after measuring |

## 🪟 Windows

| Topic | Do |
|---|---|
| Sanitizers | [MSVC offers only AddressSanitizer](https://learn.microsoft.com/en-us/cpp/build/reference/inferasanlibs?view=msvc-170). Run UBSan and TSan on Linux, or try clang-cl |
| Hot reload | A loaded DLL and its PDB are locked. Copy to a unique name, then load the copy |
| Fibres | Prefer `CreateFiber`. Hand-switching stacks must keep the thread's stack limits valid |
| Virtual memory | Reserve, then commit. Commit charge counts against the page file |
| Timing | Use high-resolution waitable timers for frame pacing |
| Display | Declare per-monitor DPI awareness, support HDR and borderless flip model |
| Exports | Mark symbols explicitly. Windows does not export by default |
| Ship | Sign executables to reduce SmartScreen warnings |

## 🍎 macOS

| Topic | Do |
|---|---|
| Target | Apple Silicon first. Add a universal binary only if Intel users matter |
| Graphics | Metal directly. MoltenVK is not the main path |
| Distribution | Outside the Mac App Store, Developer ID apps need [hardened runtime and notarization](https://developer.apple.com/videos/play/wwdc2019/703/) |
| JIT | Use `com.apple.security.cs.allow-jit` with `MAP_JIT` and [`pthread_jit_write_protect_np`](https://developer.apple.com/forums/thread/805941). Avoid unsigned-memory entitlements |
| Plugins | Every dylib must be signed. Mods should be scripts or data |
| Threads | Set QoS classes. Do not pin to cores |
| Tools | Valgrind is not a usable option on Apple Silicon. Use ASan, TSan and Instruments |

## 🤖 Android

| Topic | Do |
|---|---|
| **16 KB pages** | [Required for apps targeting API 35+ on Google Play, with updates blocked from 2027-02-01](https://developer.android.com/guide/practices/page-sizes). NDK r28+ aligns by default |
| ABI | `arm64-v8a` first |
| Sanitizer | [HWASan. NDK ASan is unsupported since 2023](https://developer.android.com/ndk/guides/asan) |
| Entry point | GameActivity from the Android Game Development Kit |
| Frame pacing | Android Frame Pacing library (Swappy) |
| Thermal | Android Dynamic Performance Framework drives the governor |
| Lifecycle | Surface can vanish at any time. Save on pause, stop GPU work, recreate on resume |
| Memory | The OS kills background apps. Keep a low-memory response per tag |
| Drivers | Vulkan quality varies by device. Keep a per-GPU quirks table, and test low-end devices |
| Delivery | App Bundle with Play Asset Delivery for large content |

## 📱 iPhone and iPad

| Topic | Do |
|---|---|
| Linking | Static link all native modules. The registry resolves at compile time |
| Scripts | Interpreter or AOT, because iOS forbids general JIT |
| Downloaded code | [Guideline 2.5.2](https://developer.apple.com/app-store/review/guidelines/) restricts it. Ship logic in the bundle, and deliver data and content updates only. Review mod support with care |
| Memory | The OS kills apps over a device-specific limit. Respond to memory warnings by evicting tagged caches |
| Background | Stop all GPU work when backgrounded. Save state first |
| Thermal | Read thermal state and lower resolution or frame rate |
| UI | Safe areas, notch and Dynamic Island, touch controls, game controller support |
| Frame rate | Support ProMotion and low power mode |
| Ship | TestFlight, then App Store. Check regional store rules |

## Agent defaults when porting

1. Build for the new target in CI first.
2. Get a headless test running there, if the OS allows it.
3. Get the first frame on a real device.
4. Run the game's budget scene on the worst supported device.
5. Add controls and UI for that device.
6. Handle lifecycle: suspend, resume, lost surface, low memory.
7. Run the store's compliance check from [idea to distribution](25-idea-to-distribution.md#compliance-checklist).
