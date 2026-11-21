# ⚔️ 35. Client and server, the way the great online games do it

**One simulation, one authority, many views.** The client sends what the player wants. The server decides what happens and tells each client only what that client may know. Games like Dota 2, League of Legends, World of Warcraft and EVE Online show this holds from a 10-player match to a persistent world.

These games are architecture references only: AnyGame copies general techniques, never their content. Facts below were checked on 2026-11-21 from search extracts, and each states how strong its evidence is. The AnyGame design is a proposal.

## What to learn from each

| Game | Technique | AnyGame takes | Evidence |
|---|---|---|---|
| Dota 2 | [No shooter-style client prediction](https://bo3.gg/dota2/news/dota2-dev-explains-input-lag-update-738), so orders feel the player's ping | Prediction is per-game and optional | Press report of a developer comment |
| Dota 2 | [Replays store periodic full snapshots plus deltas](https://whanyu1212.github.io/gem-dota/understanding/02_dem_format) | Seekable replay format | Community format docs |
| Dota 2 | [Custom games script modes, abilities and AI in Lua](https://developer.valvesoftware.com/wiki/Dota_2_Workshop_Tools/Scripting), with a separate UI layer | Mods on both client and server | Official wiki, may be dated |
| Source | [Prediction, 100 ms interpolation](https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking?language=cs), [lag compensation](https://developer.valvesoftware.com/wiki/Latency_Compensating_Methods_in_Client/Server_In-game_Protocol_Design_and_Optimization) | Standard `net.replication` tools | Official wiki |
| SourceTV | [Buffered, delayed broadcast to prevent cheating](https://developer.valvesoftware.com/wiki/Stv) | Spectator relay with a delay | Official wiki |
| League of Legends | [Server withholds enemy positions](https://technology.riotgames.com/news/demolishing-wallhacks-valorants-fog-war) | Per-client visibility filter | Riot engineering |
| League of Legends | [Deterministic server, recorded inputs, rewind](https://technology.riotgames.com/news/determinism-league-legends-introduction) | Server replay, rewind, regression tests | Riot engineering |
| VALORANT | [Fog of war against wallhacks](https://technology.riotgames.com/news/demolishing-wallhacks-valorants-fog-war) | Server-side visibility in 3D | Riot engineering |
| World of Warcraft | [Protected functions and taint for addons](https://wowpedia.fandom.com/wiki/Secure_Execution_and_Tainting) | Safe, moddable UI that cannot automate play | Community wiki |
| World of Warcraft | [Secret values limit addon use of combat data](https://warcraft.wiki.gg/wiki/Secret_Values) | Displayable values scripts cannot compute on | Community wiki |
| World of Warcraft | [Spell batching](https://us.forums.blizzard.com/en/wow/t/spell-batching-in-classic/377383) resolved simultaneous actions together | Pluggable action-ordering policy | Forum discussion, unverified detail |
| EVE Online | [Time dilation slows the game clock under load](https://eveonline.com/article/introducing-time-dilation-tidi) | Server load policy | Official dev blog |

## Choose an authority profile

One annotation system, several profiles. A kit picks a default, and a game can change it.

| Profile | Client sends | Client predicts | Server tick (starting point) | Fits |
|---|---|---|---|---|
| `orders` | Move, attack, cast, queue | Feedback only | 20–30 Hz | MOBA, RTS, ARPG, tactics |
| `action` | Inputs each tick | Own movement and abilities | 30–128 Hz | FPS, action, racing |
| `mmo` | Movement + ability requests | Own movement | 10–30 Hz by zone load | MMORPG, persistent worlds |
| `lockstep` | Inputs only | Nothing | Fixed | RTS, co-op with small state |
| `rollback` | Inputs only | Remote inputs | 60 Hz | Fighting, small action games |
| `turn` | Commands | Nothing | On command | Card, board, tactics |

Tick numbers are design starting points. Each game measures its own.

## The authoritative loop

```text
CLIENT                                    SERVER
input -> intent/order ---- network ---->  validate (policy, range, cooldown, resources)
instant local feedback                    queue by tick and ordering policy
                                          simulate
                                          compute visibility per team and client
interpolate <-- delta snapshot + events   filter -> prioritise -> delta -> send
present and reconcile                     record inputs and state for replay
```

## Every field has a visibility class

The strongest anti-cheat is data that never reaches the client.

| Class | Sent to | Example |
|---|---|---|
| `public` | Everyone | Match clock, score |
| `visible` | Clients who can currently perceive the entity | Enemy position, health |
| `team` | The owner's team | Ally cooldowns, pings |
| `owner` | That player | Inventory details, unspent resources |
| `server` | Nobody | AI plans, loot rolls, RNG seed, hidden traps |

```cpp
// Illustrative, the API is not final.
struct [[ag::component, ag::replicated(visible)]] Hero {
    [[ag::quantise(0.01)]] Vec2 position;
    float health;
    [[ag::team]] Tick ultimate_ready_at;
    [[ag::server]] u32 next_crit_roll;
};
```

**Effects leak too.** Sounds, particles, kill feed entries and animation events pass through the same filter. A sound from an unseen enemy must not reveal an exact position.

## Hide latency honestly

| Technique | Use |
|---|---|
| Instant acknowledgement | Click marker, voice line, cast animation start |
| Input and order queueing | Accept the next action slightly early, so latency does not waste time |
| Turn-rate and wind-up design | Game design absorbs round-trip time |
| Interpolation | Smooth remote entities |
| Prediction with reconciliation | Only where the profile needs it |
| Lag compensation with limits | Hit fairness in action games |
| **Never predict hidden or irreversible results** | Damage numbers, kills, loot wait for the server |

## The full session lifecycle

| Stage | Server does | Client does |
|---|---|---|
| Match found | Allocates a server through `fleet` | Preloads the match's assets |
| Connect | Authenticates a signed ticket | Verifies content hashes |
| Baseline | Sends a filtered full snapshot | Builds its World |
| Play | Sends deltas and events | Sends orders |
| Packet loss | Resends what is still current, not old state | Keeps interpolating |
| Disconnect | Holds the slot and applies game rules | Retries with backoff |
| **Reconnect** | Sends a fresh filtered snapshot | Resumes without restarting |
| Pause | Stops the game clock by rule | Stays connected |
| Abandon | Bot takeover or game-specific rule | Reports status |
| Server crash | Restores from snapshot where the profile supports it | Reconnects automatically |
| End | Validates, persists through `economy` and `persist` | Shows results |
| After | Stores replay, runs detectors | Replay available |

## Spectators and replays

- A **relay** subscribes to the server, so a thousand viewers add no simulation cost.
- **Delay is enforced by the relay,** so a spectator feed cannot be used to cheat in the live match.
- Replays hold periodic full snapshots plus deltas, so seeking is instant.
- A competitive replay records server truth, then applies a viewer's chosen fog.

## Scaling to WoW-style worlds

| Pressure | Tool |
|---|---|
| Too many players nearby | Interest management, update-rate LOD |
| Busy zone | Move authority across processes, split zones |
| Too many in one place | Instancing, phasing, layers |
| A massive battle | Server load policy: lower update rates, then time dilation |
| Long-lived data | Persistence as a subscriber, transactional economy |
| Simultaneous actions | Ordering policy: arrival, batched window, or priority rules |

Full server design: [online stack](09-online.md). Large battles: [large-scale combat](15-large-scale-combat.md).

## Mods on both sides

Following custom-game ecosystems:

- A mode has **server scripts** with authority and **client scripts** for presentation and UI.
- Typed **custom net tables** share data, with the same visibility classes.
- Clients download content by hash, so everybody runs identical rules.
- UI scripts can display values, but can trigger gameplay only through player-initiated input.

## Proposed `kit.moba`

`orders` profile, deterministic-capable server, fog of war, data-driven abilities, lane and wave AI, items, replays, spectator relay, custom modes. Original heroes and world.

## Proof

| Check | Passes when |
|---|---|
| **Packet audit** | A captured client stream contains no `server` field and no data for an unseen enemy |
| Bot cheater | A modified client sending impossible orders gains nothing |
| Reconnect | A client rejoins mid-match with correct state |
| Network chaos | Playable at the target latency, jitter and packet loss |
| Replay | A recorded match reproduces its final state |
| Load | The target player count stays inside the tick budget |
| Spectator isolation | A relay cannot receive data earlier than its delay |

## Clean-room warning

Use talks, engineering blogs, official docs and public wikis. **Do not use private-server emulator source, leaked code or decompiled clients as references.** See [CONTRIBUTING.md](../../CONTRIBUTING.md).
