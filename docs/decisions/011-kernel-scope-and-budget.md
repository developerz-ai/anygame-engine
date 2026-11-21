# 011 — The kernel has six parts and a runtime-only budget

Status: accepted
Date: 2026-11-21

## Context
The blueprint listed the kernel's parts two different ways and did not say what its 30k-line budget covers.

## Decision
Memory, jobs, data model with snapshots, reflection, registry and time. The budget covers the shipped runtime kernel. `ag` and the schema generator have their own budgets.

## Alternatives
- Count tools in the kernel budget: why not, tools never ship in a game.
- Make snapshots a module: why not, rollback, saves, replay and tests all depend on them.

## Consequences
A feature needing a seventh part must first justify why it cannot be a module.
