# Phase 0.08: `ag` CLI

> Phase: [Phase 0](phase-0-kernel.md). Depends on: [0.03](phase-0-03-registry-ports.md) to [0.07](phase-0-07-clocks-snapshots.md).

## Goal

An agent can create, build, run, inspect and test a headless project using only `ag`, with structured output.

`ag` is an interpreted Bun + TypeScript wrapper with no compile step ([decision 017](../decisions/017-ag-cli-bun-wrapper.md)). Engine work runs in the native `ag-host`.

## Design source

- [AI-first](../idea/12-ai-first.md): commands and structured errors.
- [Agent dev cycle](../idea/18-agent-dev-cycle.md): loop, targets, output rules.
- [Project organisation](../idea/24-project-organization.md): layout `ag new` creates.
- [Architecture map](../idea/33-architecture-map.md): tools sit beside the runtime.

## Files to create or change

- `tools/ag/bin/ag.ts`: entry point, loads only the requested command.
- `tools/ag/src/commands/{new,build,run,describe,query,test}.ts`.
- `tools/ag/src/{output,errors,manifest,protocol}.ts`, reusing `scripts/lib/` where it fits.
- `tools/ag-host/src/main.cpp`: small native host over public kernel APIs.
- `docs/schemas/ag-host.v1.json`: versioned JSON-lines protocol.
- `tools/ag/templates/empty/`: smallest headless project.
- `tools/ag/src/**/*.test.ts`: CLI tests beside the source.
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

1. Define exit codes, the JSON error schema and the `ag-host` protocol. Measure startup. verify: `ag --help` stays under its 50 ms target in CI, and importing it loads no command module.
2. Define the JSON error fixtures. verify: a test validates every error fixture against `docs/schemas/ag-error.v1.json`.
3. Parse `anygame.toml` with Bun's TOML parser and report errors with line numbers. verify: an invalid manifest returns a structured error.
4. Implement `ag new`. verify: in an empty directory, `ag new demo && cd demo && ag build && ag test --headless` exits 0.
5. Implement `ag run --headless`. verify: `ag run --headless --ticks 600 --json` run twice prints the same state hash.
6. Implement `ag describe` from `schema_to_json` through `ag-host`. verify: output validates against `ag-describe.v1.json` and lists every kernel component and command.
7. Implement `ag query` over snapshots through `ag-host`. verify: a query at tick 120 returns the value the test wrote at that tick.
8. Implement `ag test` with bounded output. A failure prints seed, tick, entity, system and replay command. verify: a deliberately failing fixture prints all five and exits non-zero.
9. Keep tools out of the runtime. verify: a symbol check finds no `ag-host` symbols in the kernel library, and a shipped build contains no Bun or TypeScript.
10. Add the end-to-end CI job on Linux, Windows and macOS. verify: it runs step 4 from a clean checkout on all three.
11. Run an agent-only proof. verify: a scripted session using only `ag` commands creates a project, adds a component, passes its test and queries its value.

## Must not happen

- No GUI dependency.
- No command with output only a human can parse.
- No unbounded log in default output.
- No private kernel API used by `ag` or `ag-host`.
- No compile step for `ag`, and no heavy dependency loaded at startup.
- No network access or telemetry.

## Done when

- **Owns exit check:** "`ag describe` emits the full schema as JSON."
- **Owns exit check:** "All checks pass in CI on Windows, Linux and macOS."
- Every Phase 0 slice is marked complete in [status.yml](status.yml), with evidence.
