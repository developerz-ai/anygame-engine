# 🧱 Primitives by phase

When each [primitive](../idea/23-primitives.md) first becomes usable. Every phase delivers its client and server halves together, so a primitive is not done until it works headless.

| Phase | Shared | Client | Game server | Backend |
|---|---|---|---|---|
| [0](phase-0-kernel.md) | Foundation, ECS, schema, snapshots, registry, `component`, `system`, `event`, `migration`, `test` | None | Headless runtime | None |
| [1](phase-1-2d.md) | `asset`, `prefab`, `world`, Lua, packages, 2D physics, timers | 2D render, audio, input, UI, camera, local saves, mobile | Headless 2D simulation with bots | None |
| [2](phase-2-determinism.md) | `command`, deterministic loop, replay, rollback, lockstep | Rollback presentation, replay viewer | Input relay, replay verification | None |
| [3](phase-3-3d-desktop.md) | 3D physics, navigation, abilities, replication, `policy` | 3D render, animation, prediction | Dedicated server, authority, lag compensation, server fog, bot and latency tests | None |
| [4](phase-4-backend.md) | `service`, `job` | Login, party and matchmaking flows | Session lifecycle, drain, reconnect | Identity, persistence, jobs, matchmaking, fleet, telemetry |
| [5](phase-5-world.md) | Coordinates, partitioning, PCG, simulation LOD | Streaming, large-world render | Interest management across large maps | World-state persistence |
| [6](phase-6-high-end.md) | Crowd simulation | High-end render, motion matching, physical animation | Crowd LOD and replication | None |
| [7](phase-7-mmo.md) | Hand-off contracts | Seamless zone transfer | Zones, instancing, replication layer, crash replacement | Economy, social, live ops |

## Exit check for every phase

- A sample runs on the client and on a headless server from the same project, where the phase has a server half.
- A manifest without the phase's modules builds with none of their code.
- Each new port has a conformance suite and a null or simple adapter.

## Kit and platform schedule

Each lands in the first phase that supplies all its modules ([decision 015](../decisions/015-kit-and-platform-schedule.md)), with a complete original sample game.

| Phase | Kits | Platforms and primitives |
|---|---|---|
| 1 | `platformer2d`, `narrative` | Android, iOS, 2D browser build |
| 2 | `fighting`, `rts`, `builder` | Replay viewer |
| 3 | `fps`, `thirdperson`, `topdown2d` | Web 3D light tier, console packages may start privately |
| 4 | `rpg`, `cardgame`, `mobile-casual`, `moba` | Quests, dialogue, commerce, entitlements, workshop service |
| 5 | `openworld`, `racing`, `survival` | Weather, day/night, destruction |
| 6 | None new | XR package, high-end tiers for existing kits |
| 7 | `mmo` | Guild, economy and zone blocks |
