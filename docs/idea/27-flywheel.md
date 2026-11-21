# 🔁 27. The flywheel

**The more games are built with AnyGame, the better it gets for the next one.** Each game finds a missing block, a bad error or a slow path. Fixing it once helps every game after it.

Planned design as of 2026-11.

```text
more games -> more real problems found -> better blocks, errors, playbooks
    ^                                                  |
    +------ agents build better games, faster <--------+
```

## What each game can give back

All of it is optional and chosen by the developer.

| A game discovers | It becomes |
|---|---|
| A feature it had to build itself | A new block or package |
| A block that was too slow | A faster version, with the benchmark |
| A bug | A fix plus a regression test or replay |
| A confusing error | A better message and `fix:` command |
| A missing hook | A public extension point |
| An agent's wrong guess about an API | Clearer docs or a clearer name |
| A genre lesson | A playbook update |
| Good tuning values | Better kit defaults |
| A crash on a device | A compatibility fix and a test target |
| A new adapter | A package others can install |

## How it works

| Step | Mechanism |
|---|---|
| Notice | The agent records friction while it works: wrong guesses, workarounds, failed commands |
| Report | `ag feedback` drafts an issue with a minimal reproduction, for the developer to review |
| Contribute | `ag contribute <block>` extracts a change from the game's overlay into a pull request |
| Verify | Conformance suites, benchmarks and sample games must pass |
| Release | Semver, changelog, and `ag migrate` where needed |
| Benefit | `ag upgrade` brings improvements into every game that wants them |

## Keep games in the test suite

- **Each kit's sample game** runs in engine CI, so no change merges without a real user.
- **Opt-in game registry:** open-source games can ask to be built and tested against engine release candidates, as Rust's Crater does for crates.
- **One-prompt evals:** [build a game per kit](26-one-prompt-to-game.md) with a real agent and track what fails. Each failure points to the next improvement.
- **Measure the wheel:** time to first playable, agent retries per feature, share of a game built from existing blocks, frequency of each error.

## Trust rules

The flywheel must never cost a developer control ([rule 8](01-thesis.md#design-rules)).

- **Nothing leaves a project without explicit approval.** No hidden telemetry, and no default-on reporting.
- **Reports are reviewable first,** and contain no game source, assets, keys or player data unless the developer adds them.
- **A game owes the project nothing.** No required attribution, contribution or revenue share under the MIT license.
- **A game never waits on upstream.** It keeps its overlay until a fix lands.
- **Upgrades are the game's choice.** A shipped game can stay pinned forever.
- **Improvements stay general.** A change serving one game belongs in that game's package.
