# 📺 47. Layers, rejoin, replays and live spectating

**Four features, one foundation.** A world can exist in several copies, and any client can join from a snapshot plus a stream of changes. A rejoining player, a replay viewer and a live spectator are all the same thing: a late subscriber to a match.

Planned design as of 2026-11. References were checked on 2026-11-21 from search extracts. Public detail on these games is limited, so evidence is stated and the AnyGame design is our own.

```text
             ┌──> player client   (live, filtered by visibility)
SIMULATION ──┼──> rejoining client (fresh filtered snapshot, then live)
    |        ├──> relay ──> spectators (delayed, chosen fog)
    v        └──> recorder ──> replay (keyframes + deltas + events)
 full state
```

## 🌍 Copies of a world

| Technique | What is copied | Used for | Reference | Evidence |
|---|---|---|---|---|
| **Layer** | The whole realm or continent | Launch-day crowds | [WoW Classic layering](https://mein-mmo.de/en/wow-classic-fakten-zum-layering,382317) | Press, quoting Blizzard |
| **Shard** | One zone or smaller | High-traffic areas | [WoW sharding](https://eu.forums.blizzard.com/en/wow/t/what-is-sharding/2292) | Blizzard forum post |
| **Cross-realm zone** | Merges realms into one zone | Empty areas | [Forum explanation](https://eu.forums.blizzard.com/en/wow/t/sharding-phasing-and-layering/376939) | Community |
| **Phase** | Same place, different state per player | Story progress | [Forum explanation](https://eu.forums.blizzard.com/en/wow/t/sharding-phasing-and-layering/376939) | Community |
| **Instance** | Private copy for a group | Dungeons, matches | Common practice | Recalled |
| **Mode pool** | Players opted into a ruleset | PvP on or off | [War Mode discussion](https://eu.forums.blizzard.com/en/wow/t/how-does-sharding-work/430802) | Community |

A Blizzard developer described a layer as [sharding "with a lot of sticky tape"](https://pcgamer.com/the-server-tech-that-saved-wow-10-years-ago-is-causing-problems-for-classics-season-of-discovery-dev-reveals-a-layer-is-actually-just-sharding-with-a-lot-of-sticky-tape). The lesson for AnyGame: make this one first-class primitive instead of several special cases.

### One primitive: the world copy

Every entity's location has a copy key, so interest management and replication need no special cases.

```text
address = (world, copy, cell)
visible to you = same world + same copy + nearby cell + passes phase filter
```

| Decision | Default |
|---|---|
| New player placement | Friends and party first, then least-full copy that still feels alive |
| Too crowded | Open a copy at a soft cap |
| Too empty | Merge at a safe moment, with hysteresis |
| Party on different copies | Move members to the leader at a safe moment |
| Guild, chat, mail, auction, friends | Shared across copies |
| Instances, quests, inventory | Belong to the character |
| Resource nodes, world bosses | Per copy, with rules below |

### Stop layer abuse

| Exploit | Rule |
|---|---|
| Hopping to farm resources or bosses again | Hop cooldown, and shared or per-character limits on rare spawns |
| Hopping to escape PvP | [No transfer in combat, as Blizzard described](https://us.forums.blizzard.com/en/wow/t/layering-in-classic-blizzard-responds-on-reddit/260714). Require a safe state |
| Item duplication during transfer | Exactly-once hand-off, with economy writes in a transaction |
| Mobs or players popping in | Fade transition, only at safe moments |
| Permanent layers splitting the community | Layers scale down as population falls, [as Blizzard intended in Classic](https://pcgamer.com/the-server-tech-that-saved-wow-10-years-ago-is-causing-problems-for-classics-season-of-discovery-dev-reveals-a-layer-is-actually-just-sharding-with-a-lot-of-sticky-tape) |

Server mechanics: [distributed servers](46-distributed-servers.md).

## 🔌 Rejoin

**A disconnect should cost the player seconds, not the match.** Reconnect problems have hurt even [professional Dota 2 matches](https://esports.gg/news/dota-2/og-misha-cant-reconnect-to-match-against-team-liquid-during-ti11-group-stage-valve-steps-in), and [accidental abandon clicks](https://www.sportskeeda.com/esports/the-long-standing-abandon-bug-dota-2-valve-never-fixes) were a long-running complaint.

```text
connected -> lost -> grace period -> rejoined
                         |
                         └-> timed out -> game rule: bot, AI control, forfeit or abandon
```

| Step | Server | Client |
|---|---|---|
| 1. Detect | Marks player disconnected, keeps the slot | Shows "Reconnecting" and retries with backoff |
| 2. Hold | Applies the game's rule: stand still, AI control, pause vote | Stays in the match flow |
| 3. Authenticate | Validates a short-lived resume token | Sends token and last acknowledged tick |
| 4. Catch up | Sends deltas if the gap is small, otherwise a filtered snapshot | Rebuilds its World |
| 5. Load | Waits for a ready signal | Loads assets while showing state |
| 6. Resume | Returns control | Plays a brief transition |

| Model | How to rejoin |
|---|---|
| Replication (`orders`, `action`, `mmo`) | Filtered snapshot, then deltas |
| Lockstep | Latest verified snapshot, then fast-forward through recorded inputs |
| Rollback | Snapshot from a peer or relay, then resync the input stream |
| Turn | Current state plus command history |

Rules:

- **After a crash, the launcher offers Rejoin first.** It survives client restart.
- **Leaving is a separate, deliberate action.** Never put Abandon where a reconnect button belongs.
- **Say whether it is safe to leave,** in plain language.
- **Abandon timers are game rules.** One community-reported Dota 2 example is [about five minutes](https://steamcommunity.com/app/570/discussions/0/558747922965661214).
- **Survive a network change,** such as Wi-Fi to mobile data, using connection migration where supported.
- **Do not reveal hidden state** in the rejoin snapshot.

## 🎞️ Replays

| Design | Stores | Size | Works across versions | Best for |
|---|---|---|---|---|
| **Input log** | Seed + inputs | Tiny | Only with the same deterministic build | Lockstep, fighting, verification |
| **State stream** | Keyframes + deltas + events | Larger | With schema migrations | Server-authoritative games |
| **Hybrid** | Both | Medium | Best | Competitive games |

[Dota 2 replays use periodic full snapshots plus incremental updates](https://whanyu1212.github.io/gem-dota/understanding/02_dem_format), per community format docs. [League of Legends made its server deterministic](https://technology.riotgames.com/news/determinism-league-legends-introduction) to replay recorded games and rewind them.

```text
[keyframe][delta][delta]...[keyframe][delta]...[events index][metadata]
```

| Feature | How |
|---|---|
| Instant seek | Jump to nearest keyframe, apply deltas |
| Rewind, slow motion, fast forward | Seek plus playback clock |
| Free camera, any player's view | Replay holds server truth, and the viewer applies a fog view |
| Timeline markers | Indexed kills, objectives and ability events |
| Kill cam, highlights | Short slices of the same recording |
| Old replays | Schema migrations, or an archived build |
| Bug reports | A replay is the reproduction |
| Fair-play review | [Detectors run on replays](09-online.md#fair-play-an-opinionated-stance) |
| Coaching | Team-only view and drawing tools |

**Privacy and competitive secrets are game policy.** Game communities care: [Valve restricted access to some professional replays](https://escorenews.com/en/dota-2/news/67192-the-changes-were-necessary-and-are-welcome-fly-astini-quinn-ponlo-react-to-valve-closing-access-to-professional-demos-in-dota-2), and [Riot's plan to make replays private drew backlash](https://dotesports.com/league-of-legends/news/riot-delays-league-replay-changes-patch-26-21). AnyGame provides retention, visibility, anonymisation and access controls, and each game sets them.

## 👁️ Live spectating

**Spectators subscribe to a relay and never touch the game server.** Valve's SourceTV shows the classic design: [relays form a tree, each serving many viewers, and the feed is delayed](https://developer.valvesoftware.com/wiki/SourceTV/pl).

```text
game server -> master relay (delay buffer) -> regional relays -> viewers
                       └-> keyframe + delta fragments on a CDN -> many more viewers
```

| Topic | Default |
|---|---|
| Data | Full match state, kept inside the delay buffer |
| Late join | Nearest keyframe, then deltas |
| Delay | Game setting: casual short, ranked longer, tournament longer. [DotaTV has offered a 15-minute tournament option](https://hawk.live/posts/valve-fixed-auto-delay-bug-in-dotatv) |
| Fog view | Free, per-team or per-player |
| Friends watching | Optional, respects privacy settings |
| Scale | Relay tree first, HTTP fragments through a CDN at large scale |
| Viewer tools | Director camera, stat overlays, timeline, picture-in-picture |
| Tournaments | Observer slots, caster tools, stream-safe overlay, pause sync |
| Rewind in live view | Allowed inside the buffer |

Rules:

- **The relay must be unable to serve data earlier than the delay.** Enforce it at the source, never in the client.
- **A spectator can never send gameplay commands.**
- **Spectator load must not affect the game tick.**
- **Stream sniping is reduced by delay, not eliminated.** Stream delay remains partly the streamer's choice.

## Proof

| Check | Passes when |
|---|---|
| Copy isolation | Entities in another copy never reach a client |
| Layer hop | Items and currency are unchanged across thousands of hops |
| Merge | Merging two copies mid-play loses no entity and duplicates nothing |
| Rejoin chaos | Bots disconnect at random ticks and always resume with correct state |
| Crash rejoin | Killing the client and restarting returns to the match |
| Hidden data | A rejoin snapshot passes the same packet audit as live play |
| Replay fidelity | Replay reproduces the final state checksum |
| Seek | A seek anywhere in a long match lands within the target time |
| Old replay | A replay from an earlier version loads or reports a clear error |
| Spectator delay | No relay receives a tick earlier than its configured delay |
| Spectator load | 10,000 simulated viewers do not change game server tick time |
