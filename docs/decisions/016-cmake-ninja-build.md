# 016 — The engine builds with CMake and Ninja

Status: accepted
Date: 2026-11-21

## Context
Phase 0 needs one build system across Linux, Windows, macOS, Android, iOS and Emscripten, with fast incremental builds for agents.

## Decision
CMake presets generate Ninja builds. `bin/check` wraps them, so agents never need to remember the commands.

## Alternatives
- Meson: why not, weaker reach across game platform toolchains and vendor SDKs.
- Bazel: why not, heavy setup and a poor fit for a project games must consume easily.

## Consequences
CMake stays thin and declarative. Package metadata lives in `anygame.toml`, and generated CMake is an implementation detail where possible.
