# 🏗️ Build

The order of work. The order is chosen so there is a shippable, useful engine at every stage, and so the hardest architectural bets are tested first.

**Status as of 2026-11-21: docs only. No engine code exists.**

| Phase | Doc | Deliverable | Proves |
|---|---|---|---|
| 0 | [Kernel](phase-0-kernel.md) | Memory, jobs, ECS, reflection, registry, snapshots, CLI; Windows, Linux, macOS | The plugin model and hot reload |
| 1 | [2D stack](phase-1-2d.md) | Renderer, physics, audio, input, UI, Lua; `kit.platformer2d`; Android and iOS | "Pay for what you use"; mobile; first real games |
| 2 | [Determinism](phase-2-determinism.md) | Deterministic loop + rollback + lockstep; `kit.fighting`, `kit.rts` | Snapshot and determinism design |
| 3 | [3D desktop](phase-3-3d-desktop.md) | Render graph, clustered lighting, 3D physics, animation; `kit.fps`, `kit.thirdperson`; `net.replication` | Mainstream 3D and client-server |
| 4 | [Backend](phase-4-backend.md) | Services, persist, jobs, matchmaking, fleet; `ag dev` full stack | The Rails promise |
| 5 | [World](phase-5-world.md) | 64-bit coordinates, partition and streaming, PCG, simulation LOD; `kit.openworld`, `kit.racing` | Large worlds |
| 6 | [High-end](phase-6-high-end.md) | Virtualised geometry, ray-traced GI, motion matching, crowds | AAA visuals |
| 7 | [MMO](phase-7-mmo.md) | `net.mmo`: replication layer, multi-server worlds; `kit.mmo` | Persistent scale |
| Continuous | [Continuous](continuous.md) | CLI, MCP interface, live viewer, modding and workshop, docs, conformance suites | AI-first and no-fork |

**Start here:** [how we work](how-we-work.md), and current progress in [status.yml](status.yml).

Client and server primitives per phase: [primitives by phase](primitives-by-phase.md).

Before Phase 0 code starts, settle [open questions](open-questions.md).

## Rules for every phase

- A phase is done when its exit checks pass, not when its features exist.
- Each kit ships a small complete game. No feature merges without one user.
- Exit numbers come from the [blueprint targets](../idea/13-engineering-practices.md). They are proposed goals until CI measures them.
- Reuse proven open-source parts behind interfaces. See [what not to build](../idea/14-risks.md#what-not-to-build).
