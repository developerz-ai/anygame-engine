# Phase 3: 3D desktop

**Proves:** mainstream 3D and client-server. **Depends on:** Phases 0 to 2, [open question](open-questions.md) 9. **Read:** [rendering](../idea/06-rendering.md), [simulation](../idea/08-simulation.md), [online](../idea/09-online.md).

## Build order

1. Full RHI on D3D12, Vulkan, Metal, and the shader toolchain.
2. Render graph, extract step, GPU-driven scene.
3. Desktop tier: meshlets, clustered lighting, probe GI, cascades.
4. 3D physics behind an interface, wrapping a Jolt-class library.
5. Animation with timeline events.
6. `net.replication`: prediction, lag compensation, relevancy, server fog.
7. `kit.fps` and `kit.thirdperson`, each with a small complete game.

## Exit checks

- A plugin adds a render pass with no engine source change.
- Physics backends are swappable and pass `physics.conformance`.
- No shader compilation happens during gameplay.
- Empty 3D shipped binary is under 25 MB.
- A dedicated server runs headless with no render, audio or input modules.
- Headless bots complete a full `kit.fps` match in CI.
- The server sends a client no state that client cannot perceive, proven by a packet audit that includes sounds and effects.
- A client reconnects mid-match with correct state.
- A modified bot client sending impossible commands gains nothing.
