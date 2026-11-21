# 🧠 36. NPCs and game AI

**Good game AI is not the smartest AI. It is the AI that makes the player's experience better.** Build the simplest brain that creates the intended moment, make its intent readable, keep it fair, and keep it inside budget.

Planned design as of 2026-11. No AI module exists yet. Linked facts were checked on 2026-11-21 from search extracts of the linked pages, not full reads. **All numbers are starting points to tune and measure.** Every technique is an overridable default ([rule 8](01-thesis.md#design-rules)). Games are references only: NPCs, worlds and writing stay original.

Overview: [simulation modules](08-simulation.md). Short tricks: [AI and pathing](20-tricks-30-years.md#-ai-and-pathing). Online rules: [client and server models](35-client-server-models.md).

## Rules that matter most

| Rule | Why |
|---|---|
| **Design the player-facing moment first** | "Flanks after suppressing" is a goal, "use GOAP" is not |
| **Readable beats clever** | A player must understand what an NPC is doing and why |
| **Telegraph before danger** | Wind-ups, callouts and aim time make failure feel fair |
| **Separate knowing from cheating** | NPCs act on perceived facts. Any director knowledge is deliberate |
| **Separate decide from act** | Brains choose intent, and action systems execute it |
| **Commit to decisions** | Hysteresis and minimum durations prevent twitching |
| **Tuning is data** | Ranges, weights and cooldowns stay out of code |
| **Decisions are explainable** | Every choice records why it won |
| **Unseen NPCs cost almost nothing** | Use AI LOD and time-slicing |
| **Every behaviour has a bot-runnable check** | "Looks smart" is not a test |

## The NPC stack

```text
world + stimuli
      │
SENSE      ai.perception        what can I detect now?
      │
REMEMBER   npc memory           what do I believe, and how sure am I?
      │
DECIDE     ai.decision          what should I do?
      │
PLAN       ai.planning, ai.nav  how do I get it done?
      │
ACT        gameplay.*           move, use ability, interact, speak
      │
PRESENT    anim.*, audio, UI    make the intent readable
```

| Layer | Owns | Must not |
|---|---|---|
| Sense | Detections with source, position and confidence | Change behaviour directly |
| Remember | Beliefs with timestamps and decay | Read true world state for hidden facts |
| Decide | Current goal and reason | Move entities or play clips |
| Plan | Steps, routes and fallback | Run unbounded in one frame |
| Act | Validated commands | Bypass cooldowns, ranges or server rules |
| Present | Animation, barks, audio and telegraphs | Change the simulation result |

All state lives in ECS components. Brains and plans are text assets with schemas, so they hot-reload, snapshot and diff ([kernel](04-kernel.md)).

## Choose a decision model

Start at the top. Move down only when the row above cannot produce the behaviour.

| Need | Use | Module | Avoid when |
|---|---|---|---|
| A few clear states: patrol, chase, attack | **FSM** | `ai.fsm` | Transitions become a web |
| Modes with nested sub-states | **HFSM** | `ai.fsm` | Many behaviours need reuse across modes |
| Authored priority and reusable combat logic | **Behaviour tree** | `ai.bt` | Choices depend on many continuous factors |
| Weigh many changing factors | **Utility AI** | `ai.utility` | Designers need exact scripted order |
| Multi-step goals from a set of actions | **GOAP** | `ai.planning` | World state is huge or plans change every tick |
| Structured plans, authored task knowledge | **HTN** | `ai.planning` | The domain is small enough for a tree |
| Group roles and objectives | **Squad layer + task tree** | `ai.squad` | Enemies act alone |
| Control pacing for a whole session | **Director** | `ai.director` | Authored pacing is enough |
| Natural-language conversation | **LLM layer** | `ai.llm` | The result affects deterministic state |

**Default stack:** behaviour tree for action NPCs, utility for selecting goals in open-ended games, FSM for simple creatures, and a planner only where emergent sequences are a selling point.

These models combine well: a utility layer picks the goal, a tree or planner achieves it, and an FSM controls the low-level action.

| Reference | Lesson | Source |
|---|---|---|
| Halo 2 | A prioritised behaviour DAG handled about 50 behaviours | [GDC 2005 write-up](https://gamedeveloper.com/programming/gdc-2005-proceeding-handling-complexity-in-the-i-halo-2-i-ai) |
| Halo 3 | Squads pour into a tree of prioritised objectives | [Encounter design](https://www.gamedeveloper.com/design/combat-evolved-the-encounter-design-of-halo-3) |
| F.E.A.R. | Three FSM states plus an A* action planner | [Orkin, GDC 2006](https://pages.cs.wisc.edu/~dyer/cs540/handouts/gdc2006_orkin_jeff_fear.pdf) |
| Killzone, Horizon | HTN plans built from action macros | [Horizon AI](https://gamedeveloper.com/design/behind-the-ai-of-horizon-zero-dawn-part-1-), [Decima](https://guerrilla-games.com/read/htn-planning-in-decima) |
| Left 4 Dead | A director monitors players and drives pacing | [Booth, Valve](https://cdn.fastly.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf) |
| Alien: Isolation | Macro director knows, micro creature must sense | [Analysis](https://www.gamedeveloper.com/design/the-perfect-organism-the-ai-of-alien-isolation) |
| The Sims | Objects carry their actions and effects | [Overview](https://grandtextauto.soe.ucsc.edu/?p=1778) |
| Game AI Pro | Practical chapters from working developers | [gameaipro.com](https://www.gameaipro.com/) |

### Stop bad decisions

| Symptom | Fix |
|---|---|
| Rapid switching | Hysteresis, commitment time, switch cost |
| All NPCs pick one target | Reservation tokens, distance and crowding penalties |
| Utility scores are hard to balance | Normalise to 0–1, use response curves, inspect the winning reasons |
| Tree re-evaluates too much | Event-driven wakeups, decorators with cooldowns |
| Plans break constantly | Replan on relevant events only, keep a simple fallback |
| Planner spikes | Limit nodes per tick, cache plans, spread across frames |
| NPC idles after failure | Every plan has a fallback goal |

## Perception

| Sense | Model | Tuning data |
|---|---|---|
| Sight | Range, cone, height, line of sight, light, stance, movement | Cone, ranges, detection curve |
| Hearing | Sound event with loudness, propagated through rooms or nav graph | Radius, occlusion, attention |
| Touch | Collision or damage reveals source | Reaction by type |
| Smell or magic | Trail or scent field | Decay rate |
| Stimulus | World emits `fire`, `noise`, `blood`, `alarm` through `gameplay.stim` | Tags and responses |
| Team knowledge | Shared threat with delay and comms range | Delay, radius, trust |

**Rules:** detection builds over time, cheap tests run first (distance, cone, room, then a budgeted ray), perception creates beliefs rather than true positions, and awareness is shown through icons, voice or head turns.

## Memory and blackboards

| Store | Holds | Lifetime |
|---|---|---|
| Blackboard | Current target, cover, destination | Short |
| Belief | "Enemy last seen here" with confidence | Decays |
| Episodic memory | "Player helped me" | Saved if it matters |
| Squad memory | Shared threats and assignments | Encounter |
| World knowledge | Town state, faction events | Persistent |

Use handles, timestamps and bounded sizes. Saved memory is schema-versioned ([future-ready](22-future-ready.md)).

## Movement

| Need | Use | Module |
|---|---|---|
| Tile or grid game | A* or JPS | `ai.nav.grid` |
| 3D walking | Navmesh, wrap Recast/Detour | `ai.nav.mesh` |
| Open world | Tiled, streaming navmesh with hierarchy | `ai.nav.stream` |
| Hundreds to thousands to one goal | [Flow field tiles](https://www.oreilly.com/library/view/game-ai-pro/9781482254792/K23980_C017.xhtml) | `ai.nav.flow` |
| Local crowd avoidance | [ORCA / RVO2](https://gamma.cs.unc.edu/RVO2/), Apache-2.0 | `ai.crowd` |
| Jumps, ladders, doors, vaults | Off-mesh links with animation | `ai.nav.links` |
| Cars | Lane graph with intersections | `ai.traffic` |
| Flying or swimming | Volume grid or sparse octree | `ai.nav.volume` |

ORCA handles local avoidance only. [Global routes must come from the host](https://gamma.cs.unc.edu/RVO2/documentation/2.0/index.html).

**Rules:** path requests are async and budgeted, groups share paths, stuck agents recover (teleport only off-screen), dynamic obstacles update nav tiles, cover is generated then scored and reserved, and animation agrees with movement.

## Combat AI

| Technique | Effect |
|---|---|
| **Attack tokens** | Limit how many enemies attack at once |
| Roles | Rusher, suppressor, flanker, sniper, healer |
| Position scoring | Range, cover, flank, crowding, line of fire |
| Telegraphs | Every dangerous attack is readable |
| Aim error that closes over time | Avoids instant unfair hits |
| First-shot grace | Gives the player time to notice |
| Retreat and regroup | Makes enemies feel alive |
| Reactions | Hit reactions, suppression, morale |
| Difficulty through decisions | Change aggression, tokens and timing before adding health |

### Squads, stealth and bosses

| Type | Best practice | Verify |
|---|---|---|
| Squads | Encounter sets the objective, squad assigns roles and targets, individual picks cover and aim. Halo 3's [prioritised task tree](https://www.gamedeveloper.com/design/combat-evolved-the-encounter-design-of-halo-3) is a good default. Barks explain tactics | Roles stay filled as members die |
| Stealth | States: unaware, suspicious, searching, alerted, returning. Detection meter uses distance, light, stance and sound. Search starts at last known position | NPC never detects an unsensed player |
| Bosses | Authored phases on an FSM or tree, readable wind-ups, punish windows, arena awareness | Player bot can win |

## Living worlds

| System | Best practice | Module | Verify |
|---|---|---|---|
| **Crowds** | Animated instances, flow and ORCA near the player | `ai.crowd` | 10,000 agents within budget (target) |
| **Traffic** | Lane graph, spline movement far away, physics near | `ai.traffic` | No deadlock in a one-hour soak |
| **Schedules** | Time blocks: work, eat, sleep, travel | `ai.schedule` | NPCs reach required places on time |
| **Needs** | Decaying values fed into utility | `ai.utility` | No starvation in a long sim |
| **Smart objects** | Objects advertise actions, costs and animations | `gameplay.smartobjects` | Reservations prevent double use |
| **Factions** | Relationship matrix plus events | `gameplay.factions` | Standing changes persist in saves |
| **Reputation** | Witnessed actions spread with delay | `gameplay.reputation` | Unwitnessed crimes do not spread |
| **Population** | Spawn around the player, three LOD bands | `world.population` | Promotion keeps identity and goal |

**Smart objects are the highest-return life-sim pattern.** New content adds new behaviour without changing NPC code.

## Companions

**Rules:** never block the player, never spoil stealth, stay in view without crowding, help visibly, do not steal the win, stay out of the line of fire, and catch up off-screen during traversal.

[Ellie's buddy AI talk](https://www.gamedeveloper.com/design/video-ellie-s-buddy-ai-in-i-the-last-of-us-i-) is a useful reference.

## Directors and pacing

A director manages the experience, not individual NPC decisions.

```text
measure stress -> choose phase: build, peak, relax -> spawn, hint, adjust, or wait
```

**Rules:** read player-state metrics (health, damage, ammo, deaths, time since action), enforce relax periods, spawn out of sight, keep rubber-banding subtle, seed and log every decision, and never hand NPCs hidden facts by default.

Verify with bots that intensity follows a build, peak and relax curve across seeds.

## Dialogue and barks

Quest dialogue uses authored graphs in `narrative`. Reactive lines use a rule-based bark system with criteria, weights, cooldowns and per-line memory. Critical callouts interrupt chatter, and every line has a localisation ID.

## LLM NPCs, safely

**An LLM can voice an NPC. Game rules stay in the game.** `ai.llm` is optional.

| Rule | Shape |
|---|---|
| **Never in a deterministic path** | Outputs never affect rollback, lockstep or replay state |
| **Always async** | The game continues while a response is pending |
| **Authored fallback** | Timeout, offline or refusal uses a written line |
| **Structured actions only** | Model selects from a validated schema, never free-form commands |
| **Treat player text as untrusted** | [Prompt injection is a known risk](https://dev.to/exoa/shipping-runtime-ai-in-unity-build-guardrails-before-prompts-279g) |
| **Filter before and after** | [Input and output moderation](https://preview.aclanthology.org/author-page-you-zhang-rochester/2025.inlg-demos.1.pdf), suited to the age rating |
| **Ground in allowed facts** | Pass only what this NPC may know, never hidden server state |
| **Server decides outcomes** | Rewards, quests and prices are never granted by generated text |
| **Budget every player** | Rate limits, caching, small or local models. [Cost scales with players](https://arxiv.org/pdf/2611.05427) |
| **Disclose and log** | Provenance for store rules, private logs by consent |
| **Works with it switched off** | The game remains complete |

## AI LOD and time-slicing

| Band | Sense | Decide | Move | Animate |
|---|---|---|---|---|
| Near, visible | Full | 5–10 Hz | Full | Full |
| Near, hidden | Reduced | 2–5 Hz | Simple | Reduced |
| Mid | Events | 0.5–1 Hz | Splines | Crowd or none |
| Far | None | Schedule | Teleport along schedule | None |
| Statistical | None | Aggregate per district | None | None |

**Rules:** promotion preserves identity and goal, updates are staggered, critical events wake sleeping brains, perception and scoring run in batches, and going over budget lowers update rates rather than stalling.

**Starting budget:** 2 ms per 16.6 ms frame for AI on a desktop client, measured at p99. On a server, set it from the tick budget and target NPC count.

## Client, server and determinism

| Concern | Default |
|---|---|
| Authority | Online NPC decisions run on the server |
| Client | Interpolates and presents NPCs |
| Visibility | NPC data follows [visibility classes](35-client-server-models.md#every-field-has-a-visibility-class) |
| Hidden plans | `server` fields, never replicated |
| Cosmetic ambient NPCs | May run client-only if they never affect gameplay |
| Lockstep and rollback | AI uses World RNG and clock, with stable iteration |
| Rollback cost | Keep AI state small, or avoid re-running expensive planning |
| Async results | Applied at a declared tick in deterministic worlds |
| Replay | Records inputs and seeds, and optional decision traces |

## Debugging for agents

Planned commands: `ag ai explain <entity> --tick N` (goal, alternatives, scores, winner), `ag ai trace`, `ag ai beliefs` (known vs. true), `ag ai nav`, `ag ai budget`, and `ag capture --overlay ai` (cones, paths, cover and intent on images).

## Tests every NPC system should have

| Check | Passes when |
|---|---|
| Decision unit test | Given facts, picks expected goal |
| Perception fairness | NPC cannot react to a target it cannot sense |
| No twitching | Goal switches stay under a limit |
| Navigation sweep | Agents reach sampled points, with no permanent stuck state |
| Combat sanity | NPC attacks, takes cover, retreats and does not shoot allies |
| Encounter winnable | Player bot wins at target rate per difficulty |
| Encounter challenging | Player bot sometimes loses at higher skill |
| Pacing | Intensity curve stays in range across seeds |
| Soak | No leak, deadlock or growing queue |
| LOD round-trip | Promote and demote without losing identity |
| Budget | p99 AI cost stays within budget at max NPC count |
| Determinism | Same seed gives identical decisions |
| Network | Client packet audit contains no hidden AI data |
| LLM failure | Timeout, refusal and offline all use fallbacks |

## Build order for any game

1. Write the target NPC moments, then pick the simplest decision model.
2. Build one NPC with idle, sense, act, telegraph, animation and barks.
3. Add a bot test, then variation through data.
4. Add group behaviour only if the game needs it.
5. Add LOD and measure the worst scene.
6. Tune with thousands of headless runs, then have a human judge the feel.
