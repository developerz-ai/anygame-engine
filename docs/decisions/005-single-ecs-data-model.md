# 005 — One archetype ECS is the only object model

Status: accepted
Date: 2026-11-21

## Context
Engines with two object models end up maintaining a bridge between them.

## Decision
An archetype ECS with first-class relationships. The scene tree is a view over it.

## Alternatives
- Object graph with virtual update: why not, it cannot reach high entity counts.
- ECS beside an actor model: why not, this is the two-model problem.

## Consequences
Convenience wrappers may exist on top, but never a second store of state.
