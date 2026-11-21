# 🌍 7. World

A world is a database of entities partitioned in space and in layers; what is loaded, simulated and replicated at any moment is a query against it.

- **Coordinates.** 64-bit positions in simulation, camera-relative 32-bit on the GPU. Optional nested reference frames (a ship interior, a train, a planet) each with their own physics grid.
- **Partitioning.** Automatic grid/HLOD cells with one file per entity, so 200 people can edit one map without lock contention (Unreal's World Partition and One File Per Actor).
- **Streaming.** Priority-driven async I/O with a predicted camera path. Budgets are in milliseconds and megabytes, not object counts. Target: fast vehicle or flight traversal with no hitch, as in GTA or Spider-Man.
- **Data layers.** Named layers toggle sets of entities at runtime: mission states, seasons, MMO phasing, destroyed vs. intact city blocks.
- **Simulation LOD.** Three bands. Near: full entities. Mid: simplified agents (traffic as splines, NPCs as schedules). Far: statistical (population counts per district). Entities are promoted and demoted as the player moves. This is how an open world feels alive beyond the visible radius.
- **Terrain.** Heightfield, mesh-based terrain with overhangs and caves, and voxel terrain are three interchangeable modules behind one "ground query" interface.
- **Procedural content.** A node-graph PCG framework that runs in-editor, at cook time, or at runtime, always from a seed. Rule-based placement (Decima), wave-function collapse, road and building generators, biome vegetation growth.
- **Interiors and seams.** Portals and rooms as a streaming and visibility primitive; seamless interior/exterior with no load screen.
