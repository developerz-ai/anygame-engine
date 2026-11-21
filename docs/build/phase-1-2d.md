# Phase 1: 2D stack

**Proves:** pay for what you use, mobile, first real games. **Depends on:** Phase 0, decisions [013](../decisions/013-tooling-ships-separately.md) and [014](../decisions/014-wrap-solvers-and-languages.md). **Read:** [rendering](../idea/06-rendering.md), [simulation](../idea/08-simulation.md), [scripting and tools](../idea/11-scripting-modding-tools.md), [physics](../idea/38-physics.md), [animation and feel](../idea/39-animation-camera-feel.md), [audio](../idea/40-audio.md), [UX](../idea/42-ux-accessibility-localization.md), [visual modes](../idea/44-visual-modes.md).

## Build order

1. RHI subset and `render2d`: sprite batcher, tilemaps, pixel-perfect camera.
2. `physics2d.kinematic`, input with buffering, audio playback and buses.
3. Lua VM plugin with quotas and schema-generated bindings.
4. Retained UI and immediate-mode debug UI.
5. Asset cooking, hot reload, and the [resource lifecycle](../idea/34-resource-lifecycle.md): on-demand loading, caching, eviction.
6. `kit.platformer2d` with a small complete game.
7. Android and iOS, with static linking on iOS.

## Exit checks

- The kit's game is playable start to finish on desktop, Android and iOS.
- An agent passes a headless gameplay test using only `ag` commands.
- Empty 2D shipped binary is under 5 MB and contains no 3D, navmesh or netcode symbols.
- Idle memory for an empty project is under 30 MB.
- 100,000 simple moving sprites hold 60 fps on a mid-range phone.
- Eviction chaos mode runs the sample game with no crash or stale handle.
- Memory returns to baseline after repeated level changes.
- Script reload takes under 1 s and C++ module reload under 5 s.
