# 014 — Wrap proven solvers and script languages

Status: accepted
Date: 2026-11-21

## Context
The project rejects new solvers and languages, but tiered modules need simple implementations and narrative needs a script format.

## Decision
Small kinematic controllers are allowed. Real rigid-body solving wraps a library. Narrative adopts an existing language such as Ink through an adapter.

## Alternatives
- Write a full solver: why not, it is years of specialist work.
- Invent a narrative language: why not, tools and writers already exist.

## Consequences
Library upgrades go through adapters and conformance suites.
