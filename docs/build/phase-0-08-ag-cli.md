# Phase 0.08: `ag` CLI

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.03](phase-0-03-registry-ports.md) to [0.07](phase-0-07-clocks-snapshots.md).

## Goal

An agent can create, build, run, inspect and test a headless project using only `ag`, with structured output.

`ASSUMPTION:` `ag` is C++23 in `tools/ag/`, so it shares the kernel's schema and protocol. [Decision 008](../decisions/008-bun-repo-tooling.md) leaves this open. Record the choice before starting.

## Design source

- [AI-first](../idea/12-ai-first.md): commands and structured errors.
- [Agent dev cycle](../idea/18-agent-dev-cycle.md): loop, targets, output rules.
- [Project organisation](../idea/24-project-organization.md): layout `ag new` creates.
- [Architecture map](../idea/33-architecture-map.md): tools sit beside the runtime.

## Files to create or change

- `tools/ag/src/main.cpp`, `tools/ag/src/commands/{new,build,run,describe,query,test}.cpp`.
- `tools/ag/src/{output,errors,manifest,protocol}.{h,cpp}`.
- `tools/ag/templates/empty/`: smallest headless project.
- `tools/ag/tests/`: CLI tests.
- `docs/schemas/ag-error.v1.json`, `docs/schemas/ag-describe.v1.json`.
- `.github/workflows/ci.yml`: the end-to-end job.

## Public interface sketch

| Command | Responsibility |
|---|---|
| `ag new <name>` | Scaffold a project that builds and passes first time |
| `ag build` | Configure and build through the project manifest |
| `ag run --headless --ticks N` | Run and print a final state hash |
| `ag describe [module] --format json` | Emit schema, commands, docs and examples |
| `ag query "<terms>" --at tick=N` | Read World state at a tick |
| `ag test [name] --headless` | Run gameplay tests |

Every command accepts `--json`. Errors carry `code`, `message`, `file`, `line`, `fix`, plus `entity`, `system` and `tick` when known.

## Steps

1. Define exit codes and the JSON error schema. verify: a test validates every error fixture against `docs/schemas/ag-error.v1.json`.
2. Parse `anygame.toml` with toml++ and report errors with line numbers. verify: an invalid manifest returns a structured error.
3. Implement `ag new`. verify: in an empty directory, `ag new demo && cd demo && ag build && ag test --headless` exits 0.
4. Implement `ag run --headless`. verify: `ag run --headless --ticks 600 --json` run twice prints the same state hash.
5. Implement `ag describe` from `schema_to_json`. verify: output validates against `ag-describe.v1.json` and lists every kernel component and command.
6. Implement `ag query` over snapshots. verify: a query at tick 120 returns the value the test wrote at that tick.
7. Implement `ag test` with bounded output. A failure prints seed, tick, entity, system and replay command. verify: a deliberately failing fixture prints all five and exits non-zero.
8. Keep tool code out of the runtime. verify: a symbol check finds no `tools/ag` symbols in the kernel library.
9. Add the end-to-end CI job on Linux, Windows and macOS. verify: it runs step 3 from a clean checkout on all three.
10. Run an agent-only proof. verify: a scripted session using only `ag` commands creates a project, adds a component, passes its test and queries its value.

## Must not happen

- No GUI dependency.
- No command with output only a human can parse.
- No unbounded log in default output.
- No private kernel API used by `ag`.
- No network access or telemetry.

## Done when

- **Owns exit check:** "`ag describe` emits the full schema as JSON."
- **Owns exit check:** "All checks pass in CI on Windows, Linux and macOS."
- Every Phase 0 slice is marked complete in [status.yml](status.yml), with evidence.
