# 003 — Headers plus PCH by default, named modules opt-in

Status: proposed
Date: 2026-11-21

## Context
C++ module support is uneven across compilers, generators and Apple platforms. See [C++23 craft](../idea/16-cpp23-craft.md#-named-modules-or-headers).

## Decision
Headers with PCH by default. A package may opt in to named modules after every Phase 0 platform passes.

## Alternatives
- Modules everywhere: why not, tooling gaps would block platforms.
- Unity builds only: why not, incremental rebuilds suffer, and agents rebuild constantly.

## Consequences
Re-check at each engine major version. Accepted once MSVC and Apple Clang are tested.
