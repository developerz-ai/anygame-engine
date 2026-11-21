# 006 — The core has no GUI editor

Status: accepted
Date: 2026-11-21

## Context
The primary developer is a coding agent, and everything must work headless.

## Decision
Code and text are the authoring surface. A read-mostly live viewer inspects running games.

## Alternatives
- Full visual editor: why not, huge scope, and agents cannot use it directly.
- Editor compiled into the runtime: why not, it adds weight to every game.

## Consequences
Artists rely on existing DCC tools. GUI tools can be community packages.
