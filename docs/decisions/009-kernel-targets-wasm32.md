# 009 — The kernel compiles to wasm32 from Phase 0

Status: proposed
Date: 2026-11-21

## Context
Browsers do not directly offer the fibres and virtual memory the blueprint assumed. See [platforms](../idea/30-platforms.md).

## Decision
Keep the kernel portable with a thread-only job mode and a page-allocator backend, tested in Phase 0.

## Alternatives
- Add web later: why not, the assumptions would harden and need a rewrite.
- Drop the browser: why not, it is a required target.

## Consequences
A small extra CI target from the first phase.
