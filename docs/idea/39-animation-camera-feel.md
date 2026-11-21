# 🏃 39. Animation, camera and game feel

**The player judges a game through motion and response.** Keep gameplay truth in the simulation, make presentation smooth on top of it, and measure feel instead of guessing.

Planned design as of 2026-11. Numbers are starting points to tune per game, not measurements. Unlinked technique details are recalled and unverified. Every default can be replaced ([rule 8](01-thesis.md#design-rules)). Short trick lists: [thirty years of tricks](20-tricks-30-years.md#-animation). Module overview: [simulation](08-simulation.md).

## Rules

| Rule | Why |
|---|---|
| **Gameplay reads authored events and data, never the rendered pose** | Servers run headless and frame rate cannot change outcomes |
| **Simulation owns position unless root motion is explicitly enabled** | One source of truth |
| **Blend presentation, never authoritative state** | Smoothing cannot create a desync |
| **Animation runs in batches over ECS data** | Crowds cost arrays, not objects |
| **Every expensive step has an LOD** | Distant characters do less |
| **Effects that can cause discomfort can be turned off** | Accessibility is a default |

## Pick an animation approach

| Need | Default | Move up when | Verify |
|---|---|---|---|
| 2D sprite | Flipbook with named events | Many frames or outfits | Event fires on its authored frame at every playback rate |
| 2D character with parts | 2D skeletal + mesh deformation | | Draw count stays inside budget |
| Few 3D actions | State machine | Transition count becomes hard to read | No unreachable state |
| Locomotion speed and direction | Blend space | Foot sliding remains visible | Foot-slide metric below threshold |
| Layered actions | Upper/lower-body masks + additive | | Masks do not move the root |
| Large mocap set, responsive movement | Motion matching | Memory is too high | Response and pose-error metrics pass |
| Memory-limited motion matching | [Learned motion matching](https://theorangeduck.com/media/uploads/other_stuff/Learned_Motion_Matching.pdf), optional | | Output stays within error budget |
| Reactions to impacts | Physical animation | | Character recovers without tunnelling |
| Hundreds to thousands on screen | GPU skinning, then vertex animation textures | | Crowd target holds on target GPU |

## Pipeline

```text
select clips -> sample -> blend -> root motion -> IK -> procedural -> physics blend -> final pose -> skin
                  ^                                                                  |
             compressed data                                         events and sockets for gameplay
```

| Stage | Practice | Verify |
|---|---|---|
| Skeleton | Stable bone names, shared retarget rig, sockets as data | Import fails with a coded error on a missing required bone |
| Storage | Store local transforms in SoA, keep parent indices sorted | One forward pass computes model space |
| Compression | Error measured in world space at virtual vertices | Max error stays under the asset's budget |
| Sampling | Worker jobs over batches | Zero allocations after warmup |
| Blending | Normalised quaternions, shortest arc | Property test: output stays unit length |
| Root motion | Extracted at cook time to a separate track | Replay gives the same displacement |
| Events | Authored on clip time, crossed exactly once per update | Large time steps do not skip events |

Wrap libraries first: [ACL](https://github.com/nfrechette/acl) (MIT) for compression, [ozz-animation](https://github.com/guillaumeblanc/ozz-animation) ([MIT per its docs](https://guillaumeblanc.github.io/ozz-animation/documentation/)) for runtime sampling, blending and IK jobs. Both stay behind the `anim` port.

## Transitions

| Technique | How | Use |
|---|---|---|
| Crossfade | Evaluate both clips and blend | Simple games |
| **Inertialization** | Decay the pose offset after switching | Default for responsive characters, evaluates one clip |
| [Dead blending](https://theorangeduck.com/page/dead-blending) | Extrapolate the old pose and blend into the new one | Very different poses |
| [Spring damping](https://theorangeduck.com/page/spring-roll-call) | Critically damped springs | Procedural follow, aim, camera |

Inertialization needs pose velocity at the transition. See [propagating velocities](https://theorangeduck.com/page/propagating-velocities-through-animation-systems). **Check:** no visible pop in a transition stress scene, measured as maximum bone acceleration against a limit.

## IK and procedural motion

| Feature | Practice | Verify |
|---|---|---|
| Foot placement | Two-bone IK + ground query + pelvis offset | Foot-to-ground error stays in range on slopes |
| Foot locking | Pin during contact, release before lift | Slide distance during contact near zero |
| Look and aim | Clamped joint chain with spring | Never exceeds joint limits |
| Hand on weapon or wheel | IK to a socket after other layers | Hand-to-socket error in range |
| Secondary motion | Springs on hair, cloth bits, antennae | Stable at 30 and 144 fps |
| Motion warping | Adjust root over a marked window to reach a target | Arrives within tolerance |
| Physical animation | Powered ragdoll sharing the [pose buffer](08-simulation.md#three-cross-cutting-rules) | Recovery test finishes standing |

## Combat timing

- Hit, parry, cancel and invulnerability windows are **data on the simulation tick**.
- The server runs hit logic with no skinned pose, using authored volumes.
- Client animation may speed-match to the server, but cannot extend a window.
- Each attack exposes startup, active and recovery frames to `ag describe`.

**Check:** a frame-data test asserts the exact active ticks at each supported tick rate.

## Crowds and LOD

| Band | Update | Technique |
|---|---|---|
| Hero | Every frame | Full graph, IK, cloth |
| Near | Every frame | Reduced IK, fewer bones |
| Mid | Every 2–4 frames | Sampled pose with interpolation |
| Far | Shared phase | GPU skinning or vertex animation textures |
| Very far | None | Impostors or statistics |

Budget in **ms per frame and MB per skeleton**. **Check:** the crowd scene holds the [performance target](13-engineering-practices.md#performance-is-a-feature-of-the-base-not-a-later-optimisation-pass) on target hardware.

## Networked animation

| Replicate | Do not replicate |
|---|---|
| Action ID, start tick, playback modifiers | Bone transforms |
| Locomotion inputs | Foot IK and cosmetic springs |
| Ragdoll state only if gameplay needs it | Purely visual ragdolls |

The owning client may start cosmetic animation immediately. Remote clients catch up by skipping time or blending. Hidden enemies send no animation events ([visibility](35-client-server-models.md)).

## Camera

### Pick a rig

| Genre | Rig | Must handle |
|---|---|---|
| 2D platformer | Dead zone, look-ahead, platform snap | Pixel-perfect movement, room bounds |
| Top-down, ARPG | Follow with soft zone | Occluders, cursor look-ahead |
| RTS, MOBA | Free pan, edge scroll, zoom | Map bounds, minimap jump |
| FPS | Direct input | Zero smoothing by default, separate view model FOV |
| Third-person | Spring arm with orbit | Wall collision, shoulder swap |
| Soulslike | Orbit + lock-on | Target switching, large enemies |
| Racing | Chase with speed-based lag | Stable horizon, reverse view |
| Fighting | Framing both players | Stage limits |
| Open world | Blend between mode rigs | Vehicle, on-foot, interiors |
| VR | Head pose is authoritative | Never move the view without user intent |

### Camera rules

| Topic | Practice | Verify |
|---|---|---|
| Update order | After simulation interpolation, before render extract | No one-frame jitter against the target |
| Smoothing | Frame-rate independent damping | Same path at 30, 60 and 144 fps |
| Collision | Sphere sweep, fast pull-in, slow release | Never clips through test walls |
| Occlusion | Fade small occluders, move for large ones | Target stays visible in route test |
| Framing | Composition in screen space | Target stays in safe frame |
| Lock-on | Scored by distance, angle and visibility | Stable with no flicker between targets |
| Split-screen | Separate cameras, shared world budget | Budget holds with max players |
| Precision | Camera-relative rendering | No shimmer at max world coordinate |

### Shake and FOV

Use **trauma-based shake**: impacts add trauma, trauma decays, and shake is trauma squared or cubed sampled from smooth noise, as taught in [Juicing Your Cameras With Math](https://gdcvault.com/play/1023146/Math-for-Game-Programmers-Juicing). Shake is presentation only and never changes aim or hit logic.

| Comfort feature | Default | Source |
|---|---|---|
| Shake, bob and motion blur | Off switch or slider that reaches zero | [Xbox guideline 117](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/117) |
| FOV | Adjustable, default by viewing distance | [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/if-the-game-uses-field-of-view-3d-engine-only-set-an-appropriate-default-for-the-expected-viewing-environment/) |
| Camera speed | Player can lower it | Xbox guideline 117 |
| Controller-camera mismatch | Avoid, or allow disabling | [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/avoid-or-provide-option-to-disable-any-difference-between-controller-movement-and-camera-movement/) |
| Cinematics | Respect the same settings | Xbox guideline 117 |

**Check:** with comfort settings off, a scripted run including cinematics records zero shake, bob and blur.

## Game feel

### The input latency chain

```text
device -> OS -> input sample -> simulation tick -> render submit -> GPU -> display -> player sees it
```

| Technique | Effect | Risk |
|---|---|---|
| Sample input as late as possible | Lowers latency | Must stay deterministic for replays |
| Frame pacing with a bounded queue | Lowers latency and jitter | GPU may idle slightly |
| Reduced-latency vendor plugins | Lowers render queue | Optional adapter |
| Instant local feedback | Feels immediate online | Must not claim server results |
| Avoid frame generation in competitive defaults | Keeps input response | Offer as a setting |

**Metric:** input-to-photon where hardware capture exists, and input-to-effect ticks in CI.

### Forgiving controls

| Mechanic | Starting point | Verify with a bot |
|---|---|---|
| Coyote time | 4–8 frames at 60 Hz | Jump just after a ledge succeeds |
| Jump buffer | 4–8 frames | Press just before landing jumps |
| Action buffer | 100–200 ms | Queued attack fires exactly once |
| Corner correction | A few pixels | Head-bump near a ledge passes |
| Variable jump | Early release cuts upward speed | Heights match the tuning table |
| Aim assist | Input-device specific, adjustable | Off means zero adjustment |
| Hit forgiveness | Slightly larger player attack, smaller player hurtbox | Frame-data test |

### Feedback layers

Every important action should answer: **did it work, how much, and what next?**

| Layer | Example | Rule |
|---|---|---|
| Anticipation | Wind-up, charge glow | Readable before the effect |
| Impact | Hit-stop, flash, particles | Short, scaled by importance |
| Sound | Layered transient and body | Starts on the same frame ([audio](40-audio.md)) |
| Camera | Trauma, small FOV kick | Respects comfort settings |
| Body | Squash and stretch, recoil, knockback | Keeps silhouette readable |
| UI | Damage number, meter change | Waits for authority when not predicted |
| Haptics | Short pulse | Player-adjustable |
| Aftermath | Debris, decals | Pooled and budgeted |

**Hit-stop** starts around 2–6 frames, scaled by hit strength. In online games it is applied to presentation or authored into the simulation, never as an unsynchronised local pause.

## Proof

| Check | Passes when |
|---|---|
| Frame-rate independence | Scripted motion matches at 30, 60 and 144 fps |
| Event accuracy | No event is skipped or duplicated under time-step stress |
| Headless parity | Gameplay result is identical with animation presentation disabled |
| Input latency | Stays within the kit budget |
| Comfort | All motion effects can be disabled |
| Budget | Animation and camera stay inside per-module targets |
| Feel regression | Stored bot replays keep jump height, reaction and hit timings in range |
