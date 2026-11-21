# 🤝 31. No regrets

**A developer who builds on AnyGame should never regret it, including on the day they decide to leave.** Engines earn regret through surprise fees, lock-in, breaking upgrades, abandoned features and walls found late. This page turns each one into a commitment we can be held to.

Proposed as of 2026-11. Items marked **design goal** need code and tests before they are true.

## Regrets, and how we prevent them

| The regret | Our answer | Proof |
|---|---|---|
| "They changed the price or terms" | MIT license, no royalty, no runtime fee, no seat fee | [LICENSE](../../LICENSE) |
| "We are locked in" | Open source formats, adapters, code stays yours | `ag export` (design goal) |
| "The upgrade broke our game" | Pinned versions, semver, `ag migrate`, two-release deprecation | ABI and migration tests (design goal) |
| "Our saves stopped loading" | Versioned schemas, permanent migrations | Stored fixtures in CI (design goal) |
| "We hit a wall and had to fork" | Every part is replaceable, missing hooks are engine bugs | Conformance suites (design goal) |
| "It got slow at scale, too late to fix" | Budgets from day one, data-oriented core | `ag profile --budget` (design goal) |
| "It would not ship on our platform" | Every target in CI from the phase it arrives | Device farm (design goal) |
| "They abandoned it" | Source is yours, builds from a lockfile, no required service | Offline build test (design goal) |
| "The feature was only a demo" | Each block states its maturity, each kit ships a real game | Maturity labels |
| "It spied on our players" | No telemetry by default, nothing leaves without approval | Network test on an empty game (design goal) |
| "It forced a logo on our game" | No splash screen, no branding requirement | MIT terms |
| "A service shut down and took our game with it" | No required cloud, account or license server. Runs offline | Offline build test (design goal) |
| "AI wrote code we could not trust" | Tests, sanitizers, replays and readable text assets | `ag verify` (design goal) |
| "The recommendation served them, not us" | Companions are optional, and partnerships are disclosed | [Companion tools](19-companion-tools.md) |

## Our promises

1. **Your game is yours.** Code, content, data, players and revenue.
2. **No toll.** No royalties, runtime fees or mandatory services.
3. **No trap.** You can leave at any time and take everything with you.
4. **No surprises.** Breaking changes are announced, versioned and come with a migration.
5. **No forced upgrades.** A shipped game can stay on its version forever.
6. **No hidden behaviour.** No telemetry, ads, or calls home unless you add them.
7. **No overclaiming.** Each block says what works, what does not, and how to check.

MIT applies irrevocably to each version already released. Future versions should stay permissive too.

## Tell people when not to use us

Honest fit prevents the worst regret, which is finding out two years in.

| Do not pick AnyGame today if | Because |
|---|---|
| You need to ship now | It is at the design stage, with no engine code yet |
| You need a visual editor for artists | The core is code-first. Use a community tool, or another engine |
| You rely on a large existing asset store | That ecosystem does not exist here yet |
| You need console support immediately | Platform access requires agreements and private packages |
| Your team wants no C++ or Lua anywhere | Native and script tiers are both C++ and Lua by default |

Update this table as each phase ships.

## Maturity labels

Every block carries one, visible in `ag describe`, so an agent never builds on something weaker than it looks.

| Label | Meaning |
|---|---|
| `planned` | Documented, does not exist |
| `experimental` | Works in a sample and may change |
| `beta` | Used by a real game, API settling |
| `stable` | Semver, conformance suite, shipped in a game |
| `deprecated` | Has a replacement and a migration |

## How we keep this honest

- A promise that has a test gets that test in CI.
- A regression against this page is a release blocker.
- Known gaps are published, not hidden.
- Before any change to licensing, pricing or data handling, this page is updated first and in public.
