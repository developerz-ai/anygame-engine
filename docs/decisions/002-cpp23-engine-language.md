# 002 — The engine is written in C++23

Status: accepted
Date: 2026-11-21

## Context
The goal is really good, high-performance games on every platform, with control over memory and layout.

## Decision
C++23 for the kernel and native modules.

## Alternatives
- TypeScript: why not, garbage collection and runtime cost rule out the performance target.
- Rust: why not, game middleware and platform SDKs are C and C++, and hot-reload across its unstable ABI needs the same C boundary anyway.

## Consequences
Memory safety comes from discipline and tooling: sanitizers, fuzzing, handles and lints.
