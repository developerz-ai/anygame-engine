# 001 — A game is a manifest over a small kernel

Status: accepted
Date: 2026-11-21

## Context
Monolithic engines bake in answers about time, state, authority and the frame, and each answer rules out genres.

## Decision
A small kernel plus replaceable modules. A manifest picks what each game loads.

## Alternatives
- Monolithic engine: why not, it blocks whole genres and every game pays for everything.
- One engine per genre: why not, nothing is shared and each repeats the same foundations.

## Consequences
Every interface must stay public and versioned. Abstraction cost has to be measured.
