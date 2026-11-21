# 📏 13. Engineering practices baked into the base

These are the habits that recur across engine post-mortems and studio talks; AnyGame enforces them with tooling so every new game starts with them.

| Practice | Enforcement |
|---|---|
| Data-oriented design: lay out data for how it is processed | ECS chunks by default; a lint flags per-entity heap allocation in hot systems |
| Budgets, not hopes | Each module declares CPU, GPU and memory budgets per platform tier; CI fails on regression |
| Profile on the worst target device from week one | `ag profile --device` works over the network on phones and consoles |
| Fast iteration beats features | Hard targets: script reload < 1 s, C++ module reload < 5 s, cold boot to gameplay < 10 s in dev |
| Determinism where it pays | Deterministic kits run a nightly cross-platform checksum test |
| Automate playtesting | Bots and replay tests in CI; every crash uploads a snapshot plus input log that reproduces it |
| Build the game and the engine together | Each kit ships a small complete game maintained by the engine team; no feature merges without one user |
| Keep tooling out of the runtime | Tools are separate processes; the shipped binary has no tooling code paths |
| Stable interfaces, replaceable internals | Semver on interfaces, conformance suites, deprecation windows of two releases |
| Text assets and small files | One file per entity; merge tools for scenes and graphs |
| No hidden global state | Everything lives in a World or an explicit context; enables multiple worlds, tests and hot reload |
| Ship vertical slices | [Roadmap](../build/README.md) is ordered by playable milestones, not subsystems |

## Performance is a feature of the base, not a later optimisation pass

General-purpose engines feel heavy mostly because of what every project inherits by default: a per-object update model, an editor compiled into the runtime, garbage collection or reflection walks in hot paths, thousands of shader permutations compiled on first use, and features that cost time even when unused. AnyGame's rule is zero cost for what is not loaded and measured cost for what is.

| Target (design goal, to be verified in CI) | Value |
|---|---|
| Empty 2D project, shipped binary | under 5 MB |
| Empty 3D project, shipped binary | under 25 MB |
| Idle memory, empty project | under 30 MB |
| Cold start to first frame, desktop | under 1 s |
| 100,000 simple moving sprites | 60 fps on a mid-range phone |
| 10,000 animated 3D characters (crowd tier) | 60 fps on a mid-range desktop GPU |
| Shader compilation during gameplay | none: pipelines are compiled at build or load time |
| Frame-time spikes over budget | fail the performance test |

How the architecture gets there:

- No garbage collector and no per-object virtual update in the core; systems iterate arrays.
- Systems with no matching entities do not run; modules not in the manifest are not linked.
- A small, fixed set of material permutations by design, with pipeline caches shipped with the game, to avoid shader stutter.
- The minimum-spec devices (an old integrated-GPU laptop, a low-end Android phone) are in the CI farm, and every kit template must hold its frame budget on them.
- One profiler covers CPU, GPU, memory, I/O and network per module, on device.

These numbers are targets this document proposes, not measurements.
