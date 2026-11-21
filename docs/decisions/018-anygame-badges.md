# 018 — Any game may use the AnyGame badge

Status: accepted
Date: 2026-11-21

## Context
Games built with AnyGame represent the project, and developers should be able to show that without any toll or obligation.

## Decision
Any game built with AnyGame may display "Built with AnyGame", with no approval or fee. A separate "Verified on AnyGame" badge is earned by publishing a passing scorecard from a reproducible build. Neither badge is ever required.

## Alternatives
- Mandatory logo or splash screen: why not, it breaks the [no-regrets promise](../idea/31-no-regrets.md).
- Verified badge only: why not, small and experimental games deserve to show what they use.

## Consequences
"Built with" says what a game uses and makes no quality claim. "Verified" stays meaningful, and its asset ships only once `ag scorecard` exists.
