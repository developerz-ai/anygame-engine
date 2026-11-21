# 🎯 48. Tactical shooters: lessons from CS 1.6 to CS2

**A competitive shooter lives or dies on trust: what I saw is what happened.** Counter-Strike has spent over 25 years on that problem. Counter-Strike 2 is the current version as of 2026-11, with [updates still shipping](https://www.counter-strike.net/news/updates).

These games are references for general techniques only. AnyGame ships an original `kit.fps`, never their maps, weapons, names or art. Facts were checked on 2026-11-21 from search extracts. Valve publishes little about CS2 internals, so evidence is labelled.

## What each era teaches

| Era | Technique | Lesson for AnyGame | Evidence |
|---|---|---|---|
| CS 1.6 / GoldSrc | [Client prediction and lag compensation, described in Bernier's 2001 paper](https://developer.valvesoftware.com/wiki/Latency_Compensating_Methods_in_Client/Server_In-game_Protocol_Design_and_Optimization) | Still the foundation of `net.replication` | Valve paper |
| CS 1.6 | [Movement depended on engine ticks, so frame rate changed physics](https://kz-rush.ru/en/page/kreedz-physics) | Simulation must never depend on render rate | Community physics guide |
| CS 1.6 | [Bunny hopping emerged from jump being resolved before friction](https://graffeggyfrifiadurydd.blogspot.com/2019/07/the-mathematics-of-b-hopping-you-dont.html) | Order of operations is game design. Make it explicit and tested | Developer blog |
| CS 1.6 | [Simple hitbox regions with damage multipliers](https://outscal.com/blog/the-science-of-fair-play-understanding-game-hitbox-mechanics-in-counter-strike) | Collision is gameplay data, separate from the visible mesh | Educational blog |
| Source era | [Server rewinds players to what the shooter saw](https://developer.valvesoftware.com/wiki/Lag_Compensation) | Bounded rewind, per-entity opt-in | Valve wiki |
| SourceTV | [Relay tree with a delay](https://developer.valvesoftware.com/wiki/SourceTV/pl) | [Spectator relay](47-layers-rejoin-replay-spectate.md#-live-spectating) | Valve wiki |
| CS2 | [Sub-tick: the server knows when actions happened between ticks](https://www.counter-strike.net/cs2) | Timestamped inputs | Valve |
| CS2 | [Official servers reported at 64 tick](https://www.dexerto.com/counter-strike-2/counter-strike-2-servers-still-run-at-64-ticks-while-faceit-reveals-128-tick-2286729/), and the trade-off stays [disputed by players](https://www.pcgamer.com/its-not-better-than-csgo-yet-not-even-closewhat-counter-strike-pros-think-of-cs2/) | Timestamps do not replace update rate. Make tick configurable and measure feel | Press, 2023 |
| CS2 | [Volumetric smoke reacts to bullets and grenades](https://developer.valvesoftware.com/wiki/CS2) | Effects that affect play must be gameplay state | Valve wiki |
| CS2 | [Server-side ML in VAC Live can cancel a match](https://developer.valvesoftware.com/wiki/Valve_Anti-Cheat) | Server-side detection, with safe consequences | Valve wiki |
| CS2 | [A reported exploit could falsely trigger match cancellation](https://escorenews.com/en/csgo/news/81003-hackers-found-a-vac-live-exploit-which-can-cancel-any-cs2-match-and-put-other-players-on-cooldown) | A client must never be able to trigger punishment of others | Press report |
| CS2 | [A cheater reportedly dodged a ban by crashing the server](https://dotesports.com/counter-strike/news/cs2-cheater-crashes-server-after-being-reported-sneakily-avoiding-vac-live-ban) | Persist detection evidence before acting | Press report |
| CS2 community | [A server plugin withholds hidden enemy data](https://www.pcguide.com/news/counter-strike-2-player-makes-their-own-anti-wallhack-software-for-community-servers-that-works-with-vac/) | Server-side visibility should be built in | Press report |

## The shot, from click to damage

```text
CLIENT                                 SERVER
click at time t ----------------->     validate: alive, ammo, fire rate, weapon state
instant muzzle flash, recoil, sound    place shot at timestamp t, within limits
predicted tracer                       rewind targets to what this client saw
impact effect (cosmetic)               trace against gameplay hitboxes
                                       apply penetration, range, armour, damage
confirmed hit marker  <------------    send authoritative result
```

| Rule | Default |
|---|---|
| **Client predicts feedback, server decides damage** | Blood and kill feed wait for the server, or use a clearly tentative hit marker |
| **Inputs carry timestamps** | Clamped to the command's tick window, so a client cannot invent time |
| **Rewind has a hard cap** | A starting point of about 200 ms, tuned per game |
| **Favour the shooter, within limits** | High-ping players cannot hit people long behind cover |
| **Spread is seeded and shared** | Client and server compute the same pattern from a server-issued seed |
| **Recoil is data** | Patterns are tunable assets, independent of frame rate |
| **Hitboxes are gameplay data** | Same for every [visual look](44-visual-modes.md) |
| **Fixed simulation step** | Movement and grenades give the same result at any frame rate |
| **Movement order is declared** | Jump, friction and acceleration order is explicit, with golden tests |

## What makes the game feel fair

| Problem players report | Cause | AnyGame tool |
|---|---|---|
| "I shot first" | Tick alignment | Timestamped input, tie-break rule |
| "He killed me behind the wall" | Lag compensation + latency | Rewind cap, peeker analysis |
| Peeker's advantage | Interpolation plus round trip | Low interpolation, high update rate, measured in tests |
| "My shot did not register" | Client and server disagree | Hit-disagreement telemetry with replay |
| Rubber-banding | Bad reconciliation or loss | Smooth correction, network chaos tests |
| Grenades land differently | Frame or tick dependence | Fixed-step, deterministic trajectory |
| Stutter in a duel | Frame spikes | p99 budget in combat scenes |

**Measure feel.** Track click-to-photon latency, hit-registration disagreement, correction size and peek advantage in milliseconds under a fixed test network.

## Stop wallhacks at the source

- **Do not send enemies the player cannot perceive** ([visibility classes](35-client-server-models.md#every-field-has-a-visibility-class)).
- Use a conservative potentially-visible test, so enemies appear just before they round a corner and never pop in late.
- Filter **footsteps and sounds** by audible range, and send direction with limited precision.
- Smoke, flash and darkness that block vision can also block data, where the game accepts the cost.
- Replays and spectators get the full truth only through the delayed relay.

## Fair-play safeguards

| Rule | Why |
|---|---|
| Evidence is written before a penalty applies | A crash cannot erase it |
| No client message can flag another player | Prevents framing |
| Cancel or penalise only above a conservative threshold | False positives are costly |
| Every automated action is reviewable and appealable | [No silent punishment](09-online.md#fair-play-an-opinionated-stance) |
| No kernel driver | [Project stance](09-online.md#fair-play-an-opinionated-stance) |

## Round-based match primitives

The `kit.fps` tactical preset provides, with original content:

| Primitive | Examples |
|---|---|
| Match flow | Warmup, freeze time, live round, round end, half, overtime |
| Economy | Round income, loss bonus, buy phase, drop weapons |
| Objectives | Plant and defuse style, escort, capture, elimination |
| Utility | Smoke, flash, fire, explosive as data-driven blocks |
| Communication | Radio, pings, team chat |
| Competitive | Ranked, map veto, surrender, timeouts, reconnect, coach slot |
| Community | Dedicated servers, custom maps and modes, server browser |
| Watch | Demos, GOTV-style relay, round timeline, kill cam |

## Lessons from staying alive for 25 years

- **Small and efficient wins reach.** A game that runs on weak machines builds a huge community.
- **Mods can create entire genres.** Counter-Strike itself [began as a Half-Life mod](https://en.wikipedia.org/wiki/Counter-Strike), so keep modding first-class.
- **Dedicated community servers extend a game's life.** Never remove them.
- **Do not break muscle memory.** Movement, recoil and timing changes need replay-based comparison before release.
- **A sequel needs parity first.** [Pros criticised CS2 at launch against CS:GO](https://www.pcgamer.com/its-not-better-than-csgo-yet-not-even-closewhat-counter-strike-pros-think-of-cs2/), so a remaster must match the old feel before adding to it.

## Proof

| Check | Passes when |
|---|---|
| Frame independence | Same inputs at 30, 144 and 500 fps give the same movement and grenade path |
| Timestamp abuse | Forged future or past timestamps gain nothing |
| Rewind limit | Shots beyond the cap do not hit |
| Spread | Client and server produce identical patterns for one seed |
| Hit agreement | Under the test network, disagreement stays below the game's target |
| Wallhack audit | Packet capture holds no unseen enemy |
| Framing | A malicious client cannot cause another player's penalty |
| Peek test | Measured peeker advantage is reported on each netcode change |
| Bot match | A full competitive match completes under network chaos |
