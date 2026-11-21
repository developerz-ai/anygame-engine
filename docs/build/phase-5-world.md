# Phase 5: World

**Proves:** large worlds. **Depends on:** Phases 3 and 4. **Read:** [world](../idea/07-world.md), [kits](../idea/10-kits.md), [resource lifecycle](../idea/34-resource-lifecycle.md), [large-scale combat](../idea/15-large-scale-combat.md), [NPCs and AI](../idea/36-npcs-and-ai.md), [distributed servers](../idea/46-distributed-servers.md).

## Build order

1. `world.coords`: 64-bit positions, camera-relative rendering, nested frames.
2. Partition with one file per entity, plus data layers.
3. `world.stream` with predicted paths and ms/MB budgets.
4. Terrain behind one ground-query interface.
5. Seeded PCG.
6. `sim.lod` and `world.population`, in three bands.
7. `physics.vehicle`, `kit.racing`, `kit.openworld`, each with a small complete game.

## Exit checks

- No visible precision error at the maximum supported world coordinate.
- A scripted fast-vehicle route crosses the test map with no frame over budget from streaming.
- The same seed produces byte-identical PCG output.
- Entities promote and demote between the three bands with no lost state.
- A player walks inside a moving vehicle using nested physics grids.
