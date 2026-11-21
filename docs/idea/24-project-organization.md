# 🗂️ 24. Organising a game project

**An agent should always know where a thing goes and where to find it.** `ag new` creates this layout, generators keep to it, and any agent can pick up any AnyGame project without a tour.

Planned design as of 2026-11. This is a suggested default: a game can rename, move or ignore any of it through its manifest ([rule 8](01-thesis.md#design-rules)).

## Default layout

```text
mygame/
├── anygame.toml          # manifest: modules, adapters, targets, budgets
├── anygame.lock          # exact versions, reproducible builds
├── CLAUDE.md             # the game's rules for agents
├── AGENTS.md -> CLAUDE.md
├── llms.txt              # link map for agents
├── docs/
│   ├── idea/             # what the game is: pitch, core loop, world, art direction
│   ├── build/            # order of work: milestones, slices, status
│   └── decisions/        # one-way-door choices, with rejected options
├── game/                 # shared client + server gameplay
│   ├── components/
│   ├── systems/
│   ├── events/
│   ├── commands/
│   ├── abilities/
│   ├── worlds/           # levels and matches as code
│   ├── policies/
│   └── features/         # one folder per larger feature
├── client/               # render, HUD, audio, camera, input: never on the server
│   ├── ui/
│   ├── render/
│   └── audio/
├── server/               # authority, sessions, services, jobs: never shipped to players
│   ├── services/
│   ├── jobs/
│   └── detectors/
├── schema/               # versioned schemas and migrations
├── content/              # authored source assets, text-first
│   ├── prefabs/
│   ├── data/             # balance, items, units
│   ├── narrative/
│   ├── l10n/
│   ├── meshes/
│   ├── textures/
│   └── audio/
├── packages/             # the game's own reusable blocks and overlays
├── tests/
│   ├── gameplay/
│   ├── replays/          # stored regressions: seed + input log
│   ├── golden/           # screenshots and state dumps
│   └── load/
├── tools/                # project scripts
└── out/                  # generated: builds, captures, reports. Not committed
```

## Where does it go?

| I am adding | Put it in |
|---|---|
| Data on an entity | `game/components/` |
| Logic over entities | `game/systems/` |
| Player intent | `game/commands/` |
| Rule for who may do what | `game/policies/` |
| A balance number | `content/data/`, never in code |
| A level or match | `game/worlds/` |
| HUD or menu | `client/ui/` |
| Anti-cheat or authoritative check | `server/` |
| Work outside the tick | `server/jobs/` |
| A change to saved data | `schema/` migration |
| A bug that was found | `tests/replays/`, then the fix |
| A choice that is hard to undo | `docs/decisions/` |
| Something reusable across games | `packages/` |
| A patched engine block | `packages/` overlay, never a fork |

`ag where "<thing>"` answers this from the project's actual layout.

## Organise by feature as it grows

| Project size | Shape |
|---|---|
| Jam or prototype | Flat `game/`, a few files |
| Small game | Folders by primitive, the default |
| Medium game | `game/features/<feature>/` holds its components, systems, data and tests |
| Large game | Each feature becomes a package with its own `AGENTS.md` and dependencies |
| Several games or a live service | Monorepo: `games/*` + shared `packages/*` + `services/*` |

Moving up a size is a generator step (`ag refactor feature <name>`), so structure is added when needed, not upfront.

## Keeping a project agent-friendly

| Habit | Why |
|---|---|
| Small files, one concept each | Fits in context, and parallel agents do not collide |
| One entity per file for world data | Clean diffs and merges |
| A feature folder has an `AGENTS.md` once it is non-trivial | Purpose, invariants and how to test, loaded only when relevant |
| Constants live in data | Tuning needs no rebuild |
| Decisions are written down with rejected options | The next agent does not re-argue them |
| Plans are split into independent slices | Several agents can work at once |
| Every feature has a headless test | "Done" is checkable |
| Generated output stays in `out/` | Agents never edit or read build noise |
| Dependencies point one way: `client`/`server` → `game` → engine | Server builds stay free of client code |

## From idea to organised project

1. `ag new mygame --kit <kit>` scaffolds everything above.
2. The agent turns the human's idea into `docs/idea/`.
3. It splits the work into small playable slices in `docs/build/`.
4. It builds slice by slice, recording hard choices in `docs/decisions/`.

`ag doctor` reports layout drift, misplaced code and missing tests as advice. It never blocks a build unless the game opts in.
