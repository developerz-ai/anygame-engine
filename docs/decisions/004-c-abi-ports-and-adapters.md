# 004 — Modules connect through C ABI ports and adapters

Status: accepted
Date: 2026-11-21

## Context
C++ has no stable ABI across compilers, and everything must be replaceable without a fork.

## Decision
Versioned C function-pointer interfaces, append-only within a major version. Vendors live in adapters.

## Alternatives
- C++ virtual interfaces: why not, no stable ABI, and hot reload breaks.
- Compile-time only plugins: why not, no hot reload and no third-party binaries.

## Consequences
Slight boundary friction, offset by batch APIs and static linking in shipping builds.
