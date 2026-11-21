# Phase 6: High-end

**Proves:** AAA visuals. **Depends on:** Phases 3 and 5. **Read:** [rendering](../idea/06-rendering.md), [simulation](../idea/08-simulation.md), [next-gen techniques](../idea/17-next-gen-techniques.md), [small and fast](../idea/21-small-and-fast.md).

## Build order

1. Virtualised geometry.
2. Virtual shadow maps and virtual texturing.
3. Ray-traced GI and reflections, with probe GI as fallback.
4. Motion matching and physical animation on one pose buffer.
5. Crowd instancing with simulation LOD.

## Exit checks

- The same project and materials run on mobile, desktop and high-end tiers.
- 10,000 animated 3D characters hold 60 fps on a mid-range desktop GPU.
- High-end modules add nothing to a build that does not load them.
- Time of day changes at runtime with no baked lighting.
- One profiler shows per-module CPU, GPU and memory against budgets.
