# 008 — Repo tooling is Bun and TypeScript

Status: accepted
Date: 2026-11-21

## Context
Scripts should be pleasant, fast and shared with the rest of the organisation's tooling.

## Decision
Bun + TypeScript in `scripts/`, with reusable code in `scripts/lib/`.

## Alternatives
- Python: why not, weaker reuse and a second tooling style.
- C++ tools for everything: why not, slow to iterate for glue. The `ag` CLI is a separate decision.

## Consequences
Contributors need Bun to run the gate.
