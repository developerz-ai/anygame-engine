# 🧲 38. Physics

**Use the cheapest physics that makes the game feel right.** Most gameplay needs queries and a good controller, not a full solver. Reach for rigid bodies only where emergent motion is the point.

Planned design as of 2026-11. No engine code exists. Linked facts were checked on 2026-11-21 from search extracts of the linked pages. **Every number marked "start" is a starting point to tune and measure.** Unlinked practices are recalled general knowledge. Every default here can be overridden ([rule 8](01-thesis.md#design-rules)).

Related: [simulation overview](08-simulation.md), [physics tricks](20-tricks-30-years.md#-simulation-and-physics), [large-scale combat](15-large-scale-combat.md), [client and server models](35-client-server-models.md), [libraries](17-next-gen-techniques.md#build-vs-wrap), [wrap, do not write solvers](../decisions/014-wrap-solvers-and-languages.md).

## Pick the physics model

| The object is | Use | Why |
|---|---|---|
| Decoration that never affects play | None, or vertex animation | No simulation cost |
| Trigger, pickup, damage zone | Sensor shape | Overlap only |
| Static world | Static collider | Never simulated |
| Door, lift, moving platform | Kinematic body | Script owns motion, others react |
| Player or NPC walking | Kinematic character controller | Predictable and tunable |
| 2D platformer character | Tile/AABB kinematic controller | Exact game feel |
| Bullet, arrow, grenade path | Ray or sweep per tick | Cheaper than a body |
| Crate, barrel, debris | Dynamic rigid body | Emergent motion is the point |
| Dead character | Ragdoll | Reaction without animation data |
| Car, bike, boat, aircraft | Vehicle model | Specialised forces |
| Cloth, hair, foliage | Client-only secondary motion | Visual only |
| Terrain or falling-sand material | Cellular module | Not a rigid-body problem |

**Default rule:** if a designer must be able to say exactly where it ends up, make it kinematic.

## Adapters

All physics sits behind the `physics2d` and `physics3d` ports, and game code never names a library. Defaults: built-in `physics2d.kinematic` for tile and AABB movement ([decision 014](../decisions/014-wrap-solvers-and-languages.md)), [Box2D](https://box2d.org/documentation/) for 2D rigid bodies, [Jolt](https://jrouwe.github.io/JoltPhysics/) for 3D, and a null adapter for tests. Extras are exposed through capability queries, such as "supports soft bodies?".

## Time

**Physics runs on a fixed step, independent of the display.** Use the [accumulator pattern](https://www.gafferongames.com/post/fix_your_timestep/) and render by blending the previous and current state.

```text
accumulator += min(frame_time, max_frame_time)
while accumulator >= dt and steps < max_steps:
    save previous state
    step(dt)
    accumulator -= dt
    steps += 1
alpha = accumulator / dt
render(lerp(previous, current, alpha))      // slerp for rotations
```

| Setting | Start | Use |
|---|---|---|
| General action game | 60 Hz | Default |
| Fast vehicles, sports | 120 Hz | [Rocket League GDC talk](https://www.gdcvault.com/play/1024972/), tick reported second-hand |
| Racing tyre model | 240–360 Hz sub-steps | Vehicle forces only |
| Strategy, simple gameplay | 20–30 Hz | Server cost matters more |
| Solver sub-steps | 4 | Raise for stacks and chains |
| Maximum catch-up steps per frame | 3–5 | Stops the spiral |
| Maximum frame time accepted | 100–250 ms | Hitch protection |

### Avoid the spiral of death

[If a step costs more real time than it simulates, the game falls further behind every frame.](https://www.gafferongames.com/post/fix_your_timestep/)

Keep physics well under its step time on the worst device. Cap steps per frame and **drop time** rather than queue it. Then degrade: lower physics LOD, sleep more, cull debris. On servers, lower update rates, then use [time dilation](35-client-server-models.md#scaling-to-wow-style-worlds). Report dropped time as a metric.

**Prefer sub-steps over iterations.** The [Small Steps paper](https://diglib.eg.org/items/322424d5-a24f-490a-a6bb-542233852032/full) uses many sub-steps with one solver iteration each, and [Box2D v3 now takes a sub-step count](https://box2d.org/documentation/md_migration.html).

## Units and scale

| Rule | Why |
|---|---|
| **Metres, kilograms, seconds, always** | Solver tolerances are tuned for them |
| **Never use pixels as physics units** | [Box2D's docs warn against it directly](https://box2d.org/documentation/md_faq.html) |
| Moving objects about 0.1 m to 10 m | [Box2D's stated sweet spot](https://box2d.org/documentation/md_faq.html) |
| Convert at the render boundary | 2D sprites map metres to pixels in one place |
| Imported assets are checked at import | Wrong scale and axes are a common bug |

## Collision setup

### Layers and filters

| Rule | Shape |
|---|---|
| Declare layers in data | `world`, `player`, `npc`, `projectile`, `debris`, `trigger` |
| Use a collision matrix | One readable table of what hits what |
| **Debris does not hit debris** | The largest cheap win in many scenes |
| Keep broadphase layers few | [Each Jolt broadphase layer is its own tree with overhead](https://jrouwe.github.io/JoltPhysics/) |
| Separate object layers from broadphase layers | Fine filtering without extra trees |
| Group ignores for a character's own parts | Ragdolls and vehicles do not self-collide unless wanted |

### Pick a shape

Cheapest first:

| Shape | Use |
|---|---|
| Sphere / circle | Projectiles, rolling objects, wheels |
| Capsule | Characters and limbs |
| Box | Crates, buildings |
| Convex hull | Props. Keep vertices low (start: under 32) |
| Compound of primitives | Complex dynamic objects |
| Triangle mesh | **Static world only** |
| Heightfield | Terrain |

Never use the render mesh as a dynamic collider. Author a simple collision mesh or generate one with convex decomposition at cook time, and avoid thin, huge or open triangles.

### Queries

Most gameplay physics is queries. Treat them as a first-class API.

| Query | Use |
|---|---|
| Raycast | Line of sight, hitscan, ground probe |
| Shape sweep | Character movement, thick bullets, melee arcs |
| Overlap | Explosions, area abilities, triggers |
| Closest point | AI cover, aim assist |
| Batch query | Hundreds at once on jobs |

**Query rules:** batch on jobs, filter by layer first, use the shortest distance, write into a caller-provided array, return a stable order, and run at a defined point in the schedule.

## Keep the simulation stable

| Symptom | Likely cause | Fix, in order |
|---|---|---|
| Objects pass through walls | Tunnelling | Enable CCD, thicken colliders, raise tick |
| Stack wobbles or collapses | Too few sub-steps, mass ratio | More sub-steps, closer masses, sleep it |
| Heavy on light explodes or sinks | Large mass ratio | Keep a start limit of 10:1, or fake it |
| Jitter at rest | Sleep threshold or contact tuning | Raise damping, check contact offsets |
| Joints stretch | Long chain, high ratio | Heavier root, more sub-steps, fewer links |
| Sudden explosion | Bodies spawned overlapping | Spawn clear, or limit depenetration speed |
| Character snags on seams | Internal mesh edges | Rounded shapes, edge filtering |
| Different result each run | Non-deterministic order | See [determinism](#determinism-rollback-and-rewind) |

**Sleeping and islands.** Touching awake bodies form an island, and a resting island sleeps. [Jolt does not wake bodies on creation](https://jrouwe.github.io/JoltPhysics/), which avoids load-time spikes. Keep this default when streaming content.

**CCD.** Enable it only for small, fast objects that matter. [Box2D applies it against static bodies by default, with limited support between dynamic shapes](https://box2d.org/documentation/md_simulation.html). For bullets, use a sweep.

**Friction and restitution.** Set them by surface material in data. Use restitution sparingly, because bouncing keeps islands awake. Add a speed threshold below which restitution is zero.

## Characters

**A character controller is game feel, so it is authored, not simulated.** It uses sweeps, then slides along what it hits.

| Feature | Practice | Start |
|---|---|---|
| Move and slide | Sweep, slide on the plane, repeat | 3–5 iterations |
| Slopes | Walkable below a limit, and slide above it | 45–50° |
| Steps | Sweep up, forward, then down | 0.3–0.4 m |
| Ground snap | Stick when walking downhill | 0.2–0.3 m |
| Moving platforms | Inherit platform velocity, and update after it | Keep launch velocity on jump |
| Pushing bodies | Apply a capped impulse | Designer-tuned |
| Skin width | Keep a small gap | 1–2 cm |

[Jolt's `CharacterVirtual`](https://jrouwe.github.io/JoltPhysics/class_character_virtual_settings.html) follows this approach, using collision queries outside the world step. Its docs warn of timing artefacts on descending lifts, so test elevators explicitly.

**Feel hooks are part of the block:** coyote time, jump buffering, variable jump height, apex hang, fall multiplier, corner correction, ledge forgiveness, sub-pixel movement. Details: [game feel](20-tricks-30-years.md#-game-feel). Input and tuning live in data.

## Joints, ragdolls and active ragdolls

| Topic | Practice |
|---|---|
| Ragdoll capsules | About 10–15 bodies for a humanoid (start) |
| Ragdoll start | Copy the animated pose and velocities, so there is no pop |
| Solver priority | [Jolt can prioritise joints near the root](https://jrouwe.github.io/JoltPhysics/) |
| Lifetime | Freeze, then remove or bake after a few seconds |
| Active ragdoll | Motors drive bodies toward the animation pose |
| Recovery and hits | Blend to a get-up animation, and use partial blends for hit reactions |

Animation and physics share one pose buffer ([cross-cutting rule](08-simulation.md#three-cross-cutting-rules)).

## Vehicles

| Choice | Arcade | Simulation |
|---|---|---|
| Wheels | Raycasts or shape casts | Tyre model per wheel |
| Suspension | Spring and damper | Plus geometry, roll bars |
| Grip | Curves tuned for fun | Slip-based force model |
| Drivetrain | Simple torque curve | Engine, clutch, gears, differentials |
| Step rate | Game tick | Higher vehicle sub-step |
| Fits | Most games | Racing sims |

Start arcade, and add simulation only where players feel it. Keep centre of mass low, use assists openly, and keep handling in moddable data with bot tests per car. [Jolt's `VehicleConstraint`](https://jrouwe.github.io/JoltPhysics/class_vehicle_constraint.html) provides wheeled and tracked vehicles behind the adapter.

## Projectiles and ballistics

| Projectile | Model | Authority |
|---|---|---|
| Hitscan | One ray, with lag compensation | Server |
| Fast bullet | Sweep per tick, with gravity and drag | Server |
| Slow projectile | Simulated entity, cosmetic on client | Server |
| Grenade, physics object | Rigid body or simple bounce model | Server |
| Massed bullets | Data-only array, batch sweeps | Server |

Keep the trail and impact effects client-side. Full armour and penetration pipeline: [large-scale combat](15-large-scale-combat.md).

## Destruction

| Level | How | Cost |
|---|---|---|
| Decals, swap meshes | Damage states | Very low |
| Pre-fractured | Chunks spawned on break | Medium |
| Connectivity graph | Chunks fall when support is lost | Medium |
| Voxel | Edit volume, remesh locally | High |
| Runtime fracture | Slice geometry live | High |

**Rules:** replicate the damage event rather than every chunk, keep gameplay-critical collision server-authored, keep debris cosmetic and expiring, use a support graph for structural integrity, update navigation after a break, and persist only changed cells.

## Cloth, fluids and cellular

| System | Default | Rule |
|---|---|---|
| Cloth, hair, capes | XPBD or GPU, client only | Collide against few capsules |
| Foliage | Vertex shader wind and bend | No bodies |
| Soft bodies | Adapter capability | Few, near the camera |
| Buoyancy | Sample points against a water height | No fluid solver needed |
| Water surface | Heightfield or shader | Gameplay queries a height function |
| Real fluids | Optional GPU module | Rarely gameplay-authoritative |
| Falling sand | `sim.cellular` | Chunks with dirty rectangles and [parallel updates, as in Noita](https://gdcvault.com/play/1025695/Exploring-the-Tech-and-Design) |

## Large worlds

| Rule | Shape |
|---|---|
| 64-bit world position | Physics uses a local frame near the action |
| Floating origin or physics regions | Rebase without visible pops |
| Rebase between steps | Never mid-step |
| Nested grids | A ship or train is its own frame, so interiors stay stable |
| Stream collision ahead of the player | Falling through unloaded ground is the classic bug |
| Hold bodies if ground is missing, and add bodies in batches | No falls or broadphase spikes |

See [world](07-world.md) and [resource lifecycle](34-resource-lifecycle.md).

## Determinism, rollback and rewind

Tiers are defined in [decision 012](../decisions/012-determinism-guarantee-tiers.md).

| Tier | Requirement |
|---|---|
| Same binary | Fixed step, stable ordering, same API call order |
| Cross-platform | Fixed-point, software float, or a library's verified mode |

- [Box2D reproduces a simulation for the same input and binary regardless of thread count, and added cross-platform determinism in 3.1, but does not provide rollback determinism](https://box2d.org/documentation/md_simulation.html).
- [Jolt has a `CROSS_PLATFORM_DETERMINISTIC` build option at roughly 8% cost](https://jrouwe.github.io/JoltPhysics/).
- [Jolt contact callback order and active-body order are not deterministic](https://jrouwe.github.io/JoltPhysics/), so sort before gameplay reads them.
- [Jolt `SaveState` records only what the step changes](https://jrouwe.github.io/JoltPhysics/). Game code restores anything else, and adding or removing bodies between saves breaks a restore.

**Rules:** turn physics events into sorted ECS events, avoid wall clocks and global RNG, snapshot only active bodies, keep rollback worlds small, and measure re-simulation at the worst window.

## Networking physics

| Pattern | Use | Trade-off |
|---|---|---|
| Server authority, snapshot interpolation | Most objects | Remote objects are slightly in the past |
| Client prediction with rewind | Own character or vehicle | Costs re-simulation |
| [State synchronization](https://gafferongames.com/post/state_synchronization/) | Physics-heavy co-op | Sends velocities too, approximate |
| [Deterministic lockstep](https://gafferongames.com/post/deterministic_lockstep/) | Small player counts | Needs strict determinism |
| Ownership migration | Whoever interacts simulates it, with server checks | Low latency, needs validation |
| Cosmetic only | Debris, cloth, particles | Never replicated |

**Rules:** replicate only what affects gameplay, send quantised position, rotation and velocity, smooth visuals rather than physics state, predict only what the player controls, [validate client-simulated results](09-online.md#rules-for-the-backend), and define an arbitration rule for player collisions.

## Performance

Step physics on the job system, with a [thread-only mode on the web](30-platforms.md). [Jolt contact callbacks run on several threads](https://jrouwe.github.io/JoltPhysics/), so queue changes during the step and apply them after. Do not allocate per step, and sync only changed transforms to ECS.

**Physics LOD:** near gets full bodies, ragdolls and CCD. Mid gets simple colliders at a lower rate. Far uses kinematic paths or schedules. Unimportant off-screen objects sleep or are removed.

### Starting budgets

Measure on the worst target device, and tune per game.

| Platform tier | Physics per frame (start) | Active bodies (start) | Ragdolls (start) |
|---|---|---|---|
| Low-end phone, browser | 2 ms | 100 | 2 |
| Mid phone, handheld | 3 ms | 300 | 4 |
| Console, mid PC | 4 ms | 2,000 | 16 |
| High-end PC | 5 ms | 10,000 | 32 |
| Dedicated server | By tick budget | Per match | Usually none |

## Debugging and proof

`ag physics` should expose, by command and as captures: colliders, contacts, normals, islands, sleep state, CCD paths, joints, velocities, layers, query rays, and per-island step cost.

| Test | Passes when |
|---|---|
| **Port conformance** | Every adapter passes `physics.conformance` |
| Tunnelling | A fast object never crosses a thin wall |
| Stack | A stack settles and sleeps within a time limit |
| Controller course | Bot clears slopes, steps, platforms and seams |
| Fuzzed spawn | Random overlaps give no NaN or explosion, and bad values report entity and tick |
| Determinism | Same seed and inputs give the same state hash |
| Rollback | Save, step, restore and re-step match exactly |
| Budget | Worst-case scene stays in its per-tier budget |
| Stream-in | No body falls through unloaded ground |
| Netcode | Bots stay in sync under target latency and loss |
