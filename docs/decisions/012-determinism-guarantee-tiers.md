# 012 — Determinism is promised in tiers

Status: accepted
Date: 2026-11-21

## Context
Bit-identical results across compilers and CPUs are hard with floating point.

## Decision
Tier 1: same binary and platform replays exactly. Tier 2: cross-platform replay, only with fixed-point or software-float maths. A world declares its tier.

## Alternatives
- Promise cross-platform for all floats: why not, compilers and CPUs make it unreliable.
- No determinism guarantee: why not, replay, rollback and lockstep depend on it.

## Consequences
Cross-platform lockstep kits accept the cost of deterministic maths.
