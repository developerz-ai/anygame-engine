# 013 — Tools ship separately and never in the game binary

Status: accepted
Date: 2026-11-21

## Context
The blueprint said both that shipped binaries contain no tooling and that games can include editor tooling.

## Decision
No core editor. The live viewer and `ag` are separate executables. A game may ship them as an optional modding download.

## Alternatives
- Compile tooling into the runtime: why not, it costs every player.
- Forbid shipping tools: why not, modding depends on them.

## Consequences
Docs say live viewer or tooling, not editor. In-game map tools are game packages.
