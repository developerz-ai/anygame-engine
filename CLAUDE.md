# AnyGame Engine

Open-source, AI-first game engine: small C++23 kernel + replaceable modules. A game is a manifest choosing modules.

**Objective: we provide the building blocks that help developers and their agents build their game. We never stand between them and it.** New blocks must not change the architecture: a feature needing a kernel edit means a missing extension point. When a choice trades the developer's control for engine convenience, control wins.

**Humans bring ideas. Coding agents use the kernel and modules to build any 2D or 3D game.** Everything is pluggable, extendable and replaceable. Agents are the primary user of every API, error and command: `docs/idea/18-agent-dev-cycle.md`. Think `developerz-ai/ultimate` for games: same agent experience, but every part replaceable. AnyGame is a toolbox: the developer's agent picks what the game needs.

**Current stage: docs only.** No engine code, build, or tests exist. Do not scaffold code until asked.

C++: follow `docs/idea/29-cpp-decisions.md` first (decisions already made), then `docs/idea/16-cpp23-craft.md`. Allocators, libraries, profilers: `docs/idea/28-libraries-and-profilers.md`. Optional companion tools are recommended, never required: `docs/idea/19-companion-tools.md`.

## Response rules
- Lead with the answer or action. Terse. Paths and commands stay exact.
- Disagree when the docs or the user are wrong. State the correction.
- Report what was checked, and what was not.

## Layout
- `docs/idea/` — why and what. One blueprint section per file. Start at `docs/idea/README.md`.
- `docs/build/` — order of work. One phase per file, with exit checks. Start at `docs/build/README.md`.
- `docs/idea/23-primitives.md` — every client, game server and backend primitive. Phase mapping: `docs/build/primitives-by-phase.md`.
- `docs/idea/24-project-organization.md` — default layout for game projects and where each thing goes.
- `docs/idea/25-idea-to-distribution.md` — full game lifecycle: project management, release, stores, live ops.
- `docs/idea/26-one-prompt-to-game.md` — the target experience: a human says "build a game like X", the agent has the know-how. "Like X" means genre and mechanics, always an original game.
- `docs/idea/27-flywheel.md` — each game built improves the engine for the next. Opt-in only, nothing leaves a project without approval.
- `docs/build/open-questions.md` — unresolved conflicts. Check before relying on a contested point.
- `.claude/commands/` — `/planx` (plan a build slice), `/feature` (write and ship docs).

## Doc rules
- Lead with the rule. Fragments and tables over paragraphs.
- One topic per file. One owning doc per fact; elsewhere, link it.
- Idea docs hold design. Build docs hold sequence and checks. Do not copy between them.
- Every new doc gets a row in its folder `README.md`.
- Date load-bearing claims (`As of 2026-11`). Label targets as targets until CI measures them.
- Exit checks must be observable. No "fast", "robust", "correct" without a number or test.
- No secrets, private hostnames, or client names.

## Non-negotiable design rules
Full text: `docs/idea/01-thesis.md`.
- Everything above the kernel is a plugin. First-party modules get no private API.
- Adapter-based: engine defines ports, the manifest picks adapters, no vendor name above a port. See `docs/idea/05-extending.md`.
- Modules communicate through schema-described data, not inheritance.
- C ABI at module boundaries. Interfaces are append-only within a major version.
- Determinism is opt-in per world, designed in from day one.
- Headless and scriptable first. Every operation is a command or text file.
- Pay only for what you load.
- A needed fork is an engine bug: add the extension point.
- Help, then get out of the way. Kits, conventions, gates, budgets and recommendations are overridable defaults. Never block a game's design, stack or content choice.
- Small and fast by default. Every byte and millisecond must reach the player. Show the cost of each change: `docs/idea/21-small-and-fast.md`.
- Huge catalogue, tiny build. Give agents many ready blocks, and ship only what a game loads: `docs/idea/23-primitives.md`.
- Do not reinvent the wheel. Find, use, configure, compose, wrap, replace, then improve with evidence: `docs/idea/18-agent-dev-cycle.md`.
- No regrets. No fees, lock-in, forced upgrades, hidden telemetry or overclaiming: `docs/idea/31-no-regrets.md`.
- Platforms: Linux, Windows, macOS, Android, iPhone and browser (WASM + WebGPU). The kernel must compile to `wasm32`. OS differences stay behind ports: `docs/idea/30-platforms.md`.
- Future-ready. No hard-coded ceilings, version everything that persists, every dependency has an exit: `docs/idea/22-future-ready.md`.

## Hard boundaries
These bind this project's own code, samples and kits. They do not police games built with it.
- **Clean-room.** Never use, read, paste, or summarise leaked source or decompiled binaries. See `CONTRIBUTING.md`.
- **No game recreations.** Kits and samples are original. Named games are architecture references only: no names, characters, art, music, or levels.
- **No kernel-level anti-cheat.** Not shipped, integrated, or recommended.
- **Do not build:** a new programming language, VCS, physics solver from scratch, DCC tool, or second object model beside the ECS.

## Maintenance
Supported by developerz.ai. Policy: `.dz/maintainer/maintainer.yml`. No policy line relaxes a rule in this file.

## Git
- Branch from `main`. Conventional commits (`docs(build): ...`). One concern per PR.
- No git worktrees: work in this checkout.
