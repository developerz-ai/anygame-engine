# 🌐 46. Game servers, distribution and MMO scaling

**Use the simplest server shape that fits the game, and make the next step possible without rewriting gameplay.** Most games never need a mesh. An MMO needs every layer here.

Planned design as of 2026-11, checked against search extracts of linked pages. Unlinked items are recalled general practice and unverified. All numbers are starting points to measure. Every layer is an adapter-based default a game can replace ([rule 8](01-thesis.md#design-rules)).

Related: [online stack](09-online.md), [client and server models](35-client-server-models.md), [large-scale combat](15-large-scale-combat.md#-tick-and-bandwidth-budgets), [concurrency](45-concurrency.md), [Phase 7](../build/phase-7-mmo.md).

## The scaling ladder

Stop at the first rung that meets the game's needs.

| Rung | Shape | Fits | Gameplay code changes |
|---|---|---|---|
| 0 | Single-player, no server | Offline games | None |
| 1 | Listen server or peer host | Friends, co-op | None |
| 2 | One process per match | Shooters, MOBA, racing | None |
| 3 | Many matches per host | Competitive at scale | None |
| 4 | Static zones, one process each | Small MMO, survival | Zone rules |
| 5 | Instances, layers, phases | Dungeons, crowded launch areas | Data |
| 6 | Seamless borders with hand-off | Open persistent world | Authority-aware systems |
| 7 | Replication layer, dynamic mesh | Very large shared worlds | Authority-aware systems |

The replication-layer idea comes from Cloud Imperium's published design: [state moves into a service that clients connect to, and a game server becomes a client with authority](https://starcitizen.tools/Replication_layer). That source is a community wiki of evolving plans, so treat it as a direction, not proof of shipped behaviour.

## Inside one server

| Model | How | Use when | Watch for |
|---|---|---|---|
| **Single-thread sim + I/O threads** | One tick thread owns the World | Default for many small matches per host | One slow match stalls only itself |
| **Parallel sim** | Job graph inside a tick | Large single worlds | Worker contention with other processes |
| **Shard per core** | One pinned thread owns its partition, cross-shard by message | Very high density, gateways | Cross-shard interactions |
| **One process per match** | OS isolates failures | Default for session games | Memory overhead |
| **Many matches per process** | Shared assets, isolated Worlds | Density after isolation is proven | A crash takes all matches |

**Default:** one process per match, single-thread simulation, separate I/O, share immutable assets through read-only memory mapping.

### Tick budget

```text
tick budget = (1000 ms / tick rate) x cores / matches per core, minus OS and network reserve
```

Riot's published [VALORANT target](https://technology.riotgames.com/news/valorants-128-tick-servers) is a useful worked example: more than three games per core at 128 ticks, a 10% host reserve, and about 2.34 ms per frame.

| Practice | Why |
|---|---|
| Budget by system, in microseconds | A single-system regression is visible |
| Report p50, p99 and worst tick | An average hides stutter |
| Reduce server-only work | Riot cut animation cost by [evaluating it every fourth frame](https://technology.riotgames.com/news/valorants-128-tick-servers) |
| Load test instances **together** | Shared cache contention appears only on a busy host |
| Set a shed order for overload | Cosmetic, far AI, update rates, then time dilation |

Time dilation, as [EVE Online describes it](https://eveonline.com/article/introducing-time-dilation-tidi), slows the game clock so the server's work queue stays small. Use it as the last defence before failure.

## Network pipeline

```text
socket -> decrypt -> validate -> per-client input queue -> tick
tick -> relevance -> priority -> delta encode -> packetise -> encrypt -> socket
```

| Topic | Default |
|---|---|
| Real-time transport | Encrypted UDP through the `net.transport` port |
| Browser | WebTransport, with WebSocket fallback |
| Service traffic | TCP or QUIC. [QUIC supports client connection migration](https://rfc-editor.org/rfc/rfc9000) |
| Channels | Unreliable state, reliable-ordered commands, separate streams so one loss does not block all |
| Batching | Send once per network tick, per client, with a byte budget |
| MTU | Stay under a conservative packet size and fragment rarely |
| Compression | Quantise and delta first, then a shared dictionary if measured |
| Encryption | Per-session keys, replay protection, authenticated packets |
| Parallelism | Serialise shared entity deltas once, then filter per client |
| Send budget | Priority accumulators, so low-priority entities eventually update |

## Interest management

| Structure | Best for |
|---|---|
| Uniform grid | Default for open worlds |
| Hierarchical grid | Very uneven density |
| Rooms or portals | Interiors and dungeons |
| Team visibility sets | MOBA and RTS fog of war |
| Relevance graph | High actor counts, as with [Unreal's Replication Graph](15-large-scale-combat.md#-what-to-steal) |

Rules:

- **Filter visibility before priority.** Hidden data must never enter a client's send list ([visibility classes](35-client-server-models.md#every-field-has-a-visibility-class)).
- **Use hysteresis** on enter and leave distances.
- **Share per-cell work** rather than testing every entity against every client.
- **Reduce update rate with distance,** and always keep critical entities current.

## Authority and hand-off

Exactly one server has write authority for each entity at any time. Every authority grant carries an increasing **epoch**, and stale writers are rejected.

```text
A: prepare(entity, epoch+1) -> B: ready -> A: freeze writes, send final state
B: commit authority at epoch+1 -> directory updates -> A: becomes read-only ghost
```

| Failure | Outcome |
|---|---|
| A crashes before commit | Directory keeps A's epoch, recovery restores from the last persisted state |
| B crashes before commit | A times out and unfreezes |
| Commit message is duplicated | Same hand-off ID, so it has no second effect |
| A writes after losing authority | Rejected by epoch |
| Network partition | Whichever side cannot reach the directory stops mutating |

Network delivery cannot be exactly once. **Effects are made exactly once** with stable IDs and idempotent handling, a framing the [idempotent consumer pattern](https://microservices.io/patterns/communication-style/idempotent-consumer.html) describes.

### Zone borders

| Technique | Purpose |
|---|---|
| Ghosts | Read-only copies of entities near a border |
| Overlap band | Interaction across a border without popping |
| Hand-off hysteresis | Stops flip-flopping along a border |
| Cross-server commands | Attack requests go to the target's authority |
| Atomic multi-entity action | Avoid it. Use a saga or single authority for trades |
| Avoid borders in hotspots | Place them through empty terrain |
| Dynamic split | Move cells by load, with cooldowns to prevent thrash |

## Persistence

| Data | Durability | Path |
|---|---|---|
| Position, transient combat | May lose seconds | Periodic snapshot |
| Character progress | Low loss | Write-behind with a short flush |
| Currency, trades, rare items | **No loss, no dupes** | Synchronous ACID transaction |
| Match results | Must survive | Idempotent write |
| Events and logs | Append | Bus, then analytics |

- **Write-behind** batches changed entities through dirty tracking, and flushes on logout, hand-off and shutdown.
- **Snapshots + log** restore a world: load the latest snapshot and replay later changes. PostgreSQL's [write-ahead log](https://www.postgresql.org/docs/current/wal-intro.html) shows the principle: record the change durably before applying it.
- **Every persisted row has a schema version.** Migrations run online and stay backward-compatible during a rollout.
- **Test restore regularly.** An untested backup is only a hope.

## Economy without dupes

Item duplication usually comes from an action being applied twice, or from two systems owning one item.

| Rule | Shape |
|---|---|
| One ledger owns value | The simulation displays it, and the ledger decides |
| Every operation has an idempotency key | A retry cannot apply twice |
| Items have unique IDs | A dupe is detectable and impossible by constraint |
| Double-entry | Debits equal credits in every transaction |
| Use the [transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html) | State change and its event commit together |
| Multi-service flows use sagas | Each step has a compensation |
| Lock in a stable order | Prevents deadlocks in trades |
| Nightly audit | Sum of holdings must match the ledger |

## Backend topology

```text
clients -> edge/relay -> gateway -> game servers <-> replication layer
                            |              |
                    identity, matchmaking  events bus -> jobs, telemetry, social
                            |              |
                       session cache     persistence -> databases
```

| Concern | Default | Scale by |
|---|---|---|
| Accounts, economy | PostgreSQL | Read replicas, then shard by account |
| World state | Document or graph store by adapter | Shard by world, region or cell |
| Sessions, presence | Redis-protocol cache with expiry | Cluster |
| Events | NATS-protocol | Partition by entity or account |
| Jobs | Postgres queue | Kafka, NATS or SQS |

Rules: **a cache is never the source of truth**, shard keys match access patterns, and no request crosses shards in a hot path.

## Operating a live fleet

| Topic | Practice |
|---|---|
| Fleet | Warm buffer of ready servers. [Agones fleets](https://agones.dev/site/docs/reference/fleet/) are the default Kubernetes adapter |
| Autoscale | Scale on allocated capacity and tick health, ahead of known peaks |
| Allocation | Mark a server allocated, so scale-down cannot kill a live match |
| Rolling update | [Agones surges new servers and skips allocated ones](https://agones.dev/site/docs/guides/fleet-updates/) |
| Drain | Stop new players, finish or migrate sessions, flush state, then exit |
| Regions | Route by measured latency, not geography alone |
| Login queue | Admit at a controlled rate, show honest position and wait |
| Matchmaking | Tickets with expanding rules, parties and trust score |
| Version skew | Protocol version in handshake. Servers accept N and N-1 during rollout |
| Hot patching | Data and script patches first, code patches through a rolling restart |
| Canary | Release to a small share, compare crash and tick metrics, then expand |
| Rollback | Previous build ready, and schema changes stay compatible with it |

## Failure modes

| Failure | What goes wrong | Fix |
|---|---|---|
| **Split brain** | Two servers think they own an entity | Epoch fencing, single directory, minority side stops |
| **Partition** | Part of the world cannot reach the database | Queue safe writes, block economy actions, show status |
| **Thundering herd** | All players reconnect at once | Client [full-jitter backoff](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html), admission queue |
| **Retry storm** | Retries multiply load | [Retry budgets, retry at one layer](https://sre.google/sre-book/handling-overload/) |
| **Cascading failure** | One overloaded service takes down others | [Load shedding, deadlines](https://sre.google/sre-book/addressing-cascading-failures/) |
| Shedding misread as spare capacity | Balancer sends more traffic to a rejecting server | [Count rejections as utilisation](https://sre.google/workbook/managing-load/) |
| Slow client | Send queue grows | Bounded per-client queue, drop stale state, disconnect |
| Slow database | Tick stalls | Never wait on a database in the tick |
| Poison message | Consumer crashes repeatedly | Retry limit, then dead-letter queue |
| Cache stampede | Many misses hit the database | Request coalescing, jittered expiry |
| Clock drift | Timers and ordering break | Server tick for gameplay, monotonic clocks, no wall-clock ordering |
| Crash during save | Partial state | Atomic transaction or write-new-then-swap |
| Bad deploy | Everything breaks together | Canary, automatic halt, rollback |

## Observability and capacity

| Measure | Why |
|---|---|
| Tick p50, p99, worst, overruns | Player-felt server health |
| Players, entities and bytes per client | Capacity model |
| Input-to-result latency | Real responsiveness |
| Packet loss, jitter, reconnects | Network quality |
| Hand-off count, duration, failures | Mesh health |
| Queue depths and consumer lag | Early overload warning |
| Persistence lag | Data at risk |
| Ledger audit result | Economy integrity |
| **Cost per concurrent player** | Whether the game can stay online |

Every request and hand-off carries a trace ID. Each crash stores its snapshot and input log.

```text
cost per player = (server + bandwidth + database + services) / peak concurrent players
```

Capacity planning: measure per-player cost from load tests, add headroom for peak and failure of one region, and rehearse launch-day traffic. Riot's [load-testing write-up](https://technology.riotgames.com/news/scalability-and-load-testing-valorant) is a useful model.

## Security basics

| Threat | Defence |
|---|---|
| Spoofed or replayed packets | Authenticated encryption, session tokens, sequence checks |
| Amplification | Handshake cookies, and replies no larger than requests until validated |
| Volumetric DDoS | Provider mitigation, relay network, hidden origin IPs |
| Application floods | Per-IP, per-account and per-command rate limits |
| Malformed input | Bounded parsers, fuzzing, reject and count |
| Forged match tickets | Short-lived signed tickets |
| Admin access | SSO, least privilege, audited commands |
| Internal traffic | Authenticated, private network |
| Player data | Encrypt in transit and at rest, minimise, support deletion |

## Proof

| Check | Passes when |
|---|---|
| Density | Target matches per host hold p99 tick budget |
| Kill a server | Players reconnect, and no persisted value is lost beyond its stated limit |
| Hand-off chaos | Random crashes and duplicated messages leave no lost or duplicate entity |
| Split brain | A partitioned old owner cannot commit a write |
| Dupe hunt | Bots trade through crashes, retries and hand-offs, and the ledger still balances |
| Reconnect storm | All clients reconnect after an outage and the service recovers |
| Overload | The server sheds load and keeps the tick alive |
| Rolling deploy | Version N and N-1 coexist with no dropped match |
| Restore | A backup restores to a playable world |
| Soak | Memory and latency stay flat for 72 hours |
| Security | Fuzzed packets cause no crash, and floods are rate limited |
