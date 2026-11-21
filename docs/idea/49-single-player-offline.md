# 🏠 49. Single-player, local and offline

**A game built with AnyGame needs no internet, account or server unless its developer chooses that.** Single-player is a first-class target, not multiplayer with the network removed. An offline game ships no netcode and no backend.

Planned design as of 2026-11. Every mode here is a default a game can change ([rule 8](01-thesis.md#design-rules)).

## One game, any connection

| Mode | Authority | Network | Needs a server? | Fits |
|---|---|---|---|---|
| **Offline single-player** | Local World | None | No | Campaigns, RPGs, puzzle, narrative, sims |
| **Local multiplayer** | Local World | None | No | Split-screen, shared-screen, party games |
| **LAN** | One machine hosts | Local network | No | Friends in a room, events |
| **Listen server** | One player hosts | Internet | No dedicated server | Co-op |
| **Peer-to-peer** | Lockstep or rollback | Internet | Relay or signalling at most | Fighting, RTS |
| **Dedicated server** | Server | Internet | Yes | Competitive, shooters, MOBA |
| **Persistent online** | Server fleet | Internet | Yes | MMO, live service |
| **Async online** | Backend validates | Occasional | Light backend | Turn-based, ghosts, leaderboards |

Choose in the manifest. Modules a mode does not use are not linked.

```toml
# anygame.toml: illustrative
[modes]
offline = true
local_players = 4
online = false
```

## Write once, run in any mode

Gameplay always goes through the same path:

```text
input -> command -> authority -> systems -> events -> presentation
```

| Mode | Where authority runs |
|---|---|
| Offline | Directly in the local World, with zero network code |
| Co-op host | Same systems, plus a replication module |
| Dedicated | Same systems in a headless server |

- **A campaign can add co-op later** without rewriting gameplay, because commands and components were already separate.
- **Offline pays nothing.** No serialisation, prediction or interpolation runs for a local player.
- **Do not force the client-server shape on an offline game.** A single-player game can use simple direct commands and skip the rest.

## What single-player can do that online cannot

| Feature | Primitive |
|---|---|
| **True pause** | Stop the World clock |
| Quick save and load anywhere | World snapshot |
| Rewind and undo | Snapshots |
| Slow motion, bullet time | Scaled simulation clock |
| Fast travel with no load | Streaming plus simulation LOD |
| Difficulty and assists at any time | Tuning data |
| Mods with no restriction | Full capability sandbox grant |
| Cheats and sandbox modes | The player's own game, their choice |
| Big AI budget | No server tick to share |
| Photo mode | Frozen World, free camera |
| Companion AI | [NPC blocks](36-npcs-and-ai.md) |

## Saves are sacred

Losing a save is the worst bug a single-player game can have.

| Rule | How |
|---|---|
| **Atomic writes** | Write a temp file, flush, then rename. A crash never damages the last good save |
| **Several rotating backups** | Manual, autosave and last-known-good slots |
| **Checksums** | Corruption is detected, then the backup is offered |
| **Versioned schema** | Old saves always load through migrations |
| **No hitch** | Copy-on-write snapshot, then serialise on a worker |
| **Autosave at safe moments** | Never during a fall, in a death state or mid-cutscene |
| **Save-state validation** | Detect softlocks before overwriting the only good save |
| **Portable and yours** | Documented location and export. Cloud sync is optional |
| **Handle low disk and app kill** | Mobile and browser can stop a game at any moment |
| **Mods recorded in the save** | Warn clearly if a required mod is missing |

## Offline means really offline

| Promise | Rule |
|---|---|
| Starts with no network | No login, licence check or config fetch can block boot |
| No required account | Accounts are optional, for optional online features |
| No hidden calls home | A network test on an offline build sees zero connections |
| Works forever | The game runs after every service is gone |
| Optional services fail quietly | Leaderboards or cloud saves show "offline" and gameplay continues |
| Sync later | Achievements, stats and cloud saves queue, and merge safely |
| Content is complete | All required content is on disk once installed |
| Store DRM is the developer's choice | The engine neither requires nor adds any |

## Local multiplayer

- Split-screen through multiple camera views in one render graph.
- Per-player input devices, profiles, HUD and audio mix.
- Shared-screen cameras with framing rules.
- Budget per view scales down automatically.
- Hot-join a controller, and handle a disconnect by pausing.
- Remote play from a platform can work on top without engine changes.

## Hybrid games

Many great games are mostly offline with a light online layer.

| Feature | How it stays optional |
|---|---|
| Ghosts and leaderboards | Async upload, validated by replay |
| Daily challenges | Same seed for everyone, with an offline fallback |
| Asynchronous messages | Nice to have, never required |
| Cloud saves | Conflict screen shows both, the player chooses |
| Drop-in co-op | Host's World starts replicating on demand |
| AI filling empty slots | Bots keep multiplayer modes playable offline |

## When servers end

A game should be able to outlive its servers ([no regrets](31-no-regrets.md)).

- Plan an offline or bot-backed mode when a game is designed.
- Include dedicated server binaries in a sunset package where the developer allows it.
- Keep player progress exportable.

## Proof

| Check | Passes when |
|---|---|
| **Airplane mode** | Boots and finishes the game with networking disabled |
| **Zero calls** | A network audit on an offline build sees no connection |
| Footprint | An offline build contains no netcode or backend symbols |
| Power-cut save | Killing the process during every save phase never loses the last good save |
| Corrupt save | A damaged save restores from backup with a clear message |
| Old saves | Fixtures from every released version load |
| Autosave | No frame exceeds budget during a save |
| Service outage | With every optional service down, gameplay is unaffected |
| Split-screen | Each supported player count holds its frame budget |
