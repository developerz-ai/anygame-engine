# 🚢 25. From idea to distribution

**AnyGame covers the whole life of a game, not just the code.** A human brings an idea. Agents plan, build, test, package, publish and operate it, using the same blocks and commands at every stage.

Planned design as of 2026-11. Every stage, gate and tool is a default a game can skip or replace ([rule 8](01-thesis.md#design-rules)). A weekend jam may use three stages. A live service uses them all.

## The lifecycle

```text
idea -> concept -> prototype -> vertical slice -> production -> alpha -> beta
     -> release candidate -> certification -> launch -> live ops -> sunset
```

| Stage | Question it answers | Agent produces | Command | Exit check |
|---|---|---|---|---|
| Idea | What is it, and for whom? | Pitch, audience, comparable games | `ag plan idea` | Human approves the pitch |
| Concept | Is it worth building? | Core loop, scope, risks, budget, platforms | `ag plan concept` | Biggest risks named |
| Prototype | Is the core fun? | Smallest playable loop | `ag new`, `ag run` | Human plays it and says go or no-go |
| Vertical slice | Can we make it at final quality? | One polished level or match | `ag verify` | Budgets hold on the worst target |
| Production | Build all of it | Content and features, slice by slice | `ag plan slice` | Milestones pass |
| Alpha | Is everything in? | Feature-complete build | `ag release alpha` | Bots finish the game |
| Beta | Is it stable and balanced? | Content-complete build, playtests | `ag release beta` | No blockers, telemetry healthy |
| Release candidate | Can this exact build ship? | Signed build for each store | `ag release rc` | Full gate on every target |
| Certification | Will stores accept it? | Compliance report, ratings, metadata | `ag cert check` | Store checks pass |
| Launch | Get it to players | Published build, store pages | `ag publish` | **Human approves** |
| Live ops | Keep it healthy | Patches, events, balance, support | `ag patch`, `ag live` | Crash and retention targets |
| Sunset | End it well | Offline mode or server release, archive | `ag archive` | Players keep what they can |

## Project management primitives

Plain text in the repo, so any agent can read and update them. They sync to an issue tracker through an adapter.

| Primitive | What it is | Lives in |
|---|---|---|
| `pitch` | One page: what, who, why | `docs/idea/` |
| `gdd` | Living design, one topic per file | `docs/idea/` |
| `milestone` | Playable goal with exit checks | `docs/build/` |
| `slice` | One agent-sized unit, one PR | `docs/build/` |
| `status` | Machine-readable progress and ownership | `docs/build/status.yml` |
| `decision` | One-way-door choice and rejected options | `docs/decisions/` |
| `risk` | Threat, likelihood, mitigation, owner | `docs/build/risks.md` |
| `bug` | Failure with seed, input log and replay | Tracker + `tests/replays/` |
| `playtest` | Build, goal, findings, actions | `docs/playtests/` |
| `content-list` | Every asset needed, with status and source | `content/manifest` |
| `release` | Version, build IDs, changelog, approvals | `docs/releases/` |
| `budget` | Time, money and runtime budgets | `anygame.toml`, `docs/build/` |

`ag status` answers "where are we, what is blocked, what is next?" as text or JSON.

### How agents work the plan

- **Scope to what can ship.** Cut before adding, and keep an explicit "not building" list.
- **Always stay playable.** `main` runs at every commit.
- **Split work into independent slices** so several agents can run in parallel.
- **Each slice has observable done checks.**
- **Escalate decisions, not progress.** Ask the human about direction, money, legal matters and public actions.

## The full pipeline

| Discipline | What the engine provides | Suggested tools |
|---|---|---|
| Design | Specs, balance sims, economy models | `ag sim`, bots |
| Code | Blocks, generators, gates | Coding agents |
| Art | Import, cook, visual checks | [ts23d, Kubeez](19-companion-tools.md), DCC tools |
| Audio | Import, mixing, interactive music | Any source |
| Writing | Narrative scripts, l10n extraction | Ink-style scripts |
| QA | Bots, replays, fuzzing, soak and load tests | `ag test`, `ag verify` |
| Performance | Per-module budgets on real devices | `ag profile` |
| Localisation | String extraction, pseudo-locale, layout checks | Any translation provider |
| Accessibility | Checklist, remapping, subtitles, colour checks | `ag check accessibility` |
| Backend and ops | Deploy, scale, observe | Fleet adapters |
| Marketing | Trailers from replays, capture, store assets, press kit | `ag capture`, Kubeez |
| Community | Website, news, feedback intake | [Ultimate](19-companion-tools.md), community adapters |

## Distribution

The `distribute` port has one adapter per store. A game declares targets once, and `ag publish` handles the rest.

```toml
# anygame.toml: illustrative
[distribute]
targets = ["steam", "itch", "web", "android", "ios"]
```

| Channel | Adapter handles | Human must provide |
|---|---|---|
| Steam, Epic, GOG, itch.io | Depots, branches, metadata, achievements | Publisher account, fees, tax details |
| App Store, Google Play | Signing, bundles, on-demand content, listings | Developer accounts, signing identity |
| Consoles | Private packages, certification checks | Platform agreements under NDA |
| Web | WASM bundle, CDN deploy | Domain and hosting |
| Direct | Installers, updater, signed downloads | Code-signing certificate |
| Dedicated servers | Container images, regions, rollouts | Cloud account |

| Release step | Default |
|---|---|
| Versioning | Semver plus build ID, reproducible from the lockfile |
| Packaging | Per-platform cook, small content-addressed chunks |
| Signing | Keys stay in the CI secret store, never in the repo |
| Rollout | Internal, then beta branch, then staged percentage |
| Patch | Delta only, with save-compatibility test |
| Rollback | Previous build stays one command away |
| Changelog | Generated from merged work, edited for players |
| Crash watch | Launch dashboard, automatic halt on a crash spike |

## Compliance checklist

Requirements vary by store and country and change over time. `ag cert check` flags gaps, and a person remains responsible for confirming them.

- Age ratings (such as IARC, ESRB, PEGI).
- Privacy policy, data handling, deletion requests, children's data rules.
- Store disclosure of AI-generated content, using per-asset [provenance](12-ai-first.md#the-interface).
- Asset, font, music and third-party licence inventory.
- Loot box, purchase and refund rules.
- Accessibility requirements where they apply.

## What always needs a human

Agents prepare everything. A person approves actions that are public, costly or hard to undo:

- Publishing or unlisting a game.
- Spending money, including paid generation and cloud scale-up over a limit.
- Signing agreements, accepting store terms, tax and legal matters.
- Changing prices or live economy values.
- Deleting player data or shutting servers down.
