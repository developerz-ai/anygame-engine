# 🧭 How we work

Project management for building the engine itself. For games built with it, see [idea to distribution](../idea/25-idea-to-distribution.md).

## The hierarchy

| Level | Example | Owner doc | Size |
|---|---|---|---|
| Phase | Phase 0: Kernel | `docs/build/phase-*.md` | Proves one architectural bet |
| Milestone | Memory system | [status.yml](status.yml) | A demonstrable capability |
| Slice | Generational handles | `docs/build/<phase>-<NN>-<slug>.md` from `/planx` | One agent, one PR |

## Where each fact lives

| Fact | Single home |
|---|---|
| Why and what | `docs/idea/` |
| Order and exit checks | `docs/build/phase-*.md` |
| Current progress | [`docs/build/status.yml`](status.yml) |
| Unresolved conflicts | [open questions](open-questions.md) |
| Hard-to-reverse choices | [`docs/decisions/`](../decisions/README.md) |

## The flow

1. **Decide.** Settle any open question that blocks the work, and record it.
2. **Plan.** `/planx` writes a slice with exact files, steps and checks.
3. **Claim.** Set the slice to `in_progress` in `status.yml`.
4. **Build.** One concern per branch.
5. **Gate.** `bin/check` passes locally.
6. **Review.** CI and CodeRabbit run on the PR.
7. **Merge.** Update `status.yml` with evidence in the same PR.
8. **Prove.** A phase closes only when all its exit checks pass.

## Ready and done

| A slice is ready when | A slice is done when |
|---|---|
| Its goal fits one PR | Its checks pass in CI |
| No open question blocks it | Tests cover the changed behaviour |
| Files and interfaces are named | Budgets are met and the cost is reported |
| Each step has an observable check | Docs and `status.yml` are updated |
| Dependencies are merged | It meets the [quality bar](../idea/32-quality-bar.md) |

## Rules

- **Work in phase order.** A later phase starts only when an earlier one proves its bet.
- **Parallel slices touch separate files.** No git worktrees.
- **A one-way door needs a decision record** in the same PR.
- **Never silently drop a check.** Mark it `[revised]`, state why, and record the new check.
- **Status is evidence, not opinion.** `complete` links to the PR or CI run.
