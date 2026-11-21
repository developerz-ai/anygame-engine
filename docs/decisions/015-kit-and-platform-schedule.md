# 015 — Every kit and platform has a scheduled phase

Status: accepted
Date: 2026-11-21

## Context
Seven kits, plus web, XR, consoles and several gameplay primitives had no phase.

## Decision
Use the schedule in [primitives by phase](../build/primitives-by-phase.md#kit-and-platform-schedule). Add `kit.moba` on the `orders` profile.

## Alternatives
- Build every kit early: why not, each needs a proven lower layer.
- Leave them unscheduled: why not, they would never land.

## Consequences
A kit lands in the first phase that supplies all its modules, with a complete sample game.
