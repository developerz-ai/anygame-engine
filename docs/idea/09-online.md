# 🌐 9. Online stack: netcode, servers, database, background jobs

The backend is part of the framework: the same components, schema and C++ run on client, simulation server and persistence boundary, so there is no hand-written protocol or ORM layer between them.

## Four netcode models, one annotation system

A component field is annotated once (`replicated`, `predicted`, `owner-only`, `quantise(0.01)`), and whichever netcode module is loaded uses it.

| Module | How it works | Requires | Best for |
|---|---|---|---|
| `net.rollback` | Predict remote inputs, restore snapshot and re-simulate on mismatch | Deterministic loop, fast snapshots | Fighting, platform fighters, small co-op action |
| `net.lockstep` | Exchange only inputs; every peer simulates identically | Deterministic loop | RTS, factory, turn-based, replays |
| `net.replication` | Authoritative server; delta-compressed state; client prediction and lag compensation; relevancy and priority budgets | Nothing special | Shooters, action, battle royale, racing |
| `net.mmo` | Replication plus area-of-interest grids, many server processes per world, entity hand-off | Online services below | MMOs, persistent open worlds |

Rollback's cost is why it stays in small games: full state must be saved and several frames re-simulated inside one frame. Because world snapshots are a kernel feature ([section 4](04-kernel.md)), AnyGame games get the hard part without the multi-year retrofit that shipped fighting games have paid.

## Server architecture for persistent worlds

The key idea comes from Star Citizen's published design: separate simulation from replication and state. A replication layer holds every entity's state in memory and streams it both to clients and to simulation servers; a simulation server is then just another subscriber that happens to have authority over some entities.

Consequences AnyGame adopts:

- A simulation server can crash and be replaced without disconnecting players.
- Authority over an entity can move between servers, so a crowded city splits across processes (static zones first, dynamic splitting later).
- Persistence is a subscriber too: it writes changed entities to the database continuously.

## Backend primitives (the Rails part)

| Primitive | What it gives you | Default implementation | Replaceable with |
|---|---|---|---|
| `services` | Typed RPC services generated from schema; stateless, horizontally scaled | Built-in C++ service host | Any language via generated clients |
| `persist` | Entities and documents saved by schema with versioned migrations (`ag db migrate`) | PostgreSQL for accounts/economy, embedded SQLite for local and single-player | FoundationDB, Scylla, DynamoDB |
| `cache` | Hot world state, sessions, presence | In-process, then Redis-protocol | Any KV store |
| `jobs` | Durable background jobs: retries, schedules, cron, idempotency keys | Postgres-backed queue | Kafka, NATS, SQS |
| `events` | Pub/sub bus between services and servers | NATS-protocol | Kafka |
| `identity` | Accounts, platform logins (Steam, PSN, Xbox, Apple, Google), sessions, trust scores | Built-in | Third-party identity |
| `matchmaking` | Tickets, rules, parties, backfill, lobbies | Built-in rule engine | Open Match, platform services |
| `fleet` | Start, scale and drain dedicated servers | Local process manager for `ag dev`; Kubernetes/Agones in production | Any orchestrator |
| `economy` | Wallets, inventory, trades as ACID transactions with an audit ledger | On `persist` | |
| `social` | Friends, guilds, chat channels, mail, presence | On `services` + `events` | |
| `liveops` | Remote config, feature flags, events calendar, A/B tests, hot content patches | Built-in | |
| `telemetry` | Metrics, traces, logs, crash dumps, gameplay analytics | OpenTelemetry | Any collector |
| `anticheat` | Server-side validation, replay verification, statistical detection, trust scores, cheater-pool matchmaking. No client kernel driver | Server authority by default | Custom server-side detectors |

Background jobs cover everything that should not run in the simulation tick: auction expiry, mail delivery, leaderboard rollups, guild-war scheduling, offline progress, purchase reconciliation, nightly economy audits, save-game compaction.

## Rules for the backend

- **Never trust the client.** Clients send inputs and intents; servers own outcomes.
- **Economy writes are transactions,** never part of the replicated simulation state. Item duplication bugs come from mixing the two.
- **`ag dev` runs the whole stack on a laptop:** client, simulation server, database, job runner, in one command, with hot reload.
- **Same binary modules, headless.** A dedicated server is the game minus render, audio and input modules. Load tests run thousands of headless bot clients from the same code.

## Fair play: an opinionated stance

AnyGame does not ship, integrate or recommend kernel-level client anti-cheat. A game should not require ring-0 access to a player's machine. The framework's position: make cheating hard by design, detect it on the server, and match detected cheaters with each other instead of banning them.

**Layer 1, design out the cheat.**

- Server authority over movement, hits, inventory and economy.
- Server-side fog of war: the server does not send what the player cannot perceive, so wallhacks have nothing to read. Riot describes this and authoritative movement as the first line of Valorant's defence, before any client software.
- Deterministic kits verify matches by re-simulating the input log on a server; an impossible result is proof.
- Protected-action UI model so addons cannot automate play.

**Layer 2, detect on the server.**

- Every match records inputs and state; detectors run offline on replays: aim statistics, reaction-time distributions, impossible information use, economy anomalies.
- A per-account trust score combines detectors, reports, account age and party associations. Published research on server-side FPS detection is active, and Valve's VACnet works from server-side input telemetry.
- Human review tools: sampled replays with detector overlays for moderators or community juries.

**Layer 3, pool instead of ban.**

- `matchmaking` takes trust score as a first-class input. Low-trust accounts are matched together; partying with one pulls the party into that pool.
- Precedents: Max Payne 3's cheater pool, Titanfall, and Fall Guys' Cheater Island.
- No ban wave means no clear signal for cheat developers to tune against, and no incentive to buy a fresh account.

**Costs of this stance, stated honestly.**

- Server-side detection sees less than a kernel driver. Riot credits its kernel driver with pushing cheating under 1% of ranked Valorant games; a server-only approach should expect a higher residual rate, especially for subtle aim assistance.
- Fall Guys shut its cheater island down: clips from it made the whole game look overrun, and cheaters grouped up to dodge detection. Mitigations: mark pooled matches clearly in replays and streams, apply party rules, and keep detection thresholds conservative to avoid false positives.
- False positives hurt more when silent. An appeal path and a visible trust indicator are part of the module.
- Games that need a third-party client anti-cheat can still add one as an external package; the framework will not provide or maintain it.

## Competitive multiplayer: what the leaders do

| Game | Technique | AnyGame primitive |
|---|---|---|
| Counter-Strike 2 | Sub-tick: inputs carry timestamps between server ticks, so outcomes do not depend on tick alignment | Timestamped input stream in `net.replication` |
| Valorant | High tick rate, server fog of war, authoritative movement | Per-client visibility filter before replication |
| Overwatch | ECS gameplay, predicted abilities, kill-cam from replay data, "favour the shooter" with limits | Predicted ability system, `replay` module |
| Fortnite | 100 players, replication priority and relevancy, buildable world state, cross-play from phone to PC, live in-game events | Relevancy graph, scalable render tiers, `liveops` events |
| Rocket League | Server-authoritative physics with client prediction and rewind at high tick rate | Rewindable physics |
| Dota 2, LoL | Server-authoritative with fog computed server-side, data-driven abilities, full replays, delayed spectating, custom games | `gameplay.abilities`, `replay`, mod packages |
| StarCraft II, Age of Empires | Lockstep: tiny bandwidth and perfect replays, but every client holds full state, so map hacks are possible | `net.lockstep`; plus an optional server-authoritative RTS mode with fog filtering for ranked play |
| Fighting games | Rollback with input delay tuning, spectators fed by input stream | `net.rollback` |
