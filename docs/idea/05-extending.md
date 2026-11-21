# 🧩 5. Extending without forking

People fork engines for three reasons: a hook is missing, a subsystem cannot be swapped, or upgrading breaks their changes. AnyGame removes each one with a specific mechanism.

## Six extension mechanisms, weakest to strongest

| # | Mechanism | What you do | Example |
|---|---|---|---|
| 1 | Data | Add or override assets and config, layered like USD or Paradox mods | New weapon, rebalanced stats |
| 2 | Components and systems | Register new component types and systems into the schedule, ordered by labels | Stamina system that runs before movement |
| 3 | Events and hooks | Subscribe to typed events; every engine stage emits before/after events | React to "entity damaged" |
| 4 | Graph nodes | Add passes to the render graph, nodes to anim/AI/PCG/audio graphs | Custom outline pass, new behaviour-tree task |
| 5 | Interface implementation | Provide another implementation of a service interface; manifest selects it | Swap physics backend, add a console RHI |
| 6 | Interposition | Wrap an existing implementation: receive the previous vtable, forward what you do not change | Add telemetry to every draw call; patch one physics query |

Mechanism 6 is the fork-killer. It is the game-engine equivalent of middleware, and it works because of the registry below.

## API registry

Taken from The Machinery and Bitsquid: a plugin is a shared library with one entry point. It asks the registry for the interfaces it needs and registers the ones it provides. Interfaces are plain structs of function pointers with a semantic version.

```cpp
// Stable C ABI at the boundary; ergonomic C++ wrappers are header-only on top.
struct ag_physics_api_v3 {
    ag_version version;
    ag_body  (*create_body)(ag_world, const ag_body_desc*);
    void     (*step)(ag_world, ag_seconds dt);
    uint32_t (*raycast)(ag_world, const ag_ray*, ag_hit* out, uint32_t max);
    // ... new functions are only ever appended
};

AG_PLUGIN_EXPORT void ag_load(ag_registry* reg, bool reload) {
    auto* jobs = reg->get<ag_jobs_api_v2>();           // dependency
    auto* prev = reg->get<ag_physics_api_v3>();        // may be null
    reg->provide<ag_physics_api_v3>(&my_physics, {.wraps = prev, .priority = 100});
}
```

Rules that keep it stable:

- **C ABI at module boundaries.** C++ has no stable ABI across compilers; C does. Templates, STL types and exceptions never cross a boundary.
- **Append-only interfaces within a major version.** A breaking change means a new `_v4` struct; `_v3` keeps working through an adapter for at least two engine releases.
- **Capability negotiation.** Modules declare what they need and what they provide. The loader resolves the graph and fails with a readable message, not a crash.
- **Hot reload everywhere.** Because state lives in ECS worlds and handles, not in module globals, any module, including the renderer, can be rebuilt and reloaded in a running game.
- **Static linking for shipping.** The same plugins link statically into one executable for consoles, iOS and performance; the registry becomes compile-time.

## Adapters: the shape of every integration

**The engine defines a port. Anything external plugs in through an adapter. The manifest picks which.** Engine and game code call the port and never name a vendor or library.

```toml
# anygame.toml: illustrative, the format is not final
[adapters]
physics3d = "jolt"
audio     = "miniaudio"
script    = "luau"
net.transport = "gns"
render.upscale = ["dlss", "fsr", "xess", "spatial"]   # first supported one wins

[adapters.persist]
use = "postgres"
```

| Port | Example adapters |
|---|---|
| `rhi` | D3D12, Vulkan, Metal, WebGPU, console backends |
| `render.upscale` | DLSS, FSR, XeSS, MetalFX, spatial |
| `physics2d`, `physics3d` | Built-in kinematic, Box2D, Jolt, in-house |
| `audio` | miniaudio, Steam Audio, vendor middleware |
| `script` | Luau, C#, Wren, AngelScript, WASM |
| `net.transport` | UDP, GameNetworkingSockets, WebTransport, platform relays |
| `persist`, `cache`, `events`, `jobs` | Postgres, SQLite, Redis-protocol, NATS, Kafka |
| `identity`, `commerce`, `platform.services` | Steam, PSN, Xbox, Apple, Google, a game's own |
| `asset.import` | glTF, USD, Tiled, LDtk |
| `asset.generate` | ts23d, Kubeez, local GPU models, any provider |
| `ai.llm` | On-device or hosted providers |
| `telemetry` | OpenTelemetry, any collector |

Adapter rules:

- **No vendor name above the port.** A vendor type in game or engine code is a bug.
- **Every port ships a null or simple adapter,** so headless runs and tests need no vendor SDK.
- **Every port has a conformance suite.** Passing it is what makes an adapter valid.
- **Ordered fallbacks are declared in the manifest,** and the chosen adapter is reported at startup.
- **Capabilities are queried, never assumed.** A port states what an adapter supports.
- **Adapters compose.** Interposition wraps any adapter for logging, caching, or a patch.
- **Unused adapters are not linked.**
- **A game can add its own port or adapter** with no engine change and no fork.

## Packages

- A package = manifest (`anygame.toml`) + modules + assets + schema + tests + an `AGENTS.md` describing itself to AI tools.
- A registry with semver resolution and lockfiles, like Cargo. Games depend on packages; they never copy engine source.
- An overlay mechanism lets a game pin a patched version of one package without touching the rest.
- Conformance suites: each interface ships tests that any replacement implementation must pass. A community physics backend proves itself by passing `physics.conformance`.
