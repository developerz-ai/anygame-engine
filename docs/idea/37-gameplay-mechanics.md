# 🎲 37. Gameplay mechanics

**Mechanics are data run by small systems.** An agent adds a fireball, a shop or a quest by writing validated data and a test, and writes code only for a genuinely new rule. Every block here is an overridable default ([rule 8](01-thesis.md#design-rules)).

Planned design as of 2026-11. Linked facts were checked on 2026-11-21 from search extracts, not full reads. Unlinked numbers are proposed starting values. Named games are architecture references only. Authority and visibility: [client and server models](35-client-server-models.md). Economy services: [online stack](09-online.md).

## Rules for every mechanic

| Rule | Shape |
|---|---|
| **Data first** | Tuning lives in `content/data/`, with a schema |
| **One write path** | Each kind of state changes through one system, so rules cannot be bypassed |
| **Client asks, server decides** | The client sends a `command`; the authority validates it again |
| **Validate on the server, always** | Ownership, range, cost, cooldown, target and state |
| **Use the World clock and RNG** | Named RNG streams keep replay deterministic |
| **Use ticks for time** | `ready_at_tick`, never a float countdown |
| **Use integers for value** | Money, stacks, XP and item counts are integers. Rates are basis points |
| **Check overflow** | Saturating or checked maths on every value players can grow |
| **Fix the rounding rule** | Define it once per value type, and never let rounding mint value |
| **Emit events** | UI, audio, VFX, achievements and telemetry subscribe, and do not reach into gameplay |
| **Test the failure** | Each mechanic has an illegal-command test as well as a happy path |

## Which authority does this need?

| State | Authority in online games | Client may predict? |
|---|---|---|
| Movement | Server, with reconciliation | Yes, by profile |
| Ability start and cost | Server | Yes, reversibly |
| Damage, death | Server | Show feedback, wait for result |
| Hit detection | Server, lag-compensated where the profile allows | Effects only |
| RNG outcomes, loot | Server | Never |
| Inventory, trade, currency | Server + database transaction | Never |
| Quest completion | Server | Never |
| UI layout, camera, cosmetics | Client | Not applicable |

Single-player games keep the same code path with a local authority, so adding multiplayer later is not a rewrite.

## Attributes, tags and effects

**The core model for RPGs, MOBAs, shooters and survival games.** It follows the proven shape of [Unreal's Gameplay Ability System](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system): attributes hold values, [effects change them](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine), and tags gate behaviour.

| Primitive | Data shape | Example |
|---|---|---|
| `attribute` | `base`, derived `current`, `min`, `max` | `health`, `armor`, `move_speed` |
| `tag` | Hierarchical interned ID | `status.stunned`, `damage.fire` |
| `effect` | Duration, modifiers, tags, stack rule, periodic action | Burn for 5 s |
| `modifier` | Attribute, operation, value, source | +20% move speed |
| `ability` | Costs, cooldown, targeting, phases, effects | Dash |

### Modifier stacking order

Use one published order everywhere:

```text
value = (base + sum(flat)) * (1 + sum(additive_percent)) * product(multiplicative)
value = override if present
value = clamp(value, min, max)
```

| Rule | Why |
|---|---|
| Recompute `current` from `base` plus active modifiers | Removing a buff can never leave drift |
| Store the source of every modifier | Clean removal and clear combat logs |
| Sort modifiers by stable ID | Same result on every machine |
| Set a rule for conflicting overrides | Highest priority, then stable ID |
| Clamp only at the end | Temporary negatives still add correctly |
| Keep resource pools separate from caps | Raising max health does not heal unless the design says so |

**`none`:** Unique buffs; **`refresh`:** Reapplication extends duration; **`intensity`:** Each stack adds strength; **`duration`:** Each stack adds time; **`independent`:** Separate timers; **`strongest`:** Same buff from many sources, only the best counts.

## Abilities

```text
requested -> validated -> windup -> active -> recovery -> cooldown -> ready
                 |           |         |
              rejected    cancelled  interrupted
```

| Part | Data | Rule |
|---|---|---|
| Cost | Attribute and amount | Check at start, commit at a declared phase |
| Cooldown | `ready_at_tick` | Server value wins |
| Charges | `count`, `recharge_ticks` | Single recharge timer unless specified |
| Targeting | Self, unit, point, cone, area, path | Revalidate at each commit |
| Phases | Windup, active, recovery in ticks | Timeline events drive gameplay |
| Cancels | Allowed phases and next abilities | Whitelist, never a free-for-all |
| Queue | Input buffer window | Small and tunable |
| Interrupts | Tags that cancel it | Declared in data |

### Prediction

| Rule | Why |
|---|---|
| Tag predicted changes with a prediction key | The server can confirm or reject them as a group |
| Predict deltas, not absolute values | [Unreal's prediction design](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GameplayAbilities/FPredictionKey) uses this to merge cleanly with server updates |
| Predict movement, animation, cost and cooldown | Feels instant |
| Do not predict kills, loot or hidden outcomes | Rollback here would visibly lie |
| A rejected ability rolls back every dependent change | No ghost buffs |
| Keep networked gameplay in few systems | [Overwatch's GDC talk](https://gdcvault.com/play/1024001) is the reference for ECS gameplay with netcode. Details reached us through summaries |

## Damage pipeline

One ordered pipeline, so every source behaves consistently:

```text
request -> validate -> source modifiers -> crit roll -> target mitigation
        -> shields -> health write -> on-hit effects -> death check -> events
```

| Decision | Default |
|---|---|
| Value type | Integer, with basis-point multipliers |
| Rounding | Round final damage once, with a minimum declared per game |
| Armor | Diminishing formula, avoids 100% immunity |
| Simultaneous kills | Declared rule: ordered, or resolve together in one batch |
| Damage over time | Fixed period, snapshot or live stats declared per effect |
| Reactive loops | Depth limit, and a guard so thorns cannot reflect forever |
| Attribution | Keep source, ability and owner for credit and logs |
| Overkill | Recorded separately from damage dealt |

## Status effects and system interactions

Model statuses as effects plus tags. Combine them with a data table, not hard-coded pairs.

**`damage.fire`:** `surface.oil` · Ignite surface; **`damage.electric`:** `status.wet` · Chain, stun; **`damage.cold`:** `status.wet` · Freeze; **`damage.fire`:** `status.frozen` · Remove freeze.

Rules: process reactions in a stable order, cap chain depth per tick, and add diminishing returns for crowd control.

## Hit detection, projectiles and melee

| Need | Use | Avoid |
|---|---|---|
| Fast bullet | Hitscan or short sweep | A tiny fast physics body |
| Visible slow projectile | Pooled entity with swept collision | Discrete overlap, which tunnels |
| Thousands of bullets | Batched arrays in one system | One full entity with physics each |
| Grenade | Physics body on a fixed tick | Client-owned result |
| Melee | Per-frame hit volumes from the animation timeline | One sphere at impact |
| Area damage | Query, then line-of-sight if needed | Hitting through walls by accident |

**Melee and fighting games** author moves in frames: [startup, active and recovery](https://gamerjournalist.com/how-to-read-frame-data-in-fighting-games/).

**`startup`:** Frames before it can hit. State whether the first active frame is counted; **`active`:** Frames with live hitboxes; **`recovery`:** Frames until neutral; **`on_hit`, `on_block`:** Frame advantage; **`hitstop`, `hitstun`, `blockstun`:** Impact feel and lockout; **`cancel_into`:** Allowed follow-ups, by window; **`hit_id`:** One hit per target per swing.

Tests: frame advantage from data, no double hit, and identical result under rollback.

## Stealth and stimulus/response

Objects emit stimuli and others react, the idea behind the [Dark Engine's Act/React system](https://thief.fandom.com/wiki/DromEd/Properties/Act_React/Sources).

**`stim`:** Type, strength, radius, falloff, source; **`receptor`:** Accepted stim, threshold, response; **`alert`:** Unaware, suspicious, searching, alerted; **`noise`, `light`:** Inputs to `ai.perception`.

In online games, the server computes detection and sends only the result to each client.

## Inventory, equipment and items

Separate **item definitions** (shared data) from **item instances** (owned state).

```text
ItemDef:      id, stack_max, slot, tags, base_stats, schema_version
ItemInstance: uuid, def_id, owner_id, location, quantity, affixes, durability, version
```

| Rule | Prevents |
|---|---|
| Stackables hold a count, unique items hold an ID | Unbounded row growth and identity loss |
| Every move goes through one transaction | [Trade and disconnect dupes](https://bugnet.io/blog/how-to-fix-inventory-item-duplication-bug) |
| Conditional write on owner and version | [Check-then-update races](https://builder.aws.com/content/3JVMxZ2E2JeKRJPA2EUeuwl2tpk/the-race-condition-hiding-inside-my-perfect-architecture) |
| Every command has an idempotency key | A retry charging or granting twice |
| Trades commit both sides atomically, or neither | Half-finished trades |
| Keep an append-only ledger | Auditing and rollback of an exploit |
| Run a conservation audit | Items or currency appearing from nowhere |
| Lock items while listed or in escrow | Selling and using the same item |

**Affixes** store a rolled value and the roll's seed or version, so a later balance patch has a declared policy: keep, rescale or reroll.

## Loot and randomness

**Simple drops:** Weighted table; **Nested rewards:** Tables that reference tables; **Fewer streaks:** [Pseudo-random distribution](https://liquipedia.net/dota2/Random_Number_Generation): raise the chance after each miss, reset on success; **Guaranteed reward:** Hard pity counter; **Reduce repeats:** Shuffle bag; **Fair shared rewards:** Per-player rolls.

Rules: the server rolls, one named RNG stream per purpose, and drop rates are tested statistically over many runs. **Paid randomness needs odds disclosure and legal review** in many regions ([compliance](25-idea-to-distribution.md#compliance-checklist)).

## Crafting and building

**Recipe:** Inputs, outputs, station, time, chance · Consume and grant in one transaction; **Timed craft:** `finish_at` · Server time, safe across logout; **Salvage:** Item to materials · **Value out must not exceed value in**; **Placement:** Footprint, sockets, rules · Client previews, server validates; **Structural integrity:** Support graph · Update incrementally, spread over ticks; **Base persistence:** Chunks with owner and version · Stream and migrate like saves.

Test for infinite loops: an automated check walks all craft, salvage and shop edges for any cycle that creates profit.

## Economy

Currency enters through [faucets and leaves through sinks](https://gamedeveloper.com/design/the-f-words-of-mmos-faucets). Without enough sinks, prices inflate.

**Faucets:** quests, drops, daily rewards, selling to NPCs, passive income. **Sinks:** repairs, fees, taxes, crafting, upgrades, consumables, cosmetics, respec, travel.

| Rule | Why |
|---|---|
| Integer currency with a declared cap | No float drift or overflow |
| Log every source and sink | Balance from evidence |
| Simulate with bots before release | Finds runaway inflation |
| Add a fee to player trade | A built-in sink and an anti-laundering signal |
| Never sell NPC goods below their buy-back price | No infinite money loop |
| Keep premium and earned currency separate | Refunds and compliance |
| Reconcile purchases idempotently | A webhook can arrive twice |

## Progression

**XP and levels:** Curve table · Level is derived from total XP; **Skill tree:** Graph with prerequisites · Validate on server and on load; **Respec:** Refund rule · Recompute from purchases, never subtract; **Unlocks:** Stable IDs · Never reuse an ID; **Run vs meta state:** Separate save scopes · A roguelike run can reset safely; **Offline progress:** Elapsed server time, capped · Never trust the device clock; **Seasons:** Versioned config · Old rewards stay valid.

## Quests, objectives and dialogue

| Primitive | Data | Rule |
|---|---|---|
| `quest` | States, prerequisites, objectives, rewards | Explicit state machine |
| `objective` | Event filter and counter | Progress comes from gameplay events |
| `reward` | Grant reference | Exactly once, by idempotency key |
| `dialogue` | Script ID and state | Use an existing language through an adapter |
| `world_flag` | Typed, namespaced value | No magic strings |

[Ink](https://github.com/inkle/ink/blob/master/Documentation/RunningYourInk.md) is the suggested narrative adapter: its runtime can save and reload story state as JSON. Static checks should catch unreachable quests, missing rewards and softlocks. Bots should complete every required path.

## Save data

**Save schema-described state, never raw memory:** Survives updates; **Version every save:** Permanent migrations; **Write to a temp file, flush, then atomically replace:** A crash cannot destroy the save; **Keep previous saves:** Recovery from corruption; **Add a checksum:** Detect corruption, not cheating; **Save asynchronously from a snapshot:** No frame hitch; **Never trust a local save in competitive play:** Server state wins.

## Turn-based games and rules engines

Every action is a serialisable command on a stack.

```text
command -> validate -> apply -> events -> push to history
undo    -> revert or restore snapshot
```

**Rules are pure functions of state and command:** Testable, replayable, server-verifiable; **Triggered effects enter a resolution queue:** Stable ordering; **Presentation plays events from a separate queue:** Animation never changes rules; **Hide server-only state:** Decks and hands stay secret; **Cap trigger depth:** Stops infinite combos hanging the server; **Run bots at high speed:** Balance and crash discovery.

## Spawners and waves

**`spawn_table`:** Weighted prefabs, budget · Spend a threat budget instead of fixed counts; **`wave`:** Time, groups, exit condition · Data, not script; **`spawn_point`:** Tags, cooldown, line-of-sight rule · Never appear in view unless intended; **`population`:** Caps by region and type · Protects the frame and server tick.

Use pools. Pair pacing with `ai.director` for adaptive games. Tests: caps hold, and waves always end.

## Match rules, scoring and ranked

```text
waiting -> warmup -> live -> overtime -> ended -> results persisted
```

**Authority:** Server owns the match state, timer and score; **Win conditions:** Data, checked at a declared point in the tick; **Ties:** Declared rule for simultaneous finish; **Leavers:** Declared rule in each ranked mode; **Results:** Persist once, with an idempotency key; **Rating:** [OpenSkill or TrueSkill-style models fit teams](https://arxiv.org/abs/2401.05451). Glicko-style models fit 1v1; **Abuse:** Detect win trading and smurfing with `anticheat`.

## Vehicles as gameplay

**Seats:** Entity relationship with role and permissions; **Enter and exit:** Server-validated command; **Ownership:** Driver predicts, server stays authoritative; **Damage:** Component health feeds handling and modules; **Handling:** Moddable data over `physics.vehicle`; **Weapons:** Same ability and damage pipeline; **Occupants:** Defined outcome on destruction.

Deep combat vehicle design: [large-scale combat](15-large-scale-combat.md).

## Time rewind and undo

**Puzzle undo:** Command history; **Short rewind:** Ring buffer of snapshots; **Long rewind:** Keyframes plus deltas, as discussed in [Braid's GDC talk](https://gdcvault.com/play/1012210/contactUs) (implementation details not verified here); **Rollback netcode:** Kernel snapshots; **Replay:** Seed plus input log.

Keep rewound state in the World. Audio, VFX and UI listen for rewind events.

## Agent recipe for any new mechanic

1. `ag find` an existing block, and reuse it if one fits.
2. Write data shape and schema.
3. Decide authority, visibility and prediction.
4. Name the exploits: dupes, races, overflow, rounding, loops.
5. Implement one small system over a query.
6. Emit events for presentation.
7. Test happy path, illegal command, determinism and save/load.
8. Run a bot or balance simulation.
9. Report CPU, memory and network cost ([quality bar](32-quality-bar.md)).
