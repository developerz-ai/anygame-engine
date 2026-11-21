# 💬 26. One prompt to a game

**The target experience: a human opens a coding agent and says "build a game like NFS with AnyGame". The agent already has the know-how to start, and returns something playable.**

Planned design as of 2026-11. Nothing here runs yet.

## What the agent has ready

| Know-how | Answers | Source |
|---|---|---|
| Genre playbooks | What makes this genre work, what to build first, common failures | `playbooks/<genre>.md` |
| Kits | Which modules and template to start from | [Kits](10-kits.md) |
| Blocks | What already exists | [Primitives](23-primitives.md), `ag find` |
| Tricks | How this problem was solved before | [Thirty years of tricks](20-tricks-30-years.md) |
| Layout | Where everything goes | [Project organisation](24-project-organization.md) |
| Process | What happens next, through to release | [Idea to distribution](25-idea-to-distribution.md) |
| Proof | How to know it works | [Agent dev cycle](18-agent-dev-cycle.md) |

The engine ships an agent skill and an MCP server, so the agent finds all of this from one entry point: `llms.txt`.

## "Like X" means the genre, never a copy

**The agent builds an original game with similar mechanics.** "Like NFS" means an arcade street racer: speed, drifting, police chases, car upgrades, an open city.

| Take from the reference | Make original |
|---|---|
| Genre and mechanics | Title and branding |
| Pacing and game feel goals | Characters and story |
| Technical approach | Cars, art, logos, UI look |
| Player expectations | Music, maps, levels |

Real car brands, licensed music and existing characters are left out unless the developer holds the rights.

## A playbook is deep know-how wired to primitives

**Every piece of advice names the block that implements it.** The agent should never read "add drift" and then write a drift system from scratch.

| Playbook section | Contents |
|---|---|
| Genre DNA | What players expect, what makes it feel right, what kills it |
| Core loops | Second-to-second, minute-to-minute, session-to-session |
| Block map | Each feature mapped to its primitive, module, kit and config |
| Build order | The first playable, then each next slice, with done checks |
| Tuning | Starting values and safe ranges, as data |
| Feel checklist | Each sensation, the trick behind it, and how a bot measures it |
| Tech traps | Known failures, symptoms and fixes |
| Budgets | Frame, memory, network and content targets per platform |
| Online | Which netcode fits, and what the server must own |
| Content plan | Assets needed, and how to generate or source them |
| Scope ladder | Jam, indie, large: what to include at each size |
| Test plan | Bots, replays and balance sims for this genre |

Example block-map rows, illustrative until the blocks exist:

| Feature | Use | Tune | Verify |
|---|---|---|---|
| Drift | `physics.vehicle` arcade model | `content/data/handling/*` | Bot holds a drift through a test corner |
| Police chase | `ai.director`, `ai.nav` traffic lanes | Heat levels as data | Pursuit escalates and can be escaped |
| Open city | `world.stream`, `world.population` | Streaming radius by speed | Scripted route has no frame over budget |
| Online race | `net.replication`, `matchmaking` | Tick and smoothing | Bots race under simulated 80 ms latency |

The agent loads only the sections it needs, through `ag playbook <genre> [section] --json`, so a large library never floods its context.

## How the agent responds

1. **Read the idea.** Pick sensible defaults and write them down as assumptions.
2. **Ask only what changes the build.** Usually one short message, or none.
3. **Write the pitch and scope** in `docs/idea/`.
4. **Load a playbook and kit.**
5. **Build the smallest playable loop** and prove it with a bot.
6. **Show the human** a build, video or screenshots.
7. **Take direction, then grow it** slice by slice.

## Worked example: an arcade street racer

> Human: bro build a game like NFS with anygame engine

| Step | What the agent does |
|---|---|
| Assumptions | Original title, single-player first, desktop, arcade handling, one night-time city district |
| Setup | `ag new neon-apex --kit racing`, adds `kit.openworld` blocks |
| Core loop | Drive, drift, earn, upgrade, race again |
| Blocks reused | Arcade vehicle, sub-stepped physics, chase camera, road graph, traffic, checkpoints, ghosts, HUD, garage UI |
| Tricks applied | Speed FOV, camera lag, drift assist, boost feedback, catch-up tuning, streaming along the road |
| Assets | City and original cars from code with [ts23d](19-companion-tools.md), if the developer wants it |
| First proof | Bot completes a lap, frame budget holds, handling metrics in range, video captured |
| Show human | "Here is a playable lap. Tighter drift, or police chases next?" |
| Grow | Police AI, career, garage, more districts, online races through `net.replication` |
| Ship | Website, trailer and store build through [idea to distribution](25-idea-to-distribution.md), with human approval to publish |

## What one prompt can honestly deliver

| Prompt gets | Takes more |
|---|---|
| A playable original slice of the genre | Hundreds of hours of hand-tuned content |
| Working systems, tests and a clear plan | Art direction only a person can judge |
| A base that scales without a rewrite | Fun, which needs human play and feedback |
| Online, backend and release paths ready | AAA scale, which still costs content, compute and time |

The human keeps steering: **ideas and taste come from them, and the building comes from the agent.**

## What must exist for this to work

- A playbook per genre, starting with each kit.
- An `anygame` agent skill and MCP server, installed by one command.
- `ag new` that produces a game that runs and passes its tests on first try.
- Eval: run this prompt per kit in CI with a real coding agent, and score whether a bot can finish the resulting game.
