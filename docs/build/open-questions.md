# ❓ Open questions

Conflicts and gaps found while splitting the blueprint. The idea docs keep the original wording until each is decided. A decided item becomes a record in `docs/decisions/`.

## Blocks Phase 0

| # | Question | Conflict or gap | Proposed answer |
|---|---|---|---|
| 1 | What are the kernel's five parts? | [Thesis](../idea/01-thesis.md) lists memory, jobs, data, reflection, plugins. [Kernel](../idea/04-kernel.md) lists memory, jobs, data model, reflection, time. Phase 0 also adds snapshots and a CLI | Six parts: add registry to the section 4 list. Snapshots belong to the data model. `ag` sits beside the kernel as a tool |
| 2 | Does the 30k-line budget cover the reflection tool and `ag`? | Not stated | Runtime kernel only. Tools get their own budget |
| 3 | Which build system and compilers? | The blueprint assumed C++ modules, but no build system or minimum compiler is named. Modules must work on every platform in [section 3](../idea/03-architecture.md) | Headers plus PCH by default, named modules opt-in per package ([C++23 craft](../idea/16-cpp23-craft.md)). Confirm on MSVC and Apple Clang, which are not yet tested |
| 4 | How strong is the determinism promise? | [Kernel](../idea/04-kernel.md) allows fixed-point or strict IEEE. [Risks](../idea/14-risks.md) says fixed-point or software float | Decide per guarantee: same-binary replay first, cross-platform only with fixed-point or software float |
| 16 | How does the kernel run on WebAssembly? | The blueprint assumes fibres and virtual memory. Browsers offer neither directly | Thread-only job mode and a page-allocator backend for arenas, proven in Phase 0 ([platforms](../idea/30-platforms.md)) |

## Blocks a later phase

| # | Phase | Question | Conflict or gap | Proposed answer |
|---|---|---|---|---|
| 5 | 1 | Is there an editor? | Rule 6 and [section 11](../idea/11-scripting-modding-tools.md) say no GUI editor. Sections [3](../idea/03-architecture.md), [6](../idea/06-rendering.md) and [7](../idea/07-world.md) still say "the editor" or "in-editor" | No core editor. Reword those lines to "live viewer" or "tooling" |
| 6 | 1 | Can a shipped game include tooling? | [Section 13](../idea/13-engineering-practices.md) says the shipped binary has no tooling code paths. [Section 11](../idea/11-scripting-modding-tools.md) says a shipped game can include editor tooling | Tooling ships as a separate optional executable, never in the game binary |
| 7 | 1 | Does a 2D solver count as "from scratch"? | [Risks](../idea/14-risks.md) forbids a new physics solver. Rule 3 and [section 8](../idea/08-simulation.md) need simple implementations | Allow small kinematic controllers. Wrap a library for real rigid-body solving |
| 8 | 1 | Does the narrative script count as a new language? | [Risks](../idea/14-risks.md) forbids a new language. [Section 2](../idea/02-prior-art.md) wants a writer-facing script language | Adopt an existing one such as Ink |
| 9 | 3 | Slang or HLSL? | [Section 3](../idea/03-architecture.md) leaves both open | Decide with a spike before the render graph |
| 10 | Roadmap | When do the other kits land? | Seven of the 15 kits have no phase: `topdown2d`, `rpg`, `cardgame`, `builder`, `survival`, `narrative`, `mobile-casual` | Assign each after the phase that supplies its modules |
| 11 | Roadmap | Where do XR, web and consoles land? | Listed as targets or genres, with no phase | Treat as optional packages after Phase 3 |
| 15 | Roadmap | When do quests, dialogue, workshop and commerce land? | In the [primitive catalogue](../idea/23-primitives.md), with no phase | Assign alongside the kits that first need them |
| 17 | Roadmap | Should `kit.moba` join the kits? | Proposed in [client and server models](../idea/35-client-server-models.md), with no phase | Add after Phase 3, on the `orders` profile |

## Project

| # | Question | Current state |
|---|---|---|
| 12 | Is MIT the final license? | `ASSUMPTION:` MIT, matching other developerz-ai repos |
| 13 | Which real game is each kit's flagship? | [Risks](../idea/14-risks.md) requires one per kit. None named |
| 14 | Do the sources need links? | Yes. [Sources](../idea/sources.md) has titles only |
