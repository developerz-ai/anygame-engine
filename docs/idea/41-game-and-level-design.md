# 🎯 41. Game and level design

**Design the player's experience first, then build the smallest thing that proves it.** A technically perfect game with a weak loop is still a weak game. Agents can measure many things, but the developer owns taste and fun.

Guidance as of 2026-11-21. Linked claims were checked from search extracts. Numbers without a link are starting points recalled from common practice and unverified, so tune them by playtest. Everything here is a default a game can ignore ([rule 8](01-thesis.md#design-rules)). Named games are references only, and a game built with AnyGame stays original.

Related: [kits](10-kits.md), [tricks](20-tricks-30-years.md), [idea to distribution](25-idea-to-distribution.md), [quality bar](32-quality-bar.md).

## What a machine can check, and what it cannot

| Machine can check | Needs human judgement |
|---|---|
| The game can be finished | Whether finishing it felt good |
| Time to first action, first win, first failure | Whether the opening is exciting |
| Win rates, pick rates, strategy diversity | Whether a matchup feels fair |
| Softlocks, unreachable goals, dead ends | Whether exploration feels rewarding |
| Difficulty curve from bot skill levels | Whether challenge feels earned |
| Economy inflation and sinks | Whether rewards feel meaningful |
| Text clarity, tutorial coverage | Tone, humour, emotion, story quality |
| Regression against the last build | **Is it fun? Is it the game the developer wanted?** |

**Rule for agents:** report measurements as evidence. Never say a game is fun because its metrics pass.

## Start with the core loop

Write the loop in one sentence before building anything: **the player does X to get Y so they can do X better or differently.**

| Timescale | Question | Example shape |
|---|---|---|
| Seconds | What does the player do constantly? | Aim, jump, drift, place, choose |
| Minutes | What goal does that action serve? | Clear a room, finish a lap, win a fight |
| Session | Why play one more? | New unlock, next level, a better run |
| Long term | Why come back? | Mastery, story, collection, community |

| Check | Pass condition |
|---|---|
| Second-to-second action | Satisfying in an empty test room |
| Clear goal | A new player can state what to do next |
| Feedback | Every action has a visible and audible response |
| Progress | The player can tell they got better or further |
| Failure | Understandable, quick to retry, and teaches something |

**Prototype order:** verb → feel → goal → failure → reward → content. Do not build content for an unproven verb.

## Why people play

[Self-determination research](https://link.springer.com/content/pdf/10.1007%2Fs11031-006-9051-8.pdf) found that autonomy, competence and relatedness each predicted game enjoyment and future play. Treat it as a design lens, not a scoring formula.

| Need | Design for it | Avoid |
|---|---|---|
| **Autonomy** | Real choices, multiple builds and routes | Illusory choices, forced grind |
| **Competence** | Clear goals, fair challenge, visible mastery | Hidden rules, random punishment |
| **Relatedness** | Co-op, characters, community | Forced social obligations |

## Meaningful choices

A choice is meaningful when the player understands it, its options differ, and its result matters.

| Test | Fail looks like |
|---|---|
| Are outcomes foreseeable enough? | Pure guess, then punishment |
| Is there a trade-off? | One option is always best |
| Does it change later play? | Same result either way |
| Can the player learn from it? | The cause of the result is hidden |

## Difficulty and flow

Flow studies often find [too little challenge causes boredom and too much causes frustration](https://link.springer.com/article/10.3758/s13428-023-02251-w), though [the exact shape is debated](https://peerj.com/articles/10520). A [self-selected difficulty may also matter](https://peerj.com/articles/10520), so give players control.

| Practice | How |
|---|---|
| Teach, test, twist | Introduce an idea safely, test it, then combine it |
| One new thing at a time | Do not stack new mechanics with a difficulty spike |
| Saw-tooth curve | Harder stretch, then a release, then harder again |
| Fair failure | The player can see why they lost |
| Forgiving input | Coyote time, buffering and generous hitboxes ([tricks](20-tricks-30-years.md)) |
| Player-chosen difficulty | Presets and individual assists |
| Dynamic difficulty | Subtle, optional in competitive contexts, and never pay-gated |

**Machine proxies:** per-level retry count, completion by bot skill tier, damage-source concentration, time-to-failure and quit points.

## Onboarding: teach through play

| Rule | Shape |
|---|---|
| **Play within the first minute** | Skip logos and long intros on repeat launches |
| **Teach when needed** | Show a prompt at the moment the verb matters |
| **Do before reading** | Safe space to try it, then a short prompt |
| **Prove it was learned** | Gate progress on doing it, not dismissing text |
| **Show the current input device** | Prompts match keyboard, controller or touch |
| **Let experts skip** | Tutorials can be skipped and replayed |
| **Never front-load every system** | Reveal depth over hours |

## Pacing and intensity

Plan intensity like music: build, peak, rest.

| Beat | Purpose |
|---|---|
| Quiet | Recover, explore, read the world |
| Build-up | Create anticipation |
| Peak | Boss, chase, final wave |
| Release | Reward and breathing room |
| Twist | Change mechanic, place or objective |

Graph expected intensity across the game, then compare with telemetry from bots and playtests. Long flat stretches and back-to-back peaks are warnings.

## Risk and reward

| Pattern | Example shape |
|---|---|
| Push your luck | Keep going for more, or bank it |
| Skill shot | Harder route, bigger payoff |
| Optional challenge | Side area with a stronger enemy |
| Resource spend | Use the item now or save it |

Reward should scale with risk, and players should be able to see both before committing.

## Balance methods

| Method | Use for | Limit |
|---|---|---|
| Spreadsheet model | Damage curves, costs, progression | Ignores player behaviour |
| Monte Carlo simulation | Drops, crits, economy over time | Depends on assumptions |
| Bot sweeps | [Finding weak actions and rewards at scale](https://arxiv.org/pdf/1811.06962) | Bots do not play like people |
| Planning agents by skill | [Testing designs across skill levels](https://arxiv.org/pdf/1908.01423) | Costly in deep games |
| Metagame prediction | [Estimating the effect of a balance patch](https://arxiv.org/pdf/2006.04419) | Depends on the definition of balance |
| LLM agents on rules | [Early rule balance](https://arxiv.org/html/2602.06232v1) | Proof of concept, a supplement to humans |
| Live telemetry | Real behaviour after release | Only with consent and privacy rules |

### Dominant strategy check

1. Generate many strategies, not one bot.
2. Run a round-robin tournament across seeds.
3. Flag any strategy that beats nearly all others.
4. Flag options nobody picks.
5. Check rock-paper-scissors relationships.
6. Change one variable, then re-run.

**Balance rules:** keep numbers in data, version each balance pass, compare against a baseline, and let intentional asymmetry stand when the designer chose it.

## Economy design

| Rule | Why |
|---|---|
| Every **source** has a **sink** | Prevents inflation |
| Model the economy before building it | Find runaway loops cheaply |
| Separate earned and paid currency, if any | Clear value and legal handling |
| Show real prices clearly | Trust |
| Server owns online economy | [Transactions, audit ledger](09-online.md) |

**Machine proxies:** currency in circulation over time, median time per unlock, wealth concentration, unspendable balances.

## Retention without dark patterns

**Players should return because the game is good, not because it manipulates them.** Research defines [dark game design patterns](https://research.chalmers.se/en/publication/177148) as ones intentionally used to cause negative player experiences, across temporal, monetary and social categories. The kits, blocks and playbooks will not generate them.

| Do | Do not |
|---|---|
| New content, mastery, story, community | Fear of missing out by design |
| Respect session length, with clean stopping points | Punish players for leaving |
| Show the exact price and what it buys | Confusing currencies that hide cost |
| Offer an easy way to cancel or refund | Friction designed to prevent cancelling |
| Disclose random reward odds before purchase | Hidden odds, or paying for a chance aimed at minors |
| Fair matchmaking | Tuning matches to drive purchases |
| Cosmetic or clearly stated monetisation | Pay-to-win presented as fair |
| Clear parental controls | Deceptive prompts aimed at children |

App stores have required [loot box odds disclosure](https://www.fenwick.com/insights/publications/apple-now-requires-disclosure-of-loot-box-odds), and regulators have [acted against manipulative purchase flows](https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf). Check current rules per store and country.

## Replayability

| Source | Technique |
|---|---|
| Mastery | High skill ceiling, leaderboards, time trials |
| Variety | Seeded generation, build diversity, modifiers |
| Choice | Branching paths and consequences |
| People | Co-op, competition, shared seeds |
| Creation | Mods, custom maps, level tools |

## Level design

| Principle | Practice |
|---|---|
| **Landmarks** | [Unique places that help players orient themselves](https://unity.com/blog/level-design-basics) |
| **Sightlines** | Show the goal early, control what is visible from each spot |
| **Guidance** | Light, colour, motion, composition and sound before UI markers |
| **Reward and denial** | Show a goal before offering the route to it |
| **Gating** | [Locks and keys, literal or figurative](https://gamedeveloper.com/design/level-design-tricks-of-the-trade) |
| **Critical path** | The shortest route to finish, always readable |
| **Golden path** | The intended best experience |
| **Optional space** | Rewards curiosity without blocking progress |
| **Loops** | Return the player to known places via shortcuts |
| **Blockout first** | Prove layout with simple geometry before art |

### Encounter design

| Element | Questions |
|---|---|
| Arena | Is there cover, height, routes and room to move? |
| Enemy mix | Do roles force different responses? |
| Telegraphing | Can the player read each threat before it hits? |
| Escalation | Do waves add a new problem? |
| Escape | Can the player reposition? |
| Resources | Is health or ammo placed for recovery? |
| Reset | Is retry fast, and close to the failure? |

### Multiplayer map fairness

Starting checks, not universal laws:

| Check | Method |
|---|---|
| Side balance | Win rate per side across many bot and human matches |
| Spawn safety | No line of sight into spawn, no spawn-kill loops |
| Travel time | Equal time to key objectives, or a deliberate trade-off |
| Chokepoints | At least one alternative route |
| Sightlines | Long lanes are counterable |
| Objective access | Measured contest time per team |

**Level lint:** reachable goals, no out-of-bounds holes, navigable by bots, no dead-end softlock, checkpoint spacing, collectible reachability.

## Narrative design

| Rule | Why |
|---|---|
| Story and mechanics should agree | Conflict breaks immersion |
| Show through the world | Environmental storytelling costs no player time |
| Keep exposition interruptible | Players can skip and revisit |
| Give the player agency, or be honest about linear story | False choice damages trust |
| Track state in data | Testable branches and saves |
| Write for localisation from line one | [Localisation](42-ux-accessibility-localization.md) |

**Machine checks:** every branch reachable, no missing flags, no dead-end dialogue, no unlocalised lines.

## Scope cutting

| Priority | Keep or cut |
|---|---|
| Core verb and loop | Never cut |
| Systems that strengthen the loop | Keep, simplify if needed |
| Content variety | Fewer, better pieces |
| Systems that exist because genre peers have them | Cut first |
| Multiplayer, open world, crafting, procedural story | Add only if the game needs them |

A complete small game beats an unfinished large one. Keep a written "not building" list.

## Playtesting

| Rule | Why |
|---|---|
| [Do not explain or teach during the session](https://www.cs.cornell.edu/courses/cs3152/2021sp/lessons/lesson23/slides-23.pdf) | Your explanation will not ship with the game |
| Watch what they do | Behaviour beats opinion |
| Ask open questions | "What was your goal there?" |
| [Avoid "Was it fun?"](https://wireframe.raspberrypi.com/articles/how-to-playtest-your-game-on-a-budget) | It yields little useful data |
| Use [think-aloud with care](https://gamesuserresearch.com/games-user-research-methods/) | It can change how people play |
| Test early, in small rounds | A few players expose the biggest problems |
| Prefer strangers from the target audience | Friends are kind |

## From feedback to change

An agent handles feedback in this order:

1. **Collect** notes, recordings, telemetry and replays.
2. **Separate** the problem from the player's suggested fix.
3. **Cluster** repeated issues.
4. **Find evidence** in replays and metrics.
5. **Rank** by severity, frequency and effect on the core loop.
6. **Propose** the smallest change, with a measurable expectation.
7. **Test** with bots, then a new human playtest.
8. **Record** the result and any design decision.

The agent asks the developer when feedback conflicts with the game's vision.
