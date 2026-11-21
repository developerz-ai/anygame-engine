# 🧪 8. Simulation modules

Every simulation domain is an interface with at least two implementations, and all of them read and write ECS components so they compose without knowing about each other.

| Domain | Simple implementation | AAA implementation | Notes |
|---|---|---|---|
| Physics 3D | Kinematic + basic rigid bodies | Jolt-class multithreaded solver: ragdolls, vehicles, soft bodies, destruction | Deterministic build option; rewindable for netcode |
| Physics 2D | Tile and AABB kinematic controller | Box2D-class rigid bodies | Platformers want the first, not the second |
| Vehicles | Arcade raycast car | Sub-stepped tyre, drivetrain, aero, damage; bikes, boats, aircraft | Handling data is moddable assets |
| Animation | Sprite flipbooks, clip state machines | Motion matching, IK, physical animation, facial rigs, cloth and hair, crowd instancing | Timeline events drive gameplay (hit windows, footsteps) |
| AI decision | Finite state machines | Behaviour trees, utility AI, GOAP/HTN planners, director | All graph-authored and hot-reloadable |
| AI navigation | Grid A* | Tiled streaming navmesh, flow fields, traffic lanes, flying and swimming volumes | Local avoidance (ORCA) for crowds |
| AI perception | Distance checks | Sight cones, sound propagation, stimulus system, shared squad knowledge | |
| Audio | Sample playback, buses | Procedural DSP graphs, spatial audio, occlusion and propagation, interactive music | Sample-accurate clock available as master clock |
| Gameplay | Events and timers | Ability system (tags, effects, attributes), inventory, quests, dialogue, smart objects, stim/response | Network-aware by construction |

## Three cross-cutting rules

1. **Animation and physics are one system at the high end.** Characters that stumble, brace and react (Rockstar's hallmark since GTA IV) need active ragdolls blended with animation every frame, so the two modules share one pose buffer.
2. **Gameplay state is data.** Abilities, status effects, quests and dialogue are assets with schemas, not code. That makes them moddable, replicable, saveable and writable by AI tools.
3. **Everything is debuggable in place.** Every module registers visualisers and a time-scrubbable recorder. Rewinding a bug five seconds and stepping forward is a kernel-level feature (snapshots), available to all modules.
